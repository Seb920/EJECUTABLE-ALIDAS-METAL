import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from modules.widgets import CustomWidgets, TableWidget

class ClientesGUI:
    def __init__(self, parent):
        self.parent = parent
        self.cliente_actual = None
        self.notebook = None  # ✅ Guardar referencia al notebook
        self.create_widgets()
        self.load_clientes()
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.parent)  # ✅ Guardar en atributo
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_registrar = ttk.Frame(self.notebook)
        self.notebook.add(tab_registrar, text="Registrar Cliente")
        self.create_registro_tab(tab_registrar)
        
        tab_lista = ttk.Frame(self.notebook)
        self.notebook.add(tab_lista, text="Clientes Registrados")
        self.create_lista_tab(tab_lista)
    
    def create_registro_tab(self, parent):
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="REGISTRAR NUEVO CLIENTE", 
                font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        self.entry_ruc = CustomWidgets.create_entry(main_frame, "RUC (11 dígitos):", 1, 0)
        self.entry_razon_social = CustomWidgets.create_entry(main_frame, "Razón Social:", 2, 0)
        self.entry_nombres = CustomWidgets.create_entry(main_frame, "Nombres:", 3, 0)
        self.entry_apellidos = CustomWidgets.create_entry(main_frame, "Apellidos:", 4, 0)
        
        tk.Label(main_frame, text="Dirección", 
                font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=4, pady=10)
        
        self.entry_calle = CustomWidgets.create_entry(main_frame, "Calle:", 6, 0)
        self.entry_numero = CustomWidgets.create_entry(main_frame, "Número:", 7, 0)
        self.entry_distrito = CustomWidgets.create_entry(main_frame, "Distrito:", 8, 0)
        self.entry_provincia = CustomWidgets.create_entry(main_frame, "Provincia:", 9, 0)
        self.entry_departamento = CustomWidgets.create_entry(main_frame, "Departamento:", 10, 0)
        
        tk.Label(main_frame, text="Contacto", 
                font=("Arial", 12, "bold")).grid(row=11, column=0, columnspan=4, pady=10)
        
        self.entry_telefono = CustomWidgets.create_entry(main_frame, "Teléfono (9 dígitos):", 12, 0)
        self.entry_correo = CustomWidgets.create_entry(main_frame, "Correo Electrónico:", 13, 0)
        
        frame_botones = tk.Frame(main_frame)
        frame_botones.grid(row=14, column=0, columnspan=4, pady=20, sticky="ew")
        
        self.btn_guardar = tk.Button(frame_botones, text="Guardar Cliente", 
                                    command=self.guardar_cliente,
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
                                  command=self.load_clientes,
                                  bg="#3498db", fg="white", width=15)
        btn_actualizar.grid(row=0, column=0, padx=5, pady=5)
        
        btn_editar = tk.Button(frame_botones, text="Editar Cliente", 
                              command=self.editar_cliente,
                              bg="#f39c12", fg="white", width=15)
        btn_editar.grid(row=0, column=1, padx=5, pady=5)
        
        btn_detalles = tk.Button(frame_botones, text="Ver Detalles", 
                                command=self.ver_detalles_cliente,
                                bg="#2E86AB", fg="white", width=15)
        btn_detalles.grid(row=0, column=2, padx=5, pady=5)
        
        btn_eliminar = tk.Button(frame_botones, text="Eliminar Cliente", 
                                command=self.eliminar_cliente,
                                bg="#e74c3c", fg="white", width=15)
        btn_eliminar.grid(row=0, column=3, padx=5, pady=5)
        
        columns = ["RUC", "Razón Social", "Nombres", "Apellidos", "Teléfono", "Correo"]
        self.table_clientes = TableWidget(main_frame, columns,
                                         grid_options={
                                             'row': 1,
                                             'column': 0,
                                             'sticky': 'nsew',
                                             'padx': 10,
                                             'pady': 5
                                         })
    
    def load_clientes(self):
        try:
            print("🔍 Iniciando carga de clientes...")
            
            if not db.connection:
                print("❌ No hay conexión a la base de datos")
                messagebox.showerror("Error", "No hay conexión a la base de datos")
                return
            
            query = """
            SELECT c.ruc_cliente, c.razon_social, c.nombres, c.apellidos,
                   COALESCE(tc.telefono, 'No disponible') as telefono,
                   COALESCE(cc.correo, 'No disponible') as correo
            FROM cliente c
            LEFT JOIN telefonos_c tc ON c.ruc_cliente = tc.ruc_cliente
            LEFT JOIN correos_c cc ON c.ruc_cliente = cc.ruc_cliente
            ORDER BY c.ruc_cliente
            """
            
            print("🔍 Ejecutando consulta...")
            clientes = db.fetch_all(query)
            
            print(f"✅ Se encontraron {len(clientes)} clientes")
            
            if clientes:
                for i, cliente in enumerate(clientes[:3]):
                    print(f"   Cliente {i+1}: {cliente}")
                
                self.table_clientes.update_data(clientes)
                print("✅ Tabla actualizada correctamente")
            else:
                print("ℹ️ No hay clientes registrados")
                self.table_clientes.update_data([])
                
        except Exception as e:
            error_msg = f"Error al cargar clientes: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def guardar_cliente(self):
        try:
            ruc = self.entry_ruc.get().strip()
            razon_social = self.entry_razon_social.get().strip()
            nombres = self.entry_nombres.get().strip()
            apellidos = self.entry_apellidos.get().strip()
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
            
            if self.cliente_actual:
                self.actualizar_cliente(ruc, razon_social, nombres, apellidos, calle, numero, 
                                      distrito, provincia, departamento, telefono, correo)
            else:
                self.insertar_nuevo_cliente(ruc, razon_social, nombres, apellidos, calle, numero, 
                                          distrito, provincia, departamento, telefono, correo)
            
        except Exception as e:
            error_msg = f"Error al guardar cliente: {str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def insertar_nuevo_cliente(self, ruc, razon_social, nombres, apellidos, calle, numero, 
                             distrito, provincia, departamento, telefono, correo):
        # ✅ CORREGIDO: Asegurar que el RUC se pase como string
        existe = db.fetch_one("SELECT ruc_cliente FROM cliente WHERE ruc_cliente = %s", [str(ruc)])
        if existe:
            messagebox.showerror("Error", f"El RUC {ruc} ya está registrado")
            return
        
        query_cliente = """
        INSERT INTO cliente (ruc_cliente, razon_social, nombres, apellidos) 
        VALUES (%s, %s, %s, %s)
        """
        # ✅ CORREGIDO: Pasar RUC como string
        resultado = db.execute_query(query_cliente, [str(ruc), razon_social, nombres, apellidos])
        
        if not resultado:
            messagebox.showerror("Error", "No se pudo insertar el cliente")
            return
        
        if calle:
            query_direccion = """
            INSERT INTO direccion_c (ruc_cliente, calle, numero, provincia, departamento, distrito)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # ✅ CORREGIDO: Pasar RUC como string
            db.execute_query(query_direccion, [str(ruc), calle, numero, provincia, departamento, distrito])
        
        if telefono:
            if len(telefono) != 9 or not telefono.isdigit():
                messagebox.showerror("Error", "El teléfono debe tener 9 dígitos numéricos")
                return
            
            query_telefono = "INSERT INTO telefonos_c (ruc_cliente, telefono) VALUES (%s, %s)"
            # ✅ CORREGIDO: Pasar RUC como string
            db.execute_query(query_telefono, [str(ruc), telefono])
        
        if correo:
            if '@' not in correo:
                messagebox.showerror("Error", "El correo electrónico no es válido")
                return
            
            query_correo = "INSERT INTO correos_c (ruc_cliente, correo) VALUES (%s, %s)"
            # ✅ CORREGIDO: Pasar RUC como string
            db.execute_query(query_correo, [str(ruc), correo])
        
        messagebox.showinfo("Éxito", "Cliente registrado correctamente")
        self.limpiar_campos()
        self.load_clientes()
    
    def actualizar_cliente(self, ruc, razon_social, nombres, apellidos, calle, numero, 
                         distrito, provincia, departamento, telefono, correo):
        query_cliente = """
        UPDATE cliente SET razon_social = %s, nombres = %s, apellidos = %s 
        WHERE ruc_cliente = %s
        """
        # ✅ CORREGIDO: Pasar RUC como string
        resultado = db.execute_query(query_cliente, [razon_social, nombres, apellidos, str(ruc)])
        
        if not resultado:
            messagebox.showerror("Error", "No se pudo actualizar el cliente")
            return
        
        # ✅ CORREGIDO: Pasar RUC como string en todas las eliminaciones
        db.execute_query("DELETE FROM direccion_c WHERE ruc_cliente = %s", [str(ruc)])
        if calle:
            query_direccion = """
            INSERT INTO direccion_c (ruc_cliente, calle, numero, provincia, departamento, distrito)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query_direccion, [str(ruc), calle, numero, provincia, departamento, distrito])
        
        db.execute_query("DELETE FROM telefonos_c WHERE ruc_cliente = %s", [str(ruc)])
        if telefono:
            if len(telefono) != 9 or not telefono.isdigit():
                messagebox.showerror("Error", "El teléfono debe tener 9 dígitos numéricos")
                return
            
            query_telefono = "INSERT INTO telefonos_c (ruc_cliente, telefono) VALUES (%s, %s)"
            db.execute_query(query_telefono, [str(ruc), telefono])
        
        db.execute_query("DELETE FROM correos_c WHERE ruc_cliente = %s", [str(ruc)])
        if correo:
            if '@' not in correo:
                messagebox.showerror("Error", "El correo electrónico no es válido")
                return
            
            query_correo = "INSERT INTO correos_c (ruc_cliente, correo) VALUES (%s, %s)"
            db.execute_query(query_correo, [str(ruc), correo])
        
        messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
        self.cancelar_edicion()
        self.load_clientes()
    
    def editar_cliente(self):
        selection = self.table_clientes.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la lista")
            return
        
        try:
            item = self.table_clientes.tree.item(selection[0])
            ruc = item['values'][0]
            
            # ✅ CORREGIDO: Asegurar que el RUC se pase como string
            cliente = db.fetch_one("SELECT * FROM cliente WHERE ruc_cliente = %s", [str(ruc)])
            if not cliente:
                messagebox.showerror("Error", "No se pudo cargar los datos del cliente")
                return
            
            direccion = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento 
                FROM direccion_c WHERE ruc_cliente = %s LIMIT 1
            """, [str(ruc)])
            
            telefono_data = db.fetch_one("SELECT telefono FROM telefonos_c WHERE ruc_cliente = %s LIMIT 1", [str(ruc)])
            
            correo_data = db.fetch_one("SELECT correo FROM correos_c WHERE ruc_cliente = %s LIMIT 1", [str(ruc)])
            
            self.cliente_actual = ruc
            self.entry_ruc.delete(0, tk.END)
            self.entry_ruc.insert(0, cliente[0])
            self.entry_ruc.config(state="disabled")
            
            self.entry_razon_social.delete(0, tk.END)
            self.entry_razon_social.insert(0, cliente[1])
            
            self.entry_nombres.delete(0, tk.END)
            self.entry_nombres.insert(0, cliente[2])
            
            self.entry_apellidos.delete(0, tk.END)
            self.entry_apellidos.insert(0, cliente[3])
            
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
            
            self.btn_guardar.config(text="Actualizar Cliente", bg="#f39c12")
            self.btn_cancelar.config(state="normal")
            
            # ✅ CORREGIDO: Cambiar a la pestaña correcta (Registrar Cliente)
            self.notebook.select(0)  # Índice 0 = primera pestaña (Registrar Cliente)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos para edición: {str(e)}")
    
    def ver_detalles_cliente(self):
        selection = self.table_clientes.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la lista")
            return
        
        try:
            item = self.table_clientes.tree.item(selection[0])
            ruc = item['values'][0]
            
            # ✅ CORREGIDO: Asegurar que el RUC se pase como string
            cliente = db.fetch_one("SELECT * FROM cliente WHERE ruc_cliente = %s", [str(ruc)])
            if not cliente:
                messagebox.showerror("Error", "No se pudo cargar los datos del cliente")
                return
            
            direccion = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento 
                FROM direccion_c WHERE ruc_cliente = %s LIMIT 1
            """, [str(ruc)])
            
            telefonos = db.fetch_all("SELECT telefono FROM telefonos_c WHERE ruc_cliente = %s", [str(ruc)])
            
            correos = db.fetch_all("SELECT correo FROM correos_c WHERE ruc_cliente = %s", [str(ruc)])
            
            self.mostrar_detalles_cliente(cliente, direccion, telefonos, correos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
    
    def mostrar_detalles_cliente(self, cliente, direccion, telefonos, correos):
        ventana_detalles = tk.Toplevel(self.parent)
        ventana_detalles.title(f"Detalles de Cliente - {cliente[0]}")
        ventana_detalles.geometry("500x400")
        ventana_detalles.transient(self.parent)
        ventana_detalles.grab_set()
        
        main_frame = tk.Frame(ventana_detalles)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"CLIENTE: {cliente[1]}", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        frame_info = tk.LabelFrame(main_frame, text="Información General", padx=10, pady=10)
        frame_info.pack(fill="x", pady=10)
        
        tk.Label(frame_info, text=f"RUC: {cliente[0]}", anchor="w").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(frame_info, text=f"Razón Social: {cliente[1]}", anchor="w").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Label(frame_info, text=f"Nombres: {cliente[2]}", anchor="w").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        tk.Label(frame_info, text=f"Apellidos: {cliente[3]}", anchor="w").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        
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
    
    def eliminar_cliente(self):
        selection = self.table_clientes.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la lista")
            return
        
        try:
            item = self.table_clientes.tree.item(selection[0])
            ruc = item['values'][0]
            razon_social = item['values'][1]
            
            # ✅ CORREGIDO: Conversión explícita a string
            ruc_str = str(ruc)
            
            facturas_asociadas = db.fetch_one(
                "SELECT COUNT(*) FROM factura WHERE ruc_cliente = %s", [ruc_str]
            )
            
            if facturas_asociadas and facturas_asociadas[0] > 0:
                messagebox.showerror(
                    "Error", 
                    f"No se puede eliminar el cliente {razon_social}\n\n"
                    f"Tiene {facturas_asociadas[0]} factura(s) asociada(s).\n"
                    f"Elimine primero las facturas relacionadas."
                )
                return
            
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación", 
                f"¿Está seguro de que desea eliminar el cliente?\n\n"
                f"RUC: {ruc}\n"
                f"Razón Social: {razon_social}\n\n"
                f"Esta acción no se puede deshacer."
            )
            
            if respuesta:
                # ✅ CORREGIDO: Pasar RUC como string en TODAS las consultas
                db.execute_query("DELETE FROM correos_c WHERE ruc_cliente = %s", [ruc_str])
                db.execute_query("DELETE FROM telefonos_c WHERE ruc_cliente = %s", [ruc_str])
                db.execute_query("DELETE FROM direccion_c WHERE ruc_cliente = %s", [ruc_str])
                db.execute_query("DELETE FROM cliente WHERE ruc_cliente = %s", [ruc_str])
                
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                self.load_clientes()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")
    
    def cancelar_edicion(self):
        self.cliente_actual = None
        self.limpiar_campos()
        self.entry_ruc.config(state="normal")
        self.btn_guardar.config(text="Guardar Cliente", bg="#27ae60")
        self.btn_cancelar.config(state="disabled")
    
    def limpiar_campos(self):
        entries = [self.entry_ruc, self.entry_razon_social, self.entry_nombres,
                  self.entry_apellidos, self.entry_calle, self.entry_numero,
                  self.entry_distrito, self.entry_provincia, self.entry_departamento,
                  self.entry_telefono, self.entry_correo]
        
        for entry in entries:
            entry.delete(0, tk.END)