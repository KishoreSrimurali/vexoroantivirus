"""Vexoro Antivirus — desktop GUI (tkinter, stdlib, ships with every
Windows Python install)."""
from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import autorun, engine, signatures

APP_DIR = os.path.join(os.path.expanduser("~"), ".vexoro")
QUARANTINE_DIR = os.path.join(APP_DIR, "quarantine")
DEFAULT_TARGETS = [os.path.expanduser("~/Downloads"), os.path.expanduser("~/Desktop")]

BG = "#0f1420"
PANEL = "#161d2e"
ACCENT = "#00e5a8"
TEXT = "#e6ecf5"
MUTED = "#7c8aa5"
DANGER = "#ff5470"


class VexoroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vexoro Antivirus")
        self.geometry("880x600")
        self.configure(bg=BG)
        self.minsize(760, 520)

        self.sigs = signatures.load(os.path.join(APP_DIR, "signatures.json"))
        self.quarantine = engine.Quarantine(QUARANTINE_DIR)
        self.monitor: engine.RealTimeMonitor | None = None
        self._scan_stop = False

        self._style()
        self._build_layout()
        self.refresh_quarantine()

    # ---------- styling ----------
    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT, padding=(16, 8))
        style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "#00140f")])
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground=ACCENT)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("TButton", padding=8, font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", background=ACCENT, foreground="#00140f")
        style.map("Accent.TButton", background=[("active", "#00c795")])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=26, borderwidth=0)
        style.configure("Treeview.Heading", background=BG, foreground=MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("TProgressbar", background=ACCENT, troughcolor=PANEL)

    def _build_layout(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=(16, 8))
        ttk.Label(header, text="🛡  Vexoro Antivirus", style="Header.TLabel").pack(side="left")
        self.status_label = ttk.Label(header, text=f"{len(self.sigs)} signatures loaded", style="Muted.TLabel")
        self.status_label.pack(side="right")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=20, pady=10)

        self.scan_tab = ttk.Frame(nb)
        self.protect_tab = ttk.Frame(nb)
        self.quarantine_tab = ttk.Frame(nb)
        self.autorun_tab = ttk.Frame(nb)
        nb.add(self.scan_tab, text="  Scan  ")
        nb.add(self.protect_tab, text="  Real-Time Protection  ")
        nb.add(self.quarantine_tab, text="  Quarantine  ")
        nb.add(self.autorun_tab, text="  Startup Programs  ")

        self._build_scan_tab()
        self._build_protect_tab()
        self._build_quarantine_tab()
        self._build_autorun_tab()

    # ---------- scan tab ----------
    def _build_scan_tab(self):
        t = self.scan_tab
        top = ttk.Frame(t)
        top.pack(fill="x", pady=(8, 12))
        self.target_var = tk.StringVar(value=os.path.expanduser("~"))
        entry = tk.Entry(top, textvariable=self.target_var, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                          relief="flat", font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        ttk.Button(top, text="Browse", command=self._browse).pack(side="left", padx=4)
        self.scan_btn = ttk.Button(top, text="Scan", style="Accent.TButton", command=self._start_scan)
        self.scan_btn.pack(side="left", padx=4)

        self.progress = ttk.Progressbar(t, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 4))
        self.scan_status = ttk.Label(t, text="Idle", style="Muted.TLabel")
        self.scan_status.pack(anchor="w")

        cols = ("path", "threat", "reason")
        self.results = ttk.Treeview(t, columns=cols, show="headings", height=14)
        for c, w in zip(cols, (460, 220, 100)):
            self.results.heading(c, text=c.capitalize())
            self.results.column(c, width=w, anchor="w")
        self.results.pack(fill="both", expand=True, pady=8)

        actions = ttk.Frame(t)
        actions.pack(fill="x")
        ttk.Button(actions, text="Quarantine Selected", command=self._quarantine_selected).pack(side="left")

        self._scan_verdicts: dict[str, engine.Verdict] = {}

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.target_var.get())
        if d:
            self.target_var.set(d)

    def _start_scan(self):
        target = self.target_var.get()
        if not os.path.exists(target):
            messagebox.showerror("Vexoro", "That path doesn't exist.")
            return
        self.results.delete(*self.results.get_children())
        self._scan_verdicts.clear()
        self._scan_stop = False
        self.scan_btn.config(text="Stop", command=self._stop_scan)
        threading.Thread(target=self._scan_worker, args=(target,), daemon=True).start()

    def _stop_scan(self):
        self._scan_stop = True

    def _scan_worker(self, target: str):
        total = self._count_files(target)
        self.progress.config(maximum=max(total, 1), value=0)
        seen = 0
        found = []

        def progress_cb(path):
            nonlocal seen
            seen += 1
            self.after(0, self._update_progress, seen, path)

        verdicts = engine.scan_path(target, self.sigs, progress_cb, stop_flag=lambda: self._scan_stop)
        found.extend(verdicts)
        self.after(0, self._scan_done, found)

    def _count_files(self, target: str) -> int:
        if os.path.isfile(target):
            return 1
        n = 0
        for _, _, files in os.walk(target):
            n += len(files)
        return n

    def _update_progress(self, seen, path):
        self.progress.config(value=seen)
        self.scan_status.config(text=f"Scanning: {path}")

    def _scan_done(self, verdicts: list[engine.Verdict]):
        self.scan_btn.config(text="Scan", command=self._start_scan)
        self.scan_status.config(text=f"Done. {len(verdicts)} threat(s) found." if verdicts else "Done. Clean.")
        for v in verdicts:
            iid = self.results.insert("", "end", values=(v.path, v.threat, v.reason))
            self._scan_verdicts[iid] = v

    def _quarantine_selected(self):
        for iid in self.results.selection():
            verdict = self._scan_verdicts.get(iid)
            if not verdict or not os.path.exists(verdict.path):
                continue
            self.quarantine.commit(verdict)
            self.results.delete(iid)
        self.refresh_quarantine()

    # ---------- real-time protection tab ----------
    def _build_protect_tab(self):
        t = self.protect_tab
        ttk.Label(t, text="Watched folders", style="Header.TLabel").pack(anchor="w", pady=(8, 4))
        ttk.Label(t, text="New or modified files in these folders are scanned automatically and "
                           "quarantined on detection.", style="Muted.TLabel", wraplength=760).pack(anchor="w", pady=(0, 8))

        self.watch_list = tk.Listbox(t, bg=PANEL, fg=TEXT, height=6, relief="flat",
                                      selectbackground=ACCENT, font=("Segoe UI", 10))
        for d in DEFAULT_TARGETS:
            self.watch_list.insert("end", d)
        self.watch_list.pack(fill="x", pady=4)

        row = ttk.Frame(t)
        row.pack(fill="x", pady=4)
        ttk.Button(row, text="Add Folder", command=self._add_watch).pack(side="left")
        ttk.Button(row, text="Remove Selected", command=self._remove_watch).pack(side="left", padx=8)

        self.protect_toggle = ttk.Button(t, text="Enable Real-Time Protection", style="Accent.TButton",
                                          command=self._toggle_protection)
        self.protect_toggle.pack(anchor="w", pady=12)
        self.protect_status = ttk.Label(t, text="Protection is OFF", style="Muted.TLabel")
        self.protect_status.pack(anchor="w")

        ttk.Label(t, text="Detections", style="Header.TLabel").pack(anchor="w", pady=(16, 4))
        self.protect_log = tk.Listbox(t, bg=PANEL, fg=DANGER, height=8, relief="flat", font=("Consolas", 9))
        self.protect_log.pack(fill="both", expand=True)

    def _add_watch(self):
        d = filedialog.askdirectory()
        if d:
            self.watch_list.insert("end", d)

    def _remove_watch(self):
        for i in reversed(self.watch_list.curselection()):
            self.watch_list.delete(i)

    def _toggle_protection(self):
        if self.monitor and self.monitor.running:
            self.monitor.stop()
            self.protect_toggle.config(text="Enable Real-Time Protection")
            self.protect_status.config(text="Protection is OFF")
        else:
            dirs = list(self.watch_list.get(0, "end"))
            if not dirs:
                messagebox.showwarning("Vexoro", "Add at least one folder to watch.")
                return
            self.monitor = engine.RealTimeMonitor(dirs, self.sigs, self.quarantine, on_detect=self._on_detect)
            self.monitor.start()
            self.protect_toggle.config(text="Disable Real-Time Protection")
            self.protect_status.config(text=f"Protection is ON — watching {len(dirs)} folder(s)")

    def _on_detect(self, verdict: engine.Verdict, qid: str):
        self.after(0, lambda: (
            self.protect_log.insert(0, f"[{verdict.threat}] {verdict.path} -> quarantined ({qid})"),
            self.refresh_quarantine(),
        ))

    # ---------- quarantine tab ----------
    def _build_quarantine_tab(self):
        t = self.quarantine_tab
        cols = ("threat", "original_path", "when")
        self.q_tree = ttk.Treeview(t, columns=cols, show="headings", height=16)
        for c, w in zip(cols, (200, 420, 160)):
            self.q_tree.heading(c, text=c.replace("_", " ").capitalize())
            self.q_tree.column(c, width=w, anchor="w")
        self.q_tree.pack(fill="both", expand=True, pady=8)

        row = ttk.Frame(t)
        row.pack(fill="x")
        ttk.Button(row, text="Restore", command=self._restore_selected).pack(side="left")
        ttk.Button(row, text="Delete Permanently", command=self._delete_selected).pack(side="left", padx=8)
        ttk.Button(row, text="Refresh", command=self.refresh_quarantine).pack(side="left")

    def refresh_quarantine(self):
        self.q_tree.delete(*self.q_tree.get_children())
        import datetime
        for meta in self.quarantine.list():
            when = datetime.datetime.fromtimestamp(meta["quarantined_at"]).strftime("%Y-%m-%d %H:%M")
            self.q_tree.insert("", "end", iid=meta["qid"], values=(meta["threat"], meta["path"], when))

    def _restore_selected(self):
        for qid in self.q_tree.selection():
            try:
                self.quarantine.restore(qid)
            except FileNotFoundError:
                pass
        self.refresh_quarantine()

    def _delete_selected(self):
        for qid in self.q_tree.selection():
            self.quarantine.delete(qid)
        self.refresh_quarantine()

    # ---------- autorun tab ----------
    def _build_autorun_tab(self):
        t = self.autorun_tab
        ttk.Label(t, text="Programs that launch at login", style="Header.TLabel").pack(anchor="w", pady=(8, 4))
        cols = ("name", "command", "location")
        self.autorun_tree = ttk.Treeview(t, columns=cols, show="headings", height=16)
        for c, w in zip(cols, (160, 480, 140)):
            self.autorun_tree.heading(c, text=c.capitalize())
            self.autorun_tree.column(c, width=w, anchor="w")
        self.autorun_tree.pack(fill="both", expand=True, pady=8)
        ttk.Button(t, text="Refresh", command=self._refresh_autorun).pack(anchor="w")
        self._refresh_autorun()

    def _refresh_autorun(self):
        self.autorun_tree.delete(*self.autorun_tree.get_children())
        entries = autorun.list_autoruns()
        if not entries and sys.platform != "win32":
            self.autorun_tree.insert("", "end", values=("(unavailable)", "Startup scan requires Windows", ""))
            return
        for e in entries:
            self.autorun_tree.insert("", "end", values=(e["name"], e["command"], f'{e["hive"]}\\{e["key"]}'))


def main():
    os.makedirs(APP_DIR, exist_ok=True)
    app = VexoroApp()
    app.mainloop()


if __name__ == "__main__":
    main()
