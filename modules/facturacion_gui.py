import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from database import db
from modules.widgets import CustomWidgets, TableWidget

class FacturacionGUI:
    def __init__(self, parent):
        self.parent = parent
        self.detalles_factura = []
        self.factura_editando = None  # Para controlar si estamos editando
        self.create_widgets()
    
    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña Crear/Editar Factura
        tab_crear = ttk.Frame(notebook)
        notebook.add(tab_crear, text="Crear/Editar Factura")
        self.create_factura_tab(tab_crear)
        
        # Pestaña Facturas Registradas
        tab_lista = ttk.Frame(notebook)
        notebook.add(tab_lista, text="Facturas Registradas")
        self.create_lista_tab(tab_lista)
    
    def create_factura_tab(self, parent):
        # Frame principal con scroll
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True)
        
        # Cabecera de factura
        frame_cabecera = tk.LabelFrame(main_frame, text="Datos de Factura", padx=10, pady=10)
        frame_cabecera.pack(fill="x", padx=10, pady=5)
        
        # Emisor y Cliente
        self.combo_emisor = CustomWidgets.create_combobox(
            frame_cabecera, "Emisor:", 0, 0, self.get_emisores())
        self.combo_cliente = CustomWidgets.create_combobox(
            frame_cabecera, "Cliente:", 1, 0, self.get_clientes())
        
        # Fecha y forma de pago
        self.entry_fecha = CustomWidgets.create_entry(frame_cabecera, "Fecha:", 0, 2)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        self.combo_forma_pago = CustomWidgets.create_combobox(
            frame_cabecera, "Forma de Pago:", 1, 2, ["Contado", "Credito"])
        
        self.combo_moneda = CustomWidgets.create_combobox(
            frame_cabecera, "Moneda:", 2, 0, ["PEN", "USD"])
        
        # Detalles de items
        frame_detalles = tk.LabelFrame(main_frame, text="Detalles de Factura", padx=10, pady=10)
        frame_detalles.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame para controles de items
        frame_controles = tk.Frame(frame_detalles)
        frame_controles.pack(fill="x", pady=5)
        
        # Campos para agregar items
        tk.Label(frame_controles, text="Cantidad:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_cantidad = tk.Entry(frame_controles, width=10)
        self.entry_cantidad.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_controles, text="Unidad Medida:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_unidad_medida = ttk.Combobox(frame_controles, values=["UND", "KG", "ML", "PL"], width=8)
        self.entry_unidad_medida.grid(row=0, column=3, padx=5, pady=5)
        self.entry_unidad_medida.set("UND")
        
        tk.Label(frame_controles, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_descripcion = tk.Entry(frame_controles, width=30)
        self.entry_descripcion.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        tk.Label(frame_controles, text="Valor Unitario:").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_valor_unitario = tk.Entry(frame_controles, width=10)
        self.entry_valor_unitario.grid(row=1, column=4, padx=5, pady=5)
        
        # Botón agregar producto
        btn_agregar = tk.Button(frame_controles, text="Agregar Producto", 
                               command=self.agregar_producto, bg="#2E86AB", fg="white")
        btn_agregar.grid(row=0, column=5, rowspan=2, padx=10, pady=5, sticky="ns")
        
        # Botón eliminar producto seleccionado
        btn_eliminar_item = tk.Button(frame_controles, text="Eliminar Producto", 
                                     command=self.eliminar_producto, bg="#e74c3c", fg="white")
        btn_eliminar_item.grid(row=0, column=6, rowspan=2, padx=5, pady=5, sticky="ns")
        
        # Tabla de items
        columns = ["Cantidad", "Unidad", "Descripción", "Valor Unitario", "Subtotal"]
        self.table_detalles = TableWidget(frame_detalles, columns)
        
        # Totales
        frame_totales = tk.LabelFrame(main_frame, text="Totales", padx=10, pady=10)
        frame_totales.pack(fill="x", padx=10, pady=5)
        
        self.label_subtotal = tk.Label(frame_totales, text="Subtotal: S/ 0.00", font=("Arial", 10))
        self.label_subtotal.grid(row=0, column=0, padx=20, pady=2)
        
        self.label_igv = tk.Label(frame_totales, text="IGV (18%): S/ 0.00", font=("Arial", 10))
        self.label_igv.grid(row=0, column=1, padx=20, pady=2)
        
        self.label_total = tk.Label(frame_totales, text="TOTAL: S/ 0.00", 
                                   font=("Arial", 12, "bold"))
        self.label_total.grid(row=0, column=2, padx=20, pady=2)
        
        # Botones guardar/actualizar/cancelar
        frame_botones = tk.Frame(main_frame)
        frame_botones.pack(fill="x", padx=10, pady=10)
        
        self.btn_guardar = tk.Button(frame_botones, text="GUARDAR FACTURA", 
                                    command=self.guardar_factura, 
                                    bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                                    height=2)
        self.btn_guardar.pack(side="left", padx=5, fill="x", expand=True)
        
        self.btn_actualizar = tk.Button(frame_botones, text="ACTUALIZAR FACTURA", 
                                       command=self.actualizar_factura, 
                                       bg="#f39c12", fg="white", font=("Arial", 12, "bold"),
                                       height=2, state="disabled")
        self.btn_actualizar.pack(side="left", padx=5, fill="x", expand=True)
        
        self.btn_cancelar = tk.Button(frame_botones, text="CANCELAR EDICIÓN", 
                                     command=self.cancelar_edicion, 
                                     bg="#e74c3c", fg="white", font=("Arial", 12),
                                     height=2, state="disabled")
        self.btn_cancelar.pack(side="left", padx=5, fill="x", expand=True)
    
    def create_lista_tab(self, parent):
        # Frame principal
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabla de facturas
        columns = ["Serie-Número", "Fecha", "Cliente", "RUC Cliente", "Total", "Moneda"]
        self.table_facturas = TableWidget(main_frame, columns)
        
        # Frame para botones
        frame_botones = tk.Frame(main_frame)
        frame_botones.pack(fill="x", pady=5)
        
        btn_actualizar = tk.Button(frame_botones, text="Actualizar Lista", 
                                  command=self.load_facturas, bg="#3498db", fg="white")
        btn_actualizar.pack(side="left", padx=5)
        
        btn_detalles = tk.Button(frame_botones, text="Ver Detalles", 
                                command=self.ver_detalles_factura, bg="#f39c12", fg="white")
        btn_detalles.pack(side="left", padx=5)
        
        btn_editar = tk.Button(frame_botones, text="Editar Factura", 
                              command=self.editar_factura, bg="#2E86AB", fg="white")
        btn_editar.pack(side="left", padx=5)
        
        btn_eliminar = tk.Button(frame_botones, text="Eliminar Factura", 
                                command=self.eliminar_factura, bg="#e74c3c", fg="white")
        btn_eliminar.pack(side="left", padx=5)
        
        self.load_facturas()
    
    def get_emisores(self):
        try:
            query = "SELECT ruc_empresa FROM emisor"
            emisores = db.fetch_all(query)
            return [emisor[0] for emisor in emisores] if emisores else []
        except Exception as e:
            print(f"Error al cargar emisores: {e}")
            return []
    
    def get_clientes(self):
        try:
            query = "SELECT ruc_cliente FROM cliente"
            clientes = db.fetch_all(query)
            return [cliente[0] for cliente in clientes] if clientes else []
        except Exception as e:
            print(f"Error al cargar clientes: {e}")
            return []
    
    def agregar_producto(self):
        try:
            cantidad = float(self.entry_cantidad.get() or 0)
            unidad = self.entry_unidad_medida.get()
            descripcion = self.entry_descripcion.get()
            valor_unitario = float(self.entry_valor_unitario.get() or 0)
            subtotal = cantidad * valor_unitario
            
            if not descripcion:
                messagebox.showerror("Error", "La descripción es obligatoria")
                return
            
            # Agregar a la lista
            self.detalles_factura.append({
                'cantidad': cantidad,
                'unidad_medida': unidad,
                'descripcion': descripcion,
                'valor_unitario': valor_unitario,
                'subtotal': subtotal
            })
            
            # Agregar a la tabla
            self.table_detalles.tree.insert("", "end", values=[
                f"{cantidad:.3f}", unidad, descripcion, 
                f"S/ {valor_unitario:.2f}", f"S/ {subtotal:.2f}"
            ])
            
            # Calcular totales
            self.calcular_totales()
            
            # Limpiar campos
            self.entry_cantidad.delete(0, tk.END)
            self.entry_descripcion.delete(0, tk.END)
            self.entry_valor_unitario.delete(0, tk.END)
            self.entry_cantidad.focus()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique los valores ingresados (use números)")
    
    def eliminar_producto(self):
        selection = self.table_detalles.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        try:
            item = self.table_detalles.tree.item(selection[0])
            index = self.table_detalles.tree.index(selection[0])
            
            # Eliminar de la lista
            if 0 <= index < len(self.detalles_factura):
                self.detalles_factura.pop(index)
            
            # Eliminar de la tabla visual
            self.table_detalles.tree.delete(selection[0])
            
            # Recalcular totales
            self.calcular_totales()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
    
    def calcular_totales(self):
        subtotal = sum(item['subtotal'] for item in self.detalles_factura)
        igv = subtotal * 0.18
        total = subtotal + igv
        
        self.label_subtotal.config(text=f"Subtotal: S/ {subtotal:.2f}")
        self.label_igv.config(text=f"IGV (18%): S/ {igv:.2f}")
        self.label_total.config(text=f"TOTAL: S/ {total:.2f}")
    
    def guardar_factura(self):
        try:
            if not self.detalles_factura:
                messagebox.showerror("Error", "Agregue al menos un producto")
                return
            
            emisor_ruc = self.combo_emisor.get()
            cliente_ruc = self.combo_cliente.get()
            forma_pago = self.combo_forma_pago.get()
            moneda = self.combo_moneda.get()
            
            if not all([emisor_ruc, cliente_ruc, forma_pago, moneda]):
                messagebox.showerror("Error", "Complete todos los campos obligatorios")
                return
            
            # Para simplificar, insertar directamente en lugar de usar procedimiento
            serie_numero = self.generar_numero_factura()
            fecha_emision = datetime.now().date()
            
            # Insertar factura
            query_factura = """
            INSERT INTO factura (serie_numero, fecha_emision, forma_pago, moneda, ruc_empresa, ruc_cliente)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query_factura, [serie_numero, fecha_emision, forma_pago, moneda, emisor_ruc, cliente_ruc])
            
            # Insertar detalles
            for detalle in self.detalles_factura:
                query_detalle = """
                INSERT INTO detallefactura (serie_numero, descripcion_item, cantidad, unidad_medida, valor_unitario, subtotal_item)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_query(query_detalle, [
                    serie_numero, 
                    detalle['descripcion'],
                    detalle['cantidad'],
                    detalle['unidad_medida'],
                    detalle['valor_unitario'],
                    detalle['subtotal']
                ])
            
            # Calcular totales
            db.execute_query("SELECT fn_recalcular_totales(%s)", [serie_numero])
            
            messagebox.showinfo("Éxito", f"Factura {serie_numero} creada correctamente")
            self.limpiar_factura()
            self.load_facturas()  # Actualizar lista
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar factura: {str(e)}")
    
    def actualizar_factura(self):
        try:
            if not self.detalles_factura:
                messagebox.showerror("Error", "Agregue al menos un producto")
                return
            
            if not self.factura_editando:
                messagebox.showerror("Error", "No hay factura en edición")
                return
            
            emisor_ruc = self.combo_emisor.get()
            cliente_ruc = self.combo_cliente.get()
            forma_pago = self.combo_forma_pago.get()
            moneda = self.combo_moneda.get()
            
            if not all([emisor_ruc, cliente_ruc, forma_pago, moneda]):
                messagebox.showerror("Error", "Complete todos los campos obligatorios")
                return
            
            serie_numero = self.factura_editando
            
            # Actualizar factura
            query_factura = """
            UPDATE factura SET forma_pago = %s, moneda = %s, ruc_empresa = %s, ruc_cliente = %s
            WHERE serie_numero = %s
            """
            db.execute_query(query_factura, [forma_pago, moneda, emisor_ruc, cliente_ruc, serie_numero])
            
            # Eliminar detalles antiguos
            db.execute_query("DELETE FROM detallefactura WHERE serie_numero = %s", [serie_numero])
            
            # Insertar nuevos detalles
            for detalle in self.detalles_factura:
                query_detalle = """
                INSERT INTO detallefactura (serie_numero, descripcion_item, cantidad, unidad_medida, valor_unitario, subtotal_item)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_query(query_detalle, [
                    serie_numero, 
                    detalle['descripcion'],
                    detalle['cantidad'],
                    detalle['unidad_medida'],
                    detalle['valor_unitario'],
                    detalle['subtotal']
                ])
            
            # Recalcular totales
            db.execute_query("SELECT fn_recalcular_totales(%s)", [serie_numero])
            
            messagebox.showinfo("Éxito", f"Factura {serie_numero} actualizada correctamente")
            self.cancelar_edicion()
            self.load_facturas()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar factura: {str(e)}")
    
    def generar_numero_factura(self):
        try:
            # Buscar el último número de factura
            query = "SELECT serie_numero FROM factura ORDER BY serie_numero DESC LIMIT 1"
            resultado = db.fetch_one(query)
            
            if resultado:
                ultimo_numero = resultado[0]
                # Extraer el número y incrementar
                partes = ultimo_numero.split('-')
                if len(partes) == 2:
                    numero = int(partes[1]) + 1
                    return f"{partes[0]}-{numero:06d}"
            
            # Si no hay facturas, empezar desde 1
            return "F001-000001"
        except:
            return "F001-000001"
    
    def load_facturas(self):
        try:
            facturas = db.fetch_all("""
                SELECT f.serie_numero, f.fecha_emision, c.razon_social, 
                       c.ruc_cliente, cf.importe_total, f.moneda
                FROM factura f
                JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
                JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
                ORDER BY f.fecha_emision DESC
            """)
            self.table_facturas.update_data(facturas)
        except Exception as e:
            print(f"Error al cargar facturas: {e}")
    
    def ver_detalles_factura(self):
        selection = self.table_facturas.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una factura")
            return
        
        try:
            item = self.table_facturas.tree.item(selection[0])
            serie_numero = item['values'][0]
            
            # Obtener detalles completos de la factura
            factura = db.fetch_one("""
                SELECT f.serie_numero, f.fecha_emision, f.forma_pago, f.moneda,
                       e.razon_social as emisor, c.razon_social as cliente,
                       cf.subtotal, cf.igv, cf.importe_total
                FROM factura f
                JOIN emisor e ON f.ruc_empresa = e.ruc_empresa
                JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
                JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
                WHERE f.serie_numero = %s
            """, [serie_numero])
            
            if not factura:
                messagebox.showerror("Error", "No se pudieron cargar los detalles de la factura")
                return
            
            # Obtener items de la factura
            items = db.fetch_all("""
                SELECT descripcion_item, cantidad, unidad_medida, valor_unitario, subtotal_item
                FROM detallefactura
                WHERE serie_numero = %s
                ORDER BY id_detalle
            """, [serie_numero])
            
            self.mostrar_detalles_factura(factura, items)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
    
    def mostrar_detalles_factura(self, factura, items):
        ventana_detalles = tk.Toplevel(self.parent)
        ventana_detalles.title(f"Detalles de Factura - {factura[0]}")
        ventana_detalles.geometry("800x600")
        ventana_detalles.transient(self.parent)
        ventana_detalles.grab_set()
        
        main_frame = tk.Frame(ventana_detalles)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text=f"FACTURA: {factura[0]}", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Información general
        frame_info = tk.LabelFrame(main_frame, text="Información General", padx=10, pady=10)
        frame_info.pack(fill="x", pady=10)
        
        info_text = f"""Fecha: {factura[1]}
Forma de Pago: {factura[2]}
Moneda: {factura[3]}
Emisor: {factura[4]}
Cliente: {factura[5]}"""
        
        tk.Label(frame_info, text=info_text, justify="left", font=("Arial", 10)).pack(anchor="w")
        
        # Items de la factura
        frame_items = tk.LabelFrame(main_frame, text="Items de la Factura", padx=10, pady=10)
        frame_items.pack(fill="both", expand=True, pady=10)
        
        # Tabla de items
        columns = ["Descripción", "Cantidad", "Unidad", "Valor Unitario", "Subtotal"]
        tree = ttk.Treeview(frame_items, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_items, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Insertar items
        for item in items:
            tree.insert("", "end", values=item)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Totales
        frame_totales = tk.LabelFrame(main_frame, text="Totales", padx=10, pady=10)
        frame_totales.pack(fill="x", pady=10)
        
        totales_text = f"""Subtotal: {factura[6]:.2f}
IGV (18%): {factura[7]:.2f}
TOTAL: {factura[8]:.2f} {factura[3]}"""
        
        tk.Label(frame_totales, text=totales_text, justify="left", 
                font=("Arial", 11, "bold")).pack(anchor="w")
    
    def editar_factura(self):
        selection = self.table_facturas.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una factura para editar")
            return
        
        try:
            item = self.table_facturas.tree.item(selection[0])
            serie_numero = item['values'][0]
            
            # Verificar si la factura tiene notas asociadas
            notas = db.fetch_one("SELECT COUNT(*) FROM nota WHERE serie_numero = %s", [serie_numero])
            
            if notas and notas[0] > 0:
                messagebox.showerror(
                    "Error", 
                    f"No se puede editar la factura {serie_numero}\n\n"
                    f"Tiene {notas[0]} nota(s) asociada(s).\n"
                    f"Elimine primero las notas relacionadas."
                )
                return
            
            respuesta = messagebox.askyesno(
                "Confirmar Edición", 
                f"¿Está seguro de que desea editar la factura {serie_numero}?\n\n"
                f"Esta acción cargará la factura en el formulario de edición."
            )
            
            if respuesta:
                self.cargar_factura_para_edicion(serie_numero)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar factura: {str(e)}")
    
    def cargar_factura_para_edicion(self, serie_numero):
        try:
            # Obtener datos de la factura
            factura = db.fetch_one("""
                SELECT ruc_empresa, ruc_cliente, forma_pago, moneda
                FROM factura WHERE serie_numero = %s
            """, [serie_numero])
            
            if not factura:
                messagebox.showerror("Error", "No se pudieron cargar los datos de la factura")
                return
            
            # Obtener items de la factura
            items = db.fetch_all("""
                SELECT descripcion_item, cantidad, unidad_medida, valor_unitario, subtotal_item
                FROM detallefactura WHERE serie_numero = %s
            """, [serie_numero])
            
            # Limpiar formulario actual
            self.limpiar_factura()
            
            # Cargar datos en el formulario
            self.combo_emisor.set(factura[0])
            self.combo_cliente.set(factura[1])
            self.combo_forma_pago.set(factura[2])
            self.combo_moneda.set(factura[3])
            
            # Cargar items
            self.detalles_factura = []
            for item in items:
                self.detalles_factura.append({
                    'cantidad': float(item[1]),
                    'unidad_medida': item[2],
                    'descripcion': item[0],
                    'valor_unitario': float(item[3]),
                    'subtotal': float(item[4])
                })
                
                # Agregar a la tabla visual
                self.table_detalles.tree.insert("", "end", values=[
                    f"{float(item[1]):.3f}", item[2], item[0], 
                    f"S/ {float(item[3]):.2f}", f"S/ {float(item[4]):.2f}"
                ])
            
            # Calcular totales
            self.calcular_totales()
            
            # Configurar modo edición
            self.factura_editando = serie_numero
            self.entry_fecha.config(state="disabled")
            self.btn_guardar.config(state="disabled")
            self.btn_actualizar.config(state="normal")
            self.btn_cancelar.config(state="normal")
            
            # Cambiar título de la pestaña (opcional)
            messagebox.showinfo("Éxito", f"Factura {serie_numero} cargada para edición")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar factura: {str(e)}")
    
    def cancelar_edicion(self):
        self.factura_editando = None
        self.limpiar_factura()
        self.entry_fecha.config(state="normal")
        self.btn_guardar.config(state="normal")
        self.btn_actualizar.config(state="disabled")
        self.btn_cancelar.config(state="disabled")
    
    def eliminar_factura(self):
        selection = self.table_facturas.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una factura para eliminar")
            return
        
        try:
            item = self.table_facturas.tree.item(selection[0])
            serie_numero = item['values'][0]
            cliente = item['values'][2]
            total = item['values'][4]
            
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación", 
                f"¿Está seguro de que desea eliminar la factura?\n\n"
                f"Factura: {serie_numero}\n"
                f"Cliente: {cliente}\n"
                f"Total: {total}\n\n"
                f"Esta acción no se puede deshacer."
            )
            
            if respuesta:
                # Eliminar en orden para respetar las restricciones de clave foránea
                db.execute_query("DELETE FROM nota WHERE serie_numero = %s", [serie_numero])
                db.execute_query("DELETE FROM detallefactura WHERE serie_numero = %s", [serie_numero])
                db.execute_query("DELETE FROM calculosfactura WHERE serie_numero = %s", [serie_numero])
                db.execute_query("DELETE FROM factura WHERE serie_numero = %s", [serie_numero])
                
                messagebox.showinfo("Éxito", "Factura eliminada correctamente")
                self.load_facturas()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar factura: {str(e)}")
    
    def limpiar_factura(self):
        self.detalles_factura = []
        for item in self.table_detalles.tree.get_children():
            self.table_detalles.tree.delete(item)
        
        self.calcular_totales()
        self.combo_emisor.set('')
        self.combo_cliente.set('')
        self.combo_forma_pago.set('')
        self.combo_moneda.set('PEN')
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))