"""Windows autorun/startup inspector. Reads the standard Run keys via winreg
(stdlib) so users can see, at a glance, everything set to launch at login —
a common persistence spot for malware. No-op with an empty list on non-Windows.
"""
import sys

RUN_KEYS = [
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKCU"),
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM"),
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKLM"),
]


def list_autoruns() -> list[dict]:
    if sys.platform != "win32":
        return []
    import winreg

    hives = {"HKCU": winreg.HKEY_CURRENT_USER, "HKLM": winreg.HKEY_LOCAL_MACHINE}
    entries = []
    for subkey, hive_name in RUN_KEYS:
        try:
            with winreg.OpenKey(hives[hive_name], subkey) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        entries.append({"hive": hive_name, "key": subkey, "name": name, "command": value})
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
    return entries
