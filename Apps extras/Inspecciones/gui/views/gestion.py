import customtkinter as ctk
from tkinter import messagebox
import os
import database as db
import pdf_generator as pdfgen

class GestionView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Main layout: Split into Left list panel and Right detail panel
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left Panel (Lista de Ordenes)
        self.left_panel = ctk.CTkFrame(self, corner_radius=10)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(15, 7), pady=15)

        lbl_list_title = ctk.CTkLabel(
            self.left_panel,
            text="📋 Historial de Inspecciones",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_list_title.pack(fill="x", padx=15, pady=(15, 10))

        # Buscador
        self.entry_search = ctk.CTkEntry(self.left_panel, placeholder_text="🔍 Buscar por inspector, ruta o fecha...")
        self.entry_search.pack(fill="x", padx=15, pady=(0, 10))
        self.entry_search.bind("<KeyRelease>", self.filtrar_lista)

        # Lista Scrollable
        self.orders_scroll = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.orders_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Right Panel (Detalle y Marcar Estatus)
        self.right_panel = ctk.CTkFrame(self, corner_radius=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(7, 15), pady=15)

        self.lbl_detail_title = ctk.CTkLabel(
            self.right_panel,
            text="Seleccione una inspección de la lista",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.lbl_detail_title.pack(fill="x", padx=15, pady=(15, 10))

        self.detail_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.detail_scroll.pack(fill="both", expand=True, padx=15, pady=10)

        # Bottom Actions Bar for Selected Order
        self.detail_actions = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.detail_actions.pack(fill="x", padx=15, pady=(0, 15))

        self.btn_reimprimir = ctk.CTkButton(
            self.detail_actions,
            text="📄 Exportar PDF / LaTeX",
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.reimprimir_seleccionada,
            state="disabled"
        )
        self.btn_reimprimir.pack(side="left", padx=(0, 10))

        self.btn_guardar_cambios = ctk.CTkButton(
            self.detail_actions,
            text="💾 Guardar Cambios Estatus",
            fg_color="#10B981",
            hover_color="#059669",
            command=self.guardar_estatus,
            state="disabled"
        )
        self.btn_guardar_cambios.pack(side="left")

        self.btn_eliminar = ctk.CTkButton(
            self.detail_actions,
            text="🗑️ Eliminar",
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.eliminar_orden,
            state="disabled"
        )
        self.btn_eliminar.pack(side="right")

        self.orden_actual = None
        self.item_entries = []

        self.cargar_ordenes()

    def cargar_ordenes(self):
        for child in self.orders_scroll.winfo_children():
            child.destroy()

        ordenes = db.listar_inspecciones_por_filtro("todas")
        filtro = self.entry_search.get().lower().strip() if hasattr(self, 'entry_search') else ""

        for ord_data in ordenes:
            o = ord_data["orden"]
            text_match = (
                filtro in o["fecha_corta"].lower() or
                filtro in o["inspector"].lower() or
                filtro in o["rutas_resumen"].lower()
            )
            if filtro and not text_match:
                continue

            card = ctk.CTkFrame(self.orders_scroll, corner_radius=6, fg_color="#1E293B" if self.orden_actual and self.orden_actual["orden"]["id"] == o["id"] else "#334155")
            card.pack(fill="x", pady=4, padx=2)

            lbl_f = ctk.CTkLabel(card, text=f"📅 {o['fecha_texto']}", font=ctk.CTkFont(weight="bold", size=13), anchor="w")
            lbl_f.pack(fill="x", padx=10, pady=(6, 2))

            lbl_i = ctk.CTkLabel(card, text=f"👤 Inspector: {o['inspector']}", font=ctk.CTkFont(size=11), anchor="w")
            lbl_i.pack(fill="x", padx=10, pady=(0, 2))

            lbl_r = ctk.CTkLabel(
                card,
                text=f"📍 {o['rutas_resumen']}",
                font=ctk.CTkFont(size=10),
                text_color="#94A3B8",
                anchor="w",
                justify="left",
                wraplength=260
            )
            lbl_r.pack(fill="x", padx=10, pady=(0, 6))

            # Bind click to select
            for widget in (card, lbl_f, lbl_i, lbl_r):
                widget.bind("<Button-1>", lambda e, od=ord_data: self.seleccionar_orden(od))

    def filtrar_lista(self, event=None):
        self.cargar_ordenes()

    def seleccionar_orden(self, ord_data):
        self.orden_actual = ord_data
        self.cargar_ordenes() # Actualizar resaltado

        o = ord_data["orden"]
        items = ord_data["items"]

        self.lbl_detail_title.configure(text=f"Detalle Orden #{o['id']} - {o['fecha_texto']}")

        for child in self.detail_scroll.winfo_children():
            child.destroy()

        self.item_entries.clear()

        # Meta info card con wraplength vertical para no expander horizontalmente
        info_frame = ctk.CTkFrame(self.detail_scroll, fg_color="#1E293B", corner_radius=6)
        info_frame.pack(fill="x", pady=(0, 10), ipadx=10, ipady=8)

        meta_txt = f"Horario: {o['horario']}  |  Inspector: {o['inspector']}\nOperador: {o['operador']}\nRutas: {o['rutas_resumen']}"
        lbl_meta = ctk.CTkLabel(
            info_frame,
            text=meta_txt,
            justify="left",
            anchor="w",
            wraplength=520,
            font=ctk.CTkFont(size=11)
        )
        lbl_meta.pack(anchor="w", fill="x", padx=5, pady=2)

        # Items Table Header con anchos fijos
        tbl_hdr = ctk.CTkFrame(self.detail_scroll, fg_color="#0F172A", corner_radius=4)
        tbl_hdr.pack(fill="x", pady=(5, 5))

        ctk.CTkLabel(tbl_hdr, text="Nº", width=30, font=ctk.CTkFont(weight="bold", size=11)).pack(side="left", padx=2)
        ctk.CTkLabel(tbl_hdr, text="RUTA / ESTABLECIMIENTO", width=220, font=ctk.CTkFont(weight="bold", size=11), anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(tbl_hdr, text="MES PAGO", width=75, font=ctk.CTkFont(weight="bold", size=11)).pack(side="left", padx=2)
        ctk.CTkLabel(tbl_hdr, text="REALIZADO", width=105, font=ctk.CTkFont(weight="bold", size=11)).pack(side="left", padx=2)
        ctk.CTkLabel(tbl_hdr, text="PENDIENTE / OBSERVACIÓN", width=145, font=ctk.CTkFont(weight="bold", size=11)).pack(side="left", padx=2)

        # Items Rows con wraplength estricto en el nombre del establecimiento para que crezca hacia abajo
        for it in items:
            row_f = ctk.CTkFrame(self.detail_scroll, fg_color="transparent")
            row_f.pack(fill="x", pady=3)

            ctk.CTkLabel(row_f, text=str(it['numero']), width=30, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
            
            lbl_name = f"{it['ruta']} - {it['establecimiento']}"
            # wraplength=210 obliga al texto a crecer verticalmente hacia abajo, NUNCA horizontalmente
            lbl_item_text = ctk.CTkLabel(
                row_f,
                text=lbl_name,
                width=220,
                wraplength=210,
                justify="left",
                anchor="w",
                font=ctk.CTkFont(size=11)
            )
            lbl_item_text.pack(side="left", padx=5)

            ctk.CTkLabel(row_f, text=it['mes_pago'], width=75, font=ctk.CTkFont(size=11)).pack(side="left", padx=2)

            entry_real = ctk.CTkEntry(row_f, placeholder_text="ej. ✓ / 10:30am", width=105)
            entry_real.insert(0, it.get('realizado', ''))
            entry_real.pack(side="left", padx=2)

            entry_pend = ctk.CTkEntry(row_f, placeholder_text="ej. Cerrado", width=145)
            entry_pend.insert(0, it.get('pendiente', ''))
            entry_pend.pack(side="left", padx=2)

            self.item_entries.append({
                "id": it["id"],
                "entry_real": entry_real,
                "entry_pend": entry_pend
            })

        self.btn_reimprimir.configure(state="normal")
        self.btn_guardar_cambios.configure(state="normal")
        self.btn_eliminar.configure(state="normal")

    def guardar_estatus(self):
        if not self.orden_actual:
            return

        for item_data in self.item_entries:
            real_val = item_data["entry_real"].get().strip()
            pend_val = item_data["entry_pend"].get().strip()
            db.actualizar_item_status(item_data["id"], real_val, pend_val)

        messagebox.showinfo("Éxito", "Estatus de la inspección actualizado correctamente.")
        # Recargar detalle
        orden_updated = db.obtener_inspeccion(self.orden_actual["orden"]["id"])
        self.seleccionar_orden(orden_updated)

    def reimprimir_seleccionada(self):
        if not self.orden_actual:
            return
        res = pdfgen.exportar_orden_completa(self.orden_actual)
        messagebox.showinfo("Generado", f"PDF generado:\n{res['pdf']}\nLaTeX generado:\n{res['tex']}")

    def eliminar_orden(self):
        if not self.orden_actual:
            return
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de eliminar esta orden de inspección?"):
            db.eliminar_inspeccion(self.orden_actual["orden"]["id"])
            self.orden_actual = None
            self.lbl_detail_title.configure(text="Seleccione una inspección de la lista")
            for child in self.detail_scroll.winfo_children():
                child.destroy()
            self.btn_reimprimir.configure(state="disabled")
            self.btn_guardar_cambios.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
            self.cargar_ordenes()
