import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from modules.widgets import CustomWidgets, TableWidget
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import os
from datetime import datetime
import decimal

class ReportesGUI:
    def __init__(self, parent):
        self.parent = parent
        
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
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Custom.TFrame", background=self.bg_color)
        style.configure("Custom.TLabel", background=self.bg_color, foreground=self.text_color)
    
    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        tab_consultar = ttk.Frame(notebook, style="Custom.TFrame")
        notebook.add(tab_consultar, text="Consultar Factura")
        self.create_consulta_tab(tab_consultar)
        
        tab_reportes = ttk.Frame(notebook, style="Custom.TFrame")
        notebook.add(tab_reportes, text="Reportes")
        self.create_reportes_tab(tab_reportes)
    
    def create_consulta_tab(self, parent):
        main_frame = tk.Frame(parent, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill="x", pady=(0, 30))
        
        tk.Label(title_frame, 
                text="CONSULTAR FACTURA",
                font=("Arial", 20, "bold"),
                bg=self.bg_color,
                fg=self.primary_color).pack(anchor="w")
        
        search_frame = tk.Frame(main_frame, bg=self.bg_color)
        search_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(search_frame, 
                text="Buscar Factura:",
                font=("Arial", 11, "bold"),
                bg=self.bg_color,
                fg=self.text_color).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.entry_busqueda = tk.Entry(search_frame, 
                                      width=30,
                                      font=("Arial", 10),
                                      relief="flat",
                                      bg="white",
                                      highlightbackground=self.light_gray,
                                      highlightcolor=self.secondary_color,
                                      highlightthickness=1,
                                      bd=0)
        self.entry_busqueda.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_facturas)
        
        btn_buscar = tk.Button(search_frame, 
                              text="Buscar", 
                              command=self.buscar_facturas,
                              bg=self.secondary_color,
                              fg="white",
                              font=("Arial", 10, "bold"),
                              relief="flat",
                              padx=20,
                              pady=8,
                              cursor="hand2")
        btn_buscar.grid(row=0, column=2, padx=5, pady=5)
        
        btn_pdf = tk.Button(search_frame, 
                           text="Generar PDF", 
                           command=self.generar_pdf_factura,
                           bg=self.accent_color,
                           fg="white",
                           font=("Arial", 10, "bold"),
                           relief="flat",
                           padx=20,
                           pady=8,
                           cursor="hand2")
        btn_pdf.grid(row=0, column=3, padx=5, pady=5)
        
        search_frame.grid_columnconfigure(1, weight=1)
        
        columns = ["Serie-Número", "Fecha", "Cliente", "Total", "Moneda", "Descuentos"]
        self.table_resultados = TableWidget(main_frame, columns)
    
    def create_reportes_tab(self, parent):
        main_frame = tk.Frame(parent, bg=self.bg_color, padx=40, pady=40)
        main_frame.pack(fill="both", expand=True)
        
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill="x", pady=(0, 40))
        
        tk.Label(title_frame, 
                text="GENERAR REPORTES",
                font=("Arial", 20, "bold"),
                bg=self.bg_color,
                fg=self.primary_color).pack(anchor="w")
        
        desc_frame = tk.Frame(main_frame, bg=self.bg_color)
        desc_frame.pack(fill="x", pady=(0, 30))
        
        tk.Label(desc_frame,
                text="Seleccione el tipo de reporte que desea generar:",
                font=("Arial", 12),
                bg=self.bg_color,
                fg=self.text_color).pack(anchor="w")
        
        frame_botones = tk.Frame(main_frame, bg=self.bg_color)
        frame_botones.pack(expand=True)
        
        reports = [
            ("📊 Reporte de Ventas", self.generar_reporte_ventas, self.secondary_color),
            ("👥 Reporte de Clientes", self.generar_reporte_clientes, self.success_color),
            ("📦 Productos Más Vendidos", self.generar_reporte_productos, self.warning_color),
            ("📅 Reporte Diario", self.generar_reporte_diario, self.accent_color),
            ("💰 Reporte con Descuentos", self.generar_reporte_descuentos, "#9b59b6")
        ]
        
        for i, (text, command, color) in enumerate(reports):
            btn_frame = tk.Frame(frame_botones, bg=self.bg_color)
            btn_frame.grid(row=i//2, column=i%2, padx=15, pady=15)
            
            btn = tk.Button(btn_frame, 
                          text=text, 
                          command=command,
                          bg=color,
                          fg="white",
                          font=("Arial", 12, "bold"),
                          relief="flat",
                          width=20,
                          height=3,
                          cursor="hand2")
            btn.pack(padx=10, pady=10)
    
    def buscar_facturas(self, event=None):
        try:
            criterio = self.entry_busqueda.get()
            
            if not criterio:
                self.table_resultados.update_data([])
                return
            
            query = """
            SELECT f.serie_numero, f.fecha_emision, c.razon_social, 
                   cf.importe_total, f.moneda, cf.descuento
            FROM factura f
            JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
            JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
            WHERE f.serie_numero ILIKE %s OR c.razon_social ILIKE %s
            ORDER BY f.fecha_emision DESC
            """
            
            resultados = db.fetch_all(query, [f'%{criterio}%', f'%{criterio}%'])
            self.table_resultados.update_data(resultados)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")
    
    def generar_pdf_factura(self):
        selection = self.table_resultados.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una factura para generar PDF")
            return
        
        try:
            item = self.table_resultados.tree.item(selection[0])
            serie_numero = item['values'][0]
            
            factura = db.fetch_one("""
                SELECT f.serie_numero, f.fecha_emision, f.forma_pago, f.moneda,
                       e.ruc_empresa, e.razon_social as emisor_razon, e.nombre_empresa,
                       c.ruc_cliente, c.razon_social as cliente_razon,
                       cf.subtotal, cf.descuento, cf.valor_venta, cf.igv, cf.importe_total,
                       f.nota, f.descuento_global
                FROM factura f
                JOIN emisor e ON f.ruc_empresa = e.ruc_empresa
                JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
                JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
                WHERE f.serie_numero = %s
            """, [serie_numero])
            
            if not factura:
                messagebox.showerror("Error", "No se pudieron cargar los datos de la factura")
                return
            
            items = db.fetch_all("""
                SELECT descripcion_item, cantidad, unidad_medida, valor_unitario, descuento_unitario, subtotal_item
                FROM detallefactura
                WHERE serie_numero = %s
                ORDER BY id_detalle
            """, [serie_numero])
            
            direccion_emisor = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento
                FROM direccion_e WHERE ruc_empresa = %s LIMIT 1
            """, [factura[4]])
            
            self.crear_pdf_factura(factura, items, direccion_emisor)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")
    
    def convertir_decimal(self, valor):
        """Convierte decimal.Decimal a float de forma segura"""
        if valor is None:
            return 0.0
        if isinstance(valor, decimal.Decimal):
            return float(valor)
        return float(valor)
    
    def crear_pdf_factura(self, factura, items, direccion_emisor):
        try:
            filename = f"Factura_{factura[0]}.pdf"
            filepath = os.path.join(os.getcwd(), filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm)
            elements = []
            
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            empresa_style = ParagraphStyle(
                'Empresa',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.black,
                alignment=1,
                fontName='Helvetica-Bold',
                spaceAfter=6
            )
            
            direccion_style = ParagraphStyle(
                'Direccion',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.black,
                alignment=1,
                fontName='Helvetica',
                spaceAfter=12
            )
            
            titulo_style = ParagraphStyle(
                'Titulo',
                parent=styles['Normal'],
                fontSize=16,
                textColor=colors.black,
                alignment=1,
                fontName='Helvetica-Bold',
                spaceAfter=12
            )
            
            factura_style = ParagraphStyle(
                'Factura',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.black,
                fontName='Helvetica',
                leftIndent=10
            )
            
            factura_bold_style = ParagraphStyle(
                'FacturaBold',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                leftIndent=10
            )
            
            # ENCABEZADO - Empresa y dirección
            empresa_nombre = Paragraph("ALIDA METAL E.I.R.L.", empresa_style)
            elements.append(empresa_nombre)
            
            if direccion_emisor:
                direccion_text = f"{direccion_emisor[0]} {direccion_emisor[1]}, {direccion_emisor[2]}, {direccion_emisor[3]}, {direccion_emisor[4]}"
                direccion_para = Paragraph(direccion_text.upper(), direccion_style)
                elements.append(direccion_para)
            
            # Título
            titulo = Paragraph("FACTURA ELECTRÓNICA", titulo_style)
            elements.append(titulo)
            
            # Información de la factura
            info_data = [
                [Paragraph(f"<b>RUC:</b> {factura[4]}", factura_style), 
                 Paragraph(f"<b>{factura[0]}</b>", factura_bold_style)],
                ["", Paragraph(f"<b>Fecha de Emisión:</b> {factura[1]}", factura_style)]
            ]
            
            info_table = Table(info_data, colWidths=[80*mm, 80*mm])
            info_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('PADDING', (0, 0), (-1, -1), 2),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 8))
            
            # Información del cliente
            cliente_data = [
                [Paragraph(f"<b>Señor(es):</b> {factura[8]}", factura_style)],
                [Paragraph(f"<b>RUC:</b> {factura[7]}", factura_style)],
                [Paragraph(f"<b>Tipo de Moneda:</b> {factura[3]}", factura_style)]
            ]
            
            # Mostrar Nota si existe
            if factura[14] and factura[14].strip():  # Campo nota
                cliente_data.append([Paragraph(f"<b>Nota/Observaciones:</b> {factura[14]}", factura_style)])
            
            cliente_table = Table(cliente_data, colWidths=[160*mm])
            cliente_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('PADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (0, -1), 10),
            ]))
            elements.append(cliente_table)
            elements.append(Spacer(1, 12))
            
            # TABLA DE ITEMS - SIN LÍNEAS NEGRAS
            items_header = ['Cantidad', 'Unidad Medida', 'Descripción', 'Valor Unitario', 'Desc. Unitario', 'Subtotal']
            items_data = [items_header]
            
            for item in items:
                cantidad = self.convertir_decimal(item[1])
                valor_unitario = self.convertir_decimal(item[3])
                descuento_unitario = self.convertir_decimal(item[4])
                subtotal = self.convertir_decimal(item[5])
                
                # Formatear valores monetarios
                moneda = "S/" if factura[3] == "PEN" else "$"
                
                row = [
                    f"{cantidad:.3f}",
                    str(item[2]) if item[2] else "",
                    str(item[0]) if item[0] else "",
                    f"{moneda}{valor_unitario:.2f}",
                    f"{moneda}{descuento_unitario:.2f}",
                    f"{moneda}{subtotal:+.2f}"  # Mostrar signo para valores negativos
                ]
                items_data.append(row)
            
            items_table = Table(items_data, colWidths=[20*mm, 25*mm, 65*mm, 25*mm, 25*mm, 25*mm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
                # LÍNEAS SUAVES EN LUGAR DE NEGRAS
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#dee2e6")),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#dee2e6")),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 15))
            
            # TOTAL EN LETRAS
            importe_total = self.convertir_decimal(factura[13])
            total_letras = self.numero_a_letras(abs(importe_total)) if importe_total >= 0 else f"MENOS {self.numero_a_letras(abs(importe_total))}"
            
            texto_letras = Paragraph(
                f"SON: {total_letras}", 
                ParagraphStyle(
                    'TotalLetras',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.black,
                    fontName='Helvetica-Bold',
                    alignment=0
                )
            )
            elements.append(texto_letras)
            elements.append(Spacer(1, 12))
            
            # CONVERTIR TODOS LOS VALORES
            subtotal = self.convertir_decimal(factura[9])
            descuento_total = self.convertir_decimal(factura[10])
            valor_venta = self.convertir_decimal(factura[11])
            igv = self.convertir_decimal(factura[12])
            descuento_global = self.convertir_decimal(factura[15])
            descuento_unitarios = descuento_total - descuento_global
            
            moneda = "S/" if factura[3] == "PEN" else "$"
            
            # RESUMEN DE TOTALES - FORMATEO CORRECTO
            totales_data = [
                [Paragraph(f"<b>Sub Total:</b>", factura_bold_style), Paragraph(f"{moneda}{subtotal:+.2f}", factura_style)],
                [Paragraph(f"<b>Descuentos:</b>", factura_bold_style), ""],
                [Paragraph(f"   - Descuentos Unitarios:", factura_style), Paragraph(f"{moneda}{descuento_unitarios:.2f}", factura_style)],
                [Paragraph(f"   - Descuento Global:", factura_style), Paragraph(f"{moneda}{descuento_global:.2f}", factura_style)],
                [Paragraph(f"<b>Total Descuentos:</b>", factura_bold_style), Paragraph(f"{moneda}{descuento_total:.2f}", factura_style)],
                [Paragraph(f"<b>Valor Venta:</b>", factura_bold_style), Paragraph(f"{moneda}{valor_venta:+.2f}", factura_style)],
                [Paragraph(f"<b>IGV (18%):</b>", factura_bold_style), Paragraph(f"{moneda}{igv:+.2f}", factura_style)],
                [Paragraph(f"<b>Importe Total:</b>", factura_bold_style), Paragraph(f"{moneda}{importe_total:+.2f}", factura_style)]
            ]
            
            totales_table = Table(totales_data, colWidths=[100*mm, 60*mm])
            totales_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('PADDING', (0, 0), (-1, -1), 3),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ]))
            elements.append(totales_table)
            
            # Pie de página
            elements.append(Spacer(1, 15))
            footer = Paragraph(
                f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} - Sistema ALIDA METAL",
                ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontSize=7,
                    textColor=colors.grey,
                    alignment=1
                )
            )
            elements.append(footer)
            
            doc.build(elements)
            
            messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear PDF: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def numero_a_letras(self, importe_total):
        try:
            importe_total = float(importe_total)
            
            entero = int(importe_total)
            decimales = int(round((importe_total - entero) * 100))
            
            # Listas para conversión
            unidades = ['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
            decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
            especiales = {
                11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE', 15: 'QUINCE',
                16: 'DIECISÉIS', 17: 'DIECISIETE', 18: 'DIECIOCHO', 19: 'DIECINUEVE'
            }
            
            if entero == 0:
                texto_entero = "CERO"
            elif entero < 10:
                texto_entero = unidades[entero]
            elif 10 <= entero < 20:
                texto_entero = especiales.get(entero, f"DIEZ Y {unidades[entero-10]}")
            elif entero < 100:
                decena = entero // 10
                unidad = entero % 10
                if unidad == 0:
                    texto_entero = decenas[decena]
                else:
                    texto_entero = f"{decenas[decena]} Y {unidades[unidad]}"
            else:
                # Para números mayores a 100, usar formato simple
                texto_entero = f"{entero}"
            
            return f"{texto_entero} CON {decimales:02d}/100 SOLES"
            
        except Exception as e:
            return f"{importe_total:.2f} SOLES"

    # ... (el resto de los métodos se mantienen igual)
    def generar_reporte_ventas(self):
        try:
            query = """
            SELECT f.serie_numero, f.fecha_emision, c.razon_social,
                   cf.importe_total, f.moneda, cf.descuento
            FROM factura f
            JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
            JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
            ORDER BY f.fecha_emision DESC
            """
            
            ventas = db.fetch_all(query)
            self.mostrar_reporte("Reporte de Ventas", ventas)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_clientes(self):
        try:
            query = """
            SELECT c.ruc_cliente, c.razon_social, 
                   COUNT(f.serie_numero) as total_facturas,
                   COALESCE(SUM(cf.importe_total), 0) as total_comprado,
                   COALESCE(SUM(cf.descuento), 0) as total_descuentos
            FROM cliente c
            LEFT JOIN factura f ON c.ruc_cliente = f.ruc_cliente
            LEFT JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
            GROUP BY c.ruc_cliente, c.razon_social
            ORDER BY total_comprado DESC
            """
            
            clientes = db.fetch_all(query)
            self.mostrar_reporte("Reporte de Clientes", clientes)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def mostrar_reporte(self, titulo, datos):
        ventana_reporte = tk.Toplevel(self.parent)
        ventana_reporte.title(titulo)
        ventana_reporte.geometry("900x600")
        ventana_reporte.configure(bg=self.bg_color)
        
        main_frame = tk.Frame(ventana_reporte, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, 
                text=titulo, 
                font=("Arial", 16, "bold"),
                bg=self.bg_color,
                fg=self.primary_color).pack(pady=10)
        
        if datos and len(datos) > 0:
            if "Ventas" in titulo:
                columns = ["Serie-Número", "Fecha", "Cliente", "Total", "Moneda", "Descuentos"]
            elif "Clientes" in titulo:
                columns = ["RUC", "Razón Social", "Total Facturas", "Total Comprado", "Total Descuentos"]
            elif "Productos" in titulo:
                columns = ["Producto", "Cantidad Vendida", "Total Ingresos"]
            elif "Diario" in titulo:
                if datos[-1][0] == "TOTAL DEL DÍA":
                    columns = ["Concepto", "Cliente", "Total", "Descuentos"]
                else:
                    columns = ["Serie-Número", "Cliente", "Total", "Descuento"]
            elif "Descuentos" in titulo:
                columns = ["Serie-Número", "Fecha", "Cliente", "Subtotal", "Descuento", "Total"]
            else:
                columns = [str(i) for i in range(len(datos[0]))]
            
            tabla = TableWidget(main_frame, columns)
            tabla.update_data(datos)
        else:
            tk.Label(main_frame, 
                    text="No hay datos para mostrar", 
                    font=("Arial", 12),
                    bg=self.bg_color,
                    fg=self.text_color).pack(pady=20)
    
    def generar_reporte_productos(self):
        try:
            query = """
            SELECT df.descripcion_item, 
                   SUM(df.cantidad) as total_vendido,
                   SUM(df.subtotal_item) as total_ingresos
            FROM detallefactura df
            GROUP BY df.descripcion_item
            ORDER BY total_ingresos DESC
            LIMIT 10
            """
            
            productos = db.fetch_all(query)
            self.mostrar_reporte("Productos Más Vendidos", productos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_diario(self):
        try:
            from datetime import datetime
            fecha_hoy = datetime.now().date()
            
            query = """
            SELECT f.serie_numero, c.razon_social, cf.importe_total, cf.descuento
            FROM factura f
            JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
            JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
            WHERE f.fecha_emision = %s
            ORDER BY f.serie_numero
            """
            
            ventas_hoy = db.fetch_all(query, [fecha_hoy])
            
            if ventas_hoy:
                total_dia = sum(self.convertir_decimal(venta[2]) for venta in ventas_hoy)
                total_descuentos = sum(self.convertir_decimal(venta[3]) for venta in ventas_hoy)
                datos_con_total = ventas_hoy + [("TOTAL DEL DÍA", "", total_dia, total_descuentos)]
                self.mostrar_reporte(f"Reporte Diario - {fecha_hoy}", datos_con_total)
            else:
                messagebox.showinfo("Reporte Diario", f"No hay ventas para la fecha {fecha_hoy}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte diario: {str(e)}")
    
    def generar_reporte_descuentos(self):
        try:
            query = """
            SELECT f.serie_numero, f.fecha_emision, c.razon_social,
                   cf.subtotal, cf.descuento, cf.importe_total
            FROM factura f
            JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
            JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
            WHERE cf.descuento > 0
            ORDER BY cf.descuento DESC
            """
            
            facturas_con_descuento = db.fetch_all(query)
            
            if facturas_con_descuento:
                self.mostrar_reporte("Reporte de Facturas con Descuento", facturas_con_descuento)
            else:
                messagebox.showinfo("Reporte de Descuentos", "No hay facturas con descuentos aplicados")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de descuentos: {str(e)}")