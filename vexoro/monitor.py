"""Real-time protection: a background thread that polls watched folders for
new/changed files and scans them on sight. Stdlib-only polling (no watchdog
dependency) — fine at desktop scale, upgrade to OS filesystem-event APIs
(ReadDirectoryChangesW / watchdog) if you need sub-second reaction on huge trees.
"""
from __future__ import annotations

import os
import threading
import time

from . import engine


class RealTimeMonitor:
    def __init__(self, watched_dirs: list[str], sigs: dict, quarantine: engine.Quarantine,
                 on_detect=None, interval: float = 2.0):
        self.watched_dirs = watched_dirs
        self.sigs = sigs
        self.quarantine = quarantine
        self.on_detect = on_detect
        self.interval = interval
        self._seen: dict[str, float] = {}
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 1)

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self) -> None:
        while not self._stop.is_set():
            for base in self.watched_dirs:
                if not os.path.isdir(base):
                    continue
                for dirpath, _, filenames in os.walk(base):
                    for fn in filenames:
                        path = os.path.join(dirpath, fn)
                        try:
                            mtime = os.path.getmtime(path)
                        except OSError:
                            continue
                        if self._seen.get(path) == mtime:
                            continue
                        self._seen[path] = mtime
                        verdict = engine.scan_file(path, self.sigs)
                        if verdict:
                            qid = self.quarantine.commit(verdict)
                            if self.on_detect:
                                self.on_detect(verdict, qid)
            self._stop.wait(self.interval)
