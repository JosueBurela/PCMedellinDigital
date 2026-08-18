import customtkinter as ctk
import database as db
from gui.views.nueva_inspeccion import NuevaInspeccionView
from gui.views.gestion import GestionView
from gui.views.reportes import ReportesView
from gui.views.catalogos import CatalogosView
from gui.views.configuracion import ConfiguracionView

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Inicializar Base de Datos
        db.init_db()

        # Configuración de Apariencia de la Ventana Principal
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("Sistema de Inspecciones - Protección Civil")
        self.geometry("1180x760")
        self.minsize(1000, 650)

        # Layout Principal: Sidebar Izquierda + Contenido Derecho
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Panel
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0F172A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Logo y Nombre
        self.lbl_brand_title = ctk.CTkLabel(
            self.sidebar,
            text="PROTECCIÓN CIVIL",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#F8FAFC"
        )
        self.lbl_brand_title.grid(row=0, column=0, padx=20, pady=(25, 5))

        self.lbl_brand_subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Medellín de Bravo, Ver.",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8"
        )
        self.lbl_brand_subtitle.grid(row=1, column=0, padx=20, pady=(0, 25))

        # Botones de Navegación del Sidebar
        self.buttons = {}
        nav_items = [
            ("nueva", "➕ Nueva Inspección"),
            ("gestion", "📋 Historial y Gestión"),
            ("reportes", "📊 Reportes y PDF"),
            ("catalogos", "🏢 Catálogos"),
            ("configuracion", "⚙️ Configuración")
        ]

        for idx, (key, label) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
                height=40,
                fg_color="transparent",
                text_color="#CBD5E1",
                hover_color="#1E293B",
                command=lambda k=key: self.mostrar_vista(k)
            )
            btn.grid(row=idx, column=0, padx=10, pady=4, sticky="ew")
            self.buttons[key] = btn

        # Footer Sidebar
        self.lbl_ver = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0 Local DB",
            font=ctk.CTkFont(size=10),
            text_color="#64748B"
        )
        self.lbl_ver.grid(row=7, column=0, padx=20, pady=15)

        # Container Principal para las Vistas
        self.container = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Instanciar Vistas
        self.views = {
            "nueva": NuevaInspeccionView(self.container, self),
            "gestion": GestionView(self.container, self),
            "reportes": ReportesView(self.container, self),
            "catalogos": CatalogosView(self.container, self),
            "configuracion": ConfiguracionView(self.container, self)
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        # Vista activa por defecto
        self.mostrar_vista("nueva")

    def mostrar_vista(self, key):
        # Resaltar botón activo en sidebar
        for k, btn in self.buttons.items():
            if k == key:
                btn.configure(fg_color="#3B82F6", text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color="#CBD5E1")

        # Mostrar frame seleccionado
        frame = self.views[key]
        frame.tkraise()

        if hasattr(frame, "cargar_ordenes"):
            frame.cargar_ordenes()
        elif hasattr(frame, "set_filtro") and hasattr(frame, "filtro_actual"):
            frame.set_filtro(frame.filtro_actual)

    def actualizar_vistas(self):
        if "gestion" in self.views and hasattr(self.views["gestion"], "cargar_ordenes"):
            self.views["gestion"].cargar_ordenes()
