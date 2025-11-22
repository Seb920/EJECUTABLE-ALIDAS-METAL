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
        
        if not APP_CONFIG['resizable']:
            self.root.resizable(False, False)
        
        self.create_menu()
        self.create_main_frame()
        
        # Mostrar pantalla de inicio
        self.show_inicio()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Sistema
        menu_sistema = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sistema", menu=menu_sistema)
        menu_sistema.add_command(label="Salir", command=self.root.quit)
    
    def create_main_frame(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Banner superior
        self.create_banner()
        
        # Notebook para módulos
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        banner_frame = tk.Frame(self.main_frame, bg="#2E86AB", height=100)
        banner_frame.pack(fill="x", pady=(0, 10))
        banner_frame.pack_propagate(False)
        
        title_label = tk.Label(banner_frame, 
                              text="ALIDA METAL - Sistema de Información Integral",
                              font=("Arial", 18, "bold"), 
                              bg="#2E86AB", fg="white")
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(banner_frame,
                                text="Solución completa para la gestión de facturación y clientes",
                                font=("Arial", 10),
                                bg="#2E86AB", fg="white")
        subtitle_label.pack(expand=True)
    
    def show_inicio(self):
        # Limpiar pestaña de inicio
        for widget in self.tab_inicio.winfo_children():
            widget.destroy()
        
        # Crear contenido de inicio
        frame_inicio = tk.Frame(self.tab_inicio)
        frame_inicio.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tarjetas de módulos
        modules = [
            ("Gestión de Emisor", "Configure los datos de su empresa", self.show_emisor),
            ("Gestión de Clientes", "Administre el registro de clientes", self.show_clientes),
            ("Facturación Electrónica", "Emisión de facturas y documentos", self.show_facturacion),
            ("Reportes y Consultas", "Genere reportes y consulte facturas", self.show_reportes)
        ]
        
        for i, (title, description, command) in enumerate(modules):
            card = tk.Frame(frame_inicio, relief="raised", borderwidth=1)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            tk.Label(card, text=title, font=("Arial", 12, "bold")).pack(pady=5)
            tk.Label(card, text=description, wraplength=200).pack(pady=5)
            tk.Button(card, text="Acceder", command=command, 
                     bg="#2E86AB", fg="white").pack(pady=5)
        
        # Configurar grid
        frame_inicio.grid_rowconfigure(0, weight=1)
        frame_inicio.grid_rowconfigure(1, weight=1)
        frame_inicio.grid_columnconfigure(0, weight=1)
        frame_inicio.grid_columnconfigure(1, weight=1)
        
        # Características
        features_frame = tk.LabelFrame(frame_inicio, text="Características del Sistema")
        features_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=20)
        
        features = [
            "✓ Rápido y Eficiente",
            "✓ Seguro y Confiable", 
            "✓ Base de Datos Local",
            "✓ Interfaz Responsiva"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature, font=("Arial", 10)).pack(side="left", padx=20)
    
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