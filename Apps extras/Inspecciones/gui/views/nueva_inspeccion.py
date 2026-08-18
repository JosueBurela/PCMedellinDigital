import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
import database as db
import pdf_generator as pdfgen

class NuevaInspeccionView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Scrollable container principal
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header de la Sección
        self.title = ctk.CTkLabel(
            self.scroll_frame,
            text="➕ Registrar Nueva Orden de Inspección",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        self.title.pack(fill="x", pady=(0, 15))

        # Card de Datos de la Orden (Header Metadata)
        self.card_header = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.card_header.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        lbl_header = ctk.CTkLabel(
            self.card_header,
            text="Datos Generales del Formato",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_header.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(5, 10))

        # Campo: Fecha Corta YYYY-MM-DD
        ctk.CTkLabel(self.card_header, text="Fecha (AAAA-MM-DD):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_fecha_corta = ctk.CTkEntry(self.card_header, placeholder_text="2026-08-06")
        self.entry_fecha_corta.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.entry_fecha_corta.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Campo: Fecha Formato Texto (ej. JUEVES 06/AGOSTO/26)
        ctk.CTkLabel(self.card_header, text="Fecha Formato Texto:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=2, sticky="w", padx=10, pady=5)
        self.entry_fecha_texto = ctk.CTkEntry(self.card_header, placeholder_text="JUEVES 06/AGOSTO/26")
        self.entry_fecha_texto.insert(0, "JUEVES 06/AGOSTO/26")
        self.entry_fecha_texto.grid(row=1, column=3, sticky="ew", padx=10, pady=5)

        # Campo: Horario
        ctk.CTkLabel(self.card_header, text="Horario:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_horario = ctk.CTkEntry(self.card_header, placeholder_text="De 10am A 2pm")
        self.entry_horario.insert(0, "De 10am A 2pm")
        self.entry_horario.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Campo: Inspector
        ctk.CTkLabel(self.card_header, text="Inspector(a):", font=ctk.CTkFont(weight="bold")).grid(row=2, column=2, sticky="w", padx=10, pady=5)
        self.entry_inspector = ctk.CTkEntry(self.card_header, placeholder_text="Nombre del inspector")
        self.entry_inspector.insert(0, "Larisa Pauleth Gonzalez Acosta")
        self.entry_inspector.grid(row=2, column=3, sticky="ew", padx=10, pady=5)

        # Campo: Operador
        ctk.CTkLabel(self.card_header, text="Operador:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entry_operador = ctk.CTkEntry(self.card_header, placeholder_text="Nombre del operador")
        self.entry_operador.insert(0, "ALBERTO VIQUEZ Ó CARLOS ALBERTO")
        self.entry_operador.grid(row=3, column=1, columnspan=3, sticky="ew", padx=10, pady=5)

        # Campo: Rutas Resumen
        ctk.CTkLabel(self.card_header, text="Rutas Resumen:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.entry_rutas = ctk.CTkEntry(self.card_header, placeholder_text="Rutas separadas por guion")
        self.entry_rutas.insert(0, "TEJAR-P.TORO-P.CHOCOLT-LOMAS S.GABRIEL- LA BASCULA-PTE MORENO-LAS PALMAS-LA BOCANA-SAN RAMON")
        self.entry_rutas.grid(row=4, column=1, columnspan=3, sticky="ew", padx=10, pady=5)

        self.card_header.columnconfigure((1, 3), weight=1)

        # Seccion de Tabla de Establecimientos a Realizar
        self.card_items = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.card_items.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        items_top_bar = ctk.CTkFrame(self.card_items, fg_color="transparent")
        items_top_bar.pack(fill="x", padx=10, pady=(10, 15))

        lbl_items_title = ctk.CTkLabel(
            items_top_bar,
            text="INSPECCIONES A REALIZAR",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_items_title.pack(side="left")

        btn_cargar_ejemplo = ctk.CTkButton(
            items_top_bar,
            text="📋 Cargar Datos Ejemplo",
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.cargar_datos_ejemplo
        )
        btn_cargar_ejemplo.pack(side="right", padx=(10, 0))

        btn_add_row = ctk.CTkButton(
            items_top_bar,
            text="➕ Agregar Fila",
            fg_color="#10B981",
            hover_color="#059669",
            command=self.agregar_fila
        )
        btn_add_row.pack(side="right")

        # Table Header Frame
        self.tbl_header_frame = ctk.CTkFrame(self.card_items, fg_color="#1E293B", corner_radius=5)
        self.tbl_header_frame.pack(fill="x", padx=10, pady=(0, 5))

        cols = [("Nº", 40), ("RUTA", 140), ("ESTABLECIMIENTO", 260), ("MES DE PAGO", 120), ("ACCIONES", 80)]
        for text, width in cols:
            lbl = ctk.CTkLabel(
                self.tbl_header_frame,
                text=text,
                font=ctk.CTkFont(weight="bold", size=12),
                width=width,
                anchor="center" if width <= 80 else "w"
            )
            lbl.pack(side="left", padx=5, pady=5)

        # Rows Container
        self.rows_container = ctk.CTkFrame(self.card_items, fg_color="transparent")
        self.rows_container.pack(fill="x", padx=10)

        self.rows = []

        # Botón de Guardado e Imprimir
        action_bar = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        action_bar.pack(fill="x", pady=10)

        btn_limpiar = ctk.CTkButton(
            action_bar,
            text="🗑️ Limpiar Todo",
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.limpiar_formulario
        )
        btn_limpiar.pack(side="left")

        btn_guardar = ctk.CTkButton(
            action_bar,
            text="💾 Guardar y Generar PDF/LaTeX",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=40,
            command=self.guardar_e_imprimir
        )
        btn_guardar.pack(side="right")

        # Cargar una fila por defecto
        self.agregar_fila()

    def agregar_fila(self, ruta="", establecimiento="", mes_pago=""):
        num = len(self.rows) + 1
        row_frame = ctk.CTkFrame(self.rows_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=3)

        lbl_num = ctk.CTkLabel(row_frame, text=str(num), width=40, font=ctk.CTkFont(weight="bold"))
        lbl_num.pack(side="left", padx=5)

        entry_ruta = ctk.CTkEntry(row_frame, placeholder_text="Ruta (ej. TEJAR)", width=140)
        entry_ruta.insert(0, ruta)
        entry_ruta.pack(side="left", padx=5)

        entry_est = ctk.CTkEntry(row_frame, placeholder_text="Establecimiento", width=260)
        entry_est.insert(0, establecimiento)
        entry_est.pack(side="left", padx=5)

        entry_mes = ctk.CTkEntry(row_frame, placeholder_text="Mes de Pago", width=120)
        entry_mes.insert(0, mes_pago)
        entry_mes.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(
            row_frame,
            text="❌",
            width=40,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            command=lambda r=row_frame: self.eliminar_fila(r)
        )
        btn_del.pack(side="left", padx=5)

        self.rows.append({
            "frame": row_frame,
            "lbl_num": lbl_num,
            "ruta": entry_ruta,
            "est": entry_est,
            "mes": entry_mes
        })
        self.renumerar_filas()

    def eliminar_fila(self, row_frame):
        self.rows = [r for r in self.rows if r["frame"] != row_frame]
        row_frame.destroy()
        self.renumerar_filas()

    def renumerar_filas(self):
        for idx, r in enumerate(self.rows, start=1):
            r["lbl_num"].configure(text=str(idx))

    def cargar_datos_ejemplo(self):
        self.limpiar_filas()
        ejemplos = [
            ("TEJAR", "GASOLINERA EL TEJAR", "ENERO"),
            ("TEJAR", "DEPOSITO LA VENTANITA II", "ENERO"),
            ("TEJAR", "TORTILLERIA AQUIAHUAC", "MAYO"),
            ("TEJAR", "ANTOJITOS VIKY", "MAYO"),
            ("TEJAR", "TOP VENT", "MAYO"),
            ("TEJAR", "SAND BLAST", "ABRIL"),
            ("P. DEL TORO", "RESTAURAN FELISITAS", "MARZO"),
            ("P. DEL TORO", "SONIGAS", "MARZO"),
            ("P. CHOCOLATE", "ABARROTES LA UNICA", "ENERO"),
            ("LOMAS SAN GABRIEL", "MADERAS Y TRIPLAY MEDELLIN", "ABRIL"),
            ("LA BASCULA", "ANTOJITOS EL PUNTALITO", "ABRIL"),
            ("PUENTE MORENO", "ABARROTES EL GÜERO", "FEBRERO"),
            ("FRACC LAS PALMAS", "ALPROQUIMEX", "FEBRERO"),
            ("LA BOCANA", "TRANSPORTES VICTOR", "ABRIL"),
            ("SAN RAMON", "TAQUERIA LA UNICA", "MARZO")
        ]
        for ruta, est, mes in ejemplos:
            self.agregar_fila(ruta, est, mes)

    def limpiar_filas(self):
        for r in self.rows:
            r["frame"].destroy()
        self.rows.clear()

    def limpiar_formulario(self):
        self.limpiar_filas()
        self.agregar_fila()

    def guardar_e_imprimir(self):
        fecha_corta = self.entry_fecha_corta.get().strip()
        fecha_texto = self.entry_fecha_texto.get().strip()
        horario = self.entry_horario.get().strip()
        inspector = self.entry_inspector.get().strip()
        operador = self.entry_operador.get().strip()
        rutas = self.entry_rutas.get().strip()

        if not fecha_corta or not inspector or not rutas:
            messagebox.showwarning("Campos Requeridos", "Por favor complete la fecha, inspector y rutas resumen.")
            return

        items = []
        for r in self.rows:
            ruta_val = r["ruta"].get().strip()
            est_val = r["est"].get().strip()
            mes_val = r["mes"].get().strip()
            if ruta_val or est_val:
                items.append({
                    "ruta": ruta_val,
                    "establecimiento": est_val,
                    "mes_pago": mes_val,
                    "realizado": "",
                    "pendiente": ""
                })

        if not items:
            messagebox.showwarning("Sin ítems", "Agregue al menos un establecimiento a la inspección.")
            return

        # Guardar en SQLite
        inspeccion_id = db.guardar_inspeccion(
            fecha_corta=fecha_corta,
            fecha_texto=fecha_texto,
            horario=horario,
            rutas_resumen=rutas,
            inspector=inspector,
            operador=operador,
            items=items
        )

        orden_data = db.obtener_inspeccion(inspeccion_id)

        # Generar PDF y LaTeX
        res = pdfgen.exportar_orden_completa(orden_data)

        messagebox.showinfo(
            "Éxito",
            f"¡Orden de Inspección Guardada!\n\n Archivos generados en carpeta output:\n PDF: {os.path.basename(res['pdf'])}\n LaTeX: {os.path.basename(res['tex'])}"
        )

        # Notificar a la vista de gestión
        if hasattr(self.controller, "actualizar_vistas"):
            self.controller.actualizar_vistas()
