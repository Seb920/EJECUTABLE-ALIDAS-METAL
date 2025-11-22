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

class ReportesGUI:
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña Consultar Factura
        tab_consultar = ttk.Frame(notebook)
        notebook.add(tab_consultar, text="Consultar Factura")
        self.create_consulta_tab(tab_consultar)
        
        # Pestaña Reportes
        tab_reportes = ttk.Frame(notebook)
        notebook.add(tab_reportes, text="Reportes")
        self.create_reportes_tab(tab_reportes)
    
    def create_consulta_tab(self, parent):
        # Frame principal usando grid
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configurar grid weights
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(main_frame, text="CONSULTAR FACTURA", 
                font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Búsqueda
        tk.Label(main_frame, text="Buscar Factura:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_busqueda = tk.Entry(main_frame, width=30)
        self.entry_busqueda.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_facturas)
        
        btn_buscar = tk.Button(main_frame, text="Buscar", command=self.buscar_facturas,
                              bg="#3498db", fg="white")
        btn_buscar.grid(row=1, column=2, padx=5, pady=5)
        
        # Botón generar PDF
        btn_pdf = tk.Button(main_frame, text="Generar PDF", 
                           command=self.generar_pdf_factura,
                           bg="#e74c3c", fg="white")
        btn_pdf.grid(row=1, column=3, padx=5, pady=5)
        
        # Resultados
        columns = ["Serie-Número", "Fecha", "Cliente", "Total", "Moneda"]
        self.table_resultados = TableWidget(main_frame, columns, 
                                          grid_options={
                                              'row': 2, 
                                              'column': 0, 
                                              'columnspan': 4,
                                              'sticky': 'nsew',
                                              'padx': 10, 
                                              'pady': 10
                                          })
    
    def create_reportes_tab(self, parent):
        main_frame = tk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="GENERAR REPORTES", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        # Frame para botones de reportes
        frame_botones = tk.Frame(main_frame)
        frame_botones.pack(expand=True)
        
        # Botones de reportes
        btn_ventas = tk.Button(frame_botones, text="Reporte de Ventas", 
                              command=self.generar_reporte_ventas,
                              bg="#2E86AB", fg="white", width=20, height=2)
        btn_ventas.grid(row=0, column=0, padx=10, pady=10)
        
        btn_clientes = tk.Button(frame_botones, text="Reporte de Clientes", 
                                command=self.generar_reporte_clientes,
                                bg="#3498db", fg="white", width=20, height=2)
        btn_clientes.grid(row=0, column=1, padx=10, pady=10)
        
        btn_productos = tk.Button(frame_botones, text="Productos Más Vendidos", 
                                 command=self.generar_reporte_productos,
                                 bg="#f39c12", fg="white", width=20, height=2)
        btn_productos.grid(row=1, column=0, padx=10, pady=10)
        
        btn_diario = tk.Button(frame_botones, text="Reporte Diario", 
                              command=self.generar_reporte_diario,
                              bg="#27ae60", fg="white", width=20, height=2)
        btn_diario.grid(row=1, column=1, padx=10, pady=10)
    
    def buscar_facturas(self, event=None):
        try:
            criterio = self.entry_busqueda.get()
            
            if not criterio:
                self.table_resultados.update_data([])
                return
            
            query = """
            SELECT f.serie_numero, f.fecha_emision, c.razon_social, 
                   cf.importe_total, f.moneda
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
            
            # Obtener datos completos de la factura
            factura = db.fetch_one("""
                SELECT f.serie_numero, f.fecha_emision, f.forma_pago, f.moneda,
                       e.ruc_empresa, e.razon_social as emisor_razon, e.nombre_empresa,
                       c.ruc_cliente, c.razon_social as cliente_razon,
                       cf.subtotal, cf.igv, cf.importe_total
                FROM factura f
                JOIN emisor e ON f.ruc_empresa = e.ruc_empresa
                JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
                JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
                WHERE f.serie_numero = %s
            """, [serie_numero])
            
            if not factura:
                messagebox.showerror("Error", "No se pudieron cargar los datos de la factura")
                return
            
            # Obtener items de la factura
            items = db.fetch_all("""
                SELECT descripcion_item, cantidad, unidad_medida, valor_unitario, subtotal_item
                FROM detallefactura
                WHERE serie_numero = %s
                ORDER BY id_detalle
            """, [serie_numero])
            
            # Obtener dirección del emisor
            direccion_emisor = db.fetch_one("""
                SELECT calle, numero, distrito, provincia, departamento
                FROM direccion_e WHERE ruc_empresa = %s LIMIT 1
            """, [factura[4]])
            
            # Generar PDF
            self.crear_pdf_factura(factura, items, direccion_emisor)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")
    
    def crear_pdf_factura(self, factura, items, direccion_emisor):
        try:
            # Crear nombre del archivo
            filename = f"Factura_{factura[0]}.pdf"
            filepath = os.path.join(os.getcwd(), filename)
            
            # Crear documento PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Estilo para el título principal
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Normal'],
                fontSize=16,
                textColor=colors.black,
                spaceAfter=15,
                alignment=1,
                fontName='Helvetica-Bold'
            )
            
            # Estilo para encabezados de sección
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )
            
            # Estilo normal
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                fontName='Helvetica'
            )
            
            # Estilo para información de la empresa
            empresa_style = ParagraphStyle(
                'Empresa',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                alignment=1
            )
            
            # Estilo para datos de la factura
            factura_style = ParagraphStyle(
                'Factura',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                fontName='Helvetica'
            )
            
            # ===== ENCABEZADO =====
            
            # Nombre de la empresa (ALIDA METAL E.I.R.L.)
            empresa_nombre = Paragraph("ALIDA METAL E.I.R.L.", empresa_style)
            elements.append(empresa_nombre)
            elements.append(Spacer(1, 4*mm))
            
            # Dirección del emisor (centrado)
            if direccion_emisor:
                direccion_text = f"{direccion_emisor[0]} {direccion_emisor[1]}, {direccion_emisor[2]}, {direccion_emisor[3]}, {direccion_emisor[4]}"
                direccion_para = Paragraph(direccion_text, normal_style)
                elements.append(direccion_para)
            
            elements.append(Spacer(1, 8*mm))
            
            # Título FACTURA ELECTRÓNICA
            titulo = Paragraph("FACTURA ELECTRÓNICA", title_style)
            elements.append(titulo)
            elements.append(Spacer(1, 10*mm))
            
            # ===== INFORMACIÓN DE LA FACTURA =====
            
            # Información RUC y Serie
            info_data = [
                [Paragraph(f"<b>RUC:</b> {factura[4]}", factura_style), 
                 Paragraph(f"<b>Serie:</b> {factura[0]}", factura_style)],
                [Paragraph(f"<b>Fecha de Emisión:</b> {factura[1]}", factura_style), ""]
            ]
            
            info_table = Table(info_data, colWidths=[90*mm, 80*mm])
            info_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 8*mm))
            
            # ===== INFORMACIÓN DEL CLIENTE =====
            
            # Señor(es)
            cliente_header = Paragraph(f"<b>Señor(es):</b> {factura[8]}", header_style)
            elements.append(cliente_header)
            
            # RUC del cliente
            cliente_ruc = Paragraph(f"<b>RUC:</b> {factura[7]}", factura_style)
            elements.append(cliente_ruc)
            
            # Moneda
            cliente_moneda = Paragraph(f"<b>Tipo de Moneda:</b> {factura[3]}", factura_style)
            elements.append(cliente_moneda)
            
            elements.append(Spacer(1, 8*mm))
            
            # ===== TABLA DE ITEMS =====
            
            # Encabezado de la tabla
            items_header = ['Cantidad', 'Unidad Medida', 'Descripción', 'Valor Unitario', 'Subtotal']
            items_data = [items_header]
            
            for item in items:
                row = [
                    f"{float(item[1]):.3f}",  # cantidad
                    item[2],  # unidad
                    item[0],  # descripción
                    f"S/ {float(item[3]):.2f}",  # valor unitario
                    f"S/ {float(item[4]):.2f}"   # subtotal
                ]
                items_data.append(row)
            
            items_table = Table(items_data, colWidths=[20*mm, 25*mm, 75*mm, 30*mm, 30*mm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 10*mm))
            
            # ===== TOTAL EN LETRAS =====
            
            # Importe total en letras
            total_letras = self.numero_a_letras(factura[11])
            texto_letras = Paragraph(f"<b>SON:</b> {total_letras}", header_style)
            elements.append(texto_letras)
            elements.append(Spacer(1, 6*mm))
            
            # ===== RESUMEN DE TOTALES =====
            
            totales_data = [
                [Paragraph(f"Sub Total: S/ {factura[9]:.2f}", factura_style), ""],
                [Paragraph("Descuentos: S/ 0.00", factura_style), ""],
                [Paragraph(f"Valor Venta: S/ {factura[9]:.2f}", factura_style), ""],
                [Paragraph(f"IGV (18%): S/ {factura[10]:.2f}", factura_style), ""],
                [Paragraph(f"<b>Importe Total: S/ {factura[11]:.2f}</b>", header_style), ""]
            ]
            
            totales_table = Table(totales_data, colWidths=[100*mm, 70*mm])
            totales_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -2), 10),
                ('FONTSIZE', (0, 4), (0, 4), 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 4), (0, 4), 8),
                ('BOTTOMPADDING', (0, 4), (0, 4), 8),
            ]))
            elements.append(totales_table)
            
            # Pie de página
            elements.append(Spacer(1, 15*mm))
            footer = Paragraph(
                f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} - Sistema ALIDA METAL",
                ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=1
                )
            )
            elements.append(footer)
            
            # Generar PDF
            doc.build(elements)
            
            messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear PDF: {str(e)}")
    
    def numero_a_letras(self, importe_total):
        """
        Convierte el importe total a letras (versión simplificada)
        """
        try:
            # Separar parte entera y decimal
            entero = int(importe_total)
            decimal = int(round((importe_total - entero) * 100))
            
            # Diccionarios para conversión
            unidades = ['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
            decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 
                      'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
            especiales = {
                11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE', 15: 'QUINCE',
                16: 'DIECISÉIS', 17: 'DIECISIETE', 18: 'DIECIOCHO', 19: 'DIECINUEVE'
            }
            
            if entero == 0:
                texto_entero = "CERO"
            elif entero < 10:
                texto_entero = unidades[entero]
            elif entero in especiales:
                texto_entero = especiales[entero]
            elif entero < 30:
                if entero == 20:
                    texto_entero = "VEINTE"
                else:
                    texto_entero = "VEINTI" + unidades[entero - 20]
            elif entero < 100:
                decena = entero // 10
                unidad = entero % 10
                if unidad == 0:
                    texto_entero = decenas[decena]
                else:
                    texto_entero = f"{decenas[decena]} Y {unidades[unidad]}"
            else:
                # Para números mayores a 99, usar una representación numérica
                texto_entero = f"{entero}"
            
            return f"{texto_entero} Y {decimal:02d}/100 SOLES"
            
        except Exception as e:
            return f"{importe_total:.2f} SOLES"
    
    def generar_reporte_ventas(self):
        try:
            query = """
            SELECT f.serie_numero, f.fecha_emision, c.razon_social,
                   cf.importe_total, f.moneda
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
                   COALESCE(SUM(cf.importe_total), 0) as total_comprado
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
        
        # Frame principal
        main_frame = tk.Frame(ventana_reporte)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=("Arial", 16, "bold")).pack(pady=10)
        
        # Tabla de resultados
        if datos and len(datos) > 0:
            # Definir encabezados según el tipo de reporte
            if "Ventas" in titulo:
                columns = ["Serie-Número", "Fecha", "Cliente", "Total", "Moneda"]
            elif "Clientes" in titulo:
                columns = ["RUC", "Razón Social", "Total Facturas", "Total Comprado"]
            elif "Productos" in titulo:
                columns = ["Producto", "Cantidad Vendida", "Total Ingresos"]
            elif "Diario" in titulo:
                # Verificar si es el último row que es el total
                if datos[-1][0] == "TOTAL DEL DÍA":
                    columns = ["Concepto", "Cliente", "Total"]
                else:
                    columns = ["Serie-Número", "Cliente", "Total"]
            else:
                # Por defecto, usar números de columna
                columns = [str(i) for i in range(len(datos[0]))]
            
            tabla = TableWidget(main_frame, columns)
            tabla.update_data(datos)
        else:
            tk.Label(main_frame, text="No hay datos para mostrar", 
                    font=("Arial", 12)).pack(pady=20)
    
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
            SELECT f.serie_numero, c.razon_social, cf.importe_total
            FROM factura f
            JOIN cliente c ON f.ruc_cliente = c.ruc_cliente
            JOIN calculosfactura cf ON f.serie_numero = cf.serie_numero
            WHERE f.fecha_emision = %s
            ORDER BY f.serie_numero
            """
            
            ventas_hoy = db.fetch_all(query, [fecha_hoy])
            
            if ventas_hoy:
                total_dia = sum(venta[2] for venta in ventas_hoy)
                datos_con_total = ventas_hoy + [("TOTAL DEL DÍA", "", total_dia)]
                self.mostrar_reporte(f"Reporte Diario - {fecha_hoy}", datos_con_total)
            else:
                messagebox.showinfo("Reporte Diario", f"No hay ventas para la fecha {fecha_hoy}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte diario: {str(e)}")