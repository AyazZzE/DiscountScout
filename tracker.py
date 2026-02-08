import os, requests, json, threading, webbrowser, random, time, sys
import customtkinter as ctk
from PIL import Image
from io import BytesIO
from tkinter import Canvas

# --- EXE İÇİNDE DOSYA BULMA FONKSİYONU ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- APPDATA AYARI ---
def get_save_path():
    appdata = os.getenv('APPDATA')
    path = os.path.join(appdata, "DiscountScout") # Klasör adı temizlendi
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, "games.json")

GAMES_FILE = get_save_path()
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# --- DİL SÖZLÜĞÜ ---
LANGS = {
    "TR": {
        "title": "Takip Listesi", "stats": "Trend & Analiz", "news": "Haberler",
        "search": "Oyun Ara...", "calc": "HESAPLA", "rate": "Kur", "total_val": "Listenin Toplam Değeri",
        "total_save": "Şu Anki Total Tasarruf", "news_title": "CANLI OYUN HABERLERİ",
        "best_deal": "GÜNÜN FIRSATI", "read": "OKU", "loading": "YÜKLENİYOR...", "eula_btn": "📜 Lisans (EULA)"
    },
    "EN": {
        "title": "Watchlist", "stats": "Trends & Analysis", "news": "News",
        "search": "Search Game...", "calc": "CALCULATE", "rate": "Rate", "total_val": "Total List Value",
        "total_save": "Current Total Savings", "news_title": "LIVE GAMING NEWS",
        "best_deal": "DEAL OF THE DAY", "read": "READ", "loading": "LOADING...", "eula_btn": "📜 License (EULA)"
    }
}

def get_data():
    if not os.path.exists(GAMES_FILE): return []
    try:
        with open(GAMES_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def save_data(data_list):
    with open(GAMES_FILE, "w", encoding="utf-8") as f: json.dump(data_list, f, indent=4, ensure_ascii=False)

# --- TETRIS ---
class Tetris(Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=100, height=150, bg="#020202", highlightthickness=1, highlightbackground="#1A1D26", **kwargs)
        self.columns, self.rows = 10, 15
        self.shapes = [[[1,1,1,1]], [[1,1],[1,1]], [[0,1,0],[1,1,1]], [[1,1,0],[0,1,1]], [[0,1,1],[1,1,0]], [[1,0,0],[1,1,1]], [[0,0,1],[1,1,1]]]
        self.master.winfo_toplevel().bind("<Left>", lambda e: self.move(-1))
        self.master.winfo_toplevel().bind("<Right>", lambda e: self.move(1))
        self.master.winfo_toplevel().bind("<Down>", lambda e: self.drop())
        self.master.winfo_toplevel().bind("<Up>", lambda e: self.rotate())
        self.reset_game()

    def reset_game(self):
        self.board = [[0]*self.columns for _ in range(self.rows)]
        self.game_over, self.paused = False, False
        self.new_p(); self.run()

    def toggle_pause(self):
        self.paused = not self.paused
        if not self.paused: self.run()

    def new_p(self):
        self.cp = random.choice(self.shapes); self.pp = [0, 3]
        if self.coll(self.cp, self.pp): self.game_over = True

    def coll(self, p, pos):
        for r, row in enumerate(p):
            for c, v in enumerate(row):
                if v:
                    if (pos[0]+r>=self.rows or pos[1]+c<0 or pos[1]+c>=self.columns or self.board[pos[0]+r][pos[1]+c]): return True
        return False

    def move(self, dx):
        if not self.paused and not self.game_over:
            np = [self.pp[0], self.pp[1] + dx]
            if not self.coll(self.cp, np): self.pp = np; self.draw()

    def drop(self):
        if not self.paused and not self.game_over:
            np = [self.pp[0] + 1, self.pp[1]]
            if not self.coll(self.cp, np): self.pp = np; self.draw()

    def rotate(self):
        if not self.paused and not self.game_over:
            new_shape = list(zip(*self.cp[::-1]))
            if not self.coll(new_shape, self.pp): self.cp = new_shape; self.draw()

    def run(self):
        if not self.game_over and not self.paused:
            np = [self.pp[0]+1, self.pp[1]]
            if not self.coll(self.cp, np):
                for r, row in enumerate(self.cp):
                    for c, v in enumerate(row):
                        if v: 
                            if self.pp[0]+r < self.rows and self.pp[1]+c < self.columns:
                                self.board[self.pp[0]+r][self.pp[1]+c] = 1
                self.clear(); self.new_p()
            else: self.pp = np
            self.draw(); self.after(500, self.run)

    def clear(self):
        nb = [r for r in self.board if not all(r)]
        while len(nb) < self.rows: nb.insert(0, [0]*self.columns)
        self.board = nb

    def draw(self):
        self.delete("all")
        if self.game_over: self.create_text(50, 75, text="GAME OVER", fill="#FF4D4D", font=("Segoe UI Bold", 10)); return
        for r, row in enumerate(self.board):
            for c, v in enumerate(row):
                if v: self.create_rectangle(c*10, r*10, c*10+10, r*10+10, fill="#0077B6", outline="#90E0EF")
        for r, row in enumerate(self.cp):
            for c, v in enumerate(row):
                if v: self.create_rectangle((self.pp[1]+c)*10, (self.pp[0]+r)*10, (self.pp[1]+c)*10+10, (self.pp[0]+r)*10+10, fill="#00B140", outline="#B5FFD9")

# --- UI RENKLERİ ---
DARK_BG, SIDEBAR_BG, CARD_BG = "#0B0E14", "#080A0F", "#151921"
ACCENT_BLUE, TEXT_WHITE, TEXT_GRAY = "#00B4D8", "#F0F2F5", "#9BA1A6"
DANGER_RED, DISCOUNT_GREEN, GOLD = "#FF4D4D", "#2ECC71", "#FFD700"

class GameCard(ctk.CTkFrame):
    def __init__(self, master, game_data, delete_callback, **kwargs):
        is_sale = game_data.get('on_sale', False)
        is_mega = game_data.get('raw_perc', 0) >= 70
        super().__init__(master, fg_color=CARD_BG, corner_radius=10, border_width=1 if is_mega else 0, border_color=GOLD, height=85, **kwargs)
        self.link = f"https://store.steampowered.com/app/{game_data.get('app_id')}"
        self.pack_propagate(False)
        img_lbl = ctk.CTkLabel(self, text="", width=110, height=55, fg_color="#000", corner_radius=5)
        img_lbl.pack(side="left", padx=10)
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(info, text=game_data['name'], font=("Segoe UI Semibold", 13), text_color=GOLD if is_mega else TEXT_WHITE, anchor="w").pack(fill="x", pady=(10, 0))
        price_f = ctk.CTkFrame(info, fg_color="transparent")
        price_f.pack(fill="x")
        ctk.CTkLabel(price_f, text=game_data['new'], font=("Segoe UI Bold", 14), text_color=DISCOUNT_GREEN if is_sale else TEXT_WHITE).pack(side="left")
        if is_sale:
            ctk.CTkLabel(price_f, text=game_data['old'], font=("Segoe UI", 10, "overstrike"), text_color=TEXT_GRAY).pack(side="left", padx=5)
            ctk.CTkLabel(self, text=game_data['perc'], font=("Segoe UI Bold", 9), fg_color=GOLD if is_mega else DISCOUNT_GREEN, text_color="#000", corner_radius=4, width=32).place(relx=0.98, rely=0.15, anchor="ne")
        ctk.CTkButton(self, text="×", width=15, height=15, fg_color="transparent", hover_color=DANGER_RED, text_color=TEXT_GRAY, command=delete_callback).place(relx=0.98, rely=0.88, anchor="se")
        self.bind("<Button-1>", lambda e: webbrowser.open(self.link))
        img_lbl.bind("<Button-1>", lambda e: webbrowser.open(self.link))
        def load_img():
            try:
                r = requests.get(game_data['img_url'], timeout=5)
                i = Image.open(BytesIO(r.content)).resize((110, 55))
                img = ctk.CTkImage(i, size=(110, 55))
                img_lbl.configure(image=img)
            except: pass
        threading.Thread(target=load_img, daemon=True).start()

class ScoutPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cur_lang = "TR"
        self.title("Discount Scout")
        self.geometry("1350x950")
        self.configure(fg_color=DARK_BG)
        
        # İKON AYARI
        try: 
            icon_p = resource_path("logos.ico")
            self.iconbitmap(icon_p)
        except: pass 
            
        self.game_cache, self.usd_rate, self.found_games = [], 34.50, {}
        
        # GENİŞLİK 320px
        self.grid_columnconfigure(0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_pages()
        self._switch_page("dash")
        self._sync()

    def _create_sidebar(self):
        side = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, corner_radius=0); side.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(side, text="DISCOUNT SCOUT", font=("Impact", 30), text_color=ACCENT_BLUE).pack(pady=(20, 5))
        
        self.lang_btn = ctk.CTkButton(side, text="🌐 EN / TR", width=80, height=20, font=("Segoe UI", 10), fg_color="#1A1D26", command=self._toggle_lang)
        self.lang_btn.pack(pady=(0, 15))

        self.b1 = ctk.CTkButton(side, text="🎮 Takip Listesi", anchor="w", command=lambda: self._switch_page("dash"))
        self.b1.pack(fill="x", padx=20, pady=5)
        self.b2 = ctk.CTkButton(side, text="📊 Trend & Analiz", anchor="w", fg_color="transparent", command=lambda: self._switch_page("stats"))
        self.b2.pack(fill="x", padx=20, pady=5)
        self.b3 = ctk.CTkButton(side, text="🔥 Haberler", anchor="w", fg_color="transparent", command=lambda: self._switch_page("news"))
        self.b3.pack(fill="x", padx=20, pady=5)
        
        self.search = ctk.CTkComboBox(side, values=[], command=self._on_sel, height=35)
        self.search.pack(fill="x", padx=20, pady=20); self.search.set("Oyun Ara..."); self.search._entry.bind("<KeyRelease>", self._on_srch)
        
        self.tetris = Tetris(side); self.tetris.pack(pady=5)
        t_ctrl = ctk.CTkFrame(side, fg_color="transparent"); t_ctrl.pack(pady=5)
        ctk.CTkButton(t_ctrl, text="⏸", width=35, height=25, command=self.tetris.toggle_pause).pack(side="left", padx=2)
        ctk.CTkButton(t_ctrl, text="🔄", width=35, height=25, command=self.tetris.reset_game).pack(side="left", padx=2)
        
        calc = ctk.CTkFrame(side, fg_color=CARD_BG, corner_radius=15); calc.pack(fill="x", padx=20, pady=10)
        self.rate_lbl = ctk.CTkLabel(calc, text="Kur: 1$ = ...₺", font=("Segoe UI", 11)); self.rate_lbl.pack(pady=5)
        self.usd_in = ctk.CTkEntry(calc, placeholder_text="USD", height=30, justify="center"); self.usd_in.pack(padx=15, pady=5, fill="x")
        self.calc_lbl = ctk.CTkLabel(calc, text="0.00 ₺", font=("Segoe UI Bold", 16), text_color=DISCOUNT_GREEN); self.calc_lbl.pack()
        self.calc_btn = ctk.CTkButton(calc, text="HESAPLA", command=self._calc, height=25); self.calc_btn.pack(pady=10)

        self.eula_btn = ctk.CTkButton(side, text="📜 Lisans (EULA)", fg_color="transparent", text_color=TEXT_GRAY, font=("Segoe UI", 10), command=self._show_eula)
        self.eula_btn.pack(side="bottom", pady=15)

    def _create_pages(self):
        self.p_dash = ctk.CTkFrame(self, fg_color="transparent")
        self.high = ctk.CTkFrame(self.p_dash, fg_color="#1A1D26", height=80, corner_radius=15); self.high.pack(fill="x", padx=30, pady=20)
        self.high_lbl = ctk.CTkLabel(self.high, text="YÜKLENİYOR...", font=("Segoe UI Bold", 16), text_color=GOLD); self.high_lbl.place(relx=0.5, rely=0.5, anchor="center")
        self.scroll = ctk.CTkScrollableFrame(self.p_dash, fg_color="transparent"); self.scroll.pack(fill="both", expand=True, padx=20); self.scroll.grid_columnconfigure((0,1), weight=1)
        
        self.p_stats = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_title = ctk.CTkLabel(self.p_stats, text="LİSTE ANALİZİ", font=("Segoe UI Bold", 24), text_color=ACCENT_BLUE)
        self.stats_title.pack(pady=20, padx=30, anchor="w")
        stats_box = ctk.CTkFrame(self.p_stats, fg_color=CARD_BG, height=140); stats_box.pack(fill="x", padx=30, pady=10)
        self.total_val_lbl = ctk.CTkLabel(stats_box, text="Toplam Değer: $0.00", font=("Segoe UI Semibold", 15), text_color=TEXT_WHITE); self.total_val_lbl.pack(pady=(15, 5))
        self.total_save = ctk.CTkLabel(stats_box, text="Toplam Tasarruf: $0.00", font=("Segoe UI Bold", 20), text_color=DISCOUNT_GREEN); self.total_save.pack(pady=5)
        self.trend_scroll = ctk.CTkScrollableFrame(self.p_stats, fg_color="transparent"); self.trend_scroll.pack(fill="both", expand=True, padx=20)
        
        self.p_news = ctk.CTkFrame(self, fg_color="transparent")
        self.news_title_lbl = ctk.CTkLabel(self.p_news, text="CANLI OYUN HABERLERİ", font=("Segoe UI Bold", 24), text_color=ACCENT_BLUE)
        self.news_title_lbl.pack(pady=20, padx=30, anchor="w")
        self.news_scroll = ctk.CTkScrollableFrame(self.p_news, fg_color="transparent"); self.news_scroll.pack(fill="both", expand=True, padx=20)

    def _show_eula(self):
        eula_window = ctk.CTkToplevel(self)
        eula_window.title("Lisans ve Geliştirici Bilgisi")
        eula_window.geometry("500x520")
        eula_window.attributes("-topmost", True)
        
        try:
            eula_window.after(200, lambda: eula_window.iconbitmap(resource_path("logos.ico")))
        except: pass
        
        text_area = ctk.CTkTextbox(eula_window, width=460, height=350, font=("Segoe UI", 12))
        text_area.pack(padx=20, pady=(20, 10))
        
        metin = "DISCOUNT SCOUT - SON KULLANICI LİSANS SÖZLEŞMESİ (EULA)\n\n" \
                "1. KULLANIM: Bu yazılım oyun fiyatlarını takip etmek amacıyla sunulmuştur.\n" \
                "2. SORUMLULUK: Veriler Steam API üzerinden çekilmektedir, olası hatalardan geliştirici sorumlu değildir.\n" \
                "3. TELİF: Yazılımın izinsiz kopyalanması ve ticari amaça dağıtılması yasaktır.\n\n" \
                "Bu uygulamayı kullanarak yukarıdaki şartları kabul etmiş sayılırsınız.\n" \
                "--------------------------------------------------\n" \
                "Geliştirici Notu:\n" \
                "Bu uygulama Ayaz Er tarafından geliştirilmiştir.\n" \
                "Tüm hakları saklıdır © 2026"
        
        text_area.insert("0.0", metin)
        text_area.configure(state="disabled")
        
        ctk.CTkLabel(eula_window, text="Ayaz Er Tarafından geliştirilmiştir", font=("Segoe UI Bold", 14), text_color=ACCENT_BLUE).pack(pady=5)
        ctk.CTkButton(eula_window, text="TAMAM", command=eula_window.destroy).pack(pady=10)

    def _toggle_lang(self):
        self.cur_lang = "EN" if self.cur_lang == "TR" else "TR"
        l = LANGS[self.cur_lang]
        self.b1.configure(text=f"🎮 {l['title']}")
        self.b2.configure(text=f"📊 {l['stats']}")
        self.b3.configure(text=f"🔥 {l['news']}")
        self.search.set(l['search'])
        self.calc_btn.configure(text=l['calc'])
        self.eula_btn.configure(text=l['eula_btn'])
        self.stats_title.configure(text=l['stats'].upper())
        self.news_title_lbl.configure(text=l['news_title'])
        self._fetch(); self._load_news()

    def _load_news(self):
        for w in self.news_scroll.winfo_children(): w.destroy()
        def fetch():
            sources = ["https://www.eurogamer.net/feed/news", "https://frpnet.net/feed"]
            all_n = []
            for s in sources:
                try:
                    r = requests.get(f"https://api.rss2json.com/v1/api.json?rss_url={s}", timeout=5).json()
                    if r.get('status') == 'ok': all_n.extend(r.get('items', []))
                except: continue
            all_n.sort(key=lambda x: x.get('pubDate', ''), reverse=True)
            for i in all_n[:15]:
                src = "FRPNET (TR)" if "frpnet" in i['link'] else "EUROGAMER"
                self.after(0, lambda x=i: self._create_news_card(x['title'], src, x['pubDate'].split(' ')[0], x['link']))
        threading.Thread(target=fetch, daemon=True).start()

    def _create_news_card(self, title, src, date, url):
        f = ctk.CTkFrame(self.news_scroll, fg_color=CARD_BG, corner_radius=12); f.pack(fill="x", pady=8, padx=10)
        ctk.CTkLabel(f, text=f"{src} | {date}", font=("Segoe UI", 10), text_color=ACCENT_BLUE).pack(anchor="w", padx=20, pady=(12, 0))
        ctk.CTkLabel(f, text=title, font=("Segoe UI Bold", 14), text_color=TEXT_WHITE, wraplength=600, justify="left").pack(anchor="w", padx=20, pady=(5, 10))
        ctk.CTkButton(f, text=LANGS[self.cur_lang]['read'], width=80, height=25, command=lambda: webbrowser.open(url)).pack(anchor="e", padx=20, pady=(0, 15))

    def _switch_page(self, page):
        for p in [self.p_dash, self.p_stats, self.p_news]: p.grid_forget()
        self.b1.configure(fg_color="#1D212F" if page=="dash" else "transparent")
        self.b2.configure(fg_color="#1D212F" if page=="stats" else "transparent")
        self.b3.configure(fg_color="#1D212F" if page=="news" else "transparent")
        if page=="dash": self.p_dash.grid(row=0, column=1, sticky="nsew")
        elif page=="stats": self.p_stats.grid(row=0, column=1, sticky="nsew"); self._load_trends()
        else: self.p_news.grid(row=0, column=1, sticky="nsew"); self._load_news()

    def _load_trends(self):
        for w in self.trend_scroll.winfo_children(): w.destroy()
        trends = [("GTA VI", "Rockstar Games", "2026"), ("Witcher 4", "CD Projekt Red", "UE5"), ("Hollow Knight: Silksong", "Team Cherry", "TBA")]
        for n, p, pr in trends:
            f = ctk.CTkFrame(self.trend_scroll, fg_color=CARD_BG, corner_radius=10); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=n, font=("Segoe UI Bold", 15)).pack(side="left", padx=20, pady=15)
            ctk.CTkLabel(f, text=p, text_color=TEXT_GRAY).pack(side="left", padx=30)
            ctk.CTkLabel(f, text=pr, font=("Segoe UI Bold", 13), text_color=DISCOUNT_GREEN).pack(side="right", padx=20)

    def _sync(self):
        threading.Thread(target=self._update_rate, daemon=True).start()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _update_rate(self):
        try:
            r = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
            self.usd_rate = r['rates']['TRY']
            self.after(0, lambda: self.rate_lbl.configure(text=f"{LANGS[self.cur_lang]['rate']}: 1$ = {self.usd_rate:.2f}₺"))
        except: pass

    def _on_srch(self, e):
        v = self.search.get()
        if len(v) >= 3: threading.Thread(target=self._suggest, args=(v,), daemon=True).start()

    def _suggest(self, v):
        try:
            r = requests.get(f"https://store.steampowered.com/api/storesearch/?term={v}&cc=tr").json()
            self.found_games = {i['name']: i['id'] for i in r.get('items', [])}
            self.after(0, lambda: self.search.configure(values=list(self.found_games.keys())))
        except: pass

    def _on_sel(self, c):
        gid = self.found_games.get(c)
        if gid:
            d = get_data()
            if not any(str(x['app_id']) == str(gid) for x in d):
                d.append({"app_id": str(gid), "name": c}); save_data(d); self._fetch()

    def _fetch(self):
        games, new_list = get_data(), []
        t_old, t_new = 0.0, 0.0
        for g in games:
            try:
                r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={g['app_id']}&cc=tr", headers=HEADERS).json()
                if not r or not r[str(g['app_id'])]['success']: continue
                dat = r[str(g['app_id'])]['data']; p = dat.get('price_overview', {})
                vo, vn = p.get('initial', 0)/100, p.get('final', 0)/100
                t_old += vo; t_new += vn
                new_list.append({"app_id": g['app_id'], "name": g['name'], "img_url": dat.get('header_image'), "old": f"${vo:.2f}" if vo > 0 else "N/A", "new": f"${vn:.2f}" if vn > 0 else "Free", "perc": f"-{p.get('discount_percent',0)}%", "on_sale": p.get('discount_percent',0) > 0, "raw_perc": p.get('discount_percent', 0)})
            except: continue
        self.game_cache = sorted(new_list, key=lambda x: x['on_sale'], reverse=True)
        self.after(0, lambda: self._update_ui(t_old, t_new))

    def _update_ui(self, t_old, t_new):
        for w in self.scroll.winfo_children(): w.destroy()
        l = LANGS[self.cur_lang]; max_d, best_g = -1, None
        for i, g in enumerate(self.game_cache):
            if g['on_sale'] and g['raw_perc'] > max_d: max_d = g['raw_perc']; best_g = g
            GameCard(self.scroll, g, lambda n=g['name']: self._del(n)).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
        self.total_val_lbl.configure(text=f"{l['total_val']}: ${t_old:.2f}")
        self.total_save.configure(text=f"{l['total_save']}: ${t_old - t_new:.2f}")
        if best_g: self.high_lbl.configure(text=f"🔥 {l['best_deal']}: {best_g['name']} (%{max_d}!)")

    def _del(self, n):
        save_data([g for g in get_data() if g['name'] != n]); self._fetch()

    def _calc(self):
        try: v = float(self.usd_in.get().replace(",", ".")); self.calc_lbl.configure(text=f"{v*self.usd_rate:,.2f} ₺")
        except: self.calc_lbl.configure(text="Hata!")

if __name__ == "__main__":
    app = ScoutPro(); app.mainloop()