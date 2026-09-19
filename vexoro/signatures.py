"""Signature database: sha256 -> threat name.

Ships with the standard EICAR antivirus test signature (safe, industry-standard
test string) so the engine is verifiably functional out of the box. Point
--signatures at a bigger feed (e.g. an exported hash set) to extend it.
"""
import json
import os

BUILTIN = {
    # EICAR standard antivirus test file (harmless, used to verify AV engines)
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f": "EICAR-Test-File",
}

# Extensions that should basically never run themselves out of a Downloads/
# email attachment folder without the user knowing.
DANGEROUS_EXTENSIONS = {
    ".exe", ".scr", ".pif", ".bat", ".cmd", ".com", ".vbs", ".vbe", ".js",
    ".jse", ".wsf", ".wsh", ".ps1", ".msi", ".jar", ".hta",
}


def load(path: str | None = None) -> dict[str, str]:
    sigs = dict(BUILTIN)
    if path and os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            sigs.update({k.lower(): v for k, v in json.load(f).items()})
    return sigs
