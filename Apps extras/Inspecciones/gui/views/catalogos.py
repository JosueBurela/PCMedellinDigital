import customtkinter as ctk
from tkinter import messagebox
import database as db

class CatalogosView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header Title
        lbl_title = ctk.CTkLabel(
            self.scroll_frame,
            text="🏢 Catálogos de Rutas, Establecimientos y Personal",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        lbl_title.pack(fill="x", pady=(0, 15))

        # Formulario para Agregar Nuevo Elemento
        self.card_add = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.card_add.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        lbl_add_title = ctk.CTkLabel(
            self.card_add,
            text="Agregar Nuevo Elemento al Catálogo",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_add_title.pack(anchor="w", padx=10, pady=(5, 10))

        add_bar = ctk.CTkFrame(self.card_add, fg_color="transparent")
        add_bar.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(add_bar, text="Categoría:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 5))
        self.combo_cat = ctk.CTkComboBox(
            add_bar,
            values=["Ruta", "Establecimiento", "Inspector", "Operador"],
            width=150
        )
        self.combo_cat.pack(side="left", padx=5)

        ctk.CTkLabel(add_bar, text="Nombre:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(15, 5))
        self.entry_nombre = ctk.CTkEntry(add_bar, placeholder_text="ej. TEJAR / Gasolinera El Tejar / Juan Pérez", width=250)
        self.entry_nombre.pack(side="left", padx=5)

        btn_guardar_cat = ctk.CTkButton(
            add_bar,
            text="➕ Registrar",
            fg_color="#10B981",
            hover_color="#059669",
            command=self.guardar_elemento
        )
        btn_guardar_cat.pack(side="left", padx=(15, 0))

        # Lista de Catálogos Existentes
        self.card_list = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.card_list.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        lbl_list_title = ctk.CTkLabel(
            self.card_list,
            text="Elementos Registrados en Sistema",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_list_title.pack(anchor="w", padx=10, pady=(5, 10))

        self.list_container = ctk.CTkFrame(self.card_list, fg_color="transparent")
        self.list_container.pack(fill="x", padx=10)

        self.cargar_elementos()

    def guardar_elemento(self):
        cat = self.combo_cat.get().strip().lower()
        nombre = self.entry_nombre.get().strip()

        if not nombre:
            messagebox.showwarning("Nombre Requerido", "Ingrese el nombre del elemento para el catálogo.")
            return

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO catalogos (categoria, nombre) VALUES (?, ?)", (cat, nombre))
        conn.commit()
        conn.close()

        self.entry_nombre.delete(0, "end")
        messagebox.showinfo("Éxito", f"Elemento registrado en el catálogo de {cat}.")
        self.cargar_elementos()

    def cargar_elementos(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM catalogos ORDER BY categoria, nombre")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.list_container, text="No hay elementos guardados aún en los catálogos.", font=ctk.CTkFont(size=12)).pack(padx=10, pady=10)
            return

        for r in rows:
            row_f = ctk.CTkFrame(self.list_container, fg_color="#1E293B")
            row_f.pack(fill="x", pady=3, padx=5)

            ctk.CTkLabel(row_f, text=f"[{r['categoria'].upper()}]", width=120, font=ctk.CTkFont(weight="bold", size=11), anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row_f, text=r['nombre'], font=ctk.CTkFont(size=12), anchor="w").pack(side="left", padx=10, expand=True, fill="x")

            btn_del = ctk.CTkButton(
                row_f,
                text="❌",
                width=30,
                fg_color="#7F1D1D",
                hover_color="#991B1B",
                command=lambda el_id=r['id']: self.eliminar_elemento(el_id)
            )
            btn_del.pack(side="right", padx=10, pady=5)

    def eliminar_elemento(self, el_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM catalogos WHERE id = ?", (el_id,))
        conn.commit()
        conn.close()
        self.cargar_elementos()
