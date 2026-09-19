"""Ponytail self-check: no framework, just asserts. Run with `python tests/test_engine.py`."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vexoro import engine, signatures

EICAR = (
    r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
).encode()


def test_signature_detection():
    sigs = signatures.load()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "eicar.com")
        with open(p, "wb") as f:
            f.write(EICAR)
        v = engine.scan_file(p, sigs)
        assert v is not None, "EICAR test file should be detected"
        assert v.threat == "EICAR-Test-File"
        assert v.reason == "signature"


def test_clean_file_passes():
    sigs = signatures.load()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "notes.txt")
        with open(p, "w") as f:
            f.write("just a shopping list")
        assert engine.scan_file(p, sigs) is None


def test_double_extension_heuristic():
    sigs = signatures.load()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "invoice.pdf.exe")
        with open(p, "wb") as f:
            f.write(b"not really a pdf")
        v = engine.scan_file(p, sigs)
        assert v is not None
        assert v.threat == "Suspicious.DoubleExtension"


def test_quarantine_roundtrip():
    sigs = signatures.load()
    with tempfile.TemporaryDirectory() as d:
        vault = os.path.join(d, "vault")
        target = os.path.join(d, "eicar.com")
        with open(target, "wb") as f:
            f.write(EICAR)
        v = engine.scan_file(target, sigs)
        q = engine.Quarantine(vault)
        qid = q.commit(v)
        assert not os.path.exists(target)
        assert len(q.list()) == 1
        restored = q.restore(qid)
        assert os.path.exists(restored)
        assert len(q.list()) == 0


if __name__ == "__main__":
    test_signature_detection()
    test_clean_file_passes()
    test_double_extension_heuristic()
    test_quarantine_roundtrip()
    print("All self-checks passed.")
