import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
import os
import database as db
import pdf_generator as pdfgen

class ReportesView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header Title
        lbl_title = ctk.CTkLabel(
            self.scroll_frame,
            text="📊 Exportación de Inspecciones y Reportes por Periodo",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        lbl_title.pack(fill="x", pady=(0, 15))

        # Panel de Filtros Temporales
        self.filter_card = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.filter_card.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        lbl_filter_title = ctk.CTkLabel(
            self.filter_card,
            text="Seleccionar Periodo de Inspecciones",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_filter_title.pack(anchor="w", padx=10, pady=(5, 10))

        # Botones de Filtro Rápido
        btn_bar = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=10, pady=(0, 10))

        self.filtro_actual = "todas"

        self.btn_hoy = ctk.CTkButton(btn_bar, text="📅 Hoy", width=100, command=lambda: self.set_filtro("hoy"))
        self.btn_hoy.pack(side="left", padx=5)

        self.btn_semana = ctk.CTkButton(btn_bar, text="📆 Esta Semana", width=110, command=lambda: self.set_filtro("semana"))
        self.btn_semana.pack(side="left", padx=5)

        self.btn_mes = ctk.CTkButton(btn_bar, text="🗓️ Este Mes", width=100, command=lambda: self.set_filtro("mes"))
        self.btn_mes.pack(side="left", padx=5)

        self.btn_bimestre = ctk.CTkButton(btn_bar, text="📊 Bimestre", width=100, command=lambda: self.set_filtro("bimestre"))
        self.btn_bimestre.pack(side="left", padx=5)

        self.btn_todas = ctk.CTkButton(btn_bar, text="📂 Todas", width=90, command=lambda: self.set_filtro("todas"))
        self.btn_todas.pack(side="left", padx=5)

        # Rango Específico de Fechas
        rango_bar = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        rango_bar.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(rango_bar, text="De Fecha (AAAA-MM-DD):", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 5))
        self.entry_inicio = ctk.CTkEntry(rango_bar, placeholder_text="2026-08-01", width=120)
        self.entry_inicio.pack(side="left", padx=5)

        ctk.CTkLabel(rango_bar, text="A Fecha (AAAA-MM-DD):", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(15, 5))
        self.entry_fin = ctk.CTkEntry(rango_bar, placeholder_text="2026-08-31", width=120)
        self.entry_fin.pack(side="left", padx=5)

        btn_filtrar_rango = ctk.CTkButton(
            rango_bar,
            text="🔍 Filtrar Rango Específico",
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=lambda: self.set_filtro("rango")
        )
        btn_filtrar_rango.pack(side="left", padx=(15, 0))

        # Card de Selección y Resultados
        self.results_card = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.results_card.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        self.lbl_results_count = ctk.CTkLabel(
            self.results_card,
            text="Resultados de la búsqueda: 0 órdenes encontradas",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.lbl_results_count.pack(anchor="w", padx=10, pady=(5, 10))

        # Checklist Scroll Area
        self.check_scroll = ctk.CTkScrollableFrame(self.results_card, fg_color="#1E293B", height=250)
        self.check_scroll.pack(fill="x", padx=10, pady=(0, 10))

        self.items_checklist = []

        # Acciones de Exportación
        export_bar = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        export_bar.pack(fill="x", pady=10)

        btn_select_all = ctk.CTkButton(
            export_bar,
            text="☑️ Seleccionar Todos",
            width=140,
            fg_color="#475569",
            command=self.seleccionar_todos
        )
        btn_select_all.pack(side="left", padx=(0, 10))

        btn_deselect_all = ctk.CTkButton(
            export_bar,
            text="☐ Desmarcar Todos",
            width=140,
            fg_color="#475569",
            command=self.desmarcar_todos
        )
        btn_deselect_all.pack(side="left")

        btn_export_batch = ctk.CTkButton(
            export_bar,
            text="📄 Generar PDFs y LaTeX Seleccionados",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=40,
            command=self.exportar_seleccionados
        )
        btn_export_batch.pack(side="right")

        # Cargar filtro por defecto
        self.set_filtro("todas")

    def set_filtro(self, tipo):
        self.filtro_actual = tipo
        fecha_in = self.entry_inicio.get().strip() if tipo == "rango" else None
        fecha_fi = self.entry_fin.get().strip() if tipo == "rango" else None

        ordenes = db.listar_inspecciones_por_filtro(tipo, fecha_in, fecha_fi)

        for child in self.check_scroll.winfo_children():
            child.destroy()

        self.items_checklist.clear()

        textos_filtro = {
            "todas": "Todas las órdenes",
            "hoy": "Órdenes del día de hoy",
            "semana": "Órdenes de esta semana",
            "mes": "Órdenes de este mes",
            "bimestre": "Órdenes del bimestre (últimos 60 días)",
            "rango": f"Órdenes del {fecha_in} al {fecha_fi}"
        }

        self.lbl_results_count.configure(
            text=f"Filtrado por: {textos_filtro.get(tipo, 'Filtro')} ({len(ordenes)} orden(es) encontrada(s))"
        )

        for ord_data in ordenes:
            o = ord_data["orden"]
            item_cnt = len(ord_data["items"])
            chk_var = ctk.BooleanVar(value=True)

            txt = f"ID #{o['id']} | Fecha: {o['fecha_texto']} | Inspector: {o['inspector']} | Rutas: {o['rutas_resumen']} ({item_cnt} establecimientos)"
            chk = ctk.CTkCheckBox(
                self.check_scroll,
                text=txt,
                variable=chk_var,
                font=ctk.CTkFont(size=12)
            )
            chk.pack(fill="x", padx=10, pady=5, anchor="w")

            self.items_checklist.append({
                "var": chk_var,
                "data": ord_data
            })

    def seleccionar_todos(self):
        for item in self.items_checklist:
            item["var"].set(True)

    def desmarcar_todos(self):
        for item in self.items_checklist:
            item["var"].set(False)

    def exportar_seleccionados(self):
        seleccionados = [it["data"] for it in self.items_checklist if it["var"].get()]

        if not seleccionados:
            messagebox.showwarning("Sin Selección", "Seleccione al menos una orden para exportar.")
            return

        archivos_generados = []
        for ord_data in seleccionados:
            res = pdfgen.exportar_orden_completa(ord_data)
            archivos_generados.append(res)

        out_dir = pdfgen.ensure_output_dir()

        messagebox.showinfo(
            "Exportación Completada",
            f"Se exportaron con éxito {len(archivos_generados)} reporte(s) en PDF y LaTeX.\n\nUbicación de guardado:\n{out_dir}"
        )
