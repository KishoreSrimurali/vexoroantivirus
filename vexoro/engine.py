"""Core scan engine: hashing, heuristics, quarantine. Stdlib only."""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import time
from dataclasses import dataclass, asdict
from collections import Counter

from . import signatures

CHUNK = 1 << 20  # 1 MiB
ENTROPY_THRESHOLD = 7.5  # ~max is 8.0; high entropy = packed/encrypted payload
SAMPLE_BYTES = 65536


@dataclass
class Verdict:
    path: str
    threat: str
    reason: str  # "signature" | "heuristic"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _looks_like_pe(data: bytes) -> bool:
    return data[:2] == b"MZ"


def scan_file(path: str, sigs: dict[str, str]) -> Verdict | None:
    """Return a Verdict if the file is flagged, else None."""
    try:
        digest = sha256_file(path)
    except OSError:
        return None

    if digest in sigs:
        return Verdict(path, sigs[digest], "signature")

    name = os.path.basename(path)
    parts = name.split(".")
    ext = ("." + parts[-1].lower()) if len(parts) > 1 else ""

    # Double-extension disguise, e.g. "invoice.pdf.exe"
    if len(parts) > 2 and ext in signatures.DANGEROUS_EXTENSIONS:
        return Verdict(path, "Suspicious.DoubleExtension", "heuristic")

    try:
        with open(path, "rb") as f:
            head = f.read(SAMPLE_BYTES)
    except OSError:
        return None

    # Executable content wearing a non-executable extension.
    if _looks_like_pe(head) and ext and ext not in {".exe", ".dll", ".sys", ".scr", ".com", ".msi"}:
        return Verdict(path, "Suspicious.MasqueradedExecutable", "heuristic")

    # High-entropy payload sitting behind a script/executable extension is a
    # common sign of a packed or encrypted dropper. Low-confidence heuristic
    # by design: flags for review, not an auto-detonation signal.
    if ext in signatures.DANGEROUS_EXTENSIONS and _shannon_entropy(head) >= ENTROPY_THRESHOLD:
        return Verdict(path, "Suspicious.HighEntropyPacked", "heuristic")

    return None


def scan_path(root: str, sigs: dict[str, str], progress_cb=None, stop_flag=None) -> list[Verdict]:
    """Walk root recursively, scanning every file. progress_cb(path) is called
    per file; stop_flag is a callable returning True to abort early."""
    verdicts = []
    if os.path.isfile(root):
        files = [root]
    else:
        files = (
            os.path.join(dirpath, fn)
            for dirpath, _, filenames in os.walk(root)
            for fn in filenames
        )
    for path in files:
        if stop_flag and stop_flag():
            break
        if progress_cb:
            progress_cb(path)
        v = scan_file(path, sigs)
        if v:
            verdicts.append(v)
    return verdicts


class Quarantine:
    """Moves flagged files into a sandboxed vault: renamed so they can't be
    double-clicked back into execution, with a JSON sidecar recording where
    they came from so they can be restored."""

    def __init__(self, vault_dir: str):
        self.vault_dir = vault_dir
        os.makedirs(vault_dir, exist_ok=True)

    def _meta_path(self, qid: str) -> str:
        return os.path.join(self.vault_dir, qid + ".json")

    def commit(self, verdict: Verdict) -> str:
        qid = f"{int(time.time() * 1000)}_{os.path.basename(verdict.path)}"
        dest = os.path.join(self.vault_dir, qid + ".quarantined")
        shutil.move(verdict.path, dest)
        meta = {**asdict(verdict), "qid": qid, "quarantined_at": time.time()}
        with open(self._meta_path(qid), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        return qid

    def list(self) -> list[dict]:
        out = []
        for fn in os.listdir(self.vault_dir):
            if fn.endswith(".json"):
                with open(os.path.join(self.vault_dir, fn), encoding="utf-8") as f:
                    out.append(json.load(f))
        return sorted(out, key=lambda m: m["quarantined_at"], reverse=True)

    def restore(self, qid: str) -> str:
        with open(self._meta_path(qid), encoding="utf-8") as f:
            meta = json.load(f)
        src = os.path.join(self.vault_dir, qid + ".quarantined")
        dest = meta["path"]
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        shutil.move(src, dest)
        os.remove(self._meta_path(qid))
        return dest

    def delete(self, qid: str) -> None:
        quarantined = os.path.join(self.vault_dir, qid + ".quarantined")
        if os.path.exists(quarantined):
            os.remove(quarantined)
        meta = self._meta_path(qid)
        if os.path.exists(meta):
            os.remove(meta)
