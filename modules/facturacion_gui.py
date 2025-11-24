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
        self.factura_editando = None
        self.tipo_cambio = 3.50  # ✅ TIPO DE CAMBIO FIJO
        self.create_widgets()
    
    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_crear = ttk.Frame(notebook)
        notebook.add(tab_crear, text="Crear/Editar Factura")
        self.create_factura_tab(tab_crear)
        
        tab_lista = ttk.Frame(notebook)
        notebook.add(tab_lista, text="Facturas Registradas")
        self.create_lista_tab(tab_lista)
    
    def create_factura_tab(self, parent):
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_frame, bg='white')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 0))
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # CABECERA DE FACTURA
        frame_cabecera = tk.LabelFrame(scrollable_frame, text="Datos de Factura", padx=10, pady=10)
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
        
        # Descuento Global (COMO PORCENTAJE)
        self.entry_descuento = CustomWidgets.create_entry(frame_cabecera, "Descuento Global (%):", 2, 2)
        self.entry_descuento.insert(0, "0.00")
        
        # ✅ NUEVO: Mostrar tipo de cambio
        frame_tipo_cambio = tk.Frame(frame_cabecera)
        frame_tipo_cambio.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)
        
        tk.Label(frame_tipo_cambio, text=f"Tipo de Cambio: 1 USD = S/ {self.tipo_cambio:.2f}", 
                font=("Arial", 9, "bold"), fg="blue").pack(anchor="w")
        
        # Campo para Nota/Observaciones
        frame_nota = tk.Frame(frame_cabecera)
        frame_nota.grid(row=4, column=0, columnspan=4, sticky="ew", pady=10)
        
        tk.Label(frame_nota, text="Nota/Observaciones:").grid(row=0, column=0, sticky="w", padx=5)
        self.entry_nota = tk.Text(frame_nota, height=3, width=60)
        self.entry_nota.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # DETALLES DE ITEMS
        frame_detalles = tk.LabelFrame(scrollable_frame, text="Detalles de Factura", padx=10, pady=10)
        frame_detalles.pack(fill="both", expand=True, padx=10, pady=5)
        
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
        
        # Descuento unitario (COMO PORCENTAJE)
        tk.Label(frame_controles, text="Descuento Unitario (%):").grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.entry_descuento_unitario = tk.Entry(frame_controles, width=10)
        self.entry_descuento_unitario.grid(row=0, column=6, padx=5, pady=5)
        self.entry_descuento_unitario.insert(0, "0.00")
        
        btn_agregar = tk.Button(frame_controles, text="Agregar Producto", 
                               command=self.agregar_producto, bg="#2E86AB", fg="white")
        btn_agregar.grid(row=0, column=7, rowspan=2, padx=10, pady=5, sticky="ns")
        
        btn_eliminar_item = tk.Button(frame_controles, text="Eliminar Producto", 
                                     command=self.eliminar_producto, bg="#e74c3c", fg="white")
        btn_eliminar_item.grid(row=0, column=8, rowspan=2, padx=5, pady=5, sticky="ns")
        
        # Tabla de items - AGREGAR COLUMNA DE DESCUENTO
        columns = ["Cantidad", "Unidad", "Descripción", "Valor Unitario", "Desc. Unit. (%)", "Subtotal"]
        self.table_detalles = TableWidget(frame_detalles, columns)
        
        # TOTALES
        frame_totales = tk.LabelFrame(scrollable_frame, text="Totales", padx=10, pady=10)
        frame_totales.pack(fill="x", padx=10, pady=5)
        
        self.label_subtotal = tk.Label(frame_totales, text="Subtotal: S/ 0.00", font=("Arial", 10))
        self.label_subtotal.grid(row=0, column=0, padx=20, pady=2)
        
        self.label_descuento_unitarios = tk.Label(frame_totales, text="Desc. Unitarios: S/ 0.00", font=("Arial", 10))
        self.label_descuento_unitarios.grid(row=1, column=0, padx=20, pady=2)
        
        self.label_descuento_global = tk.Label(frame_totales, text="Desc. Global: S/ 0.00", font=("Arial", 10))
        self.label_descuento_global.grid(row=2, column=0, padx=20, pady=2)
        
        self.label_total_descuentos = tk.Label(frame_totales, text="Total Descuentos: S/ 0.00", font=("Arial", 10, "bold"))
        self.label_total_descuentos.grid(row=3, column=0, padx=20, pady=2)
        
        self.label_valor_venta = tk.Label(frame_totales, text="Valor Venta: S/ 0.00", font=("Arial", 10))
        self.label_valor_venta.grid(row=0, column=1, padx=20, pady=2)
        
        self.label_igv = tk.Label(frame_totales, text="IGV (18%): S/ 0.00", font=("Arial", 10))
        self.label_igv.grid(row=1, column=1, padx=20, pady=2)
        
        self.label_total = tk.Label(frame_totales, text="TOTAL: S/ 0.00", 
                                   font=("Arial", 12, "bold"))
        self.label_total.grid(row=0, column=2, rowspan=4, padx=20, pady=2)
        
        # BOTONES
        frame_botones = tk.Frame(scrollable_frame)
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
        
        # Vincular eventos para recalcular
        self.entry_descuento.bind('<KeyRelease>', lambda e: self.calcular_totales())
        self.combo_moneda.bind('<<ComboboxSelected>>', lambda e: self.calcular_totales())
    
    def create_lista_tab(self, parent):
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ["Serie-Número", "Fecha", "Cliente", "RUC Cliente", "Total", "Moneda", "Descuentos"]
        self.table_facturas = TableWidget(main_frame, columns)
        
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
    
    def convertir_a_soles(self, valor, moneda):
        """✅ CONVERTIR A SOLES SI LA MONEDA ES USD"""
        if moneda == "USD":
            return valor * self.tipo_cambio
        return valor
    
    def agregar_producto(self):
        try:
            cantidad = float(self.entry_cantidad.get() or 0)
            unidad = self.entry_unidad_medida.get()
            descripcion = self.entry_descripcion.get()
            valor_unitario = float(self.entry_valor_unitario.get() or 0)
            moneda_actual = self.combo_moneda.get()
            
            # ✅ CORREGIDO: Convertir a soles si es USD
            valor_unitario_soles = self.convertir_a_soles(valor_unitario, moneda_actual)
            
            # ✅ CORREGIDO: Ambos descuentos como porcentajes (dividir entre 100)
            descuento_unitario_porcentaje = float(self.entry_descuento_unitario.get() or 0)
            descuento_unitario_decimal = descuento_unitario_porcentaje / 100
            
            # Calcular subtotal bruto (sin descuentos) EN SOLES
            subtotal_bruto = cantidad * valor_unitario_soles
            
            # Calcular descuento unitario en moneda EN SOLES
            descuento_total_item = subtotal_bruto * descuento_unitario_decimal
            
            # Calcular subtotal neto (con descuento aplicado) EN SOLES
            subtotal_neto = subtotal_bruto - descuento_total_item
            
            if not descripcion:
                messagebox.showerror("Error", "La descripción es obligatoria")
                return
            
            if subtotal_neto < 0:
                messagebox.showerror("Error", "El descuento no puede ser mayor al valor del producto")
                return
            
            self.detalles_factura.append({
                'cantidad': cantidad,
                'unidad_medida': unidad,
                'descripcion': descripcion,
                'valor_unitario': valor_unitario,  # Valor original
                'valor_unitario_soles': valor_unitario_soles,  # Valor en soles
                'moneda': moneda_actual,
                'descuento_unitario': descuento_unitario_decimal,  # Guardar como decimal
                'descuento_unitario_porcentaje': descuento_unitario_porcentaje,  # Guardar porcentaje para mostrar
                'subtotal_bruto': subtotal_bruto,
                'descuento_total_item': descuento_total_item,
                'subtotal': subtotal_neto
            })
            
            # Mostrar en la tabla con la moneda original
            simbolo_moneda = "$" if moneda_actual == "USD" else "S/"
            self.table_detalles.tree.insert("", "end", values=[
                f"{cantidad:.3f}", 
                unidad, 
                descripcion, 
                f"{simbolo_moneda} {valor_unitario:.2f}",
                f"{descuento_unitario_porcentaje:.2f}%",  # Mostrar como porcentaje
                f"S/ {subtotal_neto:.2f}"  # Siempre mostrar subtotal en soles
            ])
            
            self.calcular_totales()
            
            # Limpiar campos de producto (pero mantener otros datos)
            self.entry_cantidad.delete(0, tk.END)
            self.entry_descripcion.delete(0, tk.END)
            self.entry_valor_unitario.delete(0, tk.END)
            self.entry_descuento_unitario.delete(0, tk.END)
            self.entry_descuento_unitario.insert(0, "0.00")
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
            
            if 0 <= index < len(self.detalles_factura):
                self.detalles_factura.pop(index)
            
            self.table_detalles.tree.delete(selection[0])
            self.calcular_totales()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
    
    def calcular_totales(self):
        # Calcular subtotal bruto (suma de todos los items sin descuentos) EN SOLES
        subtotal_bruto = sum(item['subtotal_bruto'] for item in self.detalles_factura)
        
        # Calcular descuentos unitarios (suma de descuentos por item) EN SOLES
        descuento_unitarios = sum(item['descuento_total_item'] for item in self.detalles_factura)
        
        # ✅ CORREGIDO: Descuento global como porcentaje (dividir entre 100)
        try:
            descuento_global_porcentaje = float(self.entry_descuento.get() or 0)
            descuento_global_decimal = descuento_global_porcentaje / 100
            descuento_global_monto = subtotal_bruto * descuento_global_decimal
        except ValueError:
            descuento_global_porcentaje = 0
            descuento_global_decimal = 0
            descuento_global_monto = 0
            self.entry_descuento.delete(0, tk.END)
            self.entry_descuento.insert(0, "0.00")
        
        # Total de descuentos (unitarios + global) EN SOLES
        total_descuentos = descuento_unitarios + descuento_global_monto
        
        # Valor de venta (subtotal bruto - todos los descuentos) EN SOLES
        valor_venta = subtotal_bruto - total_descuentos
        
        # IGV (18% del valor de venta) EN SOLES
        igv = valor_venta * 0.18
        
        # Total final EN SOLES
        total = valor_venta + igv
        
        # Actualizar labels - SIEMPRE EN SOLES
        self.label_subtotal.config(text=f"Subtotal: S/ {subtotal_bruto:.2f}")
        self.label_descuento_unitarios.config(text=f"Desc. Unitarios: S/ {descuento_unitarios:.2f}")
        self.label_descuento_global.config(text=f"Desc. Global: S/ {descuento_global_monto:.2f}")
        self.label_total_descuentos.config(text=f"Total Descuentos: S/ {total_descuentos:.2f}")
        self.label_valor_venta.config(text=f"Valor Venta: S/ {valor_venta:.2f}")
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
            
            # ✅ CORREGIDO: Ambos descuentos como porcentajes
            try:
                descuento_global_porcentaje = float(self.entry_descuento.get() or 0)
            except ValueError:
                descuento_global_porcentaje = 0
            
            nota = self.entry_nota.get("1.0", tk.END).strip()
            
            serie_numero = self.generar_numero_factura()
            fecha_emision = datetime.now().date()
            
            # Insertar factura con descuento global (guardar el porcentaje)
            query_factura = """
            INSERT INTO factura (serie_numero, fecha_emision, forma_pago, moneda, ruc_empresa, ruc_cliente, descuento_global, nota)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query_factura, [
                serie_numero, fecha_emision, forma_pago, moneda, 
                emisor_ruc, cliente_ruc, descuento_global_porcentaje, nota  # Guardar porcentaje
            ])
            
            # Insertar detalles con descuento unitario (guardar como decimal)
            for detalle in self.detalles_factura:
                query_detalle = """
                INSERT INTO detallefactura (serie_numero, descripcion_item, cantidad, unidad_medida, valor_unitario, descuento_unitario, subtotal_item)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                db.execute_query(query_detalle, [
                    serie_numero, 
                    detalle['descripcion'],
                    detalle['cantidad'],
                    detalle['unidad_medida'],
                    detalle['valor_unitario'],  # Guardar valor original (no convertido)
                    detalle['descuento_unitario'],  # Guardar como decimal
                    detalle['subtotal']  # Guardar subtotal en soles
                ])
            
            # Calcular totales
            db.execute_query("SELECT fn_recalcular_totales(%s)", [serie_numero])
            
            messagebox.showinfo("Éxito", f"Factura {serie_numero} creada correctamente")
            
            # ✅ CORREGIDO: Reiniciar completamente la factura
            self.limpiar_factura_completa()
            self.load_facturas()
            
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
            
            # ✅ CORREGIDO: Descuento global como porcentaje
            try:
                descuento_global_porcentaje = float(self.entry_descuento.get() or 0)
            except ValueError:
                descuento_global_porcentaje = 0
            
            nota = self.entry_nota.get("1.0", tk.END).strip()
            
            serie_numero = self.factura_editando
            
            # Actualizar factura con descuento (guardar porcentaje)
            query_factura = """
            UPDATE factura SET forma_pago = %s, moneda = %s, ruc_empresa = %s, ruc_cliente = %s, 
            descuento_global = %s, nota = %s
            WHERE serie_numero = %s
            """
            db.execute_query(query_factura, [
                forma_pago, moneda, emisor_ruc, cliente_ruc, 
                descuento_global_porcentaje, nota, serie_numero  # Guardar porcentaje
            ])
            
            # Eliminar detalles antiguos
            db.execute_query("DELETE FROM detallefactura WHERE serie_numero = %s", [serie_numero])
            
            # Insertar nuevos detalles con descuento unitario (guardar como decimal)
            for detalle in self.detalles_factura:
                query_detalle = """
                INSERT INTO detallefactura (serie_numero, descripcion_item, cantidad, unidad_medida, valor_unitario, descuento_unitario, subtotal_item)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                db.execute_query(query_detalle, [
                    serie_numero, 
                    detalle['descripcion'],
                    detalle['cantidad'],
                    detalle['unidad_medida'],
                    detalle['valor_unitario'],  # Guardar valor original
                    detalle['descuento_unitario'],  # Guardar como decimal
                    detalle['subtotal']  # Guardar subtotal en soles
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
            query = "SELECT serie_numero FROM factura ORDER BY serie_numero DESC LIMIT 1"
            resultado = db.fetch_one(query)
            
            if resultado:
                ultimo_numero = resultado[0]
                partes = ultimo_numero.split('-')
                if len(partes) == 2:
                    numero = int(partes[1]) + 1
                    return f"{partes[0]}-{numero:06d}"
            
            return "F001-000001"
        except:
            return "F001-000001"
    
    def load_facturas(self):
        try:
            facturas = db.fetch_all("""
                SELECT f.serie_numero, f.fecha_emision, c.razon_social, 
                       c.ruc_cliente, cf.importe_total, f.moneda, cf.descuento
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
            
            factura = db.fetch_one("""
                SELECT f.serie_numero, f.fecha_emision, f.forma_pago, f.moneda,
                       e.razon_social as emisor, c.razon_social as cliente,
                       cf.subtotal, cf.descuento, cf.valor_venta, cf.igv, cf.importe_total,
                       f.nota, f.descuento_global
                FROM factura f
                JOIN emisor e ON f.ruc_empresa = e.ruc_empresa
                JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
                JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
                WHERE f.serie_numero = %s
            """, [serie_numero])
            
            if not factura:
                messagebox.showerror("Error", "No se pudieron cargar los detalles de la factura")
                return
            
            items = db.fetch_all("""
                SELECT descripcion_item, cantidad, unidad_medida, valor_unitario, descuento_unitario, subtotal_item
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
        ventana_detalles.geometry("1000x700")
        ventana_detalles.transient(self.parent)
        ventana_detalles.grab_set()
        
        main_frame = tk.Frame(ventana_detalles)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
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
        
        # Mostrar Nota si existe
        if factura[11]:  # Campo nota
            frame_nota = tk.LabelFrame(main_frame, text="Nota/Observaciones", padx=10, pady=10)
            frame_nota.pack(fill="x", pady=10)
            
            tk.Label(frame_nota, text=factura[11], justify="left", 
                    font=("Arial", 10), wraplength=800).pack(anchor="w")
        
        # Items de la factura
        frame_items = tk.LabelFrame(main_frame, text="Items de la Factura", padx=10, pady=10)
        frame_items.pack(fill="both", expand=True, pady=10)
        
        columns = ["Descripción", "Cantidad", "Unidad", "Valor Unitario", "Desc. Unitario", "Subtotal"]
        tree = ttk.Treeview(frame_items, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_items, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        for item in items:
            # Convertir descuento unitario de decimal a porcentaje para mostrar
            descuento_porcentaje = float(item[4]) * 100
            simbolo_moneda = "$" if factura[3] == "USD" else "S/"
            tree.insert("", "end", values=(
                item[0], item[1], item[2], f"{simbolo_moneda} {float(item[3]):.2f}", 
                f"{descuento_porcentaje:.2f}%", f"S/ {float(item[5]):.2f}"
            ))
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Totales con descuentos
        frame_totales = tk.LabelFrame(main_frame, text="Totales", padx=10, pady=10)
        frame_totales.pack(fill="x", pady=10)
        
        # Calcular descuentos unitarios y global
        descuento_global_monto = factura[12] * factura[6] / 100  # porcentaje * subtotal
        descuento_unitarios = factura[7] - descuento_global_monto
        
        totales_text = f"""Subtotal: {factura[6]:.2f}
Descuentos Totales: {factura[7]:.2f}
  - Descuentos Unitarios: {descuento_unitarios:.2f}
  - Descuento Global ({factura[12]:.2f}%): {descuento_global_monto:.2f}
Valor Venta: {factura[8]:.2f}
IGV (18%): {factura[9]:.2f}
TOTAL: {factura[10]:.2f} {factura[3]}"""
        
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
            factura = db.fetch_one("""
                SELECT ruc_empresa, ruc_cliente, forma_pago, moneda, descuento_global, nota
                FROM factura WHERE serie_numero = %s
            """, [serie_numero])
            
            if not factura:
                messagebox.showerror("Error", "No se pudieron cargar los datos de la factura")
                return
            
            items = db.fetch_all("""
                SELECT descripcion_item, cantidad, unidad_medida, valor_unitario, descuento_unitario, subtotal_item
                FROM detallefactura WHERE serie_numero = %s
            """, [serie_numero])
            
            self.limpiar_factura()
            
            self.combo_emisor.set(factura[0])
            self.combo_cliente.set(factura[1])
            self.combo_forma_pago.set(factura[2])
            self.combo_moneda.set(factura[3])
            
            # ✅ CORREGIDO: Cargar descuento global como porcentaje
            self.entry_descuento.delete(0, tk.END)
            self.entry_descuento.insert(0, f"{factura[4]:.2f}")  # Ya está guardado como porcentaje
            
            self.entry_nota.delete("1.0", tk.END)
            if factura[5]:
                self.entry_nota.insert("1.0", factura[5])
            
            self.detalles_factura = []
            for item in items:
                # Convertir descuento unitario de decimal a porcentaje para mostrar
                descuento_unitario_porcentaje = float(item[4]) * 100
                
                self.detalles_factura.append({
                    'cantidad': float(item[1]),
                    'unidad_medida': item[2],
                    'descripcion': item[0],
                    'valor_unitario': float(item[3]),
                    'valor_unitario_soles': self.convertir_a_soles(float(item[3]), factura[3]),
                    'moneda': factura[3],
                    'descuento_unitario': float(item[4]),  # Guardar como decimal
                    'descuento_unitario_porcentaje': descuento_unitario_porcentaje,  # Guardar porcentaje para mostrar
                    'subtotal_bruto': (float(item[1]) * self.convertir_a_soles(float(item[3]), factura[3])),
                    'descuento_total_item': (float(item[1]) * self.convertir_a_soles(float(item[3]), factura[3]) * float(item[4])),
                    'subtotal': float(item[5])
                })
                
                simbolo_moneda = "$" if factura[3] == "USD" else "S/"
                self.table_detalles.tree.insert("", "end", values=[
                    f"{float(item[1]):.3f}", 
                    item[2], 
                    item[0], 
                    f"{simbolo_moneda} {float(item[3]):.2f}",
                    f"{descuento_unitario_porcentaje:.2f}%",  # Mostrar como porcentaje
                    f"S/ {float(item[5]):.2f}"
                ])
            
            self.calcular_totales()
            
            self.factura_editando = serie_numero
            self.entry_fecha.config(state="disabled")
            self.btn_guardar.config(state="disabled")
            self.btn_actualizar.config(state="normal")
            self.btn_cancelar.config(state="normal")
            
            messagebox.showinfo("Éxito", f"Factura {serie_numero} cargada para edición")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar factura: {str(e)}")
    
    def cancelar_edicion(self):
        self.factura_editando = None
        self.limpiar_factura_completa()
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
                db.execute_query("DELETE FROM nota WHERE serie_numero = %s", [serie_numero])
                db.execute_query("DELETE FROM detallefactura WHERE serie_numero = %s", [serie_numero])
                db.execute_query("DELETE FROM calculosfactura WHERE serie_numero = %s", [serie_numero])
                db.execute_query("DELETE FROM factura WHERE serie_numero = %s", [serie_numero])
                
                messagebox.showinfo("Éxito", "Factura eliminada correctamente")
                self.load_facturas()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar factura: {str(e)}")
    
    def limpiar_factura(self):
        """Limpia solo los productos, mantiene otros datos"""
        self.detalles_factura = []
        for item in self.table_detalles.tree.get_children():
            self.table_detalles.tree.delete(item)
        
        self.calcular_totales()
    
    def limpiar_factura_completa(self):
        """✅ NUEVO: Limpia completamente todos los campos para nueva factura"""
        self.detalles_factura = []
        for item in self.table_detalles.tree.get_children():
            self.table_detalles.tree.delete(item)
        
        self.calcular_totales()
        self.combo_emisor.set('')
        self.combo_cliente.set('')
        self.combo_forma_pago.set('')
        self.combo_moneda.set('PEN')
        self.entry_descuento.delete(0, tk.END)
        self.entry_descuento.insert(0, "0.00")
        self.entry_descuento_unitario.delete(0, tk.END)
        self.entry_descuento_unitario.insert(0, "0.00")
        self.entry_nota.delete("1.0", tk.END)
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Limpiar campos de producto
        self.entry_cantidad.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)
        self.entry_valor_unitario.delete(0, tk.END)
        self.entry_unidad_medida.set("UND")