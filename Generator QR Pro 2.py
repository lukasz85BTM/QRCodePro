import sys
import subprocess
import importlib.util
import urllib.parse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import qrcode
from PIL import Image, ImageTk
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer, 
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer
)

def install_dependencies():
    required = {
        'qrcode': 'qrcode[pil]',
        'PIL': 'Pillow'
    }
    missing = []
    for package, install_name in required.items():
        if not importlib.util.find_spec(package):
            missing.append(install_name)
    
    if missing:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            messagebox.showinfo("Sukces", "Zależności zainstalowane!\nUruchom program ponownie.")
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd instalacji:\n{str(e)}\nZainstaluj ręcznie: pip install {' '.join(missing)}")
            sys.exit(1)

class QRGeneratorPro:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Professional")
        self.root.geometry("800x700")

        # Inicjalizacja stałych i zmiennych PRZED tworzeniem widgetów
        self.MAX_TEXT_CHARS = 500  # Dodane tutaj
        self.logo_path = None
        self.qr_image = None
        self.qr_data = None
        
        # Kolory dla motywu jasnego
        self.light_theme = {
            'bg': '#f0f4f8',
            'fg': '#333333',
            'accent': '#4a6fa5',
            'highlight': '#6a98d4',
            'button': 'deepskyblue',  # Zmieniono na deepskyblue
            'button_text': '#000000',  # Czarny tekst
            'entry_bg': '#ffffff',
            'tab_bg': '#e0e8f0',
            'tab_active': '#ffffff',
            'border': '#bccee4'
        }
        
        # Kolory dla motywu ciemnego
        self.dark_theme = {
            'bg': '#1e2430',
            'fg': '#e0e0e0',
            'accent': '#5b8ad4',
            'highlight': '#73a1e6',
            'button': 'deepskyblue',
            'button_text': '#000000',
            'entry_bg': '#2a3446',
            'tab_bg': '#2a3446',       # Ciemniejsze tło zakładek
            'tab_active': '#1e2430',   # Najciemniejsze tło dla aktywnej zakładki
            'border': '#4a5566'
        }
        
        # Inicjalizacja zmiennych kolorów
        self.primary_color = "#000000"
        self.bg_color = "#FFFFFF"
        
        self.module_drawers = {
            "Kwadraty": SquareModuleDrawer(),
            "Kwadraty z przerwami": GappedSquareModuleDrawer(),
            "Kropki": CircleModuleDrawer(),
            "Zaokrąglone": RoundedModuleDrawer(),
            "Pionowe paski": VerticalBarsDrawer(),
            "Poziome paski": HorizontalBarsDrawer()
        }
        
        self.current_theme = "light"
        self.theme_data = self.light_theme
        
        self.style = ttk.Style()
        self.setup_theme()
        
        self.create_widgets()
        self.setup_layout()
        
        self.logo_path = None
        self.qr_image = None
        self.qr_data = None
        self.MAX_TEXT_CHARS = 500

    def setup_theme(self):
        """Konfiguruje styl aplikacji na podstawie bieżącego motywu"""
        theme = self.theme_data
        
        # Konfiguracja podstawowego stylu
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('TButton', 
                            background=theme['button'],
                            foreground='#000000',  # Czarny tekst na przyciskach
                            padding=5, 
                            relief=tk.RAISED, 
                            borderwidth=1)
        
        # Konfiguracja notatnika i zakładek
        self.style.configure('TNotebook', 
                            background=theme['bg'], 
                            borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                            background=theme['tab_bg'],
                            foreground='#000000',  # WYMUSZONY CZARNY TEKST
                            padding=[15, 5], 
                            font=('Helvetica', 10))
        self.style.map('TNotebook.Tab',
                    background=[('selected', theme['tab_active'])],
                    foreground=[('selected', '#000000')])  # Czarne teksty nawet dla aktywnej zakładki
        
        # Reszta konfiguracji
        self.style.map('TButton',
                    foreground=[('active', '#000000'), ('pressed', '#000000')],
                    background=[('active', theme['highlight']), ('pressed', theme['highlight'])])
        
        self.style.configure('Action.TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'), padding=5)
        self.style.configure('TLabelframe', 
                            background=theme['bg'], 
                            foreground=theme['accent'],
                            borderwidth=2, 
                            relief=tk.GROOVE)
        self.style.configure('TLabelframe.Label', 
                            background=theme['bg'], 
                            foreground=theme['accent'],
                            font=('Helvetica', 11, 'bold'))
        self.style.configure('TEntry', 
                            padding=5, 
                            fieldbackground=theme['entry_bg'], 
                            foreground=theme['fg'])
        self.style.configure('TCombobox', 
                            padding=5, 
                            fieldbackground=theme['entry_bg'], 
                            foreground=theme['fg'])
        
        self.root.configure(background=theme['bg'])
        
        # Aktualizacja kolorów istniejących widgetów
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Text):
                widget.configure(
                    background=theme['entry_bg'],
                    foreground=theme['fg'],
                    insertbackground=theme['fg'],
                    selectbackground=theme['accent']
                )
            elif isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Text):
                        child.configure(
                            background=theme['entry_bg'],
                            foreground=theme['fg'],
                            insertbackground=theme['fg'],
                            selectbackground=theme['accent']
                        )

    def toggle_theme(self):
        """Przełącza między jasnym i ciemnym motywem"""
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.theme_data = self.dark_theme
            self.theme_button.config(text="☀️ Tryb jasny")
        else:
            self.current_theme = "light"
            self.theme_data = self.light_theme
            self.theme_button.config(text="🌙 Tryb ciemny")
            
        self.setup_theme()
        
        # Aktualizacja kolorów dla wszystkich widgetów tekstowych
        for tab in self.notebook.tabs():
            for widget in self.notebook.nametowidget(tab).winfo_children():
                if isinstance(widget, tk.Text):
                    widget.configure(background=self.theme_data['entry_bg'], foreground=self.theme_data['fg'],
                                  insertbackground=self.theme_data['fg'], selectbackground=self.theme_data['accent'])
        # Aktualizacja kolorów zakładek
        self.setup_theme()
        self.notebook.config(style='TNotebook')
        for tab in self.notebook.tabs():
            self.notebook.nametowidget(tab).config(style='TFrame')
            
    def create_widgets(self):
        # Tworzenie górnego menu
        self.create_top_menu()
        
        # Tworzenie głównego notatnika
        self.notebook = ttk.Notebook(self.root)
        
        # Tworzenie zakładek
        self.create_text_tab()
        self.create_url_tab()
        self.create_wifi_tab()
        self.create_email_tab()
        self.create_sms_tab()
        self.create_vcard_tab()
        
        # Tworzenie kontrolek i podglądu
        self.create_controls()
        self.create_preview_frame()

    def create_top_menu(self):
        """Tworzenie górnego menu aplikacji"""
        self.menu_frame = ttk.Frame(self.root)
        
        # Logo i nazwa aplikacji
        logo_label = ttk.Label(self.menu_frame, text="QR Code Pro", 
                              font=('Helvetica', 16, 'bold'), 
                              foreground=self.theme_data['accent'])
        logo_label.pack(side=tk.LEFT, padx=10)
        
        # Przycisk zmiany motywu
        self.theme_button = ttk.Button(self.menu_frame, text="🌙 Tryb ciemny" if self.current_theme == "light" else "☀️ Tryb jasny", 
                                     command=self.toggle_theme, style='Action.TButton')
        self.theme_button.pack(side=tk.RIGHT, padx=10)
        
        self.menu_frame.pack(fill=tk.X, padx=5, pady=5)

    def setup_layout(self):
        self.notebook.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        self.controls_frame.pack(padx=15, pady=5, fill=tk.X)
        self.preview_frame.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

    def create_text_tab(self):
        frame = ttk.Frame(self.notebook)
        ttk.Label(frame, text="Wprowadź tekst do zakodowania:", style='Header.TLabel').pack(pady=(10,5), anchor=tk.W)
        
        self.text_input = tk.Text(frame, height=8, wrap=tk.WORD, font=('Arial', 10),
                                background=self.theme_data['entry_bg'], foreground=self.theme_data['fg'],
                                insertbackground=self.theme_data['fg'], selectbackground=self.theme_data['accent'],
                                relief=tk.SUNKEN, borderwidth=1)
        self.text_input.bind("<KeyRelease>", self.update_char_counter)
        self.text_input.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.char_counter = ttk.Label(frame, text=f"Znaki: 0/{self.MAX_TEXT_CHARS}", style='Header.TLabel')
        self.char_counter.pack(padx=10, anchor=tk.E)
        
        self.notebook.add(frame, text="Tekst")

    def create_url_tab(self):
        frame = ttk.Frame(self.notebook)
        ttk.Label(frame, text="Wprowadź adres URL:", style='Header.TLabel').pack(pady=(10,5), anchor=tk.W)
        
        url_example = ttk.Label(frame, text="Przykład: https://example.com", foreground=self.theme_data['accent'])
        url_example.pack(anchor=tk.W, padx=10)
        
        self.url_entry = ttk.Entry(frame, width=40, font=('Arial', 10))
        self.url_entry.pack(padx=10, pady=10, fill=tk.X)
        
        self.notebook.add(frame, text="URL")

    def create_wifi_tab(self):
        frame = ttk.Frame(self.notebook)
        
        ttk.Label(frame, text="Konfiguracja sieci Wi-Fi:", style='Header.TLabel').pack(pady=(10,5), anchor=tk.W)
        
        form_frame = ttk.Frame(frame)
        
        ttk.Label(form_frame, text="SSID (nazwa sieci):", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.wifi_ssid = ttk.Entry(form_frame, font=('Arial', 10))
        self.wifi_ssid.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Hasło:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.wifi_pass = ttk.Entry(form_frame, show="*", font=('Arial', 10))
        self.wifi_pass.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Typ zabezpieczenia:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.wifi_type = ttk.Combobox(form_frame, values=["WEP", "WPA", "WPA2", "nopass"], state="readonly", font=('Arial', 10))
        self.wifi_type.current(2)
        self.wifi_type.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        self.wifi_hidden = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="Ukryta sieć", variable=self.wifi_hidden).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        form_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        
        self.notebook.add(frame, text="Wi-Fi")

    def create_email_tab(self):
        frame = ttk.Frame(self.notebook)
        ttk.Label(frame, text="Tworzenie wiadomości e-mail:", style='Header.TLabel').pack(pady=(10,5), anchor=tk.W)
        
        ttk.Label(frame, text="Adresat:").pack(anchor=tk.W, padx=10, pady=(10,2))
        self.email_to = ttk.Entry(frame, width=40, font=('Arial', 10))
        self.email_to.pack(padx=10, pady=2, fill=tk.X)
        
        ttk.Label(frame, text="Temat:").pack(anchor=tk.W, padx=10, pady=(10,2))
        self.email_subj = ttk.Entry(frame, font=('Arial', 10))
        self.email_subj.pack(padx=10, pady=2, fill=tk.X)
        
        ttk.Label(frame, text="Treść:").pack(anchor=tk.W, padx=10, pady=(10,2))
        self.email_body = tk.Text(frame, height=5, wrap=tk.WORD, font=('Arial', 10),
                                background=self.theme_data['entry_bg'], foreground=self.theme_data['fg'],
                                insertbackground=self.theme_data['fg'], selectbackground=self.theme_data['accent'],
                                relief=tk.SUNKEN, borderwidth=1)
        self.email_body.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.notebook.add(frame, text="Email")

    def create_sms_tab(self):
        frame = ttk.Frame(self.notebook)
        ttk.Label(frame, text="Tworzenie wiadomości SMS:", style='Header.TLabel').pack(pady=(10,5), anchor=tk.W)
        
        ttk.Label(frame, text="Numer telefonu:").pack(anchor=tk.W, padx=10, pady=(10,2))
        self.sms_number = ttk.Entry(frame, font=('Arial', 10))
        self.sms_number.pack(padx=10, pady=2, fill=tk.X)
        
        ttk.Label(frame, text="Wiadomość:").pack(anchor=tk.W, padx=10, pady=(10,2))
        self.sms_message = tk.Text(frame, height=5, wrap=tk.WORD, font=('Arial', 10),
                                 background=self.theme_data['entry_bg'], foreground=self.theme_data['fg'],
                                 insertbackground=self.theme_data['fg'], selectbackground=self.theme_data['accent'],
                                 relief=tk.SUNKEN, borderwidth=1)
        self.sms_message.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.notebook.add(frame, text="SMS")

    def create_vcard_tab(self):
        frame = ttk.Frame(self.notebook)
        ttk.Label(frame, text="Tworzenie wizytówki:", style='Header.TLabel').pack(pady=(10,5), anchor=tk.W)
        
        form_frame = ttk.Frame(frame)
        
        entries = [
            ("Imię:", "vcard_fname"), 
            ("Nazwisko:", "vcard_lname"),
            ("Firma:", "vcard_company"), 
            ("Telefon:", "vcard_phone"),
            ("Email:", "vcard_email"), 
            ("Strona www:", "vcard_url")
        ]
        
        for i, (label, var_name) in enumerate(entries):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=30, font=('Arial', 10))
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=5)
            setattr(self, var_name, entry)
            
        form_frame.columnconfigure(1, weight=1)
        form_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        
        self.notebook.add(frame, text="Wizytówka")

    def create_controls(self):
        self.controls_frame = ttk.Frame(self.root)
        
        # Ramka dla kolorów
        color_frame = ttk.LabelFrame(self.controls_frame, text="Kolory")
        
        # Przycisk i podgląd koloru głównego
        primary_frame = ttk.Frame(color_frame)
        ttk.Button(primary_frame, text="Kolor QR", command=lambda: self.set_color("primary")).pack(side=tk.LEFT, padx=5)
        self.primary_preview = tk.Canvas(primary_frame, width=30, height=30, bg=self.primary_color, relief=tk.SUNKEN, borderwidth=1)
        self.primary_preview.pack(side=tk.LEFT, padx=5)
        primary_frame.pack(pady=5)
        
        # Przycisk i podgląd koloru tła
        bg_frame = ttk.Frame(color_frame)
        ttk.Button(bg_frame, text="Kolor tła", command=lambda: self.set_color("bg")).pack(side=tk.LEFT, padx=5)
        self.bg_preview = tk.Canvas(bg_frame, width=30, height=30, bg=self.bg_color, relief=tk.SUNKEN, borderwidth=1)
        self.bg_preview.pack(side=tk.LEFT, padx=5)
        bg_frame.pack(pady=5)
        
        color_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Ramka dla stylu punktów
        style_frame = ttk.LabelFrame(self.controls_frame, text="Styl punktów")
        ttk.Label(style_frame, text="Wybierz styl:").pack(pady=(5,2))
        self.module_style = ttk.Combobox(style_frame, values=list(self.module_drawers.keys()), state="readonly", width=20)
        self.module_style.current(0)
        self.module_style.pack(pady=(2,5))
        style_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Ramka dla logo
        logo_frame = ttk.LabelFrame(self.controls_frame, text="Logo")
        ttk.Button(logo_frame, text="Dodaj Logo", command=self.add_logo).pack(pady=5)
        ttk.Button(logo_frame, text="Usuń Logo", command=lambda: setattr(self, 'logo_path', None)).pack(pady=5)
        logo_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Ramka dla ustawień
        settings_frame = ttk.LabelFrame(self.controls_frame, text="Ustawienia")
        ttk.Label(settings_frame, text="Rozmiar:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.box_size = tk.IntVar(value=10)
        ttk.Spinbox(settings_frame, from_=5, to=20, textvariable=self.box_size, width=4).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(settings_frame, text="Korekcja:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.error_correction = ttk.Combobox(settings_frame, values=["L", "M", "Q", "H"], width=4, state="readonly")
        self.error_correction.current(2)
        self.error_correction.grid(row=1, column=1, padx=5, pady=2)
        settings_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y)

    def create_preview_frame(self):
        self.preview_frame = ttk.LabelFrame(self.root, text="Podgląd")
        
        self.generate_btn = ttk.Button(self.preview_frame, text="📱 Generuj QR", 
                                     command=self.generate_qr, style='Action.TButton',
                                     padding=10)
        self.generate_btn.pack(pady=(10,5))
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(padx=10, pady=10)
        
        btn_frame = ttk.Frame(self.preview_frame)
        ttk.Button(btn_frame, text="💾 Zapisz PNG", command=lambda: self.save_qr("png")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Zapisz SVG", command=lambda: self.save_qr("svg")).pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=(5,10))

    def set_color(self, color_type):
        color = colorchooser.askcolor(title="Wybierz kolor")[1]
        if color:
            if color_type == "primary":
                self.primary_color = color
                self.primary_preview.config(bg=color)
            else:
                self.bg_color = color
                self.bg_preview.config(bg=color)
            # Regeneruj QR jeśli już istnieje
            if self.qr_image:
                self.generate_qr()

    def update_char_counter(self, event=None):
        count = len(self.text_input.get("1.0", tk.END)) - 1
        self.char_counter.config(text=f"Znaki: {min(count, self.MAX_TEXT_CHARS)}/{self.MAX_TEXT_CHARS}")

    def add_logo(self):
        self.logo_path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.png *.jpg *.jpeg")])
        if self.logo_path and self.qr_image:
            self.generate_qr()

    def generate_qr(self):
        data = self.get_current_data()
        if not data:
            messagebox.showerror("Błąd", "Brak danych wejściowych!")
            return
        
        try:
            qr = qrcode.QRCode(
                version=5,
                error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{self.error_correction.get()}"),
                box_size=self.box_size.get(),
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            selected_style = self.module_style.get()
            module_drawer = self.module_drawers[selected_style]
            
            img = qr.make_image(
                fill_color=self.primary_color,
                back_color=self.bg_color,
                image_factory=StyledPilImage,
                module_drawer=module_drawer
            )
            
            if self.logo_path:
                try:
                    logo = Image.open(self.logo_path).convert("RGBA")
                    logo_size = (img.size[0]//4, img.size[1]//4)
                    logo.thumbnail(logo_size)
                    pos = ((img.size[0]-logo.size[0])//2, (img.size[1]-logo.size[1])//2)
                    img.paste(logo, pos, logo)
                except Exception as e:
                    messagebox.showerror("Błąd logo", f"Nie można dodać logo:\n{str(e)}")
            
            self.show_preview(img)
            self.qr_image = img
            self.generate_svg(data)
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Generowanie nieudane:\n{str(e)}")

    def generate_svg(self, data):
        try:
            qr = qrcode.QRCode(
                version=5,
                error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{self.error_correction.get()}"),
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            size = qr.modules_count * 10
            svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" 
                             width="{size}" 
                             height="{size}" 
                             viewBox="0 0 {size} {size}">
                             <rect width="100%" height="100%" fill="{self.bg_color}"/>'''
            
            modules = qr.modules
            box_size = 10
            
            for y in range(len(modules)):
                for x in range(len(modules)):
                    if modules[y][x]:
                        if self.module_style.get() == "Kropki":
                            svg_content += f'<circle cx="{(x + 0.5) * box_size}" cy="{(y + 0.5) * box_size}" r="{box_size / 2}" fill="{self.primary_color}"/>'
                        elif self.module_style.get() == "Zaokrąglone":
                            svg_content += f'<rect x="{x * box_size}" y="{y * box_size}" width="{box_size}" height="{box_size}" rx="{box_size / 4}" ry="{box_size / 4}" fill="{self.primary_color}"/>'
                        else:
                            svg_content += f'<rect x="{x * box_size}" y="{y * box_size}" width="{box_size}" height="{box_size}" fill="{self.primary_color}"/>'
            
            svg_content += '</svg>'
            self.qr_svg_content = svg_content
            
        except Exception as e:
            messagebox.showerror("Błąd SVG", f"Generowanie SVG nieudane:\n{str(e)}")

    def show_preview(self, img):
        img.thumbnail((300, 300))
        self.preview_image = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_image)

    def save_qr(self, file_type):
        if not self.qr_image:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wygeneruj kod QR!")
            return
        
        if file_type == "png":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Wszystkie pliki", "*.*")]
            )
            if file_path:
                try:
                    # Konwertujemy na RGB jeśli jest w trybie RGBA (z przezroczystością)
                    if self.qr_image.mode == 'RGBA':
                        self.qr_image.convert('RGB').save(file_path)
                    else:
                        self.qr_image.save(file_path)
                    messagebox.showinfo("Sukces", f"Zapisano PNG w:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Błąd zapisu", f"Nie można zapisać pliku:\n{str(e)}")
        
        elif file_type == "svg":
            if not hasattr(self, 'qr_svg_content'):
                messagebox.showerror("Błąd", "Nie wygenerowano obrazu SVG!")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG", "*.svg"), ("Wszystkie pliki", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(self.qr_svg_content)
                    messagebox.showinfo("Sukces", f"Zapisano SVG w:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Błąd zapisu", f"Nie można zapisać pliku:\n{str(e)}")

    def get_current_data(self):
        tab = self.notebook.tab(self.notebook.select(), "text")
        
        if tab == "Tekst":
            text = self.text_input.get("1.0", tk.END).strip()
            return text[:self.MAX_TEXT_CHARS]
            
        elif tab == "URL":
            url = self.url_entry.get().strip()
            if not url:
                return ""
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            return url
            
        elif tab == "Wi-Fi":
            ssid = self.wifi_ssid.get().strip()
            password = self.wifi_pass.get().strip()
            security = self.wifi_type.get()
            hidden = self.wifi_hidden.get()
            
            if not ssid:
                return ""
            
            # Poprawne kodowanie specjalnych znaków
            ssid_encoded = urllib.parse.quote(ssid)
            password_encoded = urllib.parse.quote(password)
            
            # Poprawne wartości dla typu szyfrowania
            security_map = {
                "WPA": "WPA",
                "WPA2": "WPA",
                "WEP": "WEP",
                "nopass": "nopass"
            }
            security = security_map.get(security, "WPA")
            
            parts = []
            parts.append(f"WIFI:T:{security};")
            parts.append(f"S:{ssid_encoded};")
            if security != "nopass":
                parts.append(f"P:{password_encoded};")
            if hidden:
                parts.append("H:true;")
            
            return ''.join(parts) + ';'  # Kończymy dodatkowym średnikiem
            
        elif tab == "Email":
            to_email = self.email_to.get().strip()
            subject = self.email_subj.get().strip()
            body = self.email_body.get("1.0", tk.END).strip()
            
            if not to_email:
                return ""
                
            params = []
            if subject:
                params.append(f"subject={urllib.parse.quote(subject)}")
            if body:
                params.append(f"body={urllib.parse.quote(body)}")
                
            return f"mailto:{to_email}?{'&'.join(params)}" if params else f"mailto:{to_email}"
            
        elif tab == "SMS":
            number = self.sms_number.get().strip()
            message = self.sms_message.get("1.0", tk.END).strip()
            
            if not number:
                return ""
                
            return f"smsto:{number}:{urllib.parse.quote(message)}" if message else f"smsto:{number}"
            
        elif tab == "Wizytówka":
            vcard = [
                "BEGIN:VCARD",
                "VERSION:3.0",
                f"FN:{self.vcard_fname.get().strip()} {self.vcard_lname.get().strip()}",
                f"ORG:{self.vcard_company.get().strip()}",
                f"TEL:{self.vcard_phone.get().strip()}",
                f"EMAIL:{self.vcard_email.get().strip()}",
                f"URL:{self.vcard_url.get().strip()}",
                "END:VCARD"
            ]
            return '\n'.join([line for line in vcard if not line.endswith(':')])
            
        return ""
    
if __name__ == "__main__":
    install_dependencies()  # Sprawdź zależności przed uruchomieniem
    root = tk.Tk()
    app = QRGeneratorPro(root)
    root.mainloop()
