# -*- coding: utf-8 -*-
"""
SecureSH - SSH/SFTP Browser + Terminal
SSHv2 · private key auth · Duo/2FA · port 10022
Sessions saved to %APPDATA%/SecureSH/sessions.json
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import socket  as _socket
import queue   as _queue
import os
import re
import stat
import json
import time
import paramiko

# ─────────────────────────────────────────────
#  Theme
# ─────────────────────────────────────────────
BG          = "#ffffff"
BG2         = "#f7f7f7"
SIDEBAR_BG  = "#f0f2f5"
ACCENT      = "#0078d4"
ACCENT_HOV  = "#106ebe"
ACCENT_ACT  = "#005a9e"
TEXT        = "#1b1b1b"
TEXT2       = "#6e6e6e"
BORDER      = "#dde1e6"
SEL_BG      = "#d0e7f8"
HOV_BG      = "#e8f2fb"
SUCCESS_FG  = "#107c10"
WARN_FG     = "#ca5010"
ERR_FG      = "#c42b1c"
TERM_BG     = "#1e1e1e"
TERM_FG     = "#d4d4d4"

_UI   = ("Segoe UI", 9)
_UIsm = ("Segoe UI", 8)
_UIb  = ("Segoe UI", 9,  "bold")
_UIh  = ("Segoe UI", 11, "bold")
_MONO = ("Consolas", 10)


def _apply_theme(root: tk.Tk):
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(bg=BG)

    s.configure(".",
        background=BG, foreground=TEXT,
        font=_UI, borderwidth=0, focuscolor=ACCENT)

    # ── Frames ──
    s.configure("TFrame",        background=BG)
    s.configure("Sidebar.TFrame", background=SIDEBAR_BG)
    s.configure("Card.TFrame",   background=BG,
                relief="flat", borderwidth=1)

    # ── Labels ──
    s.configure("TLabel",       background=BG,         foreground=TEXT)
    s.configure("Dim.TLabel",   background=BG,         foreground=TEXT2,  font=_UIsm)
    s.configure("Sidebar.TLabel", background=SIDEBAR_BG, foreground=TEXT)
    s.configure("SHdr.TLabel",  background=SIDEBAR_BG, foreground=TEXT2,
                font=("Segoe UI", 8, "bold"))
    s.configure("Success.TLabel", background=BG, foreground=SUCCESS_FG)
    s.configure("Warn.TLabel",    background=BG, foreground=WARN_FG)

    # ── Buttons ──
    s.configure("TButton",
        background=BG2, foreground=TEXT,
        relief="flat", borderwidth=1,
        padding=(10, 5), font=_UI,
        bordercolor=BORDER)
    s.map("TButton",
        background=[("active", HOV_BG), ("pressed", SEL_BG)],
        bordercolor=[("focus", ACCENT)])

    s.configure("Accent.TButton",
        background=ACCENT, foreground="white",
        relief="flat", borderwidth=0,
        padding=(12, 5), font=_UIb)
    s.map("Accent.TButton",
        background=[("active", ACCENT_HOV), ("pressed", ACCENT_ACT)])

    s.configure("Ghost.TButton",
        background=SIDEBAR_BG, foreground=ACCENT,
        relief="flat", borderwidth=0, padding=(6, 3))
    s.map("Ghost.TButton",
        background=[("active", HOV_BG)])

    s.configure("Danger.TButton",
        background=BG2, foreground=ERR_FG,
        relief="flat", borderwidth=1, padding=(10, 5),
        bordercolor=BORDER)
    s.map("Danger.TButton",
        background=[("active", "#fde7e9")])

    # ── Entry ──
    s.configure("TEntry",
        fieldbackground="white", foreground=TEXT,
        borderwidth=1, relief="solid",
        padding=(6, 4), bordercolor=BORDER,
        insertcolor=TEXT)
    s.map("TEntry",
        bordercolor=[("focus", ACCENT)])

    # ── Combobox ──
    s.configure("TCombobox",
        fieldbackground="white", foreground=TEXT,
        borderwidth=1, relief="solid",
        padding=(4, 3), bordercolor=BORDER)
    s.map("TCombobox",
        bordercolor=[("focus", ACCENT)])

    # ── Notebook ──
    s.configure("TNotebook",
        background=BG2, borderwidth=0, tabmargins=0)
    s.configure("TNotebook.Tab",
        background=BG2, foreground=TEXT2,
        padding=(14, 7), borderwidth=0, font=_UI)
    s.map("TNotebook.Tab",
        background=[("selected", BG),  ("active", HOV_BG)],
        foreground=[("selected", ACCENT)],
        expand=[("selected", [0, 0, 0, 2])])

    # ── Treeview (file list) ──
    s.configure("Treeview",
        background="white", fieldbackground="white",
        foreground=TEXT, rowheight=26,
        borderwidth=0, relief="flat")
    s.configure("Treeview.Heading",
        background=BG2, foreground=TEXT2,
        relief="flat", padding=(6, 5), font=_UIsm)
    s.map("Treeview",
        background=[("selected", SEL_BG)],
        foreground=[("selected", TEXT)])

    # ── Sidebar Treeview ──
    s.configure("Sidebar.Treeview",
        background=SIDEBAR_BG, fieldbackground=SIDEBAR_BG,
        foreground=TEXT, rowheight=28, font=_UI,
        borderwidth=0, relief="flat", indent=14)
    s.map("Sidebar.Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "white")])

    # ── Scrollbar ──
    s.configure("TScrollbar",
        background=BG2, troughcolor=BG2,
        borderwidth=0, arrowsize=13,
        relief="flat")
    s.map("TScrollbar",
        background=[("active", BORDER), ("pressed", TEXT2)])

    # ── Separator ──
    s.configure("TSeparator", background=BORDER)

    # ── Checkbutton ──
    s.configure("TCheckbutton",
        background=BG, foreground=TEXT, font=_UI)
    s.map("TCheckbutton", background=[("active", BG)])

    # ── Progressbar (future use) ──
    s.configure("TProgressbar",
        troughcolor=BG2, background=ACCENT, borderwidth=0)


# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────
DEFAULT_PORT  = 10022
DEFAULT_KEY   = r"C:\Users\me\.ssh\tgt"
APP_DIR       = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")), "SecureSH")
SESSIONS_FILE = os.path.join(APP_DIR, "sessions.json")

FOLDER_PFX  = "folder|"
SESSION_PFX = "session|"


# ─────────────────────────────────────────────
#  Session persistence
# ─────────────────────────────────────────────
def _ensure_app_dir():
    os.makedirs(APP_DIR, exist_ok=True)

def load_sessions() -> list[dict]:
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_sessions(sessions: list[dict]):
    _ensure_app_dir()
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


# ─────────────────────────────────────────────
#  Keyboard-interactive / Duo dialog  (fixed)
# ─────────────────────────────────────────────
class KeyboardInteractiveDialog(tk.Toplevel):
    """
    Clean dialog for Duo / OTP / any keyboard-interactive challenge.
    Shows server instructions in a styled info box, then one entry per prompt.
    """
    def __init__(self, parent,
                 title: str, instructions: str,
                 fields: list[tuple[str, bool]]):
        super().__init__(parent)
        self.title(title.strip() or "Authentication Required")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.responses = None

        pad = dict(padx=20, pady=6)

        # ── Instructions box ──────────────────────────
        if instructions and instructions.strip():
            box = tk.Frame(self, bg="#e8f4fb",
                           highlightbackground="#b3d7f0",
                           highlightthickness=1)
            box.pack(fill="x", padx=16, pady=(16, 8))
            tk.Label(box, text=instructions.strip(),
                     bg="#e8f4fb", fg=TEXT,
                     font=("Consolas", 9),
                     justify="left", wraplength=400,
                     padx=12, pady=10).pack(fill="x")

        # ── Prompt fields ─────────────────────────────
        field_frame = ttk.Frame(self)
        field_frame.pack(fill="x", padx=16, pady=4)

        self._entries: list[ttk.Entry] = []
        for row_idx, (prompt, echo) in enumerate(fields):
            ttk.Label(field_frame, text=prompt.strip(),
                      style="TLabel").grid(
                row=row_idx, column=0,
                sticky="w", padx=(0, 10), pady=5)
            e = ttk.Entry(field_frame, show="" if echo else "*", width=28)
            e.grid(row=row_idx, column=1, sticky="ew", pady=5)
            self._entries.append(e)

        field_frame.columnconfigure(1, weight=1)

        # ── Buttons ───────────────────────────────────
        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=16, pady=(8, 0))

        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=16, pady=12)
        ttk.Button(btn_row, text="Cancel", command=self._cancel,
                   width=10).pack(side="right", padx=(6, 0))
        ttk.Button(btn_row, text="OK", command=self._ok,
                   style="Accent.TButton", width=10).pack(side="right")

        if self._entries:
            self._entries[0].focus_set()
        self.bind("<Return>", lambda _: self._ok())
        self.bind("<Escape>", lambda _: self._cancel())

        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(),     parent.winfo_y()
        w,  h  = self.winfo_width(),   self.winfo_height()
        self.geometry(f"+{px + (pw-w)//2}+{py + (ph-h)//2}")

        self.grab_set()
        self.wait_window()

    def _ok(self):
        self.responses = [e.get() for e in self._entries]
        self.destroy()

    def _cancel(self):
        self.responses = None
        self.destroy()


# ─────────────────────────────────────────────
#  Connect / Session dialog
# ─────────────────────────────────────────────
class ConnectDialog(tk.Toplevel):
    def __init__(self, parent, prefill: dict | None = None,
                 existing_folders: list[str] | None = None):
        super().__init__(parent)
        self.title("New Connection" if not prefill else "Edit Connection")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.result  = None
        self.session = None

        existing_folders = existing_folders or []

        # ── Header ───────────────────────────────────
        hdr = tk.Frame(self, bg=ACCENT, height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr,
                 text="Edit Connection" if prefill else "New Connection",
                 bg=ACCENT, fg="white",
                 font=("Segoe UI", 11, "bold")).pack(
            side="left", padx=16, pady=12)

        # ── Body ─────────────────────────────────────
        body = ttk.Frame(self)
        body.pack(fill="both", padx=24, pady=16)

        def row(r, label, widget_factory):
            ttk.Label(body, text=label, style="Dim.TLabel").grid(
                row=r, column=0, sticky="w", pady=(0, 2))
            w = widget_factory(body)
            w.grid(row=r+1, column=0, columnspan=2,
                   sticky="ew", pady=(0, 10))
            return w

        # Session name
        ttk.Label(body, text="SESSION NAME", style="Dim.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 2))
        self.session_name = ttk.Entry(body, width=38)
        if prefill:
            self.session_name.insert(0, prefill.get("name", ""))
        self.session_name.grid(row=1, column=0, columnspan=2,
                               sticky="ew", pady=(0, 10))

        # Folder
        ttk.Label(body, text="FOLDER (optional)", style="Dim.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 2))
        self.folder = ttk.Combobox(body, values=existing_folders, width=36)
        if prefill:
            self.folder.set(prefill.get("folder", ""))
        self.folder.grid(row=3, column=0, columnspan=2,
                         sticky="ew", pady=(0, 10))

        ttk.Separator(body, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # Host + Port on same line
        ttk.Label(body, text="HOST", style="Dim.TLabel").grid(
            row=5, column=0, sticky="w", pady=(0, 2))
        ttk.Label(body, text="PORT", style="Dim.TLabel").grid(
            row=5, column=1, sticky="w", padx=(8, 0), pady=(0, 2))
        self.host = ttk.Entry(body, width=28)
        if prefill:
            self.host.insert(0, prefill.get("host", ""))
        self.host.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        self.port = ttk.Entry(body, width=8)
        self.port.insert(0, str(prefill.get("port", DEFAULT_PORT))
                         if prefill else str(DEFAULT_PORT))
        self.port.grid(row=6, column=1, sticky="w",
                       padx=(8, 0), pady=(0, 10))

        # Username
        ttk.Label(body, text="USERNAME", style="Dim.TLabel").grid(
            row=7, column=0, sticky="w", pady=(0, 2))
        self.user = ttk.Entry(body, width=38)
        if prefill:
            self.user.insert(0, prefill.get("username", ""))
        self.user.grid(row=8, column=0, columnspan=2,
                       sticky="ew", pady=(0, 10))

        # Private key
        ttk.Label(body, text="PRIVATE KEY", style="Dim.TLabel").grid(
            row=9, column=0, sticky="w", pady=(0, 2))
        krow = ttk.Frame(body)
        krow.grid(row=10, column=0, columnspan=2,
                  sticky="ew", pady=(0, 10))
        self.key_path = ttk.Entry(krow)
        self.key_path.pack(side="left", fill="x", expand=True)
        self.key_path.insert(
            0, prefill.get("key_path", DEFAULT_KEY) if prefill else DEFAULT_KEY)
        ttk.Button(krow, text="Browse…", command=self._browse_key,
                   width=9).pack(side="left", padx=(6, 0))

        # Passphrase
        ttk.Label(body, text="KEY PASSPHRASE (if any)", style="Dim.TLabel").grid(
            row=11, column=0, sticky="w", pady=(0, 2))
        self.passphrase = ttk.Entry(body, show="●", width=38)
        self.passphrase.grid(row=12, column=0, columnspan=2,
                             sticky="ew", pady=(0, 10))

        # Save checkbox
        self.save_var = tk.BooleanVar(value=bool(prefill))
        ttk.Checkbutton(body, text="Save / update this session",
                        variable=self.save_var).grid(
            row=13, column=0, columnspan=2, sticky="w")

        body.columnconfigure(0, weight=1)

        # ── Footer ───────────────────────────────────
        ttk.Separator(self, orient="horizontal").pack(fill="x")
        foot = ttk.Frame(self)
        foot.pack(fill="x", padx=24, pady=12)
        ttk.Button(foot, text="Cancel", command=self.destroy,
                   width=10).pack(side="right", padx=(6, 0))
        ttk.Button(foot, text="Connect", command=self._ok,
                   style="Accent.TButton", width=10).pack(side="right")

        self.host.focus_set()
        self.bind("<Return>", lambda _: self._ok())
        self.grab_set()
        self.wait_window()

    def _browse_key(self):
        path = filedialog.askopenfilename(
            title="Select private key",
            initialdir=os.path.expanduser("~"))
        if path:
            self.key_path.delete(0, "end")
            self.key_path.insert(0, path)

    def _ok(self):
        host = self.host.get().strip()
        if not host:
            messagebox.showerror("Error", "Host is required.", parent=self)
            return
        try:
            port = int(self.port.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Port must be a number.", parent=self)
            return
        self.result = {
            "host":       host,
            "port":       port,
            "username":   self.user.get().strip(),
            "key_path":   self.key_path.get().strip(),
            "passphrase": self.passphrase.get() or None,
        }
        if self.save_var.get():
            name   = (self.session_name.get().strip()
                      or f"{self.result['username']}@{host}:{port}")
            folder = self.folder.get().strip()
            self.session = {
                "name":     name,
                "host":     host,
                "port":     port,
                "username": self.result["username"],
                "key_path": self.result["key_path"],
            }
            if folder:
                self.session["folder"] = folder
        self.destroy()


# ─────────────────────────────────────────────
#  Sessions sidebar  (with folder grouping)
# ─────────────────────────────────────────────
class SessionsSidebar(tk.Frame):
    def __init__(self, parent, on_connect, on_new):
        super().__init__(parent, bg=SIDEBAR_BG)
        self.on_connect = on_connect   # (session_dict) → None
        self.on_new     = on_new       # () → None
        self._sessions: list[dict] = load_sessions()

        self._build_ui()
        self._repopulate()

    # ── Build ────────────────────────────────────

    def _build_ui(self):
        # Header row
        hdr = tk.Frame(self, bg=SIDEBAR_BG)
        hdr.pack(fill="x", padx=10, pady=(12, 4))
        tk.Label(hdr, text="SESSIONS", bg=SIDEBAR_BG,
                 fg=TEXT2, font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(hdr, text="+ New", bg=SIDEBAR_BG, fg=ACCENT,
                  bd=0, relief="flat", cursor="hand2",
                  font=("Segoe UI", 8, "bold"),
                  activebackground=SIDEBAR_BG, activeforeground=ACCENT_HOV,
                  command=self.on_new).pack(side="right")

        # Treeview
        tv_frame = tk.Frame(self, bg=SIDEBAR_BG)
        tv_frame.pack(fill="both", expand=True, padx=4, pady=2)

        self.tree = ttk.Treeview(tv_frame, style="Sidebar.Treeview",
                                  show="tree", selectmode="browse")
        vsb = ttk.Scrollbar(tv_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>",  self._on_double_click)
        self.tree.bind("<Button-3>",  self._ctx_menu)
        self.tree.bind("<Return>",    lambda _: self._quick_connect())

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=4)

        # Button grid
        grid = tk.Frame(self, bg=SIDEBAR_BG)
        grid.pack(fill="x", padx=8, pady=8)

        btns = [
            ("Connect", self._quick_connect, "Accent.TButton"),
            ("Edit",    self._edit,          "TButton"),
            ("Delete",  self._delete,        "Danger.TButton"),
            ("Export",  self._export,        "TButton"),
            ("Import",  self._import,        "TButton"),
        ]
        for i, (label, cmd, style) in enumerate(btns):
            r, c = divmod(i, 2)
            ttk.Button(grid, text=label, command=cmd,
                       style=style).grid(
                row=r, column=c, padx=2, pady=2, sticky="ew")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    # ── Data helpers ─────────────────────────────

    def _folders(self) -> list[str]:
        return sorted({s["folder"] for s in self._sessions if s.get("folder")})

    def _session_by_name(self, name: str) -> dict | None:
        return next((s for s in self._sessions if s["name"] == name), None)

    def _save(self):
        save_sessions(self._sessions)

    def upsert(self, session: dict):
        for i, s in enumerate(self._sessions):
            if s["name"] == session["name"]:
                self._sessions[i] = session
                self._repopulate()
                self._save()
                return
        self._sessions.append(session)
        self._repopulate()
        self._save()

    # ── Tree population ──────────────────────────

    def _repopulate(self):
        # Remember which folders were open
        open_folders = {
            iid for iid in self.tree.get_children()
            if self.tree.item(iid, "open")
        }
        self.tree.delete(*self.tree.get_children())

        folders = self._folders()

        # Insert folder nodes
        folder_iids: dict[str, str] = {}
        for folder in folders:
            fid = FOLDER_PFX + folder
            was_open = fid in open_folders or True   # default open
            self.tree.insert("", "end", iid=fid,
                             text=f"  📁  {folder}",
                             open=was_open,
                             tags=("folder",))
            folder_iids[folder] = fid

        # Insert sessions
        for s in self._sessions:
            folder = s.get("folder", "")
            sid    = SESSION_PFX + s["name"]
            parent = folder_iids.get(folder, "") if folder else ""
            self.tree.insert(parent, "end", iid=sid,
                             text=f"  {s['name']}",
                             tags=("session",))

        self.tree.tag_configure("folder",  foreground=ACCENT,   font=_UIb)
        self.tree.tag_configure("session", foreground=TEXT)

    # ── Selection helpers ────────────────────────

    def _sel_iid(self) -> str | None:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _sel_session(self) -> dict | None:
        iid = self._sel_iid()
        if not iid or not iid.startswith(SESSION_PFX):
            return None
        return self._session_by_name(iid[len(SESSION_PFX):])

    def _sel_folder(self) -> str | None:
        iid = self._sel_iid()
        if not iid or not iid.startswith(FOLDER_PFX):
            return None
        return iid[len(FOLDER_PFX):]

    # ── Events ───────────────────────────────────

    def _on_double_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid and iid.startswith(SESSION_PFX):
            self._quick_connect()

    def _ctx_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
        m = tk.Menu(self, tearoff=0, font=_UI,
                    bg=BG, fg=TEXT, activebackground=SEL_BG,
                    activeforeground=TEXT, relief="flat",
                    bd=1)
        if iid and iid.startswith(SESSION_PFX):
            m.add_command(label="Connect",        command=self._quick_connect)
            m.add_command(label="Edit…",          command=self._edit)
            m.add_separator()
            m.add_command(label="Move to Folder…",command=self._move_to_folder)
            m.add_separator()
            m.add_command(label="Delete",         command=self._delete)
        elif iid and iid.startswith(FOLDER_PFX):
            m.add_command(label="Rename Folder…", command=self._rename_folder)
            m.add_separator()
            m.add_command(label="Delete Folder…", command=self._delete_folder)
        else:
            m.add_command(label="New Connection…",command=self.on_new)
        m.post(event.x_root, event.y_root)

    # ── Actions ──────────────────────────────────

    def _quick_connect(self):
        s = self._sel_session()
        if not s:
            messagebox.showinfo("Sessions", "Select a session first.")
            return
        self.on_connect(s)

    def _edit(self):
        s = self._sel_session()
        if not s:
            messagebox.showinfo("Sessions", "Select a session to edit.")
            return
        dlg = ConnectDialog(self.winfo_toplevel(),
                            prefill=s,
                            existing_folders=self._folders())
        if dlg.session:
            self._sessions = [x for x in self._sessions if x["name"] != s["name"]]
            self._sessions.append(dlg.session)
            self._repopulate()
            self._save()
        if dlg.result:
            self.on_connect(dlg.result)

    def _delete(self):
        s = self._sel_session()
        if not s:
            return
        if messagebox.askyesno("Delete Session", f"Delete  '{s['name']}'?"):
            self._sessions.remove(s)
            self._repopulate()
            self._save()

    def _rename_folder(self):
        folder = self._sel_folder()
        if not folder:
            return
        new = simpledialog.askstring("Rename Folder", "New name:",
                                     initialvalue=folder, parent=self)
        if new and new.strip() and new.strip() != folder:
            for s in self._sessions:
                if s.get("folder") == folder:
                    s["folder"] = new.strip()
            self._save()
            self._repopulate()

    def _delete_folder(self):
        folder = self._sel_folder()
        if not folder:
            return
        inside = [s for s in self._sessions if s.get("folder") == folder]
        if inside:
            choice = messagebox.askyesnocancel(
                "Delete Folder",
                f'"{folder}" contains {len(inside)} session(s).\n\n'
                "Yes  -> delete folder and all its sessions\n"
                "No   -> delete folder, keep sessions at root\n"
                "Cancel -> abort",
                parent=self)
            if choice is None:
                return
            if choice:
                self._sessions = [x for x in self._sessions
                                  if x.get("folder") != folder]
            else:
                for s in self._sessions:
                    if s.get("folder") == folder:
                        s.pop("folder", None)
        self._save()
        self._repopulate()

    def _move_to_folder(self):
        s = self._sel_session()
        if not s:
            return
        folders = self._folders()
        hint = ("Existing: " + ", ".join(folders)) if folders else ""
        target = simpledialog.askstring(
            "Move to Folder",
            f"{hint}\nEnter folder name (blank = root):".strip(),
            initialvalue=s.get("folder", ""),
            parent=self)
        if target is None:
            return
        target = target.strip()
        if target:
            s["folder"] = target
        else:
            s.pop("folder", None)
        self._save()
        self._repopulate()

    def _export(self):
        path = filedialog.asksaveasfilename(
            title="Export sessions", defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._sessions, f, indent=2)
        messagebox.showinfo("Export", f"Saved to:\n{path}")

    def _import(self):
        path = filedialog.askopenfilename(
            title="Import sessions",
            filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Expected a JSON array.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
            return
        valid = [e for e in data
                 if isinstance(e, dict) and "name" in e and "host" in e]
        for entry in valid:
            self.upsert(entry)
        messagebox.showinfo("Import", f"Imported {len(valid)} session(s).")


# ─────────────────────────────────────────────
#  SSH Terminal
# ─────────────────────────────────────────────
_KEY_MAP = {
    "Return":   "\r",   "KP_Enter": "\r",
    "BackSpace": "\x7f","Tab":       "\t",
    "Escape":    "\x1b",
    "Up":    "\x1b[A",  "Down":  "\x1b[B",
    "Right": "\x1b[C",  "Left":  "\x1b[D",
    "Home":  "\x1b[H",  "End":   "\x1b[F",
    "Delete":"\x1b[3~", "Insert":"\x1b[2~",
    "Prior": "\x1b[5~", "Next":  "\x1b[6~",
    "F1": "\x1bOP",  "F2": "\x1bOQ",  "F3": "\x1bOR",  "F4": "\x1bOS",
    "F5": "\x1b[15~","F6": "\x1b[17~","F7": "\x1b[18~","F8": "\x1b[19~",
    "F9": "\x1b[20~","F10":"\x1b[21~","F11":"\x1b[23~","F12":"\x1b[24~",
}

_ANSI_RE = re.compile(
    r"\x1b(\[[0-9;]*[A-Za-z]|[()][AB012]|\][^\x07]*\x07|[=>])")

def _strip_ansi(t: str) -> str:
    return _ANSI_RE.sub("", t)


class SSHTerminal(tk.Frame):
    def __init__(self, parent, transport: paramiko.Transport):
        super().__init__(parent, bg=TERM_BG)
        self._transport = transport
        self._channel   = None
        self._running   = False

        self.text = tk.Text(
            self,
            bg=TERM_BG, fg=TERM_FG,
            font=_MONO,
            insertbackground=TERM_FG,
            selectbackground="#264f78",
            selectforeground=TERM_FG,
            wrap="char", cursor="xterm",
            relief="flat", bd=0,
            padx=6, pady=4,
        )
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)
        self.text.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.text.bind("<Key>",      self._on_key)
        self.text.bind("<Button-1>", lambda _: self.text.focus_set())
        self.text.bind("<<Paste>>",  self._on_paste)

        self._open_shell()

    def _open_shell(self):
        try:
            chan = self._transport.open_session()
            chan.get_pty(term="xterm", width=220, height=50)
            chan.invoke_shell()
            chan.settimeout(0.05)
            self._channel = chan
            self._running = True
            threading.Thread(target=self._read_loop, daemon=True).start()
            self.text.focus_set()
        except Exception as e:
            self._append(f"[Terminal error: {e}]\n")

    def _read_loop(self):
        while self._running:
            try:
                data = self._channel.recv(4096)
                if data:
                    txt = _strip_ansi(
                        data.decode("utf-8", errors="replace"))
                    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
                    self.after(0, self._append, txt)
                elif self._channel.closed or self._channel.exit_status_ready():
                    break
            except Exception:
                time.sleep(0.05)
        self.after(0, self._append, "\n[Session closed]\n")

    def _append(self, txt: str):
        self.text.insert("end", txt)
        self.text.see("end")

    def _on_key(self, event):
        if not self._channel or self._channel.closed:
            return "break"
        if event.state & 0x4:
            if len(event.keysym) == 1 and event.keysym.isalpha():
                self._send(chr(ord(event.keysym.upper()) - 64))
                return "break"
        send = _KEY_MAP.get(event.keysym) or (event.char or None)
        if send:
            self._send(send)
        return "break"

    def _on_paste(self, _):
        try:
            self._send(self.clipboard_get())
        except Exception:
            pass
        return "break"

    def _send(self, data: str):
        try:
            self._channel.send(data)
        except Exception:
            pass

    def close(self):
        self._running = False
        if self._channel:
            try:  self._channel.close()
            except Exception: pass


# ─────────────────────────────────────────────
#  SFTP Browser
# ─────────────────────────────────────────────
class SFTPBrowser(tk.Frame):
    def __init__(self, parent, sftp: paramiko.SFTPClient,
                 cwd: str, status_var: tk.StringVar):
        super().__init__(parent, bg=BG)
        self.sftp       = sftp
        self.cwd        = cwd
        self.status_var = status_var

        # Toolbar
        tb = tk.Frame(self, bg=BG2, height=38)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        for label, cmd in [
            ("↑ Up",       self._go_up),
            ("⟳ Refresh",  self._refresh),
            ("+ Mkdir",    self._mkdir),
            ("↓ Download", self._download),
            ("↑ Upload",   self._upload),
            ("✕ Delete",   self._delete),
        ]:
            ttk.Button(tb, text=label, command=cmd).pack(
                side="left", padx=(4, 0), pady=4)

        # Path bar
        pb = tk.Frame(self, bg=BG, pady=4)
        pb.pack(fill="x", padx=8)
        ttk.Label(pb, text="Path:", style="Dim.TLabel").pack(side="left")
        self.path_var = tk.StringVar(value=cwd)
        pe = ttk.Entry(pb, textvariable=self.path_var)
        pe.pack(side="left", fill="x", expand=True, padx=(6, 0))
        pe.bind("<Return>", lambda _: self._navigate(self.path_var.get()))

        # File tree
        cols = ("name", "size", "type", "permissions")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                  selectmode="browse")
        for col, w, anchor in [
            ("name", 300, "w"), ("size", 90, "e"),
            ("type", 70, "center"), ("permissions", 110, "center"),
        ]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w, anchor=anchor)

        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.bind("<Double-1>", self._on_double_click)

        self._refresh()

    def _navigate(self, path: str):
        path = path.strip()
        try:
            self.sftp.stat(path)
            self.cwd = path
            self.path_var.set(self.cwd)
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _go_up(self):
        self._navigate(os.path.dirname(self.cwd.rstrip("/")) or "/")

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        self.status_var.set(f"Loading {self.cwd} …")
        threading.Thread(target=self._load_dir, daemon=True).start()

    def _load_dir(self):
        try:
            entries = self.sftp.listdir_attr(self.cwd)
        except Exception as e:
            self.after(0, lambda msg=str(e):
                       messagebox.showerror("Error", msg))
            return
        rows = []
        for e in sorted(entries,
                        key=lambda x: (not stat.S_ISDIR(x.st_mode or 0),
                                       x.filename)):
            is_dir = stat.S_ISDIR(e.st_mode or 0)
            rows.append((
                e.filename,
                "" if is_dir else _fmt_size(e.st_size or 0),
                "DIR" if is_dir else "FILE",
                stat.filemode(e.st_mode or 0),
            ))
        self.after(0, self._populate, rows)

    def _populate(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row,
                             tags=("dir" if row[2] == "DIR" else "file",))
        self.tree.tag_configure("dir",  foreground=ACCENT)
        self.tree.tag_configure("file", foreground=TEXT)
        self.status_var.set(f"{self.cwd}  ({len(rows)} items)")

    def _on_double_click(self, _):
        item = self.tree.focus()
        if not item:
            return
        name, _, ftype, _ = self.tree.item(item, "values")
        if ftype == "DIR":
            self._navigate(self.cwd.rstrip("/") + "/" + name)

    def _sel(self):
        item = self.tree.focus()
        return self.tree.item(item, "values")[0] if item else None

    def _mkdir(self):
        name = simpledialog.askstring("Make Directory",
                                      "New directory name:", parent=self)
        if not name:
            return
        try:
            self.sftp.mkdir(self.cwd.rstrip("/") + "/" + name)
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _download(self):
        name = self._sel()
        if not name:
            messagebox.showinfo("Download", "Select a file first.")
            return
        dest = filedialog.askdirectory(title="Download to…")
        if not dest:
            return
        remote = self.cwd.rstrip("/") + "/" + name
        local  = os.path.join(dest, name)
        self.status_var.set(f"Downloading {name}…")
        def _do():
            try:
                self.sftp.get(remote, local)
                self.after(0, lambda: self.status_var.set(
                    f"Downloaded → {local}"))
            except Exception as e:
                self.after(0, lambda msg=str(e):
                           messagebox.showerror("Error", msg))
        threading.Thread(target=_do, daemon=True).start()

    def _upload(self):
        local = filedialog.askopenfilename(title="Upload file…")
        if not local:
            return
        name   = os.path.basename(local)
        remote = self.cwd.rstrip("/") + "/" + name
        self.status_var.set(f"Uploading {name}…")
        def _do():
            try:
                self.sftp.put(local, remote)
                self.after(0, self._refresh)
                self.after(0, lambda: self.status_var.set(f"Uploaded {name}"))
            except Exception as e:
                self.after(0, lambda msg=str(e):
                           messagebox.showerror("Error", msg))
        threading.Thread(target=_do, daemon=True).start()

    def _delete(self):
        name = self._sel()
        if not name:
            messagebox.showinfo("Delete", "Select a file or directory first.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete  '{name}'?"):
            return
        remote = self.cwd.rstrip("/") + "/" + name
        try:
            try:
                self.sftp.remove(remote)
            except IOError:
                self.sftp.rmdir(remote)
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ─────────────────────────────────────────────
#  Main application
# ─────────────────────────────────────────────
class SecureSHApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SecureSH")
        self.geometry("1160x680")
        self.minsize(800, 480)
        _apply_theme(self)

        # tab_id → (transport, sftp, terminal)
        self._tab_handles: dict[str, tuple] = {}

        self._build_menu()
        self._build_titlebar()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Frame(self, bg=BG2, height=24)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        tk.Frame(status, bg=ACCENT, width=3).pack(side="left", fill="y")
        tk.Label(status, textvariable=self.status_var,
                 bg=BG2, fg=TEXT2, font=_UIsm,
                 anchor="w").pack(side="left", padx=8)

        # Paned layout
        pane = tk.PanedWindow(self, orient="horizontal",
                              sashwidth=1, sashrelief="flat",
                              bg=BORDER, bd=0)
        pane.pack(fill="both", expand=True)

        self.sidebar  = SessionsSidebar(pane,
                                        on_connect=self._connect_with,
                                        on_new=self._connect)
        self.notebook = ttk.Notebook(pane)
        pane.add(self.sidebar,  minsize=180, width=200)
        pane.add(self.notebook, minsize=500)

        self._welcome()

    # ── Menu ──────────────────────────────────────

    def _build_menu(self):
        mb = tk.Menu(self)
        self.config(menu=mb)

        conn = tk.Menu(mb, tearoff=0)
        conn.add_command(label="New Connection…",
                         command=self._connect,     accelerator="Ctrl+N")
        conn.add_command(label="Disconnect Active",
                         command=self._disconnect_active, accelerator="Ctrl+D")
        conn.add_separator()
        conn.add_command(label="Exit", command=self._on_close)
        mb.add_cascade(label="Connection", menu=conn)

        sess = tk.Menu(mb, tearoff=0)
        sess.add_command(label="Export Sessions…",
                         command=lambda: self.sidebar._export())
        sess.add_command(label="Import Sessions…",
                         command=lambda: self.sidebar._import())
        mb.add_cascade(label="Sessions", menu=sess)

        self.bind_all("<Control-n>", lambda _: self._connect())
        self.bind_all("<Control-d>", lambda _: self._disconnect_active())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=BG2, height=42)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        tk.Frame(bar, bg=ACCENT, width=4).pack(side="left", fill="y")

        ttk.Button(bar, text="New Connection",
                   command=self._connect,
                   style="Accent.TButton").pack(side="left", padx=8, pady=6)
        ttk.Button(bar, text="Disconnect",
                   command=self._disconnect_active).pack(
            side="left", pady=6)

        tk.Frame(bar, bg=BORDER, width=1).pack(
            side="left", fill="y", padx=10, pady=8)

        self.conn_label = tk.Label(bar, text="No active session",
                                   bg=BG2, fg=TEXT2, font=_UIsm)
        self.conn_label.pack(side="left")

    def _welcome(self):
        f = tk.Frame(self.notebook, bg=BG)
        tk.Label(f, text="SecureSH",
                 bg=BG, fg=ACCENT,
                 font=("Segoe UI", 28, "bold")).pack(pady=(80, 4))
        tk.Label(f, text="Double-click a saved session  •  Ctrl+N for a new connection",
                 bg=BG, fg=TEXT2, font=("Segoe UI", 10)).pack()
        tk.Label(f, text=f"Default port {DEFAULT_PORT}  ·  Key  {DEFAULT_KEY}",
                 bg=BG, fg=TEXT2, font=_UIsm).pack(pady=4)
        self.notebook.add(f, text="  Welcome  ")

    # ── Connection flow ───────────────────────────

    def _connect(self):
        dlg = ConnectDialog(self, existing_folders=self.sidebar._folders())
        if dlg.result is None:
            return
        if dlg.session:
            self.sidebar.upsert(dlg.session)
        self._launch(dlg.result)

    def _connect_with(self, session: dict):
        dlg = ConnectDialog(self, prefill=session,
                            existing_folders=self.sidebar._folders())
        if dlg.result is None:
            return
        if dlg.session:
            self.sidebar.upsert(dlg.session)
        self._launch(dlg.result)

    def _launch(self, p: dict):
        self.conn_label.config(text="Connecting…", fg=WARN_FG)
        self.status_var.set("Connecting…")
        threading.Thread(target=self._do_connect, args=(p,), daemon=True).start()

    def _do_connect(self, p: dict):
        t = None
        try:
            key = _load_key(p["key_path"], p["passphrase"])

            sock = _socket.create_connection((p["host"], p["port"]), timeout=15)
            t = paramiko.Transport(sock)
            t.banner_timeout = 15
            t.start_client(timeout=15)

            username = p["username"]

            # Factor 1 – public key
            try:
                t.auth_publickey(username, key)
            except paramiko.AuthenticationException:
                raise paramiko.AuthenticationException(
                    "Public key authentication failed.\n"
                    "Check username and key file.")

            # Factor 2 – keyboard-interactive (Duo etc.)
            if not t.is_authenticated():
                self.after(0, lambda: self.status_var.set(
                    "Waiting for 2FA…"))
                t.auth_interactive(username, self._ki_handler())

            if not t.is_authenticated():
                raise paramiko.AuthenticationException(
                    "Authentication failed after all factors.")

            sftp = paramiko.SFTPClient.from_transport(t)
            cwd  = sftp.normalize(".")

        except Exception as e:
            if t:
                try:  t.close()
                except Exception: pass
            self.after(0, lambda msg=str(e): self._fail(msg))
            return

        label = f"{p['username']}@{p['host']}:{p['port']}"
        self.after(0, lambda: self._ok(t, sftp, cwd, label))

    def _ki_handler(self):
        """Keyboard-interactive handler — shows a GUI dialog, no stdin needed."""
        def handler(title, instructions, fields):
            if not fields:
                return []
            q = _queue.Queue()
            def _show():
                dlg = KeyboardInteractiveDialog(
                    self, title, instructions, fields)
                q.put(dlg.responses if dlg.responses is not None
                      else [""] * len(fields))
            self.after(0, _show)
            try:
                return q.get(timeout=120)
            except _queue.Empty:
                return [""] * len(fields)
        return handler

    def _ok(self, transport, sftp, cwd, label):
        self.conn_label.config(text=f"  ● {label}", fg=SUCCESS_FG)
        self.status_var.set(f"Connected  {label}")

        sub = ttk.Notebook(self.notebook)

        terminal = SSHTerminal(sub, transport)
        sub.add(terminal, text="  Terminal  ")

        browser = SFTPBrowser(sub, sftp, cwd, self.status_var)
        sub.add(browser, text="  SFTP  ")

        self.notebook.add(sub, text=f"  {label}  ")
        self.notebook.select(sub)

        tab_id = self.notebook.select()
        self._tab_handles[tab_id] = (transport, sftp, terminal)
        self.notebook.bind("<<NotebookTabChanged>>", self._tab_changed)

        terminal.text.focus_set()

    def _fail(self, msg: str):
        self.conn_label.config(text="No active session", fg=TEXT2)
        self.status_var.set("Connection failed.")
        messagebox.showerror("Connection Failed", msg)

    def _tab_changed(self, _=None):
        tab = self.notebook.select()
        if tab in self._tab_handles:
            title = self.notebook.tab(tab, "text").strip()
            self.conn_label.config(text=f"  ● {title}", fg=SUCCESS_FG)
        else:
            self.conn_label.config(text="No active session", fg=TEXT2)

    def _disconnect_active(self):
        tab = self.notebook.select()
        if tab not in self._tab_handles:
            return
        transport, sftp, terminal = self._tab_handles.pop(tab)
        terminal.close()
        for obj in (sftp, transport):
            try:  obj.close()
            except Exception: pass
        self.notebook.forget(tab)
        self.status_var.set("Disconnected.")
        if not self._tab_handles:
            self.conn_label.config(text="No active session", fg=TEXT2)

    def _on_close(self):
        for transport, sftp, terminal in self._tab_handles.values():
            terminal.close()
            for obj in (sftp, transport):
                try:  obj.close()
                except Exception: pass
        self.destroy()


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def _load_key(path: str, passphrase: str | None) -> paramiko.PKey:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Private key not found:\n{path}\n\n"
            "Check the key path in the connection dialog.")
    for loader in (paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey):
        try:
            return loader.from_private_key_file(path, password=passphrase)
        except paramiko.ssh_exception.SSHException:
            continue
        except Exception as e:
            last_err = e
    raise locals().get("last_err", Exception(
        "Could not load private key — unsupported type or wrong passphrase."))


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} PB"


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = SecureSHApp()
    app.mainloop()
