import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from modules.widgets import CustomWidgets, TableWidget

class EmisorGUI:
    def __init__(self, parent):
        self.parent = parent
        self.emisor_actual = None
        self.notebook = None
        
        # Colores del tema
        self.bg_color = "#f8f9fa"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.accent_color = "#e74c3c"
        self.success_color = "#27ae60"
        self.warning_color = "#f39c12"
        self.text_color = "#2c3e50"
        self.light_gray = "#ecf0f1"
        self.card_bg = "white"
        
        self.setup_styles()
        self.create_widgets()
        self.load_emisores()
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Custom.TFrame", background=self.bg_color)
        style.configure("Custom.TLabel", background=self.bg_color, foreground=self.text_color)
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        tab_registrar = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(tab_registrar, text="Registrar Emisor")
        self.create_registro_tab(tab_registrar)
        
        tab_lista = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(tab_lista, text="Emisores Registrados")
        self.create_lista_tab(tab_lista)
    
    def create_registro_tab(self, parent):
        main_frame = tk.Frame(parent, bg=self.bg_color, padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)
        
        # Título principal
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill="x", pady=(0, 30))
        
        tk.Label(title_frame, 
                text="GESTIÓN DE EMISOR",
                font=("Arial", 20, "bold"),
                bg=self.bg_color,
                fg=self.primary_color).pack(anchor="w")
        
        # Frame principal con grid
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True)
        
        # Información Básica
        basic_frame = tk.LabelFrame(content_frame, 
                                   text="  Información Básica  ",
                                   font=("Arial", 12, "bold"),
                                   bg=self.card_bg,
                                   fg=self.primary_color,
                                   padx=20,
                                   pady=20,
                                   relief="flat",
                                   borderwidth=1,
                                   highlightbackground=self.light_gray,
                                   highlightthickness=1)
        basic_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(0, 15), pady=(0, 20))
        
        self.entry_ruc = self.create_modern_entry(basic_frame, "RUC Empresa (11 dígitos):", 0, 0)
        self.entry_razon_social = self.create_modern_entry(basic_frame, "Razón Social:", 1, 0)
        self.entry_nombre_comercial = self.create_modern_entry(basic_frame, "Nombre Comercial:", 2, 0)
        
        # Dirección
        address_frame = tk.LabelFrame(content_frame,
                                     text="  Dirección Principal  ",
                                     font=("Arial", 12, "bold"),
                                     bg=self.card_bg,
                                     fg=self.primary_color,
                                     padx=20,
                                     pady=20,
                                     relief="flat",
                                     borderwidth=1,
                                     highlightbackground=self.light_gray,
                                     highlightthickness=1)
        address_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 15), pady=(0, 20))
        
        self.entry_calle = self.create_modern_entry(address_frame, "Calle:", 0, 0)
        self.entry_numero = self.create_modern_entry(address_frame, "Número:", 1, 0)
        self.entry_distrito = self.create_modern_entry(address_frame, "Distrito:", 2, 0)
        self.entry_provincia = self.create_modern_entry(address_frame, "Provincia:", 3, 0)
        self.entry_departamento = self.create_modern_entry(address_frame, "Departamento:", 4, 0)
        
        # Contacto
        contact_frame = tk.LabelFrame(content_frame,
                                     text="  Contacto  ",
                                     font=("Arial", 12, "bold"),
                                     bg=self.card_bg,
                                     fg=self.primary_color,
                                     padx=20,
                                     pady=20,
                                     relief="flat",
                                     borderwidth=1,
                                     highlightbackground=self.light_gray,
                                     highlightthickness=1)
        contact_frame.grid(row=1, column=1, sticky="nsew", pady=(0, 20))
        
        self.entry_telefono = self.create_modern_entry(contact_frame, "Teléfono (9 dígitos):", 0, 0)
        self.entry_correo = self.create_modern_entry(contact_frame, "Correo Electrónico:", 1, 0)
        
        # Configurar grid weights
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Botones
        button_frame = tk.Frame(content_frame, bg=self.bg_color)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        self.btn_guardar = tk.Button(button_frame, 
                                   text="GUARDAR EMISOR", 
                                   command=self.guardar_emisor,
                                   bg=self.success_color,
                                   fg="white",
                                   font=("Arial", 12, "bold"),
                                   relief="flat",
                                   padx=30,
                                   pady=12,
                                   cursor="hand2")
        self.btn_guardar.pack(side="left", padx=(0, 10))
        
        self.btn_cancelar = tk.Button(button_frame, 
                                     text="CANCELAR EDICIÓN", 
                                     command=self.cancelar_edicion,
                                     bg="#95a5a6",
                                     fg="white",
                                     font=("Arial", 10),
                                     relief="flat",
                                     padx=20,
                                     pady=10,
                                     state="disabled",
                                     cursor="hand2")
        self.btn_cancelar.pack(side="left")
    
    def create_modern_entry(self, parent, label_text, row, column):
        # Frame para grupo label + entry
        frame = tk.Frame(parent, bg=self.card_bg)
        frame.grid(row=row, column=column, sticky="ew", pady=8)
        frame.grid_columnconfigure(1, weight=1)
        
        # Label
        label = tk.Label(frame, 
                        text=label_text,
                        font=("Arial", 10, "bold"),
                        bg=self.card_bg,
                        fg=self.text_color,
                        anchor="w")
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Entry
        entry = tk.Entry(frame,
                        font=("Arial", 10),
                        relief="flat",
                        bg="white",
                        highlightbackground=self.light_gray,
                        highlightcolor=self.secondary_color,
                        highlightthickness=1,
                        bd=0)
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        return entry

    def create_lista_tab(self, parent):
        main_frame = tk.Frame(parent, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Barra de botones
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        buttons = [
            ("Actualizar Lista", self.load_emisores, self.secondary_color),
            ("Editar Emisor", self.editar_emisor, self.warning_color),
            ("Ver Detalles", self.ver_detalles_emisor, "#2E86AB"),
            ("Eliminar Emisor", self.eliminar_emisor, self.accent_color)
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(button_frame, 
                          text=text, 
                          command=command,
                          bg=color,
                          fg="white",
                          font=("Arial", 10, "bold"),
                          relief="flat",
                          padx=20,
                          pady=8,
                          cursor="hand2")
            btn.grid(row=0, column=i, padx=5)
        
        # Tabla de emisores
        columns = ["RUC", "Razón Social", "Nombre Comercial"]
        self.table_emisores = TableWidget(main_frame, columns,
                                         grid_options={
                                             'row': 1,
                                             'column': 0,
                                             'sticky': 'nsew',
                                             'padx': 0,
                                             'pady': 0
                                         })
        
        # Configurar estilo de la tabla
        style = ttk.Style()
        style.configure("Treeview", 
                       background="white",
                       foreground=self.text_color,
                       rowheight=25,
                       fieldbackground="white")
        style.configure("Treeview.Heading",
                       background=self.primary_color,
                       foreground="white",
                       font=('Arial', 10, 'bold'))
        style.map("Treeview", background=[('selected', self.secondary_color)])

    # ========== MÉTODOS FUNCIONALES ==========

    def guardar_emisor(self):
        try:
            ruc = self.entry_ruc.get().strip()
            razon_social = self.entry_razon_social.get().strip()
            nombre_comercial = self.entry_nombre_comercial.get().strip()
            calle = self.entry_calle.get().strip()
            numero = self.entry_numero.get().strip()
            distrito = self.entry_distrito.get().strip()
            provincia = self.entry_provincia.get().strip()
            departamento = self.entry_departamento.get().strip()
            telefono = self.entry_telefono.get().strip()
            correo = self.entry_correo.get().strip()
            
            if not ruc:
                messagebox.showerror("Error", "El RUC es obligatorio")
                return
            
            if len(ruc) != 11 or not ruc.isdigit():
                messagebox.showerror("Error", "RUC debe tener 11 dígitos numéricos")
                return
            
            if not razon_social:
                messagebox.showerror("Error", "La Razón Social es obligatoria")
                return
            
            if self.emisor_actual:
                self.actualizar_emisor(ruc, razon_social, nombre_comercial, calle, numero, 
                                      distrito, provincia, departamento, telefono, correo)
            else:
                self.insertar_nuevo_emisor(ruc, razon_social, nombre_comercial, calle, numero, 
                                          distrito, provincia, departamento, telefono, correo)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar emisor: {str(e)}")
    
    def insertar_nuevo_emisor(self, ruc, razon_social, nombre_comercial, calle, numero, 
                             distrito, provincia, departamento, telefono, correo):
        try:
            # Asegurar que el RUC sea tratado como string
            ruc_str = str(ruc)
            
            # Verificar si ya existe
            existe = db.fetch_one("SELECT ruc_empresa FROM emisor WHERE ruc_empresa = %s", [ruc_str])
            if existe:
                messagebox.showerror("Error", f"El RUC {ruc} ya está registrado")
                return
            
            # Insertar emisor
            query_emisor = "INSERT INTO emisor (ruc_empresa, razon_social, nombre_empresa) VALUES (%s, %s, %s)"
            resultado = db.execute_query(query_emisor, [ruc_str, razon_social, nombre_comercial])
            
            if not resultado:
                messagebox.showerror("Error", "No se pudo insertar el emisor")
                return
            
            # Insertar dirección (siempre insertar, incluso si está vacío)
            query_direccion = """
            INSERT INTO direccion_e (ruc_empresa, calle, numero, provincia, departamento, distrito)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query_direccion, [
                ruc_str, 
                calle if calle else "", 
                numero if numero else "",
                provincia if provincia else "",
                departamento if departamento else "", 
                distrito if distrito else ""
            ])
            
            # Insertar teléfono (siempre insertar, incluso si está vacío)
            if telefono:
                if len(telefono) != 9 or not telefono.isdigit():
                    messagebox.showwarning("Advertencia", "El teléfono debe tener 9 dígitos numéricos. Se guardará sin teléfono.")
                    telefono = ""
            
            query_telefono = "INSERT INTO telefonos_e (ruc_empresa, telefono) VALUES (%s, %s)"
            db.execute_query(query_telefono, [ruc_str, telefono if telefono else ""])
            
            # Insertar correo (siempre insertar, incluso si está vacío)
            if correo and '@' not in correo:
                messagebox.showwarning("Advertencia", "El correo electrónico no es válido. Se guardará sin correo.")
                correo = ""
            
            query_correo = "INSERT INTO correos_e (ruc_empresa, correo) VALUES (%s, %s)"
            db.execute_query(query_correo, [ruc_str, correo if correo else ""])
            
            messagebox.showinfo("Éxito", "Emisor registrado correctamente")
            self.limpiar_campos()
            self.load_emisores()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al insertar emisor: {str(e)}")
    
    def actualizar_emisor(self, ruc, razon_social, nombre_comercial, calle, numero, 
                         distrito, provincia, departamento, telefono, correo):
        try:
            # Asegurar que el RUC sea tratado como string
            ruc_str = str(ruc)
            
            query_emisor = """
            UPDATE emisor SET razon_social = %s, nombre_empresa = %s 
            WHERE ruc_empresa = %s
            """
            resultado = db.execute_query(query_emisor, [razon_social, nombre_comercial, ruc_str])
            
            if not resultado:
                messagebox.showerror("Error", "No se pudo actualizar el emisor")
                return
            
            # Actualizar dirección
            db.execute_query("DELETE FROM direccion_e WHERE ruc_empresa = %s", [ruc_str])
            query_direccion = """
            INSERT INTO direccion_e (ruc_empresa, calle, numero, provincia, departamento, distrito)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query_direccion, [
                ruc_str, 
                calle if calle else "", 
                numero if numero else "",
                provincia if provincia else "",
                departamento if departamento else "", 
                distrito if distrito else ""
            ])
            
            # Actualizar teléfono
            db.execute_query("DELETE FROM telefonos_e WHERE ruc_empresa = %s", [ruc_str])
            if telefono:
                if len(telefono) != 9 or not telefono.isdigit():
                    messagebox.showwarning("Advertencia", "El teléfono debe tener 9 dígitos numéricos. Se guardará sin teléfono.")
                    telefono = ""
            
            query_telefono = "INSERT INTO telefonos_e (ruc_empresa, telefono) VALUES (%s, %s)"
            db.execute_query(query_telefono, [ruc_str, telefono if telefono else ""])
            
            # Actualizar correo
            db.execute_query("DELETE FROM correos_e WHERE ruc_empresa = %s", [ruc_str])
            if correo and '@' not in correo:
                messagebox.showwarning("Advertencia", "El correo electrónico no es válido. Se guardará sin correo.")
                correo = ""
            
            query_correo = "INSERT INTO correos_e (ruc_empresa, correo) VALUES (%s, %s)"
            db.execute_query(query_correo, [ruc_str, correo if correo else ""])
            
            messagebox.showinfo("Éxito", "Emisor actualizado correctamente")
            self.cancelar_edicion()
            self.load_emisores()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar emisor: {str(e)}")
    
    def editar_emisor(self):
        selection = self.table_emisores.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un emisor de la lista")
            return
        
        try:
            item = self.table_emisores.tree.item(selection[0])
            ruc = item['values'][0]
            
            # Asegurar que el RUC sea tratado como string
            ruc_str = str(ruc)
            
            # Cargar datos del emisor
            emisor = db.fetch_one("SELECT * FROM emisor WHERE ruc_empresa = %s", [ruc_str])
            if not emisor:
                messagebox.showerror("Error", "No se pudo cargar los datos del emisor")
                return
            
            # Cargar dirección
            direccion = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento 
                FROM direccion_e WHERE ruc_empresa = %s LIMIT 1
            """, [ruc_str])
            
            # Cargar teléfono
            telefono_data = db.fetch_one("SELECT telefono FROM telefonos_e WHERE ruc_empresa = %s LIMIT 1", [ruc_str])
            
            # Cargar correo
            correo_data = db.fetch_one("SELECT correo FROM correos_e WHERE ruc_empresa = %s LIMIT 1", [ruc_str])
            
            # Configurar modo edición
            self.emisor_actual = ruc_str
            self.entry_ruc.delete(0, tk.END)
            self.entry_ruc.insert(0, emisor[0])
            self.entry_ruc.config(state="disabled")
            
            self.entry_razon_social.delete(0, tk.END)
            self.entry_razon_social.insert(0, emisor[1] if emisor[1] else "")
            
            self.entry_nombre_comercial.delete(0, tk.END)
            self.entry_nombre_comercial.insert(0, emisor[2] if emisor[2] else "")
            
            # Cargar dirección
            if direccion:
                self.entry_calle.delete(0, tk.END)
                self.entry_calle.insert(0, direccion[0] if direccion[0] else "")
                
                self.entry_numero.delete(0, tk.END)
                self.entry_numero.insert(0, direccion[1] if direccion[1] else "")
                
                self.entry_distrito.delete(0, tk.END)
                self.entry_distrito.insert(0, direccion[2] if direccion[2] else "")
                
                self.entry_provincia.delete(0, tk.END)
                self.entry_provincia.insert(0, direccion[3] if direccion[3] else "")
                
                self.entry_departamento.delete(0, tk.END)
                self.entry_departamento.insert(0, direccion[4] if direccion[4] else "")
            
            # Cargar teléfono
            if telefono_data:
                self.entry_telefono.delete(0, tk.END)
                self.entry_telefono.insert(0, telefono_data[0] if telefono_data[0] else "")
            else:
                self.entry_telefono.delete(0, tk.END)
            
            # Cargar correo
            if correo_data:
                self.entry_correo.delete(0, tk.END)
                self.entry_correo.insert(0, correo_data[0] if correo_data[0] else "")
            else:
                self.entry_correo.delete(0, tk.END)
            
            self.btn_guardar.config(text="Actualizar Emisor", bg=self.warning_color)
            self.btn_cancelar.config(state="normal")
            
            # Cambiar a la pestaña de registro
            self.notebook.select(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos para edición: {str(e)}")
    
    def ver_detalles_emisor(self):
        selection = self.table_emisores.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un emisor de la lista")
            return
        
        try:
            item = self.table_emisores.tree.item(selection[0])
            ruc = item['values'][0]
            
            # Asegurar que el RUC sea tratado como string
            ruc_str = str(ruc)
            
            # Cargar datos del emisor
            emisor = db.fetch_one("SELECT * FROM emisor WHERE ruc_empresa = %s", [ruc_str])
            if not emisor:
                messagebox.showerror("Error", "No se pudo cargar los datos del emisor")
                return
            
            # Cargar dirección
            direccion = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento 
                FROM direccion_e WHERE ruc_empresa = %s LIMIT 1
            """, [ruc_str])
            
            # Cargar teléfonos
            telefonos = db.fetch_all("SELECT telefono FROM telefonos_e WHERE ruc_empresa = %s", [ruc_str])
            
            # Cargar correos
            correos = db.fetch_all("SELECT correo FROM correos_e WHERE ruc_empresa = %s", [ruc_str])
            
            self.mostrar_detalles_emisor(emisor, direccion, telefonos, correos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
    
    def mostrar_detalles_emisor(self, emisor, direccion, telefonos, correos):
        ventana_detalles = tk.Toplevel(self.parent)
        ventana_detalles.title(f"Detalles de Emisor - {emisor[0]}")
        ventana_detalles.geometry("500x400")
        ventana_detalles.transient(self.parent)
        ventana_detalles.grab_set()
        ventana_detalles.configure(bg=self.bg_color)
        
        main_frame = tk.Frame(ventana_detalles, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"EMISOR: {emisor[1]}", 
                font=("Arial", 16, "bold"),
                bg=self.bg_color,
                fg=self.primary_color).pack(pady=10)
        
        # Información General
        frame_info = tk.LabelFrame(main_frame, 
                                  text="  Información General  ",
                                  font=("Arial", 12, "bold"),
                                  bg=self.card_bg,
                                  fg=self.primary_color,
                                  padx=15,
                                  pady=15,
                                  relief="flat",
                                  borderwidth=1,
                                  highlightbackground=self.light_gray,
                                  highlightthickness=1)
        frame_info.pack(fill="x", pady=10)
        
        tk.Label(frame_info, text=f"RUC: {emisor[0]}", 
                anchor="w", 
                font=("Arial", 10),
                bg=self.card_bg,
                fg=self.text_color).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(frame_info, text=f"Razón Social: {emisor[1]}", 
                anchor="w", 
                font=("Arial", 10),
                bg=self.card_bg,
                fg=self.text_color).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Label(frame_info, text=f"Nombre Comercial: {emisor[2]}", 
                anchor="w", 
                font=("Arial", 10),
                bg=self.card_bg,
                fg=self.text_color).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        # Dirección
        frame_direccion = tk.LabelFrame(main_frame, 
                                       text="  Dirección  ",
                                       font=("Arial", 12, "bold"),
                                       bg=self.card_bg,
                                       fg=self.primary_color,
                                       padx=15,
                                       pady=15,
                                       relief="flat",
                                       borderwidth=1,
                                       highlightbackground=self.light_gray,
                                       highlightthickness=1)
        frame_direccion.pack(fill="x", pady=10)
        
        if direccion and any(direccion):
            direccion_parts = []
            if direccion[0]: direccion_parts.append(direccion[0])
            if direccion[1]: direccion_parts.append(direccion[1])
            if direccion[2]: direccion_parts.append(direccion[2])
            if direccion[3]: direccion_parts.append(direccion[3])
            if direccion[4]: direccion_parts.append(direccion[4])
            
            if direccion_parts:
                direccion_text = ", ".join(direccion_parts)
                tk.Label(frame_direccion, 
                        text=direccion_text, 
                        anchor="w", 
                        font=("Arial", 10),
                        bg=self.card_bg,
                        fg=self.text_color).pack(fill="x", padx=5, pady=2)
            else:
                tk.Label(frame_direccion, 
                        text="No especificada", 
                        anchor="w", 
                        font=("Arial", 10), 
                        fg="gray",
                        bg=self.card_bg).pack(fill="x", padx=5, pady=2)
        else:
            tk.Label(frame_direccion, 
                    text="No especificada", 
                    anchor="w", 
                    font=("Arial", 10), 
                    fg="gray",
                    bg=self.card_bg).pack(fill="x", padx=5, pady=2)
        
        # Teléfonos
        frame_telefonos = tk.LabelFrame(main_frame, 
                                       text="  Teléfonos  ",
                                       font=("Arial", 12, "bold"),
                                       bg=self.card_bg,
                                       fg=self.primary_color,
                                       padx=15,
                                       pady=15,
                                       relief="flat",
                                       borderwidth=1,
                                       highlightbackground=self.light_gray,
                                       highlightthickness=1)
        frame_telefonos.pack(fill="x", pady=10)
        
        if telefonos and any(telefonos):
            telefonos_validos = [t[0] for t in telefonos if t[0] and t[0].strip()]
            if telefonos_validos:
                for i, telefono in enumerate(telefonos_validos):
                    tk.Label(frame_telefonos, 
                            text=telefono, 
                            anchor="w", 
                            font=("Arial", 10),
                            bg=self.card_bg,
                            fg=self.text_color).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            else:
                tk.Label(frame_telefonos, 
                        text="No disponible", 
                        anchor="w", 
                        font=("Arial", 10), 
                        fg="gray",
                        bg=self.card_bg).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        else:
            tk.Label(frame_telefonos, 
                    text="No disponible", 
                    anchor="w", 
                    font=("Arial", 10), 
                    fg="gray",
                    bg=self.card_bg).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        # Correos
        frame_correos = tk.LabelFrame(main_frame, 
                                     text="  Correos Electrónicos  ",
                                     font=("Arial", 12, "bold"),
                                     bg=self.card_bg,
                                     fg=self.primary_color,
                                     padx=15,
                                     pady=15,
                                     relief="flat",
                                     borderwidth=1,
                                     highlightbackground=self.light_gray,
                                     highlightthickness=1)
        frame_correos.pack(fill="x", pady=10)
        
        if correos and any(correos):
            correos_validos = [c[0] for c in correos if c[0] and c[0].strip()]
            if correos_validos:
                for i, correo in enumerate(correos_validos):
                    tk.Label(frame_correos, 
                            text=correo, 
                            anchor="w", 
                            font=("Arial", 10),
                            bg=self.card_bg,
                            fg=self.text_color).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            else:
                tk.Label(frame_correos, 
                        text="No disponible", 
                        anchor="w", 
                        font=("Arial", 10), 
                        fg="gray",
                        bg=self.card_bg).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        else:
            tk.Label(frame_correos, 
                    text="No disponible", 
                    anchor="w", 
                    font=("Arial", 10), 
                    fg="gray",
                    bg=self.card_bg).grid(row=0, column=0, sticky="w", padx=5, pady=2)
    
    def eliminar_emisor(self):
        selection = self.table_emisores.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un emisor de la lista")
            return
        
        try:
            item = self.table_emisores.tree.item(selection[0])
            ruc = item['values'][0]
            razon_social = item['values'][1]
            
            # Asegurar que el RUC sea tratado como string
            ruc_str = str(ruc)
            
            # Verificar si hay facturas asociadas
            facturas_asociadas = db.fetch_one(
                "SELECT COUNT(*) FROM factura WHERE ruc_empresa = %s", [ruc_str]
            )
            
            if facturas_asociadas and facturas_asociadas[0] > 0:
                messagebox.showerror(
                    "Error", 
                    f"No se puede eliminar el emisor {razon_social}\n\n"
                    f"Tiene {facturas_asociadas[0]} factura(s) asociada(s).\n"
                    f"Elimine primero las facturas relacionadas."
                )
                return
            
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación", 
                f"¿Está seguro de que desea eliminar el emisor?\n\n"
                f"RUC: {ruc}\n"
                f"Razón Social: {razon_social}\n\n"
                f"Esta acción no se puede deshacer."
            )
            
            if respuesta:
                # Eliminar en orden correcto (primero tablas relacionadas)
                db.execute_query("DELETE FROM correos_e WHERE ruc_empresa = %s", [ruc_str])
                db.execute_query("DELETE FROM telefonos_e WHERE ruc_empresa = %s", [ruc_str])
                db.execute_query("DELETE FROM direccion_e WHERE ruc_empresa = %s", [ruc_str])
                db.execute_query("DELETE FROM emisor WHERE ruc_empresa = %s", [ruc_str])
                
                messagebox.showinfo("Éxito", "Emisor eliminado correctamente")
                self.load_emisores()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar emisor: {str(e)}")
    
    def cancelar_edicion(self):
        self.emisor_actual = None
        self.limpiar_campos()
        self.entry_ruc.config(state="normal")
        self.btn_guardar.config(text="Guardar Emisor", bg=self.success_color)
        self.btn_cancelar.config(state="disabled")
    
    def load_emisores(self):
        try:
            query = "SELECT ruc_empresa, razon_social, nombre_empresa FROM emisor ORDER BY ruc_empresa"
            emisores = db.fetch_all(query)
            self.table_emisores.update_data(emisores)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar emisores: {str(e)}")
    
    def limpiar_campos(self):
        entries = [self.entry_ruc, self.entry_razon_social, self.entry_nombre_comercial,
                  self.entry_calle, self.entry_numero, self.entry_distrito,
                  self.entry_provincia, self.entry_departamento, self.entry_telefono,
                  self.entry_correo]
        
        for entry in entries:
            entry.delete(0, tk.END)