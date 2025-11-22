import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from modules.widgets import CustomWidgets, TableWidget

class EmisorGUI:
    def __init__(self, parent):
        self.parent = parent
        self.emisor_actual = None
        self.notebook = None  # ✅ Guardar referencia al notebook
        self.create_widgets()
        self.load_emisores()
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.parent)  # ✅ Guardar en atributo
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_registrar = ttk.Frame(self.notebook)
        self.notebook.add(tab_registrar, text="Registrar Emisor")
        self.create_registro_tab(tab_registrar)
        
        tab_lista = ttk.Frame(self.notebook)
        self.notebook.add(tab_lista, text="Emisores Registrados")
        self.create_lista_tab(tab_lista)
    
    def create_registro_tab(self, parent):
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="REGISTRAR NUEVO EMISOR", 
                font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        self.entry_ruc = CustomWidgets.create_entry(main_frame, "RUC Empresa (11 dígitos):", 1, 0)
        self.entry_razon_social = CustomWidgets.create_entry(main_frame, "Razón Social:", 2, 0)
        self.entry_nombre_comercial = CustomWidgets.create_entry(main_frame, "Nombre Comercial:", 3, 0)
        
        tk.Label(main_frame, text="Dirección Principal", 
                font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=4, pady=10)
        
        self.entry_calle = CustomWidgets.create_entry(main_frame, "Calle:", 5, 0)
        self.entry_numero = CustomWidgets.create_entry(main_frame, "Número:", 6, 0)
        self.entry_distrito = CustomWidgets.create_entry(main_frame, "Distrito:", 7, 0)
        self.entry_provincia = CustomWidgets.create_entry(main_frame, "Provincia:", 8, 0)
        self.entry_departamento = CustomWidgets.create_entry(main_frame, "Departamento:", 9, 0)
        
        tk.Label(main_frame, text="Contacto", 
                font=("Arial", 12, "bold")).grid(row=10, column=0, columnspan=4, pady=10)
        
        self.entry_telefono = CustomWidgets.create_entry(main_frame, "Teléfono (9 dígitos):", 11, 0)
        self.entry_correo = CustomWidgets.create_entry(main_frame, "Correo Electrónico:", 12, 0)
        
        frame_botones = tk.Frame(main_frame)
        frame_botones.grid(row=13, column=0, columnspan=4, pady=20, sticky="ew")
        
        self.btn_guardar = tk.Button(frame_botones, text="Guardar Emisor", 
                                    command=self.guardar_emisor,
                                    bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                    width=15)
        self.btn_guardar.pack(side="left", padx=5)
        
        self.btn_cancelar = tk.Button(frame_botones, text="Cancelar Edición", 
                                     command=self.cancelar_edicion,
                                     bg="#e74c3c", fg="white", font=("Arial", 10),
                                     width=15, state="disabled")
        self.btn_cancelar.pack(side="left", padx=5)
    
    def create_lista_tab(self, parent):
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        frame_botones = tk.Frame(main_frame)
        frame_botones.grid(row=0, column=0, sticky="ew", pady=5)
        
        btn_actualizar = tk.Button(frame_botones, text="Actualizar Lista", 
                                  command=self.load_emisores,
                                  bg="#3498db", fg="white", width=15)
        btn_actualizar.grid(row=0, column=0, padx=5, pady=5)
        
        btn_editar = tk.Button(frame_botones, text="Editar Emisor", 
                              command=self.editar_emisor,
                              bg="#f39c12", fg="white", width=15)
        btn_editar.grid(row=0, column=1, padx=5, pady=5)
        
        btn_detalles = tk.Button(frame_botones, text="Ver Detalles", 
                                command=self.ver_detalles_emisor,
                                bg="#2E86AB", fg="white", width=15)
        btn_detalles.grid(row=0, column=2, padx=5, pady=5)
        
        btn_eliminar = tk.Button(frame_botones, text="Eliminar Emisor", 
                                command=self.eliminar_emisor,
                                bg="#e74c3c", fg="white", width=15)
        btn_eliminar.grid(row=0, column=3, padx=5, pady=5)
        
        columns = ["RUC", "Razón Social", "Nombre Comercial"]
        self.table_emisores = TableWidget(main_frame, columns,
                                         grid_options={
                                             'row': 1,
                                             'column': 0,
                                             'sticky': 'nsew',
                                             'padx': 10,
                                             'pady': 5
                                         })
    
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
            
            if len(ruc) != 11:
                messagebox.showerror("Error", "RUC debe tener 11 dígitos")
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
        # ✅ CORREGIDO: Asegurar que el RUC se pase como string
        existe = db.fetch_one("SELECT ruc_empresa FROM emisor WHERE ruc_empresa = %s", [str(ruc)])
        if existe:
            messagebox.showerror("Error", f"El RUC {ruc} ya está registrado")
            return
        
        query_emisor = "INSERT INTO emisor (ruc_empresa, razon_social, nombre_empresa) VALUES (%s, %s, %s)"
        # ✅ CORREGIDO: Pasar RUC como string
        resultado = db.execute_query(query_emisor, [str(ruc), razon_social, nombre_comercial])
        
        if not resultado:
            messagebox.showerror("Error", "No se pudo insertar el emisor")
            return
        
        if calle:
            query_direccion = """
            INSERT INTO direccion_e (ruc_empresa, calle, numero, provincia, departamento, distrito)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # ✅ CORREGIDO: Pasar RUC como string
            db.execute_query(query_direccion, [str(ruc), calle, numero, provincia, departamento, distrito])
        
        if telefono:
            if len(telefono) != 9 or not telefono.isdigit():
                messagebox.showerror("Error", "El teléfono debe tener 9 dígitos numéricos")
                return
            
            query_telefono = "INSERT INTO telefonos_e (ruc_empresa, telefono) VALUES (%s, %s)"
            # ✅ CORREGIDO: Pasar RUC como string
            db.execute_query(query_telefono, [str(ruc), telefono])
        
        if correo:
            if '@' not in correo:
                messagebox.showerror("Error", "El correo electrónico no es válido")
                return
            
            query_correo = "INSERT INTO correos_e (ruc_empresa, correo) VALUES (%s, %s)"
            # ✅ CORREGIDO: Pasar RUC como string
            db.execute_query(query_correo, [str(ruc), correo])
        
        messagebox.showinfo("Éxito", "Emisor registrado correctamente")
        self.limpiar_campos()
        self.load_emisores()
    
    def actualizar_emisor(self, ruc, razon_social, nombre_comercial, calle, numero, 
                         distrito, provincia, departamento, telefono, correo):
        query_emisor = """
        UPDATE emisor SET razon_social = %s, nombre_empresa = %s 
        WHERE ruc_empresa = %s
        """
        # ✅ CORREGIDO: Pasar RUC como string
        resultado = db.execute_query(query_emisor, [razon_social, nombre_comercial, str(ruc)])
        
        if not resultado:
            messagebox.showerror("Error", "No se pudo actualizar el emisor")
            return
        
        # ✅ CORREGIDO: Pasar RUC como string en todas las eliminaciones
        db.execute_query("DELETE FROM direccion_e WHERE ruc_empresa = %s", [str(ruc)])
        if calle:
            query_direccion = """
            INSERT INTO direccion_e (ruc_empresa, calle, numero, provincia, departamento, distrito)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query_direccion, [str(ruc), calle, numero, provincia, departamento, distrito])
        
        db.execute_query("DELETE FROM telefonos_e WHERE ruc_empresa = %s", [str(ruc)])
        if telefono:
            if len(telefono) != 9 or not telefono.isdigit():
                messagebox.showerror("Error", "El teléfono debe tener 9 dígitos numéricos")
                return
            
            query_telefono = "INSERT INTO telefonos_e (ruc_empresa, telefono) VALUES (%s, %s)"
            db.execute_query(query_telefono, [str(ruc), telefono])
        
        db.execute_query("DELETE FROM correos_e WHERE ruc_empresa = %s", [str(ruc)])
        if correo:
            if '@' not in correo:
                messagebox.showerror("Error", "El correo electrónico no es válido")
                return
            
            query_correo = "INSERT INTO correos_e (ruc_empresa, correo) VALUES (%s, %s)"
            db.execute_query(query_correo, [str(ruc), correo])
        
        messagebox.showinfo("Éxito", "Emisor actualizado correctamente")
        self.cancelar_edicion()
        self.load_emisores()
    
    def editar_emisor(self):
        selection = self.table_emisores.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un emisor de la lista")
            return
        
        try:
            item = self.table_emisores.tree.item(selection[0])
            ruc = item['values'][0]
            
            # ✅ CORREGIDO: Asegurar que el RUC se pase como string
            emisor = db.fetch_one("SELECT * FROM emisor WHERE ruc_empresa = %s", [str(ruc)])
            if not emisor:
                messagebox.showerror("Error", "No se pudo cargar los datos del emisor")
                return
            
            direccion = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento 
                FROM direccion_e WHERE ruc_empresa = %s LIMIT 1
            """, [str(ruc)])
            
            telefono_data = db.fetch_one("SELECT telefono FROM telefonos_e WHERE ruc_empresa = %s LIMIT 1", [str(ruc)])
            
            correo_data = db.fetch_one("SELECT correo FROM correos_e WHERE ruc_empresa = %s LIMIT 1", [str(ruc)])
            
            self.emisor_actual = ruc
            self.entry_ruc.delete(0, tk.END)
            self.entry_ruc.insert(0, emisor[0])
            self.entry_ruc.config(state="disabled")
            
            self.entry_razon_social.delete(0, tk.END)
            self.entry_razon_social.insert(0, emisor[1])
            
            self.entry_nombre_comercial.delete(0, tk.END)
            self.entry_nombre_comercial.insert(0, emisor[2])
            
            if direccion:
                self.entry_calle.delete(0, tk.END)
                self.entry_calle.insert(0, direccion[0] or "")
                
                self.entry_numero.delete(0, tk.END)
                self.entry_numero.insert(0, direccion[1] or "")
                
                self.entry_distrito.delete(0, tk.END)
                self.entry_distrito.insert(0, direccion[2] or "")
                
                self.entry_provincia.delete(0, tk.END)
                self.entry_provincia.insert(0, direccion[3] or "")
                
                self.entry_departamento.delete(0, tk.END)
                self.entry_departamento.insert(0, direccion[4] or "")
            
            if telefono_data:
                self.entry_telefono.delete(0, tk.END)
                self.entry_telefono.insert(0, telefono_data[0] or "")
            
            if correo_data:
                self.entry_correo.delete(0, tk.END)
                self.entry_correo.insert(0, correo_data[0] or "")
            
            self.btn_guardar.config(text="Actualizar Emisor", bg="#f39c12")
            self.btn_cancelar.config(state="normal")
            
            # ✅ CORREGIDO: Cambiar a la pestaña correcta (Registrar Emisor)
            self.notebook.select(0)  # Índice 0 = primera pestaña (Registrar Emisor)
            
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
            
            # ✅ CORREGIDO: Asegurar que el RUC se pase como string
            emisor = db.fetch_one("SELECT * FROM emisor WHERE ruc_empresa = %s", [str(ruc)])
            if not emisor:
                messagebox.showerror("Error", "No se pudo cargar los datos del emisor")
                return
            
            direccion = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento 
                FROM direccion_e WHERE ruc_empresa = %s LIMIT 1
            """, [str(ruc)])
            
            telefonos = db.fetch_all("SELECT telefono FROM telefonos_e WHERE ruc_empresa = %s", [str(ruc)])
            
            correos = db.fetch_all("SELECT correo FROM correos_e WHERE ruc_empresa = %s", [str(ruc)])
            
            self.mostrar_detalles_emisor(emisor, direccion, telefonos, correos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
    
    def mostrar_detalles_emisor(self, emisor, direccion, telefonos, correos):
        ventana_detalles = tk.Toplevel(self.parent)
        ventana_detalles.title(f"Detalles de Emisor - {emisor[0]}")
        ventana_detalles.geometry("500x400")
        ventana_detalles.transient(self.parent)
        ventana_detalles.grab_set()
        
        main_frame = tk.Frame(ventana_detalles)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"EMISOR: {emisor[1]}", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        frame_info = tk.LabelFrame(main_frame, text="Información General", padx=10, pady=10)
        frame_info.pack(fill="x", pady=10)
        
        tk.Label(frame_info, text=f"RUC: {emisor[0]}", anchor="w").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(frame_info, text=f"Razón Social: {emisor[1]}", anchor="w").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Label(frame_info, text=f"Nombre Comercial: {emisor[2]}", anchor="w").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        if direccion:
            frame_direccion = tk.LabelFrame(main_frame, text="Dirección", padx=10, pady=10)
            frame_direccion.pack(fill="x", pady=10)
            
            direccion_completa = f"{direccion[0]} {direccion[1]}, {direccion[2]}, {direccion[3]}, {direccion[4]}"
            tk.Label(frame_direccion, text=direccion_completa, anchor="w").pack(fill="x", padx=5, pady=2)
        
        if telefonos:
            frame_telefonos = tk.LabelFrame(main_frame, text="Teléfonos", padx=10, pady=10)
            frame_telefonos.pack(fill="x", pady=10)
            
            for i, telefono in enumerate(telefonos):
                tk.Label(frame_telefonos, text=telefono[0], anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=2)
        
        if correos:
            frame_correos = tk.LabelFrame(main_frame, text="Correos Electrónicos", padx=10, pady=10)
            frame_correos.pack(fill="x", pady=10)
            
            for i, correo in enumerate(correos):
                tk.Label(frame_correos, text=correo[0], anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=2)
    
    def eliminar_emisor(self):
        selection = self.table_emisores.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un emisor de la lista")
            return
        
        try:
            item = self.table_emisores.tree.item(selection[0])
            ruc = item['values'][0]
            razon_social = item['values'][1]
            
            # ✅ CORREGIDO: Conversión explícita a string
            ruc_str = str(ruc)
            
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación", 
                f"¿Está seguro de que desea eliminar el emisor?\n\n"
                f"RUC: {ruc}\n"
                f"Razón Social: {razon_social}\n\n"
                f"Esta acción no se puede deshacer."
            )
            
            if respuesta:
                # ✅ CORREGIDO: Pasar RUC como string en TODAS las consultas
                db.execute_query("DELETE FROM nota WHERE serie_numero IN (SELECT serie_numero FROM factura WHERE ruc_empresa = %s)", [ruc_str])
                db.execute_query("DELETE FROM detallefactura WHERE serie_numero IN (SELECT serie_numero FROM factura WHERE ruc_empresa = %s)", [ruc_str])
                db.execute_query("DELETE FROM calculosfactura WHERE serie_numero IN (SELECT serie_numero FROM factura WHERE ruc_empresa = %s)", [ruc_str])
                db.execute_query("DELETE FROM factura WHERE ruc_empresa = %s", [ruc_str])
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
        self.btn_guardar.config(text="Guardar Emisor", bg="#27ae60")
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
