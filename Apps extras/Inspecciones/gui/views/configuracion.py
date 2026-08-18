import customtkinter as ctk
from tkinter import messagebox
import database as db

class ConfiguracionView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header Title
        lbl_title = ctk.CTkLabel(
            self.scroll_frame,
            text="⚙️ Configuración del Sistema y Formato Oficial",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        lbl_title.pack(fill="x", pady=(0, 15))

        # Card de Configuración
        self.card_conf = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.card_conf.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        lbl_sec = ctk.CTkLabel(
            self.card_conf,
            text="Parámetros del Documento y Firmas Oficiales",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_sec.pack(anchor="w", padx=10, pady=(5, 15))

        form_frame = ctk.CTkFrame(self.card_conf, fg_color="transparent")
        form_frame.pack(fill="x", padx=10)

        # Director Nombre
        ctk.CTkLabel(form_frame, text="Nombre del Director Municipal:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.entry_director = ctk.CTkEntry(form_frame, width=400)
        self.entry_director.grid(row=0, column=1, sticky="w", padx=10, pady=8)

        # Cargo Director
        ctk.CTkLabel(form_frame, text="Cargo Completo para Firma:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="nw", pady=8)
        self.txt_cargo = ctk.CTkTextbox(form_frame, width=400, height=80)
        self.txt_cargo.grid(row=1, column=1, sticky="w", padx=10, pady=8)

        # Título Encabezado
        ctk.CTkLabel(form_frame, text="Título de la Dependencia:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=8)
        self.entry_header = ctk.CTkEntry(form_frame, width=400)
        self.entry_header.grid(row=2, column=1, sticky="w", padx=10, pady=8)

        # Horario Default
        ctk.CTkLabel(form_frame, text="Horario Predeterminado:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", pady=8)
        self.entry_horario = ctk.CTkEntry(form_frame, width=400)
        self.entry_horario.grid(row=3, column=1, sticky="w", padx=10, pady=8)

        # Save Button
        btn_save = ctk.CTkButton(
            self.card_conf,
            text="💾 Guardar Configuración",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=40,
            command=self.guardar_configuracion
        )
        btn_save.pack(anchor="e", padx=10, pady=15)

        self.cargar_configuracion()

    def cargar_configuracion(self):
        conf = db.get_config()
        self.entry_director.insert(0, conf.get("director_nombre", ""))
        
        self.txt_cargo.delete("1.0", "end")
        self.txt_cargo.insert("1.0", conf.get("director_cargo", ""))

        self.entry_header.insert(0, conf.get("header_title", ""))
        self.entry_horario.insert(0, conf.get("horario_default", ""))

    def guardar_configuracion(self):
        db.set_config("director_nombre", self.entry_director.get().strip())
        db.set_config("director_cargo", self.txt_cargo.get("1.0", "end").strip())
        db.set_config("header_title", self.entry_header.get().strip())
        db.set_config("horario_default", self.entry_horario.get().strip())

        messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
