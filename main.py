import tkinter as tk
from tkinter import ttk, messagebox
from config import APP_CONFIG
from modules.emisor_gui import EmisorGUI
from modules.clientes_gui import ClientesGUI
from modules.facturacion_gui import FacturacionGUI
from modules.reportes_gui import ReportesGUI

class AlidaMetalApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_CONFIG['title'])
        self.root.geometry(APP_CONFIG['geometry'])
        
        # Configurar estilo moderno
        self.setup_styles()
        
        if not APP_CONFIG['resizable']:
            self.root.resizable(False, False)
        
        self.create_menu()
        self.create_main_frame()
        
        # Mostrar pantalla de inicio
        self.show_inicio()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        self.bg_color = "#f8f9fa"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.accent_color = "#e74c3c"
        self.text_color = "#2c3e50"
        self.light_gray = "#ecf0f1"
        
        # Configurar estilos de widgets
        style.configure("TNotebook", background=self.light_gray)
        style.configure("TNotebook.Tab", 
                       padding=[20, 8], 
                       background=self.light_gray,
                       foreground=self.text_color,
                       font=('Arial', 10, 'bold'))
        style.map("TNotebook.Tab", 
                 background=[("selected", self.primary_color)],
                 foreground=[("selected", 'white')])
        
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("TButton", 
                       padding=[15, 8], 
                       font=('Arial', 10),
                       background=self.secondary_color,
                       foreground='white')
        style.map("TButton", 
                 background=[('active', self.primary_color)])
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Sistema
        menu_sistema = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.text_color)
        menubar.add_cascade(label="Sistema", menu=menu_sistema)
        menu_sistema.add_command(label="Salir", command=self.root.quit)
    
    def create_main_frame(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Banner superior
        self.create_banner()
        
        # Notebook para módulos
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Pestaña de Inicio
        self.tab_inicio = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_inicio, text="Inicio")
        
        # Módulos
        self.tab_emisor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_emisor, text="Gestión de Emisor")
        
        self.tab_clientes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_clientes, text="Gestión de Clientes")
        
        self.tab_facturacion = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_facturacion, text="Facturación Electrónica")
        
        self.tab_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reportes, text="Reportes y Consultas")
        
        # Inicializar módulos
        self.emisor_gui = EmisorGUI(self.tab_emisor)
        self.clientes_gui = ClientesGUI(self.tab_clientes)
        self.facturacion_gui = FacturacionGUI(self.tab_facturacion)
        self.reportes_gui = ReportesGUI(self.tab_reportes)
    
    def create_banner(self):
        banner_frame = tk.Frame(self.main_frame, bg=self.primary_color, height=120)
        banner_frame.pack(fill="x", pady=(0, 20))
        banner_frame.pack_propagate(False)
        
        # Logo y título
        content_frame = tk.Frame(banner_frame, bg=self.primary_color)
        content_frame.pack(expand=True)
        
        title_label = tk.Label(content_frame, 
                              text="ALIDA METAL",
                              font=("Arial", 24, "bold"), 
                              bg=self.primary_color, 
                              fg="white")
        title_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(content_frame,
                                text="Sistema de Información Integral",
                                font=("Arial", 12),
                                bg=self.primary_color, 
                                fg="white")
        subtitle_label.pack(pady=(0, 10))
    
    def show_inicio(self):
        # Limpiar pestaña de inicio
        for widget in self.tab_inicio.winfo_children():
            widget.destroy()
        
        # Crear contenido de inicio
        frame_inicio = tk.Frame(self.tab_inicio, bg=self.bg_color)
        frame_inicio.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Título de bienvenida
        welcome_label = tk.Label(frame_inicio, 
                               text="Bienvenido al Sistema ALIDA METAL",
                               font=("Arial", 20, "bold"),
                               bg=self.bg_color,
                               fg=self.primary_color)
        welcome_label.pack(pady=(0, 30))
        
        # Descripción
        desc_label = tk.Label(frame_inicio,
                            text="Solución completa para la gestión de facturación y clientes",
                            font=("Arial", 12),
                            bg=self.bg_color,
                            fg=self.text_color)
        desc_label.pack(pady=(0, 40))
        
        # Frame para tarjetas de módulos
        cards_frame = tk.Frame(frame_inicio, bg=self.bg_color)
        cards_frame.pack(fill="both", expand=True)
        
        # Tarjetas de módulos
        modules = [
            ("Gestión de Emisor", "Configure los datos de su empresa", "#3498db", self.show_emisor),
            ("Gestión de Clientes", "Administre el registro de clientes", "#2ecc71", self.show_clientes),
            ("Facturación Electrónica", "Emisión de facturas y documentos", "#e74c3c", self.show_facturacion),
            ("Reportes y Consultas", "Genere reportes y consulte facturas", "#f39c12", self.show_reportes)
        ]
        
        for i, (title, description, color, command) in enumerate(modules):
            card = tk.Frame(cards_frame, 
                           bg='white', 
                           relief='flat', 
                           borderwidth=1,
                           highlightbackground=self.light_gray,
                           highlightthickness=1)
            card.grid(row=i//2, column=i%2, padx=15, pady=15, sticky="nsew")
            card.grid_propagate(False)
            card.config(width=300, height=180)
            
            # Color accent
            color_bar = tk.Frame(card, bg=color, height=5)
            color_bar.pack(fill="x")
            
            # Contenido de la tarjeta
            content_frame = tk.Frame(card, bg='white', padx=20, pady=20)
            content_frame.pack(fill="both", expand=True)
            
            tk.Label(content_frame, text=title, 
                    font=("Arial", 14, "bold"), 
                    bg='white',
                    fg=self.primary_color).pack(anchor="w", pady=(0, 10))
            
            tk.Label(content_frame, text=description, 
                    wraplength=250,
                    justify="left",
                    bg='white',
                    fg=self.text_color,
                    font=("Arial", 10)).pack(anchor="w", pady=(0, 20))
            
            # Botón de acceso
            btn = tk.Button(content_frame, 
                          text="Acceder →", 
                          command=command,
                          bg=color,
                          fg="white",
                          font=("Arial", 10, "bold"),
                          relief="flat",
                          padx=20,
                          pady=8)
            btn.pack(anchor="w")
        
        # Configurar grid
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        
        # Footer con características
        features_frame = tk.Frame(frame_inicio, bg=self.light_gray, padx=30, pady=20)
        features_frame.pack(fill="x", pady=(40, 0))
        
        features = [
            "✓ Rápido y Eficiente",
            "✓ Seguro y Confiable", 
            "✓ Base de Datos Local",
            "✓ Interfaz Responsiva"
        ]
        
        for feature in features:
            tk.Label(features_frame, 
                    text=feature, 
                    font=("Arial", 10),
                    bg=self.light_gray,
                    fg=self.text_color).pack(side="left", padx=20)
    
    def show_emisor(self):
        self.notebook.select(self.tab_emisor)
    
    def show_clientes(self):
        self.notebook.select(self.tab_clientes)
    
    def show_facturacion(self):
        self.notebook.select(self.tab_facturacion)
    
    def show_reportes(self):
        self.notebook.select(self.tab_reportes)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlidaMetalApp(root)
    root.mainloop()