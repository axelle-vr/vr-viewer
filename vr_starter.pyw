# -*- coding: utf-8 -*-
"""
VR-viewer starter
-----------------
Kies je hoofdmap met VR-modellen en klik op Start.
De app start zelf een lokale webserver en een ngrok-tunnel en toont
de https-link die je op de Meta Quest opent.

Gebruikt enkel de standaardbibliotheek van Python (geen extra installaties).
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

APP_NAME = "VR-viewer starter"
DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "VRViewerStarter")
SETTINGS_FILE = os.path.join(DATA_DIR, "instellingen.json")
NGROK_ZIP_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
NGROK_TOKEN_PAGE = "https://dashboard.ngrok.com/get-started/your-authtoken"
NGROK_SIGNUP_PAGE = "https://dashboard.ngrok.com/signup"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW

# ---------- kleuren en letters ----------
BG = "#eef0f3"
CARD = "#ffffff"
BORDER = "#dde1e7"
INK = "#1c2330"
INK_2 = "#2a3342"
MUTED = "#5f6878"
HEADER_MUTED = "#9aa7b8"
YELLOW = "#f2b705"
YELLOW_HOVER = "#ffc62e"
YELLOW_SOFT = "#fff6d6"
STEEL = "#8fb0d1"
GREEN = "#2f7d4f"
GREEN_SOFT = "#e3f2e8"
RED = "#b3261e"
CODE_BG = "#f3f5f8"

FONT = "Segoe UI"
FONT_SEMI = "Segoe UI Semibold"
MONO = "Consolas"

LOGO_HEADER = "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"
LOGO_ICON = "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"


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


class QuietHandler(SimpleHTTPRequestHandler):
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        ".glb": "model/gltf-binary",
        ".gltf": "model/gltf+json",
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".wasm": "application/wasm",
    })

    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


# ---------- eigen knoppen en onderdelen ----------
class FlatButton(tk.Label):
    """Platte knop met hover-effect."""
    STYLES = {
        "primary": (YELLOW, INK, YELLOW_HOVER, None),
        "secondary": (CARD, INK, CODE_BG, BORDER),
        "ghost": (CARD, MUTED, CODE_BG, None),
    }

    def __init__(self, parent, text, command, kind="secondary", big=False, **kw):
        bg, fg, hover, border = self.STYLES[kind]
        font = (FONT_SEMI, 13 if big else 10)
        padx, pady = (26, 10) if big else (12, 6)
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady,
                         cursor="hand2", highlightthickness=1 if border else 0,
                         highlightbackground=border or bg, **kw)
        self._bg, self._hover, self._fg = bg, hover, fg
        self.command = command
        self.enabled = True
        self.bind("<Enter>", lambda e: self.enabled and self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg if self.enabled else "#e6e8ec"))
        self.bind("<Button-1>", self._click)

    def _click(self, _):
        if self.enabled and self.command:
            self.command()

    def set_enabled(self, on):
        self.enabled = on
        self.configure(bg=self._bg if on else "#e6e8ec", fg=self._fg if on else "#a1a8b3",
                       cursor="hand2" if on else "arrow")


class StepBadge(tk.Canvas):
    def __init__(self, parent, number):
        super().__init__(parent, width=30, height=30, bg=CARD, highlightthickness=0)
        self.number = number
        self.set_done(False)

    def set_done(self, done):
        self.delete("all")
        if done:
            self.create_oval(2, 2, 28, 28, fill=GREEN, outline=GREEN)
            self.create_text(15, 15, text="✓", fill="#ffffff", font=(FONT_SEMI, 12))
        else:
            self.create_oval(2, 2, 28, 28, fill=CARD, outline=INK, width=2)
            self.create_text(15, 15, text=str(self.number), fill=INK, font=(FONT_SEMI, 11))


class Card(tk.Frame):
    def __init__(self, parent, number, title, subtitle=""):
        super().__init__(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        head = tk.Frame(self, bg=CARD)
        head.pack(fill="x", padx=18, pady=(16, 10))
        self.badge = StepBadge(head, number)
        self.badge.pack(side="left", padx=(0, 12))
        titles = tk.Frame(head, bg=CARD)
        titles.pack(side="left", fill="x", expand=True)
        tk.Label(titles, text=title, bg=CARD, fg=INK, font=(FONT_SEMI, 12), anchor="w").pack(fill="x")
        if subtitle:
            tk.Label(titles, text=subtitle, bg=CARD, fg=MUTED, font=(FONT, 9), anchor="w").pack(fill="x")
        self.body = tk.Frame(self, bg=CARD)
        self.body.pack(fill="x", padx=(60, 18), pady=(0, 16))


class App:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.server = None
        self.ngrok_proc = None
        self.ngrok_output = []
        self.port = None
        self.public_url = None
        self.running = False
        self.model_links = []  # (naam, url)

        root.title(APP_NAME)
        root.configure(bg=BG)
        root.minsize(660, 800)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            self.icon_img = tk.PhotoImage(data=LOGO_ICON)
            root.iconphoto(True, self.icon_img)
        except tk.TclError:
            self.icon_img = None
        try:
            ico = os.path.join(app_dir(), "app.ico")
            if os.path.isfile(ico):
                root.iconbitmap(default=ico)
        except tk.TclError:
            pass

        self.build_ui()

        folder = self.settings.get("map", "")
        if folder and os.path.isdir(folder):
            self.folder_var.set(folder)
        self.refresh_files()
        self.refresh_ngrok_status()
        self.set_state("stopped")

    # ---------- opbouw ----------
    def build_ui(self):
        # kopbalk
        header = tk.Frame(self.root, bg=INK)
        header.pack(fill="x")
        tk.Frame(header, bg=YELLOW, height=4).pack(fill="x", side="top")
        inner = tk.Frame(header, bg=INK)
        inner.pack(fill="x", padx=20, pady=16)
        try:
            self.logo_img = tk.PhotoImage(data=LOGO_HEADER)
            tk.Label(inner, image=self.logo_img, bg=INK).pack(side="left", padx=(0, 14))
        except tk.TclError:
            self.logo_img = None
        titles = tk.Frame(inner, bg=INK)
        titles.pack(side="left")
        tk.Label(titles, text="VR-viewer starter", bg=INK, fg="#ffffff",
                 font=(FONT_SEMI, 17), anchor="w").pack(anchor="w")
        tk.Label(titles, text="Je constructie in VR op de Meta Quest", bg=INK, fg=HEADER_MUTED,
                 font=(FONT, 10), anchor="w").pack(anchor="w")
        self.pill = tk.Label(inner, text="", font=(FONT_SEMI, 9), padx=12, pady=4)
        self.pill.pack(side="right")

        tip = ("Tip: open op de Quest enkel het begin van de link en maak er een bladwijzer van. "
               "Je ziet dan telkens al je modellen.")
        tk.Label(self.root, text=tip, bg=BG, fg=MUTED, font=(FONT, 9), anchor="w", justify="left",
                 wraplength=600).pack(side="bottom", fill="x", padx=22, pady=(0, 14))

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=18)

        # kaart 1: map
        c1 = Card(body, 1, "Kies je map met VR-modellen", "Eén hoofdmap, eventueel met een submap per model")
        c1.pack(fill="x", pady=(0, 12))
        self.card_folder = c1
        row = tk.Frame(c1.body, bg=CARD)
        row.pack(fill="x")
        self.folder_var = tk.StringVar()
        entry_wrap = tk.Frame(row, bg=CODE_BG, highlightthickness=1, highlightbackground=BORDER)
        entry_wrap.pack(side="left", fill="x", expand=True)
        self.folder_entry = tk.Entry(entry_wrap, textvariable=self.folder_var, relief="flat", bg=CODE_BG,
                                     fg=INK, font=(FONT, 10), insertbackground=INK)
        self.folder_entry.pack(fill="x", padx=8, pady=6)
        self.folder_entry.bind("<Return>", lambda e: self.folder_changed())
        self.folder_entry.bind("<FocusOut>", lambda e: self.folder_changed())
        FlatButton(row, "Bladeren…", self.choose_folder).pack(side="left", padx=(8, 0))
        self.files_label = tk.Label(c1.body, text="", bg=CARD, fg=MUTED, font=(FONT, 9),
                                    anchor="w", justify="left", wraplength=500)
        self.files_label.pack(fill="x", pady=(8, 0))

        # kaart 2: ngrok
        c2 = Card(body, 2, "ngrok instellen", "Zorgt voor de beveiligde link. Eén keer instellen.")
        c2.pack(fill="x", pady=(0, 12))
        self.card_ngrok = c2
        self.ngrok_label = tk.Label(c2.body, text="", bg=CARD, fg=INK, font=(FONT, 10),
                                    anchor="w", justify="left", wraplength=500)
        self.ngrok_label.pack(fill="x")
        nrow = tk.Frame(c2.body, bg=CARD)
        nrow.pack(anchor="w", pady=(10, 0))
        self.dl_btn = FlatButton(nrow, "Download ngrok", self.download_ngrok)
        self.dl_btn.pack(side="left")
        self.token_btn = FlatButton(nrow, "Authtoken invullen…", self.ask_token)
        self.token_btn.pack(side="left", padx=(8, 0))
        FlatButton(nrow, "Gratis account maken", lambda: webbrowser.open(NGROK_SIGNUP_PAGE),
                   kind="ghost").pack(side="left", padx=(8, 0))

        # kaart 3: starten
        c3 = Card(body, 3, "Start en open op de Quest", "Laat dit venster open zolang je de Quest gebruikt")
        c3.pack(fill="both", expand=True)
        self.card_run = c3
        top = tk.Frame(c3.body, bg=CARD)
        top.pack(fill="x")
        self.start_btn = FlatButton(top, "▶  Start", self.toggle, kind="primary", big=True)
        self.start_btn.pack(side="left")
        self.status_label = tk.Label(top, text="", bg=CARD, fg=MUTED, font=(FONT, 10),
                                     anchor="w", justify="left", wraplength=320)
        self.status_label.pack(side="left", padx=(14, 0), fill="x", expand=True)

        # grote link
        self.link_box = tk.Frame(c3.body, bg=YELLOW_SOFT, highlightthickness=1, highlightbackground=YELLOW)
        tk.Label(self.link_box, text="TYP DIT IN DE BROWSER VAN JE QUEST", bg=YELLOW_SOFT, fg=MUTED,
                 font=(FONT_SEMI, 8), anchor="w").pack(fill="x", padx=14, pady=(10, 0))
        self.big_link = tk.Label(self.link_box, text="", bg=YELLOW_SOFT, fg=INK, font=(MONO, 13, "bold"),
                                 anchor="w", justify="left", wraplength=480)
        self.big_link.pack(fill="x", padx=14, pady=(2, 8))
        lrow = tk.Frame(self.link_box, bg=YELLOW_SOFT)
        lrow.pack(anchor="w", padx=14, pady=(0, 12))
        FlatButton(lrow, "Kopieer link", self.copy_link).pack(side="left")
        FlatButton(lrow, "Test op deze computer", self.open_local).pack(side="left", padx=(8, 0))

        # modellenlijst
        self.models_title = tk.Label(c3.body, text="MODELLEN IN JE MAP", bg=CARD, fg=MUTED,
                                     font=(FONT_SEMI, 8), anchor="w")
        self.models_frame = tk.Frame(c3.body, bg=CARD)
        self.links = tk.Listbox(self.models_frame, height=5, font=(FONT, 10), activestyle="none",
                                bg=CODE_BG, fg=INK, relief="flat", highlightthickness=0,
                                selectbackground=YELLOW, selectforeground=INK, borderwidth=0)
        self.links.pack(fill="both", expand=True)
        self.links.bind("<<ListboxSelect>>", lambda e: self.show_selected())


    # ---------- toestand ----------
    def set_state(self, state, text=None):
        if state == "stopped":
            self.pill.configure(text="●  GESTOPT", bg=INK_2, fg=HEADER_MUTED)
            self.start_btn.configure(text="▶  Start")
            self.status_label.configure(text=text or "Klik op Start als stap 1 en 2 in orde zijn.", fg=MUTED)
            self.link_box.pack_forget()
            self.models_title.pack_forget()
            self.models_frame.pack_forget()
            self.card_run.badge.set_done(False)
        elif state == "starting":
            self.pill.configure(text="●  OPSTARTEN…", bg=YELLOW, fg=INK)
            self.start_btn.configure(text="■  Stop")
            self.status_label.configure(text=text or "Server en ngrok worden gestart…", fg=MUTED)
        elif state == "active":
            self.pill.configure(text="●  ACTIEF", bg=GREEN, fg="#ffffff")
            self.start_btn.configure(text="■  Stop")
            self.status_label.configure(text=text or "Klaar. Open de link hieronder op je Quest.", fg=GREEN)
            self.link_box.pack(fill="x", pady=(14, 0))
            self.card_run.badge.set_done(True)

    def flash(self, text, color=GREEN):
        self.status_label.configure(text=text, fg=color)

    # ---------- map ----------
    def choose_folder(self):
        start = self.folder_var.get() or os.path.expanduser("~")
        d = filedialog.askdirectory(initialdir=start, title="Kies je map met VR-modellen")
        if d:
            self.folder_var.set(os.path.normpath(d))
            self.folder_changed()

    def folder_changed(self):
        self.settings["map"] = self.folder_var.get()
        save_settings(self.settings)
        self.refresh_files()

    def html_files(self):
        """HTML-bestanden in de map en in submappen (tot 2 niveaus diep), als relatieve paden."""
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            return []
        found = []
        base_depth = folder.rstrip("\\/").count(os.sep)
        for root, dirs, files in os.walk(folder):
            dirs[:] = sorted(d for d in dirs if not d.startswith((".", "_")))
            if root.count(os.sep) - base_depth >= 2:
                dirs[:] = []
            for f in sorted(files):
                if f.lower().endswith((".html", ".htm")):
                    rel = os.path.relpath(os.path.join(root, f), folder).replace(os.sep, "/")
                    found.append(rel)
        return found

    def refresh_files(self):
        folder = self.folder_var.get()
        ok = False
        if not folder:
            txt = "Nog geen map gekozen."
        elif not os.path.isdir(folder):
            txt = "Deze map bestaat niet."
        else:
            html = self.html_files()
            if not html:
                txt = "Geen VR-pagina's (HTML) gevonden. Zet het bestand dat Claude maakte in deze map."
            else:
                ok = True
                names = ", ".join(html[:6]) + (" …" if len(html) > 6 else "")
                txt = "✓ {} model{} gevonden: {}".format(len(html), "" if len(html) == 1 else "len", names)
        self.files_label.configure(text=txt, fg=GREEN if ok else MUTED)
        self.card_folder.badge.set_done(ok)
        if self.running and self.public_url:
            self.fill_links()

    # ---------- ngrok ----------
    def find_ngrok(self):
        for c in (os.path.join(app_dir(), "ngrok.exe"),
                  os.path.join(self.folder_var.get() or "", "ngrok.exe"),
                  os.path.join(DATA_DIR, "ngrok.exe")):
            if c and os.path.isfile(c):
                return c
        return shutil.which("ngrok")

    def refresh_ngrok_status(self):
        exe = self.find_ngrok()
        token = self.settings.get("token_ingesteld")
        if exe and token:
            txt, color = "✓ ngrok is klaar voor gebruik.", GREEN
        elif exe:
            txt, color = "ngrok is gedownload. Vul nog één keer je authtoken in.", INK
        else:
            txt, color = "ngrok ontbreekt nog. Klik op ‘Download ngrok’ (±10 MB).", INK
        self.ngrok_label.configure(text=txt, fg=color)
        self.dl_btn.set_enabled(not exe)
        self.token_btn.set_enabled(bool(exe))
        self.card_ngrok.badge.set_done(bool(exe and token))

    def download_ngrok(self):
        self.dl_btn.set_enabled(False)
        self.ngrok_label.configure(text="ngrok wordt gedownload…", fg=MUTED)

        def work():
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                zpath = os.path.join(DATA_DIR, "ngrok.zip")
                urllib.request.urlretrieve(NGROK_ZIP_URL, zpath)
                with zipfile.ZipFile(zpath) as z:
                    z.extract("ngrok.exe", DATA_DIR)
                os.remove(zpath)
                self.root.after(0, self.refresh_ngrok_status)
            except Exception as e:
                msg = ("Download mislukt: {}\n\nDownload ngrok zelf via ngrok.com en zet ngrok.exe "
                       "naast deze app.").format(e)
                self.root.after(0, lambda: (messagebox.showerror(APP_NAME, msg), self.refresh_ngrok_status()))

        threading.Thread(target=work, daemon=True).start()

    def ask_token(self):
        exe = self.find_ngrok()
        if not exe:
            return
        if messagebox.askyesno(APP_NAME, "Je authtoken staat op je ngrok-dashboard.\n\nWil je die pagina nu openen?"):
            webbrowser.open(NGROK_TOKEN_PAGE)
        token = simpledialog.askstring(APP_NAME, "Plak hier je ngrok-authtoken:", parent=self.root)
        if not token:
            return
        token = token.strip().split()[-1]  # werkt ook als je het hele commando plakt
        try:
            r = subprocess.run([exe, "config", "add-authtoken", token], capture_output=True,
                               text=True, creationflags=NO_WINDOW, timeout=30)
            if r.returncode == 0:
                self.settings["token_ingesteld"] = True
                save_settings(self.settings)
                messagebox.showinfo(APP_NAME, "Authtoken opgeslagen. Je hoeft dit niet opnieuw te doen.")
            else:
                messagebox.showerror(APP_NAME, "Dat lukte niet:\n\n" + (r.stderr or r.stdout))
        except Exception as e:
            messagebox.showerror(APP_NAME, "Dat lukte niet: {}".format(e))
        self.refresh_ngrok_status()

    # ---------- start / stop ----------
    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning(APP_NAME, "Kies eerst een map (stap 1).")
            return
        exe = self.find_ngrok()
        if not exe:
            messagebox.showwarning(APP_NAME, "Download eerst ngrok (stap 2).")
            return
        self.folder_changed()

        handler = partial(QuietHandler, directory=folder)
        self.server = None
        for port in range(8000, 8020):
            try:
                self.server = ThreadingHTTPServer(("127.0.0.1", port), handler)
                self.port = port
                break
            except OSError:
                continue
        if not self.server:
            messagebox.showerror(APP_NAME, "Geen vrije poort gevonden (8000–8019).")
            return
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

        self.ngrok_output = []
        try:
            self.ngrok_proc = subprocess.Popen(
                [exe, "http", str(self.port), "--log", "stdout"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                creationflags=NO_WINDOW)
        except Exception as e:
            self.stop()
            messagebox.showerror(APP_NAME, "ngrok kon niet starten: {}".format(e))
            return
        threading.Thread(target=self.read_ngrok, daemon=True).start()

        self.running = True
        self.set_state("starting")
        threading.Thread(target=self.wait_for_url, daemon=True).start()

    def read_ngrok(self):
        proc = self.ngrok_proc
        try:
            for line in proc.stdout:
                self.ngrok_output.append(line.strip())
                if len(self.ngrok_output) > 200:
                    self.ngrok_output.pop(0)
        except Exception:
            pass

    def url_from_log(self):
        for line in list(self.ngrok_output):
            if "started tunnel" in line and "url=https://" in line:
                return line.split("url=", 1)[1].split()[0].strip('"')
        return None

    def api_addr_from_log(self):
        for line in list(self.ngrok_output):
            if "starting web service" in line and "addr=" in line:
                return line.split("addr=", 1)[1].split()[0].strip('"')
        return None

    def wait_for_url(self):
        deadline = time.time() + 25
        while time.time() < deadline and self.running:
            url = self.url_from_log()
            if url:
                self.root.after(0, lambda u=url: self.on_url(u))
                return
            if self.ngrok_proc and self.ngrok_proc.poll() is not None:
                break
            addr = self.api_addr_from_log()
            if addr:
                try:
                    with urllib.request.urlopen("http://{}/api/tunnels".format(addr), timeout=2) as r:
                        data = json.loads(r.read().decode("utf-8"))
                    for t in data.get("tunnels", []):
                        if t.get("public_url", "").startswith("https://"):
                            url = t["public_url"]
                            self.root.after(0, lambda u=url: self.on_url(u))
                            return
                except Exception:
                    pass
            time.sleep(0.5)
        if self.running:
            self.root.after(0, self.on_ngrok_failed)

    def on_url(self, url):
        self.public_url = url
        self.set_state("active")
        self.fill_links()

    def fill_links(self):
        base = self.public_url.rstrip("/")
        self.model_links = [("Alle modellen (startpagina)", base + "/")]
        for rel in self.html_files():
            self.model_links.append((rel, base + "/" + urllib.parse.quote(rel)))
        self.links.delete(0, "end")
        for name, _ in self.model_links:
            self.links.insert("end", "  " + name.replace("/", "  ›  "))
        self.links.configure(height=min(len(self.model_links), 6))
        if len(self.model_links) > 1:
            self.models_title.pack(fill="x", pady=(14, 4))
            self.models_frame.pack(fill="both", expand=True)
        self.links.selection_clear(0, "end")
        self.links.selection_set(0)
        self.show_selected()

    def on_ngrok_failed(self):
        out = "\n".join(self.ngrok_output[-15:])
        self.stop()
        if "4018" in out or "authtoken" in out.lower():
            self.settings["token_ingesteld"] = False
            save_settings(self.settings)
            self.refresh_ngrok_status()
            messagebox.showwarning(APP_NAME, "ngrok vraagt om je authtoken.\n\n"
                                             "Klik op ‘Authtoken invullen…’ in stap 2 en probeer opnieuw.")
        elif "108" in out or "already online" in out.lower():
            messagebox.showwarning(APP_NAME, "Er draait al een andere ngrok (bv. in een terminalvenster). "
                                             "Sluit die eerst via Taakbeheer en probeer opnieuw.")
        else:
            messagebox.showerror(APP_NAME, "ngrok gaf geen link.\n\nLaatste meldingen:\n" + (out or "(geen)"))

    def stop(self):
        self.running = False
        if self.ngrok_proc:
            try:
                self.ngrok_proc.terminate()
                self.ngrok_proc.wait(timeout=5)
            except Exception:
                try:
                    self.ngrok_proc.kill()
                except Exception:
                    pass
            self.ngrok_proc = None
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.server = None
        self.public_url = None
        self.model_links = []
        self.links.delete(0, "end")
        self.set_state("stopped", "Gestopt.")

    # ---------- links ----------
    def selected(self):
        sel = self.links.curselection()
        if not sel or sel[0] >= len(self.model_links):
            return self.model_links[0] if self.model_links else None
        return self.model_links[sel[0]]

    def show_selected(self):
        item = self.selected()
        self.big_link.configure(text=item[1].replace("https://", "") if item else "")

    def copy_link(self):
        item = self.selected()
        if not item:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(item[1])
        self.flash("✓ Link gekopieerd.")

    def open_local(self):
        if not self.server:
            return
        item = self.selected()
        path = item[1].split(self.public_url.rstrip("/"), 1)[-1] if item else "/"
        webbrowser.open("http://localhost:{}{}".format(self.port, path or "/"))

    def on_close(self):
        self.stop()
        self.root.destroy()


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # scherpe tekst op hoge-resolutieschermen
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("VRViewerStarter")  # eigen icoon in taakbalk
    except Exception:
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
