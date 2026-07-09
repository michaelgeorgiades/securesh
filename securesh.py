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
import stat
import json
import sys
import subprocess
import time
import paramiko

# ─────────────────────────────────────────────
#  Themes
# ─────────────────────────────────────────────
# Each theme is a fully self-contained palette + font + style bundle.
# "classic" STYLE = solid filled accent buttons / selection blocks
# (the original Fluent-ish look). "glow" STYLE = outline buttons that
# invert to a solid fill on hover — a terminal "select to activate" feel,
# used by the darker/techier themes.
THEMES: dict[str, dict] = {
    "Light (Default)": dict(
        BG="#ffffff", BG2="#f7f7f7", SIDEBAR_BG="#f0f2f5", FIELD_BG="#ffffff",
        ACCENT="#0078d4", ACCENT_HOV="#106ebe", ACCENT_ACT="#005a9e", ACCENT_TEXT="#ffffff",
        TEXT="#1b1b1b", TEXT2="#6e6e6e", BORDER="#dde1e6",
        SEL_BG="#d0e7f8", HOV_BG="#e8f2fb",
        SUCCESS_FG="#107c10", WARN_FG="#ca5010", ERR_FG="#c42b1c",
        INFO_BG="#e8f4fb", INFO_BORDER="#b3d7f0",
        TERM_BG="#1e1e1e", TERM_FG="#d4d4d4", TERM_SEL_BG="#264f78",
        MONO=("Consolas", 10), LABEL=("Segoe UI", 8), LABELB=("Segoe UI", 8, "bold"),
        STYLE="classic", WELCOME_CURSOR=False,
        DANGER_HOVER_BG="#fde7e9", DANGER_PRESS_BG="#f8d0d3",
        GRADIENT_START="#0078d4", GRADIENT_END="#0078d4",
    ),
    "Midnight Cyan": dict(
        BG="#0a0e17", BG2="#111827", SIDEBAR_BG="#0d1420", FIELD_BG="#0f1621",
        ACCENT="#22d3ee", ACCENT_HOV="#67e8f9", ACCENT_ACT="#0891b2", ACCENT_TEXT="#04141a",
        TEXT="#e6edf3", TEXT2="#7d8b9c", BORDER="#232c3d",
        SEL_BG="#163647", HOV_BG="#141c2b",
        SUCCESS_FG="#3fb950", WARN_FG="#e3b341", ERR_FG="#f85149",
        INFO_BG="#0f2630", INFO_BORDER="#1c4a5c",
        TERM_BG="#0a0e17", TERM_FG="#c9d1d9", TERM_SEL_BG="#163647",
        MONO=("Cascadia Mono", 10), LABEL=("Cascadia Mono", 8), LABELB=("Cascadia Mono", 8, "bold"),
        STYLE="glow", WELCOME_CURSOR=True,
        DANGER_HOVER_BG="#3b1219", DANGER_PRESS_BG="#8f1f1a",
        GRADIENT_START="#22d3ee", GRADIENT_END="#22d3ee",
    ),
    "Matrix Green": dict(
        BG="#060a07", BG2="#0d130e", SIDEBAR_BG="#080c09", FIELD_BG="#0a100b",
        ACCENT="#39ff14", ACCENT_HOV="#8aff6b", ACCENT_ACT="#1a8f00", ACCENT_TEXT="#031a08",
        TEXT="#dbe8de", TEXT2="#7c9284", BORDER="#1f2e24",
        SEL_BG="#123322", HOV_BG="#0f1912",
        SUCCESS_FG="#4ade80", WARN_FG="#e3b341", ERR_FG="#f85149",
        INFO_BG="#08150c", INFO_BORDER="#1d4a2c",
        TERM_BG="#060a07", TERM_FG="#c7d6cb", TERM_SEL_BG="#123322",
        MONO=("Cascadia Mono", 10), LABEL=("Cascadia Mono", 8), LABELB=("Cascadia Mono", 8, "bold"),
        STYLE="glow", WELCOME_CURSOR=True,
        DANGER_HOVER_BG="#3b1219", DANGER_PRESS_BG="#8f1f1a",
        GRADIENT_START="#39ff14", GRADIENT_END="#39ff14",
    ),
    "Cyberpunk": dict(
        BG="#0a0a0a", BG2="#161616", SIDEBAR_BG="#0c0c0c", FIELD_BG="#131313",
        ACCENT="#ff6a00", ACCENT_HOV="#ffab5e", ACCENT_ACT="#cc5500", ACCENT_TEXT="#170900",
        TEXT="#e8e6e3", TEXT2="#8a8781", BORDER="#2b2b2b",
        SEL_BG="#3a2210", HOV_BG="#1c1c1c",
        SUCCESS_FG="#4ade80", WARN_FG="#ffd166", ERR_FG="#ff4d4d",
        INFO_BG="#1a120a", INFO_BORDER="#4a2f10",
        TERM_BG="#0a0a0a", TERM_FG="#d8d5cf", TERM_SEL_BG="#3a2210",
        MONO=("Cascadia Mono", 10), LABEL=("Cascadia Mono", 8), LABELB=("Cascadia Mono", 8, "bold"),
        STYLE="glow", WELCOME_CURSOR=True,
        DANGER_HOVER_BG="#3d1010", DANGER_PRESS_BG="#7a1f1f",
        GRADIENT_START="#ff6a00", GRADIENT_END="#ff6a00",
    ),
    "Slate Graphite": dict(
        BG="#111318", BG2="#181b21", SIDEBAR_BG="#0e1015", FIELD_BG="#1b1e25",
        ACCENT="#6ea8fe", ACCENT_HOV="#9dc2ff", ACCENT_ACT="#3d7de0", ACCENT_TEXT="#0a0e17",
        TEXT="#e3e5e8", TEXT2="#8a8f98", BORDER="#2a2e37",
        SEL_BG="#22293a", HOV_BG="#1d2129",
        SUCCESS_FG="#4ade80", WARN_FG="#e3b341", ERR_FG="#f87171",
        INFO_BG="#161c2b", INFO_BORDER="#2d3a55",
        TERM_BG="#111318", TERM_FG="#d7dae0", TERM_SEL_BG="#22293a",
        MONO=("Cascadia Mono", 10), LABEL=("Segoe UI", 8), LABELB=("Segoe UI", 8, "bold"),
        STYLE="glow", WELCOME_CURSOR=False,
        DANGER_HOVER_BG="#3a1616", DANGER_PRESS_BG="#6a2323",
        GRADIENT_START="#6ea8fe", GRADIENT_END="#6ea8fe",
    ),
    "Aurora": dict(
        BG="#0b0713", BG2="#140f22", SIDEBAR_BG="#0d0918", FIELD_BG="#120c1f",
        # ACCENT is deliberately brighter than a true 50/50 blend of
        # GRADIENT_START/END — the muted midpoint blue looked "hollow"/
        # broken when used as small bold ttk-button text (ClearType's
        # subpixel color fringing overwhelms a low-luminance color at
        # that size). The literal gradient bars/text still use the true
        # violet->cyan endpoints below, which are big enough not to have
        # this problem.
        ACCENT="#8fa8ff", ACCENT_HOV="#c0cdff", ACCENT_ACT="#5a72d1", ACCENT_TEXT="#0a0713",
        TEXT="#ece7f5", TEXT2="#8b7fa0", BORDER="#2a2140",
        SEL_BG="#241a3d", HOV_BG="#191228",
        SUCCESS_FG="#4ade80", WARN_FG="#ffb020", ERR_FG="#ff5470",
        INFO_BG="#160f26", INFO_BORDER="#3d2a5c",
        TERM_BG="#0b0713", TERM_FG="#ded4ec", TERM_SEL_BG="#2a1f4a",
        MONO=("Cascadia Mono", 10), LABEL=("Cascadia Mono", 8), LABELB=("Cascadia Mono", 8, "bold"),
        STYLE="gradient", WELCOME_CURSOR=True,
        DANGER_HOVER_BG="#3d0f2a", DANGER_PRESS_BG="#7a1f4f",
        GRADIENT_START="#7c3aed", GRADIENT_END="#22d3ee",
    ),
}
DEFAULT_THEME = "Light (Default)"
CURRENT_THEME = DEFAULT_THEME

_UI   = ("Segoe UI", 9)
_UIsm = ("Segoe UI", 8)
_UIb  = ("Segoe UI", 9,  "bold")
_UIh  = ("Segoe UI", 11, "bold")


def _activate_theme(name: str):
    """Populate the module-level color/font globals from THEMES[name].

    Must run before any widget is constructed — everything else in this
    file reads these names live (inside method bodies), so reassigning
    them here is enough to make the whole app pick up a new palette,
    provided no widgets exist yet from a previous theme.
    """
    global BG, BG2, SIDEBAR_BG, FIELD_BG
    global ACCENT, ACCENT_HOV, ACCENT_ACT, ACCENT_TEXT
    global TEXT, TEXT2, BORDER, SEL_BG, HOV_BG
    global SUCCESS_FG, WARN_FG, ERR_FG
    global INFO_BG, INFO_BORDER
    global TERM_BG, TERM_FG, TERM_SEL_BG
    global _MONO, _LABEL, _LABELb
    global _THEME_STYLE, _WELCOME_CURSOR
    global DANGER_HOVER_BG, DANGER_PRESS_BG
    global GRADIENT_START, GRADIENT_END
    global CURRENT_THEME

    t = THEMES.get(name, THEMES[DEFAULT_THEME])
    CURRENT_THEME = name if name in THEMES else DEFAULT_THEME

    BG, BG2, SIDEBAR_BG, FIELD_BG = t["BG"], t["BG2"], t["SIDEBAR_BG"], t["FIELD_BG"]
    ACCENT, ACCENT_HOV, ACCENT_ACT, ACCENT_TEXT = (
        t["ACCENT"], t["ACCENT_HOV"], t["ACCENT_ACT"], t["ACCENT_TEXT"])
    TEXT, TEXT2, BORDER = t["TEXT"], t["TEXT2"], t["BORDER"]
    SEL_BG, HOV_BG = t["SEL_BG"], t["HOV_BG"]
    SUCCESS_FG, WARN_FG, ERR_FG = t["SUCCESS_FG"], t["WARN_FG"], t["ERR_FG"]
    INFO_BG, INFO_BORDER = t["INFO_BG"], t["INFO_BORDER"]
    TERM_BG, TERM_FG, TERM_SEL_BG = t["TERM_BG"], t["TERM_FG"], t["TERM_SEL_BG"]
    _MONO, _LABEL, _LABELb = t["MONO"], t["LABEL"], t["LABELB"]
    _THEME_STYLE = t["STYLE"]
    _WELCOME_CURSOR = t["WELCOME_CURSOR"]
    DANGER_HOVER_BG, DANGER_PRESS_BG = t["DANGER_HOVER_BG"], t["DANGER_PRESS_BG"]
    GRADIENT_START, GRADIENT_END = t["GRADIENT_START"], t["GRADIENT_END"]


_activate_theme(DEFAULT_THEME)


def _apply_theme(root: tk.Tk):
    # "gradient" reuses the glow (outline/invert) ttk styling everywhere a
    # true multi-color gradient isn't feasible in ttk; the gradient itself
    # is layered on top at a few specific spots via the Gradient* widgets.
    glow = (_THEME_STYLE in ("glow", "gradient"))

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
    s.configure("Dim.TLabel",   background=BG,         foreground=TEXT2,  font=_LABEL)
    s.configure("Sidebar.TLabel", background=SIDEBAR_BG, foreground=TEXT)
    s.configure("SHdr.TLabel",  background=SIDEBAR_BG,
                foreground=(ACCENT if glow else TEXT2),
                font=_LABELb)
    s.configure("Success.TLabel", background=BG, foreground=SUCCESS_FG)
    s.configure("Warn.TLabel",    background=BG, foreground=WARN_FG)

    # ── Buttons ──
    # NOTE on focuscolor: ttk's "clam" theme draws keyboard focus as a
    # dotted ring inset just inside the button's own border. The original
    # theme set focuscolor=ACCENT globally, which was invisible against
    # the original solid-filled accent buttons (accent-colored dots on an
    # accent-colored fill). The glow/gradient outline buttons below have a
    # dark interior, so that same dotted ring lands right on top of the
    # bold accent-colored label text and reads as broken/cut-off glyphs.
    # Blending focuscolor into each button's own fill keeps the ring
    # functional for keyboard users without visually colliding with the
    # text — classic style is untouched, matching the original look.
    s.configure("TButton",
        background=BG2, foreground=TEXT,
        relief="flat", borderwidth=1,
        padding=(10, 5), font=_UI,
        bordercolor=BORDER)
    if glow:
        s.configure("TButton", focuscolor=BG2)
        s.map("TButton",
            background=[("active", HOV_BG), ("pressed", SEL_BG)],
            foreground=[("active", ACCENT)],
            bordercolor=[("focus", ACCENT), ("active", ACCENT)])
    else:
        s.map("TButton",
            background=[("active", HOV_BG), ("pressed", SEL_BG)],
            bordercolor=[("focus", ACCENT)])

    if glow:
        # Glow-outline buttons: dark fill, bright bordered text at rest;
        # invert to a solid glowing fill on hover/press — a terminal
        # "select to activate" look instead of a flat filled button.
        s.configure("Accent.TButton",
            background=FIELD_BG, foreground=ACCENT,
            relief="solid", borderwidth=1, bordercolor=ACCENT,
            padding=(12, 5), font=_UIb, focuscolor=FIELD_BG)
        s.map("Accent.TButton",
            background=[("pressed", ACCENT_ACT), ("active", ACCENT)],
            foreground=[("pressed", ACCENT_TEXT), ("active", ACCENT_TEXT)],
            bordercolor=[("active", ACCENT_HOV)])
    else:
        s.configure("Accent.TButton",
            background=ACCENT, foreground=ACCENT_TEXT,
            relief="flat", borderwidth=0,
            padding=(12, 5), font=_UIb)
        s.map("Accent.TButton",
            background=[("active", ACCENT_HOV), ("pressed", ACCENT_ACT)])

    s.configure("Ghost.TButton",
        background=SIDEBAR_BG, foreground=ACCENT,
        relief="flat", borderwidth=0, padding=(6, 3),
        focuscolor=(SIDEBAR_BG if glow else ACCENT))
    s.map("Ghost.TButton",
        background=[("active", HOV_BG)],
        foreground=[("active", ACCENT_HOV)])

    if glow:
        s.configure("Danger.TButton",
            background=FIELD_BG, foreground=ERR_FG,
            relief="solid", borderwidth=1, padding=(10, 5),
            bordercolor=ERR_FG, focuscolor=FIELD_BG)
        s.map("Danger.TButton",
            background=[("pressed", DANGER_PRESS_BG), ("active", ERR_FG)],
            foreground=[("pressed", TEXT), ("active", ACCENT_TEXT)],
            bordercolor=[("active", ERR_FG)])
    else:
        s.configure("Danger.TButton",
            background=BG2, foreground=ERR_FG,
            relief="flat", borderwidth=1, padding=(10, 5),
            bordercolor=BORDER)
        s.map("Danger.TButton",
            background=[("active", DANGER_HOVER_BG)])

    # ── Entry ──
    s.configure("TEntry",
        fieldbackground=FIELD_BG, foreground=TEXT,
        borderwidth=1, relief="solid",
        padding=(6, 4), bordercolor=BORDER,
        insertcolor=(ACCENT if glow else TEXT))
    s.map("TEntry",
        bordercolor=[("focus", ACCENT)])

    # ── Combobox ──
    s.configure("TCombobox",
        fieldbackground=FIELD_BG, background=FIELD_BG, foreground=TEXT,
        arrowcolor=TEXT2, selectbackground=FIELD_BG, selectforeground=TEXT,
        borderwidth=1, relief="solid",
        padding=(4, 3), bordercolor=BORDER)
    s.map("TCombobox",
        bordercolor=[("focus", ACCENT)],
        fieldbackground=[("readonly", FIELD_BG)],
        arrowcolor=[("active", ACCENT)])
    root.option_add("*TCombobox*Listbox.background", FIELD_BG)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", SEL_BG)
    root.option_add("*TCombobox*Listbox.selectForeground", TEXT)

    # ── Notebook ──
    s.configure("TNotebook",
        background=BG2, borderwidth=0, tabmargins=0)
    s.configure("TNotebook.Tab",
        background=BG2, foreground=TEXT2,
        padding=(14, 5), borderwidth=0, font=_UI)
    s.map("TNotebook.Tab",
        background=[("selected", BG),  ("active", HOV_BG)],
        foreground=[("selected", ACCENT)] + ([("active", ACCENT)] if glow else []),
        padding=[("selected", (14, 10))],
        expand=[("selected", [0, 0, 0, 2])])

    # ── Treeview (file list) ──
    s.configure("Treeview",
        background=FIELD_BG, fieldbackground=FIELD_BG,
        foreground=TEXT, rowheight=26,
        borderwidth=0, relief="flat")
    s.configure("Treeview.Heading",
        background=BG2, foreground=TEXT2,
        relief="flat", padding=(6, 5), font=_LABEL)
    if glow:
        s.map("Treeview.Heading", foreground=[("active", ACCENT)])
    s.map("Treeview",
        background=[("selected", SEL_BG)],
        foreground=[("selected", ACCENT if glow else TEXT)])

    # ── Sidebar Treeview ──
    s.configure("Sidebar.Treeview",
        background=SIDEBAR_BG, fieldbackground=SIDEBAR_BG,
        foreground=TEXT, rowheight=22, font=_UI,
        borderwidth=0, relief="flat", indent=14)
    if glow:
        s.map("Sidebar.Treeview",
            background=[("selected", SEL_BG)],
            foreground=[("selected", ACCENT)])
    else:
        s.map("Sidebar.Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", ACCENT_TEXT)])

    # ── Scrollbar ──
    s.configure("TScrollbar",
        background=BG2, troughcolor=BG,
        borderwidth=0, arrowsize=13,
        relief="flat")
    s.map("TScrollbar",
        background=[("active", ACCENT if glow else BORDER),
                     ("pressed", ACCENT_ACT if glow else TEXT2)])

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
#  Gradient primitives — Tkinter has no native gradient support, so these
#  hand-draw one on a Canvas. Used only when the active theme's STYLE is
#  "gradient" (currently just "Aurora"); every other theme ignores them.
# ─────────────────────────────────────────────
def _lerp_color(c1: str, c2: str, t: float) -> str:
    c1, c2 = c1.lstrip("#"), c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class GradientBar(tk.Canvas):
    """A thin strip filled with a smooth horizontal or vertical gradient —
    a drop-in replacement for a solid-color accent Frame."""
    def __init__(self, parent, c1: str, c2: str, vertical: bool = False, **kw):
        # tk.Canvas defaults to ~200x150px for any dimension the caller
        # doesn't specify (unlike Frame, it has no content to size itself
        # from) — callers of GradientBar only ever set the *thickness*
        # dimension (height for a horizontal bar, width for a vertical
        # one) and rely on sticky/fill to stretch the other, so default
        # the unset one to 1px instead of letting it silently balloon
        # the whole bar (and anything gridded alongside it) to ~200px.
        kw.setdefault("width", 1)
        kw.setdefault("height", 1)
        super().__init__(parent, highlightthickness=0, bd=0, **kw)
        self._c1, self._c2, self._vertical = c1, c2, vertical
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _=None):
        self.delete("grad")
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 1 or h <= 1:
            return
        if self._vertical:
            for y in range(h):
                t = y / max(h - 1, 1)
                self.create_line(0, y, w, y, fill=_lerp_color(self._c1, self._c2, t), tags="grad")
        else:
            for x in range(w):
                t = x / max(w - 1, 1)
                self.create_line(x, 0, x, h, fill=_lerp_color(self._c1, self._c2, t), tags="grad")
        self.tag_lower("grad")   # keep any overlaid text/items on top


def _draw_gradient_text(canvas: tk.Canvas, x: int, y: int, text: str,
                         font, c1: str, c2: str, anchor: str = "nw") -> int:
    """Draw `text` on `canvas` character-by-character, interpolating fill
    color left-to-right across the string. Returns the total pixel width."""
    import tkinter.font as tkfont
    f = tkfont.Font(font=font)
    total_w = f.measure(text)
    cx = x
    for ch in text:
        cw = f.measure(ch)
        t = 0.0 if total_w <= 0 else ((cx - x) + cw / 2) / total_w
        canvas.create_text(cx, y, text=ch, font=font,
                            fill=_lerp_color(c1, c2, t), anchor=anchor)
        cx += cw
    return total_w


class GradientBorderButton(tk.Frame):
    """A real ttk.Button ringed by a thin gradient border, built from plain
    grid-managed strips (top/bottom gradient bars, solid left/right edges)
    rather than embedding the button inside a Canvas. An earlier version
    used Canvas.create_window() to embed the button and resized it on
    <Configure> — on Windows that leaves the embedded native button
    clipped/stale after a resize (the HWND doesn't always repaint), so
    the button text rendered cut off. Plain grid geometry management
    sizes the button the normal, reliable way."""
    def __init__(self, parent, text: str, command, style: str,
                 c1: str, c2: str, bg: str, thickness: int = 2, **btn_kw):
        super().__init__(parent, bg=bg)
        btn = ttk.Button(self, text=text, command=command, style=style, **btn_kw)

        top    = GradientBar(self, c1, c2, height=thickness, bg=bg)
        bottom = GradientBar(self, c1, c2, height=thickness, bg=bg)
        left   = tk.Frame(self, bg=c1, width=thickness)
        right  = tk.Frame(self, bg=c2, width=thickness)

        top.grid(   row=0, column=0, columnspan=3, sticky="ew")
        left.grid(  row=1, column=0, sticky="ns")
        # sticky="ew" only (not "nsew") — force-stretching the button
        # vertically to exactly match the grid row's computed height
        # clipped the tops of round glyphs ("o" rendering flat-topped)
        # on displays where that computation rounds a pixel short (seen
        # at non-100% Windows display scaling). Leaving height alone lets
        # the button keep its own natural, correctly-measured height.
        btn.grid(   row=1, column=1, sticky="ew")
        right.grid( row=1, column=2, sticky="ns")
        bottom.grid(row=2, column=0, columnspan=3, sticky="ew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)


# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────
DEFAULT_PORT  = 10022
DEFAULT_KEY   = r"C:\Users\me\.ssh\tgt"
APP_DIR       = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")), "SecureSH")
SESSIONS_FILE = os.path.join(APP_DIR, "sessions.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

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
#  Settings persistence
# ─────────────────────────────────────────────
def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_settings(settings: dict):
    _ensure_app_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


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
            box = tk.Frame(self, bg=INFO_BG,
                           highlightbackground=INFO_BORDER,
                           highlightthickness=1)
            box.pack(fill="x", padx=16, pady=(16, 8))
            tk.Label(box, text=instructions.strip(),
                     bg=INFO_BG, fg=(ACCENT if _THEME_STYLE == "glow" else TEXT),
                     font=(_MONO[0], 9),
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
        title_text = "Edit Connection" if prefill else "New Connection"
        if _THEME_STYLE == "gradient":
            hdr = GradientBar(self, GRADIENT_START, GRADIENT_END, height=48, bg=BG)
            hdr.pack(fill="x")
            hdr.create_text(16, 24, text=title_text, fill=ACCENT_TEXT,
                             font=("Segoe UI", 11, "bold"), anchor="w")
        else:
            hdr = tk.Frame(self, bg=ACCENT, height=48)
            hdr.pack(fill="x")
            hdr.pack_propagate(False)
            tk.Label(hdr, text=title_text,
                     bg=ACCENT, fg=ACCENT_TEXT,
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
        if _THEME_STYLE == "gradient":
            import tkinter.font as tkfont
            tf = tkfont.Font(font=_LABELb)
            tw, th = tf.measure("SESSIONS"), tf.metrics("linespace")
            hdr_canvas = tk.Canvas(hdr, width=tw, height=th, bg=SIDEBAR_BG,
                                    highlightthickness=0, bd=0)
            _draw_gradient_text(hdr_canvas, 0, 0, "SESSIONS", _LABELb,
                                 GRADIENT_START, GRADIENT_END, anchor="nw")
            hdr_canvas.pack(side="left")
        else:
            tk.Label(hdr, text="SESSIONS", bg=SIDEBAR_BG,
                     fg=(ACCENT if _THEME_STYLE == "glow" else TEXT2),
                     font=_LABELb).pack(side="left")
        tk.Button(hdr, text="+ New", bg=SIDEBAR_BG, fg=ACCENT,
                  bd=0, relief="flat", cursor="hand2",
                  font=_LABELb,
                  activebackground=SIDEBAR_BG, activeforeground=ACCENT_HOV,
                  command=self.on_new).pack(side="right")

        # Search box
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._repopulate())
        ttk.Entry(self, textvariable=self._search_var,
                  font=_UIsm).pack(fill="x", padx=8, pady=(0, 4))

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
            if _THEME_STYLE == "gradient" and style == "Accent.TButton":
                btn = GradientBorderButton(grid, label, cmd, style,
                                            GRADIENT_START, GRADIENT_END, bg=SIDEBAR_BG)
            else:
                btn = ttk.Button(grid, text=label, command=cmd, style=style)
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
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
        query = self._search_var.get().lower().strip() if hasattr(self, "_search_var") else ""

        # Remember which folders were open
        open_folders = {
            iid for iid in self.tree.get_children()
            if self.tree.item(iid, "open")
        }
        self.tree.delete(*self.tree.get_children())

        visible = sorted(self._sessions, key=lambda x: x["name"].lower())
        if query:
            visible = [s for s in visible
                       if query in s["name"].lower()
                       or query in s.get("host", "").lower()]

        # Only show folders that contain at least one visible session
        folders = sorted({s["folder"] for s in visible if s.get("folder")})

        # Insert folder nodes
        folder_iids: dict[str, str] = {}
        for folder in folders:
            fid = FOLDER_PFX + folder
            self.tree.insert("", "end", iid=fid,
                             text=f"  📁  {folder}",
                             open=True,
                             tags=("folder",))
            folder_iids[folder] = fid

        # Insert sessions (alphabetical within each group)
        for s in visible:
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

# ─────────────────────────────────────────────
#  VT100 screen — pyte-backed with scrollback
# ─────────────────────────────────────────────
import pyte

TERM_COLS = 220
TERM_ROWS = 50

# Standard 16 ANSI colours (VS Code dark-terminal palette)
_ANSI_COLORS: dict[str, str] = {
    "black":          "#000000", "red":            "#cd3131",
    "green":          "#0dbc79", "yellow":         "#e5e510",
    "blue":           "#2472c8", "magenta":        "#bc3fbc",
    "cyan":           "#11a8cd", "white":          "#e5e5e5",
    "bright-black":   "#666666", "bright-red":     "#f14c4c",
    "bright-green":   "#23d18b", "bright-yellow":  "#f5f543",
    "bright-blue":    "#3b8eea", "bright-magenta": "#d670d6",
    "bright-cyan":    "#29b8db", "bright-white":   "#e5e5e5",
}
# un-hyphenated aliases (different pyte builds vary)
_ANSI_COLORS.update({k.replace("-", ""): v for k, v in _ANSI_COLORS.items() if "-" in k})
_ANSI_PALETTE = list(_ANSI_COLORS.values())[:16]   # indexed 0-15

def _256_color(n: int) -> str:
    if n < 16:
        return _ANSI_PALETTE[n]
    if n < 232:
        n -= 16
        b, n = n % 6, n // 6
        g, r = n % 6, n // 6
        def lv(x): return 0 if x == 0 else 55 + x * 40
        return f"#{lv(r):02x}{lv(g):02x}{lv(b):02x}"
    v = 8 + (n - 232) * 10
    return f"#{v:02x}{v:02x}{v:02x}"


class _TrackingScreen(pyte.Screen):
    """
    pyte.Screen subclass that records lines as they scroll off the top,
    so we can append them as permanent history in the Text widget.
    """
    def __init__(self, cols, rows):
        super().__init__(cols, rows)
        self.scrolled_off: list[str] = []

    def index(self):
        """Called by pyte on every LF — but only actually scrolls when the
        cursor sits on the bottom margin.  Capture the departing line only
        when a real scroll is about to happen AND the scroll region spans the
        full screen (shell output, not an ncurses app's internal viewport)."""
        if self.margins is None:
            top, bottom = 0, self.lines - 1
        else:
            top, bottom = self.margins.top, self.margins.bottom

        full_screen = (top == 0 and bottom == self.lines - 1)

        if full_screen and self.cursor.y == bottom:
            line = "".join(
                self.buffer[0][col].data or " "
                for col in range(self.columns)
            ).rstrip()
            self.scrolled_off.append(line)
        super().index()


# ─────────────────────────────────────────────
#  SSH Terminal widget
# ─────────────────────────────────────────────
class SSHTerminal(tk.Frame):
    def __init__(self, parent, transport: paramiko.Transport):
        super().__init__(parent, bg=TERM_BG)
        self._transport = transport
        self._channel   = None
        self._running   = False

        # pyte virtual terminal
        self._screen = _TrackingScreen(TERM_COLS, TERM_ROWS)
        self._stream = pyte.ByteStream(self._screen)
        self._history_lines = 0   # lines permanently written above active screen
        self._tag_cache: dict[tuple, str] = {}
        self._prev_cursor_row: int | None = None

        # Render coalescing — prevents queue build-up when holding keys
        self._render_pending = False
        self._pending_dirty: set[int] = set()
        self._pending_scrolled: list[str] = []
        self._screen_lock = threading.Lock()

        # ── Text widget ──
        self.text = tk.Text(
            self,
            bg=TERM_BG, fg=TERM_FG,
            font=_MONO,
            insertwidth=0,
            selectbackground=TERM_SEL_BG,
            selectforeground=TERM_FG,
            wrap="none", cursor="xterm",
            relief="flat", bd=0,
            padx=6, pady=4,
        )
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)
        # Small gutter so the scrollbar isn't flush against the window edge.
        tk.Frame(self, bg=TERM_BG, width=4).pack(side="right", fill="y")
        vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # Pre-allocate active screen rows in the Text widget
        self.text.insert("1.0", "\n" * (TERM_ROWS - 1))
        # Disable editing so the Text class never inserts/deletes on keypress;
        # our instance bindings still fire, and we re-enable briefly for rendering.
        self.text.configure(state="disabled")

        # ── Bindings ──
        self.text.bind("<Key>",             self._on_key)
        self.text.bind("<Tab>",             self._on_key)   # explicit: beats Text class <Tab> insert
        self.text.bind("<Button-1>",        lambda _: self.text.focus_set())
        self.text.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.text.bind("<<Paste>>",         self._on_paste)
        self.text.bind("<Control-Shift-C>", self._copy_selection)
        self.text.bind("<Control-Shift-V>", self._on_paste)
        self.text.bind("<Button-3>",        self._on_right_click)

        self._open_shell()

    # ── Colour helpers ────────────────────────

    def _resolve_color(self, raw, default: str) -> str:
        if raw == "default" or raw is None:
            return default
        if isinstance(raw, str):
            if raw in _ANSI_COLORS:
                return _ANSI_COLORS[raw]
            if len(raw) == 6:
                try:
                    int(raw, 16)
                    return f"#{raw}"
                except ValueError:
                    pass
        if isinstance(raw, int):
            return _256_color(raw)
        return default

    def _get_tag(self, fg: str, bg: str, bold: bool) -> str:
        key = (fg, bg, bold)
        if key not in self._tag_cache:
            name = f"t{len(self._tag_cache)}"
            font = (_MONO[0], _MONO[1], "bold") if bold else _MONO
            self.text.tag_configure(name, foreground=fg, background=bg, font=font)
            self._tag_cache[key] = name
            self.text.tag_raise("sel")  # new tags would outrank sel; keep sel on top
        return self._tag_cache[key]

    # ── Shell setup ───────────────────────────

    def _open_shell(self):
        try:
            chan = self._transport.open_session()
            chan.get_pty(term="xterm", width=TERM_COLS, height=TERM_ROWS)
            chan.invoke_shell()
            chan.settimeout(0.05)
            self._channel = chan
            self._running = True
            threading.Thread(target=self._read_loop, daemon=True).start()
            self.text.focus_set()
        except Exception as e:
            self._status(f"[Terminal error: {e}]\n")

    # ── Read loop ─────────────────────────────

    def _read_loop(self):
        while self._running:
            try:
                data = self._channel.recv(4096)
                if data:
                    self._stream.feed(data)
                    with self._screen_lock:
                        self._pending_dirty.update(self._screen.dirty)
                        self._screen.dirty.clear()
                        self._pending_scrolled.extend(self._screen.scrolled_off)
                        self._screen.scrolled_off.clear()
                    if not self._render_pending:
                        self._render_pending = True
                        self.after(0, self._do_render)
                elif self._channel.closed or self._channel.exit_status_ready():
                    break
            except Exception:
                time.sleep(0.05)
        self.after(0, self._status, "\n[Session closed]\n")

    # ── Rendering ─────────────────────────────

    def _do_render(self):
        """Drain the accumulated dirty/scrolled state and render once."""
        with self._screen_lock:
            dirty = frozenset(self._pending_dirty)
            self._pending_dirty.clear()
            scrolled = list(self._pending_scrolled)
            self._pending_scrolled.clear()
        self._render_pending = False
        self._render(dirty, scrolled)

    def _tw_line(self, screen_row: int) -> int:
        """Map pyte screen row (0-based) → Text widget line number (1-based)."""
        return self._history_lines + screen_row + 1

    def _render(self, dirty: frozenset, scrolled: list[str]):
        self.text.configure(state="normal")
        # 1. Append scrolled-off lines as permanent history (plain text)
        if scrolled:
            insert_at = f"{self._history_lines + 1}.0"
            self.text.insert(insert_at, "\n".join(scrolled) + "\n")
            self._history_lines += len(scrolled)

        # 2. Re-render dirty rows + cursor rows (current and previous)
        cur_y = self._screen.cursor.y
        cur_x = self._screen.cursor.x

        # When a full-screen app (nano, vim, etc.) has a scroll region active,
        # redraw every row. Relying solely on pyte's dirty set leaves stale
        # widget content whenever scrolling uses delete_lines or index with
        # margins — the safest fix is a complete repaint in that mode.
        if self._screen.margins is not None:
            rows_to_render = set(range(TERM_ROWS))
        else:
            rows_to_render = set(dirty) | {cur_y}
            if self._prev_cursor_row is not None:
                rows_to_render.add(self._prev_cursor_row)

        for row in rows_to_render:
            if row >= TERM_ROWS:
                continue
            tw = self._tw_line(row)

            end_line = int(self.text.index("end").split(".")[0]) - 1
            while end_line < tw:
                self.text.insert("end", "\n")
                end_line += 1

            self.text.delete(f"{tw}.0", f"{tw}.end")

            # Find last column that needs rendering
            render_to = -1
            for c in range(TERM_COLS - 1, -1, -1):
                ch = self._screen.buffer[row][c]
                if (ch.data and ch.data.strip()) or ch.bg != "default" or ch.reverse:
                    render_to = c
                    break
            if row == cur_y:
                render_to = max(render_to, cur_x)
            if render_to < 0:
                continue

            # Build colour runs and insert
            run_chars: list[str] = []
            run_tag:   str | None = None
            run_start: int        = 0

            for col in range(render_to + 1):
                char = self._screen.buffer[row][col]
                ch   = char.data if char.data else " "

                fg = self._resolve_color(char.fg, TERM_FG)
                bg = self._resolve_color(char.bg, TERM_BG)

                if char.reverse:
                    fg, bg = bg, fg
                if row == cur_y and col == cur_x:   # block cursor
                    fg, bg = bg, fg
                    if fg == bg:
                        fg, bg = TERM_BG, TERM_FG

                tag = self._get_tag(fg, bg, char.bold)

                if tag == run_tag:
                    run_chars.append(ch)
                else:
                    if run_chars:
                        self.text.insert(f"{tw}.{run_start}", "".join(run_chars), run_tag)
                    run_chars = [ch]
                    run_tag   = tag
                    run_start = col

            if run_chars:
                self.text.insert(f"{tw}.{run_start}", "".join(run_chars), run_tag)

        self._prev_cursor_row = cur_y

        # 3. Scroll to show the cursor row
        self.text.see(f"{self._tw_line(cur_y)}.0")
        self.text.configure(state="disabled")

    def _status(self, msg: str):
        self.text.configure(state="normal")
        self.text.insert("end", msg)
        self.text.see("end")
        self.text.configure(state="disabled")

    # ── Input ─────────────────────────────────

    def _on_key(self, event):
        if not self._channel or self._channel.closed:
            return "break"
        # Ctrl+letter → control character (Ctrl+C = ^C, etc.)
        if event.state & 0x4:
            if len(event.keysym) == 1 and event.keysym.isalpha():
                self._send(chr(ord(event.keysym.upper()) - 64))
                return "break"
        send = _KEY_MAP.get(event.keysym) or (event.char or None)
        if send:
            self._send(send)
        return "break"

    def _on_paste(self, _=None):
        try:
            self._send(self.clipboard_get())
        except Exception:
            pass
        return "break"

    def _copy_selection(self, _=None):
        try:
            txt = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(txt)
        except tk.TclError:
            pass
        return "break"

    def _on_mouse_release(self, _=None):
        try:
            txt = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if txt:
                self.clipboard_clear()
                self.clipboard_append(txt)
        except tk.TclError:
            pass

    def _on_right_click(self, _=None):
        self._on_paste()

    def _select_all(self):
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def _clear_history(self):
        """Remove history lines, keep the active screen intact."""
        if self._history_lines:
            self.text.configure(state="normal")
            self.text.delete("1.0", f"{self._history_lines + 1}.0")
            self.text.configure(state="disabled")
            self._history_lines = 0

    def _send(self, data: str):
        try:
            self._channel.send(data)
        except Exception:
            pass

    # ── Cleanup ───────────────────────────────

    def close(self):
        self._running = False
        if self._channel:
            try:  self._channel.send("\x04")   # EOF → shell exits cleanly, saves history
            except Exception: pass
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
        self._welcome_tab: str | None = None

        self._build_menu()
        self._build_titlebar()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Frame(self, bg=BG2, height=24)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        if _THEME_STYLE == "gradient":
            GradientBar(status, GRADIENT_START, GRADIENT_END, vertical=True,
                        width=3, bg=BG2).pack(side="left", fill="y")
        else:
            tk.Frame(status, bg=ACCENT, width=3).pack(side="left", fill="y")
        tk.Label(status, textvariable=self.status_var,
                 bg=BG2, fg=TEXT2, font=_UIsm,
                 anchor="w").pack(side="left", padx=8)

        # Paned layout — sashwidth wide enough to grab & drag comfortably
        # (a 1px sash is technically draggable but nearly impossible to
        # grab with a mouse), so the sidebar can be widened for long
        # server names.
        pane = tk.PanedWindow(self, orient="horizontal",
                              sashwidth=6, sashrelief="flat",
                              bg=BORDER, bd=0, opaqueresize=True)
        pane.pack(fill="both", expand=True)

        self.sidebar  = SessionsSidebar(pane,
                                        on_connect=self._connect_with,
                                        on_new=self._connect)

        # Wrap the notebook so there's a small margin before the window's
        # right edge (previously content ran flush to it) — applies to
        # every tab, not just an active terminal.
        content_wrap = tk.Frame(pane, bg=BG)
        self.notebook = ttk.Notebook(content_wrap)
        self.notebook.bind("<Button-3>", self._on_tab_right_click)
        self.notebook.pack(side="left", fill="both", expand=True)
        tk.Frame(content_wrap, bg=BG, width=6).pack(side="right", fill="y")

        pane.add(self.sidebar,     minsize=180, width=200)
        pane.add(content_wrap,     minsize=500)

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

        self._theme_var = tk.StringVar(value=CURRENT_THEME)
        theme_menu = tk.Menu(mb, tearoff=0)
        for name in THEMES:
            theme_menu.add_radiobutton(
                label=name, value=name, variable=self._theme_var,
                command=lambda n=name: self._change_theme(n))
        mb.add_cascade(label="Theme", menu=theme_menu)

        self.bind_all("<Control-n>", lambda _: self._connect())
        self.bind_all("<Control-d>", lambda _: self._disconnect_active())
        self.bind_all("<Control-w>", lambda _: self._disconnect_active())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_titlebar(self):
        # height=48, not 42: the gradient theme's New Connection button
        # (GradientBorderButton) is a couple pixels taller than a plain
        # ttk.Button — its own hand-drawn border adds to the button's
        # natural height. At 42 + pack_propagate(False) that overflow
        # got clipped by the fixed-height frame, shaving the tops off
        # round glyphs ("o" rendering flat). 48 gives every theme's
        # button comfortable headroom regardless.
        bar = tk.Frame(self, bg=BG2, height=48)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        if _THEME_STYLE == "gradient":
            GradientBar(bar, GRADIENT_START, GRADIENT_END, vertical=True,
                        width=4, bg=BG2).pack(side="left", fill="y")
            GradientBorderButton(bar, "New Connection", self._connect,
                                  "Accent.TButton", GRADIENT_START, GRADIENT_END,
                                  bg=BG2).pack(side="left", padx=8, pady=6)
        else:
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
        if _WELCOME_CURSOR:
            title, title_font = "SecureSH_", (_MONO[0], 30, "bold")
            info_font, info_text = _MONO, f"default port {DEFAULT_PORT}  ·  key {DEFAULT_KEY}"
        else:
            title, title_font = "SecureSH", ("Segoe UI", 28, "bold")
            info_font, info_text = _UIsm, f"Default port {DEFAULT_PORT}  ·  Key  {DEFAULT_KEY}"
        if _THEME_STYLE == "gradient":
            import tkinter.font as tkfont
            tf = tkfont.Font(font=title_font)
            tw, th = tf.measure(title), tf.metrics("linespace")
            title_canvas = tk.Canvas(f, width=tw, height=th, bg=BG,
                                      highlightthickness=0, bd=0)
            _draw_gradient_text(title_canvas, 0, 0, title, title_font,
                                 GRADIENT_START, GRADIENT_END, anchor="nw")
            title_canvas.pack(pady=(80, 4))
        else:
            tk.Label(f, text=title,
                     bg=BG, fg=ACCENT,
                     font=title_font).pack(pady=(80, 4))
        tk.Label(f, text="Double-click a saved session  •  Ctrl+N for a new connection",
                 bg=BG, fg=TEXT2, font=("Segoe UI", 10)).pack()
        tk.Label(f, text=info_text,
                 bg=BG, fg=TEXT2, font=info_font).pack(pady=6)
        self.notebook.add(f, text="  Welcome  ")
        self._welcome_tab = self.notebook.tabs()[-1]

    # ── Connection flow ───────────────────────────

    def _connect(self):
        dlg = ConnectDialog(self, existing_folders=self.sidebar._folders())
        if dlg.result is None:
            return
        if dlg.session:
            self.sidebar.upsert(dlg.session)
            dlg.result["name"] = dlg.session["name"]
        self._launch(dlg.result)

    def _connect_with(self, session: dict):
        dlg = ConnectDialog(self, prefill=session,
                            existing_folders=self.sidebar._folders())
        if dlg.result is None:
            return
        if dlg.session:
            self.sidebar.upsert(dlg.session)
        dlg.result["name"] = (dlg.session or session).get("name")
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

        conn_str  = f"{p['username']}@{p['host']}:{p['port']}"
        tab_label = p.get("name") or conn_str
        self.after(0, lambda: self._ok(t, sftp, cwd, tab_label, conn_str))

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

    def _ok(self, transport, sftp, cwd, tab_label, conn_str):
        self.conn_label.config(text=f"  ● {tab_label}", fg=SUCCESS_FG)
        self.status_var.set(f"Connected  {conn_str}")

        if self._welcome_tab and self._welcome_tab in self.notebook.tabs():
            self.notebook.forget(self._welcome_tab)
            self._welcome_tab = None

        sub = ttk.Notebook(self.notebook)

        terminal = SSHTerminal(sub, transport)
        sub.add(terminal, text="  Terminal  ")

        browser = SFTPBrowser(sub, sftp, cwd, self.status_var)
        sub.add(browser, text="  SFTP  ")

        self.notebook.add(sub, text=f"  {tab_label}  ")
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

    def _on_tab_right_click(self, event):
        try:
            idx = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        tab_id = self.notebook.tabs()[idx]
        if tab_id not in self._tab_handles:
            return
        label = self.notebook.tab(tab_id, "text").strip()
        m = tk.Menu(self, tearoff=0, font=_UI,
                    bg=BG, fg=TEXT, activebackground=SEL_BG,
                    activeforeground=TEXT, relief="flat", bd=1)
        m.add_command(label=f"Close  '{label}'",
                      command=lambda t=tab_id: self._close_tab(t))
        m.post(event.x_root, event.y_root)

    def _close_tab(self, tab_id: str):
        if tab_id in self._tab_handles:
            transport, sftp, terminal = self._tab_handles.pop(tab_id)
            terminal.close()
            for obj in (sftp, transport):
                try:  obj.close()
                except Exception: pass
        self.notebook.forget(tab_id)
        self.status_var.set("Disconnected.")
        if not self._tab_handles:
            self.conn_label.config(text="No active session", fg=TEXT2)

    def _disconnect_active(self):
        tab = self.notebook.select()
        if tab not in self._tab_handles:
            return
        self._close_tab(tab)

    def _on_close(self):
        for transport, sftp, terminal in self._tab_handles.values():
            terminal.close()
            for obj in (sftp, transport):
                try:  obj.close()
                except Exception: pass
        self.destroy()

    def _change_theme(self, name: str):
        if name == CURRENT_THEME:
            return
        settings = load_settings()
        settings["theme"] = name
        save_settings(settings)

        msg = f'Theme set to "{name}".\n\nRestart SecureSH now to apply it?'
        if self._tab_handles:
            msg = (f'Theme set to "{name}".\n\n'
                   "You have active session(s) — restarting now will "
                   "disconnect them.\n\nRestart SecureSH now to apply it?")
        if not messagebox.askyesno("Theme Changed", msg, parent=self):
            return

        if getattr(sys, "frozen", False):
            subprocess.Popen([sys.executable] + sys.argv[1:])
        else:
            subprocess.Popen([sys.executable, os.path.abspath(__file__)] + sys.argv[1:])
        self._on_close()


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
    _activate_theme(load_settings().get("theme", DEFAULT_THEME))
    app = SecureSHApp()
    app.mainloop()
