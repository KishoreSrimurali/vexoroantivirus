# Vexoro Antivirus

A desktop antivirus app for Windows: on-demand scanning, real-time folder
protection, quarantine, and a startup-programs (autorun) inspector — with a
dark tkinter UI. Pure Python standard library, no third-party dependencies.

## Run it

```
python main.py
```

Requires Python 3.10+ with tkinter (bundled with the official python.org
Windows installer — tick "tcl/tk" if you customized the install).

## How detection works

- **Signature matching** — SHA-256 of every scanned file against a hash
  database (`~/.vexoro/signatures.json`, seeded with the built-in EICAR test
  signature). Point that file at a larger hash feed to extend coverage.
- **Heuristics** — double-extension disguises (`invoice.pdf.exe`), PE
  executables wearing a non-executable extension, and high-entropy payloads
  behind script/executable extensions (packed/encrypted dropper signal).
- **Real-time protection** — a background thread polls watched folders
  (default: Downloads, Desktop) every 2s for new/changed files and
  auto-quarantines detections.
- **Quarantine** — flagged files are moved to `~/.vexoro/quarantine`, renamed
  so they can't be executed by double-click, restorable from the UI.
- **Startup inspector** — lists everything registered in the Windows
  `Run`/`RunOnce` registry keys, a common persistence spot for malware.

Try it: create a text file containing the EICAR test string
(`X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*`,
industry-standard, completely harmless) and scan the folder it's in.

## Tests

```
python tests/test_engine.py
```

## Build a standalone .exe (on Windows)

```
pip install pyinstaller
pyinstaller --noconsole --onefile --name VexoroAntivirus main.py
```

The binary lands in `dist/VexoroAntivirus.exe`.

## Scope

This is a real, working scanner (hash + heuristic detection, quarantine,
real-time watch, autorun audit) — not a mock. It ships with one built-in
signature (EICAR) rather than a proprietary malware corpus; production use
means feeding it a real hash database via `signatures.json`.
