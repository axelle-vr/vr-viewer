# -*- coding: utf-8 -*-
"""
VR-viewer starter
-----------------
Kies een map met je VR-pagina's (HTML) en klik op Start.
De app start zelf een lokale webserver en een ngrok-tunnel en toont
de https-link die je op de Meta Quest intypt.

Werkt als gewone app (GitHub-download) en als Microsoft Store-app (MSIX).
Gebruikt enkel de standaardbibliotheek van Python.
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
from tkinter import filedialog, messagebox, simpledialog, ttk

APP_NAME = "VR-viewer starter"
APP_VERSION = "2.0.0"

# Alles wat de app bewaart, staat in de gebruikersmap (AppData\Local).
# Een Store-app (MSIX) mag niet in zijn eigen installatiemap schrijven.
DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "VRViewerStarter")
SETTINGS_FILE = os.path.join(DATA_DIR, "instellingen.json")
NGROK_CONFIG = os.path.join(DATA_DIR, "ngrok.yml")

NGROK_ZIP_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
NGROK_DOWNLOAD_PAGE = "https://ngrok.com/download"
NGROK_TOKEN_PAGE = "https://dashboard.ngrok.com/get-started/your-authtoken"
NGROK_SIGNUP_PAGE = "https://dashboard.ngrok.com/signup"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW

HTML_EXT = (".html", ".htm")
MODEL_EXT = (".glb", ".gltf")
MAX_DEPTH = 3  # hoe diep de app in submappen zoekt

# kleuren
BG = "#eef0f3"
CARD = "#ffffff"
INK = "#1c2330"
MUTED = "#5b6475"
LINE = "#dde1e7"
YELLOW = "#f2b705"
YELLOW_SOFT = "#fff4cc"
GREEN = "#2f7d4f"
RED = "#b3261e"

LOGO_PNG = (
    "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"
)


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_dir():
    # PyInstaller zet meegeleverde bestanden (zoals 'voorbeeld') in _MEIPASS
    return getattr(sys, "_MEIPASS", app_dir())


def example_dir():
    for base in (resource_dir(), app_dir()):
        p = os.path.join(base, "voorbeeld")
        if os.path.isdir(p):
            return p
    return None


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


def scan_folder(folder):
    """Geeft (html-bestanden, 3D-modellen) terug als relatieve paden, ook uit submappen."""
    html, models = [], []
    folder = os.path.abspath(folder)
    base_depth = folder.rstrip(os.sep).count(os.sep)
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith((".", "_")) and d.lower() != "node_modules")
        if root.rstrip(os.sep).count(os.sep) - base_depth >= MAX_DEPTH:
            dirs[:] = []
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), folder).replace(os.sep, "/")
            low = f.lower()
            if low.endswith(HTML_EXT):
                html.append(rel)
            elif low.endswith(MODEL_EXT):
                models.append(rel)
    html.sort(key=lambda p: (p.count("/"), p.lower()))
    return html, models


def pretty(rel):
    return rel.replace("/", " › ")


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
        # altijd de nieuwste versie tonen (handig als je het bestand aanpast)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


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
        self.link_targets = []

        root.title(APP_NAME)
        root.configure(bg=BG)
        root.minsize(720, 820)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            self.logo = tk.PhotoImage(data=LOGO_PNG)
            root.iconphoto(True, self.logo)
        except Exception:
            self.logo = None

        self.build_styles()
        self.build_ui()

        folder = self.settings.get("map", "")
        if folder and os.path.isdir(folder):
            self.folder_var.set(folder)
        self.refresh_files()
        self.refresh_ngrok_status()
        self.set_pill("Gestopt", "#4a5468")

    # ---------- UI ----------
    def build_styles(self):
        st = ttk.Style()
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure(".", background=BG, foreground=INK, font=("Segoe UI", 10))
        st.configure("Card.TFrame", background=CARD)
        st.configure("Card.TLabel", background=CARD, foreground=INK)
        st.configure("Muted.TLabel", background=CARD, foreground=MUTED)
        st.configure("Foot.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        st.configure("H2.TLabel", background=CARD, foreground=INK, font=("Segoe UI Semibold", 12))
        st.configure("TButton", padding=(10, 5), background="#f4f5f7", bordercolor=LINE,
                     lightcolor="#f4f5f7", darkcolor="#f4f5f7", relief="flat")
        st.map("TButton", background=[("active", "#e6e9ee"), ("disabled", "#f4f5f7")])
        st.configure("Big.TButton", font=("Segoe UI Semibold", 13), padding=(22, 9),
                     background=YELLOW, bordercolor=YELLOW, lightcolor=YELLOW, darkcolor=YELLOW)
        st.map("Big.TButton", background=[("active", "#ffc933"), ("disabled", "#e3e5ea")])
        st.configure("TEntry", fieldbackground="#f7f8fa", bordercolor=LINE, lightcolor=LINE, darkcolor=LINE)

    def card(self, parent, title, step):
        outer = tk.Frame(parent, bg=CARD, highlightbackground=LINE, highlightthickness=1)
        outer.pack(fill="x", pady=(0, 10))
        inner = ttk.Frame(outer, style="Card.TFrame", padding=(14, 12))
        inner.pack(fill="both", expand=True)
        head = ttk.Frame(inner, style="Card.TFrame")
        head.pack(fill="x", pady=(0, 8))
        badge = tk.Label(head, text=str(step), bg=INK, fg=CARD, width=2,
                         font=("Segoe UI Semibold", 11))
        badge.pack(side="left", padx=(0, 10))
        badge.step = step
        ttk.Label(head, text=title, style="H2.TLabel").pack(side="left")
        body = ttk.Frame(inner, style="Card.TFrame")
        body.pack(fill="x")
        return body, badge

    def set_done(self, badge, done):
        if done:
            badge.configure(text="✓", bg=GREEN)
        else:
            badge.configure(text=str(badge.step), bg=INK)

    def build_ui(self):
        # donkere kopbalk
        header = tk.Frame(self.root, bg=INK)
        header.pack(fill="x")
        hin = tk.Frame(header, bg=INK)
        hin.pack(fill="x", padx=16, pady=12)
        if self.logo:
            tk.Label(hin, image=self.logo, bg=INK).pack(side="left", padx=(0, 12))
        titles = tk.Frame(hin, bg=INK)
        titles.pack(side="left")
        tk.Label(titles, text=APP_NAME, bg=INK, fg="#ffffff",
                 font=("Segoe UI Semibold", 16)).pack(anchor="w")
        tk.Label(titles, text="Je constructie in VR op de Meta Quest", bg=INK, fg="#b8c0cc",
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.pill = tk.Label(hin, text="", fg="#ffffff", font=("Segoe UI Semibold", 9), padx=10, pady=3)
        self.pill.pack(side="right")
        tk.Frame(self.root, bg=YELLOW, height=4).pack(fill="x")

        wrap = ttk.Frame(self.root, padding=16)
        wrap.pack(fill="both", expand=True)

        # Stap 1: map
        b1, self.badge1 = self.card(wrap, "Kies je map met VR-modellen", 1)
        row = ttk.Frame(b1, style="Card.TFrame")
        row.pack(fill="x")
        self.folder_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.folder_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Kies map…", command=self.choose_folder).pack(side="left", padx=(8, 0))
        if example_dir():
            ttk.Button(row, text="Voorbeeld proberen", command=self.use_example).pack(side="left", padx=(8, 0))
        self.files_label = ttk.Label(b1, text="", style="Muted.TLabel", wraplength=600, justify="left")
        self.files_label.pack(anchor="w", pady=(8, 0))

        # Stap 2: ngrok
        b2, self.badge2 = self.card(wrap, "ngrok (voor de beveiligde link)", 2)
        self.ngrok_label = ttk.Label(b2, text="", style="Card.TLabel", wraplength=600, justify="left")
        self.ngrok_label.pack(anchor="w")
        nrow = ttk.Frame(b2, style="Card.TFrame")
        nrow.pack(anchor="w", pady=(8, 0))
        self.dl_btn = ttk.Button(nrow, text="Download ngrok", command=self.download_ngrok)
        self.dl_btn.pack(side="left")
        ttk.Button(nrow, text="Kies ngrok.exe…", command=self.choose_ngrok).pack(side="left", padx=(8, 0))
        ttk.Button(nrow, text="Authtoken invullen…", command=self.ask_token).pack(side="left", padx=(8, 0))
        ttk.Button(nrow, text="Gratis account maken",
                   command=lambda: webbrowser.open(NGROK_SIGNUP_PAGE)).pack(side="left", padx=(8, 0))

        # Stap 3: start
        b3, self.badge3 = self.card(wrap, "Start en open op de Quest", 3)
        srow = ttk.Frame(b3, style="Card.TFrame")
        srow.pack(fill="x")
        self.start_btn = ttk.Button(srow, text="Start", style="Big.TButton", command=self.toggle)
        self.start_btn.pack(side="left")
        self.status_label = ttk.Label(srow, text="Nog niet gestart.", style="Muted.TLabel",
                                      wraplength=440, justify="left")
        self.status_label.pack(side="left", padx=(14, 0))

        ttk.Label(b3, text="Kies een model:", style="Card.TLabel").pack(anchor="w", pady=(12, 4))
        lb_frame = tk.Frame(b3, bg=LINE, padx=1, pady=1)
        lb_frame.pack(fill="both", expand=True)
        self.links = tk.Listbox(lb_frame, height=5, font=("Segoe UI", 10), activestyle="none",
                                bg="#f7f8fa", fg=INK, relief="flat", highlightthickness=0,
                                selectbackground=YELLOW, selectforeground=INK, borderwidth=6)
        self.links.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(lb_frame, orient="vertical", command=self.links.yview)
        sb.pack(side="left", fill="y")
        self.links.configure(yscrollcommand=sb.set)
        self.links.bind("<<ListboxSelect>>", lambda e: self.show_selected())

        box = tk.Frame(b3, bg=YELLOW_SOFT, highlightbackground=YELLOW, highlightthickness=2)
        box.pack(fill="x", pady=(10, 8))
        tk.Label(box, text="Typ dit in de browser van je Quest:", bg=YELLOW_SOFT, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(8, 0))
        self.big_link = tk.Label(box, text="—", bg=YELLOW_SOFT, fg=INK, font=("Consolas", 13, "bold"),
                                 wraplength=640, justify="left")
        self.big_link.pack(anchor="w", padx=12, pady=(2, 10))
        box.bind("<Configure>", lambda e: self.big_link.configure(wraplength=max(200, e.width - 30)))

        brow = ttk.Frame(b3, style="Card.TFrame")
        brow.pack(anchor="w")
        ttk.Button(brow, text="Kopieer link", command=self.copy_link).pack(side="left")
        ttk.Button(brow, text="Test op deze computer", command=self.open_local).pack(side="left", padx=(8, 0))

        tip = ("Tip: maak op de Quest een bladwijzer van de link. Klik op ‘Visit Site’ als ngrok dat vraagt "
               "en druk op ‘Start VR’. Laat dit venster open zolang je de Quest gebruikt.")
        ttk.Label(wrap, text=tip, style="Foot.TLabel", wraplength=620, justify="left").pack(anchor="w", pady=(2, 0))
        ttk.Label(wrap, text="Versie " + APP_VERSION, style="Foot.TLabel").pack(anchor="e", pady=(6, 0))

    def set_pill(self, text, color):
        self.pill.configure(text="● " + text, bg=color)

    # ---------- map ----------
    def choose_folder(self):
        start = self.folder_var.get() or os.path.expanduser("~")
        d = filedialog.askdirectory(initialdir=start, title="Kies je map met VR-modellen")
        if d:
            self.folder_var.set(os.path.normpath(d))
            self.settings["map"] = self.folder_var.get()
            save_settings(self.settings)
            if not self.running:
                self.stop_server()
            self.refresh_files()

    def use_example(self):
        if self.running:
            messagebox.showinfo(APP_NAME, "Klik eerst op Stop.")
            return
        # niet bewaren: na een update van de app verandert de installatiemap
        self.folder_var.set(example_dir())
        self.stop_server()
        self.refresh_files()

    def html_files(self):
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            return []
        return scan_folder(folder)[0]

    def refresh_files(self):
        folder = self.folder_var.get()
        ok = False
        if not folder:
            txt = "Nog geen map gekozen. Geen modellen bij de hand? Klik op ‘Voorbeeld proberen’."
        elif not os.path.isdir(folder):
            txt = "Deze map bestaat niet (meer). Kies een andere map."
        else:
            html, models = scan_folder(folder)
            if not html:
                txt = ("Geen VR-pagina’s (HTML) gevonden. Zet het bestand dat Claude voor je maakte "
                       "in deze map, eventueel in een eigen submap per model.")
            else:
                ok = True
                shown = [pretty(h) for h in html[:6]]
                txt = "{} VR-pagina{} gevonden: {}".format(len(html), "" if len(html) == 1 else "’s",
                                                             ", ".join(shown))
                if len(html) > 6:
                    txt += " …"
                if models:
                    txt += "   ·   {} 3D-model{}".format(len(models), "" if len(models) == 1 else "len")
        self.files_label.configure(text=txt)
        self.set_done(self.badge1, ok)

    # ---------- ngrok ----------
    def find_ngrok(self):
        candidates = [
            self.settings.get("ngrok_pad", ""),
            os.path.join(DATA_DIR, "ngrok.exe"),
            os.path.join(app_dir(), "ngrok.exe"),
        ]
        for c in candidates:
            if c and os.path.isfile(c):
                return c
        return shutil.which("ngrok")

    def ngrok_cmd(self, exe, *args):
        cmd = [exe] + list(args)
        # eigen config in de datamap; een eerder ingestelde (standaard) config blijft ook werken
        if os.path.isfile(NGROK_CONFIG):
            cmd += ["--config", NGROK_CONFIG]
        return cmd

    def refresh_ngrok_status(self):
        exe = self.find_ngrok()
        token = bool(self.settings.get("token_ingesteld"))
        if exe:
            txt = "✓ ngrok gevonden."
            txt += " Authtoken is ingesteld." if token else " Vul nu één keer je authtoken in (van je gratis ngrok-account)."
            self.dl_btn.state(["disabled"])
        else:
            txt = ("ngrok is een apart, gratis programma dat de beveiligde link maakt. "
                   "Klik op ‘Download ngrok’ (±10 MB), of download het zelf via ngrok.com en kies het met ‘Kies ngrok.exe…’.")
            self.dl_btn.state(["!disabled"])
        self.ngrok_label.configure(text=txt)
        self.set_done(self.badge2, bool(exe and token))

    def download_ngrok(self):
        if not messagebox.askyesno(APP_NAME,
                                   "De app downloadt nu ngrok.exe van de officiële website van ngrok "
                                   "en bewaart het in je gebruikersmap.\n\nDoorgaan?"):
            return
        self.dl_btn.state(["disabled"])
        self.ngrok_label.configure(text="ngrok wordt gedownload…")

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
                msg = ("Download mislukt: {}\n\nDownload ngrok zelf via ngrok.com en kies het bestand "
                       "met ‘Kies ngrok.exe…’.").format(e)
                self.root.after(0, lambda: (messagebox.showerror(APP_NAME, msg), self.refresh_ngrok_status()))

        threading.Thread(target=work, daemon=True).start()

    def choose_ngrok(self):
        if messagebox.askyesno(APP_NAME, "Heb je ngrok nog niet gedownload?\n\n"
                                         "Klik op Ja om de downloadpagina van ngrok te openen, "
                                         "of op Nee als je ngrok.exe al hebt."):
            webbrowser.open(NGROK_DOWNLOAD_PAGE)
            return
        p = filedialog.askopenfilename(title="Kies ngrok.exe",
                                       filetypes=[("ngrok", "ngrok.exe"), ("Programma's", "*.exe")])
        if p:
            self.settings["ngrok_pad"] = os.path.normpath(p)
            save_settings(self.settings)
            self.refresh_ngrok_status()

    def ask_token(self):
        exe = self.find_ngrok()
        if not exe:
            messagebox.showinfo(APP_NAME, "Download of kies eerst ngrok.")
            return
        if messagebox.askyesno(APP_NAME, "Je authtoken staat op je ngrok-dashboard.\n\n"
                                         "Wil je die pagina nu openen?"):
            webbrowser.open(NGROK_TOKEN_PAGE)
        token = simpledialog.askstring(APP_NAME, "Plak hier je ngrok-authtoken:", parent=self.root)
        if not token:
            return
        token = token.strip().split()[-1]  # werkt ook als je het hele commando plakt
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            r = subprocess.run([exe, "config", "add-authtoken", token, "--config", NGROK_CONFIG],
                               capture_output=True, text=True, creationflags=NO_WINDOW, timeout=30)
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

    def set_status(self, text, color=MUTED):
        self.status_label.configure(text=text, foreground=color)

    def start(self):
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning(APP_NAME, "Kies eerst een map (stap 1).")
            return
        exe = self.find_ngrok()
        if not exe:
            messagebox.showwarning(APP_NAME, "Download of kies eerst ngrok (stap 2).")
            return
        if folder != example_dir():
            self.settings["map"] = folder
            save_settings(self.settings)
        self.refresh_files()

        if self.server:  # draaide al voor 'Test op deze computer'
            self.stop_server()
        if not self.start_server(folder):
            return

        self.ngrok_output = []
        try:
            self.ngrok_proc = subprocess.Popen(
                self.ngrok_cmd(exe, "http", str(self.port), "--log", "stdout"),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
        except Exception as e:
            self.stop()
            messagebox.showerror(APP_NAME, "ngrok kon niet starten: {}".format(e))
            return
        threading.Thread(target=self.read_ngrok, daemon=True).start()

        self.running = True
        self.start_btn.configure(text="Stop")
        self.set_status("Bezig met opstarten…")
        self.set_pill("Opstarten", "#a77d00")
        threading.Thread(target=self.wait_for_url, daemon=True).start()

    def start_server(self, folder):
        # webserver: alleen op deze computer bereikbaar, ngrok maakt de rest
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
            return False
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return True

    def stop_server(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.server = None

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
        # ngrok schrijft zelf de link in zijn meldingen: ... msg="started tunnel" ... url=https://...
        for line in list(self.ngrok_output):
            if "started tunnel" in line and "url=https://" in line:
                return line.split("url=", 1)[1].split()[0].strip('"')
        return None

    def api_addr_from_log(self):
        # het adres van ngrok's eigen webpagina (4040, of 4041/4042 als 4040 bezet is)
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
        self.public_url = url.rstrip("/")
        self.set_status("✓ Actief. Kies een model en typ de link in je Quest.", GREEN)
        self.set_pill("Actief", GREEN)
        self.set_done(self.badge3, True)
        self.fill_links()

    def fill_links(self):
        self.links.delete(0, "end")
        self.link_targets = []
        files = self.html_files()
        if not files:
            self.links.insert("end", "  (hoofdmap)")
            self.link_targets.append(self.public_url + "/")
        for f in files:
            self.links.insert("end", "  " + pretty(f))
            self.link_targets.append("{}/{}".format(self.public_url, urllib.parse.quote(f)))
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
        elif "108" in out or "already" in out.lower():
            messagebox.showwarning(APP_NAME, "Er draait al een andere ngrok (bv. in een terminalvenster). "
                                             "Sluit die eerst en probeer opnieuw.")
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
        self.stop_server()
        self.public_url = None
        self.start_btn.configure(text="Start")
        self.set_status("Gestopt.")
        self.set_pill("Gestopt", "#4a5468")
        self.set_done(self.badge3, False)
        self.links.delete(0, "end")
        self.link_targets = []
        self.big_link.configure(text="—")

    # ---------- links ----------
    def selected_link(self):
        sel = self.links.curselection()
        if not sel or sel[0] >= len(self.link_targets):
            return None
        return self.link_targets[sel[0]]

    def show_selected(self):
        link = self.selected_link()
        # zonder https:// – dat hoef je op de Quest niet te typen
        self.big_link.configure(text=link.split("://", 1)[-1] if link else "—")

    def copy_link(self):
        link = self.selected_link()
        if not link:
            messagebox.showinfo(APP_NAME, "Start eerst en kies een model.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        self.set_status("Link gekopieerd.", GREEN)

    def open_local(self):
        # werkt ook zonder ngrok: dan start enkel de webserver op deze computer
        if not self.server:
            folder = self.folder_var.get()
            if not folder or not os.path.isdir(folder):
                messagebox.showinfo(APP_NAME, "Kies eerst een map (stap 1).")
                return
            if not self.start_server(folder):
                return
            self.set_status("Enkel op deze computer actief (zonder Quest-link).")
        link = self.selected_link() or ""
        path = link.split(self.public_url, 1)[-1] if (self.public_url and link) else ""
        if not path:
            html = self.html_files()
            path = "/" + urllib.parse.quote(html[0]) if html else "/"
        webbrowser.open("http://localhost:{}{}".format(self.port, path))

    def on_close(self):
        self.stop()
        self.root.destroy()


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # scherpe tekst op hoge-resolutieschermen
    except Exception:
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
