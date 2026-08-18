import os
import sys
import shutil
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw

from database import DatabaseManager
from card_generator import CardGenerator
from migration import exportar_respaldo, importar_respaldo

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("System")  # Modos: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

def get_asset_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class ContactCardProApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurar Ventana
        self.title("ContactCard")
        self.geometry("980x685")
        self.minsize(920, 620)
        
        # Establecer Icono de Ventana
        ico_path = get_asset_path(os.path.join("assets", "logo.ico"))
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass
        
        # Inicializar Motores
        self.db = DatabaseManager("directorio.db")
        self.card_gen = CardGenerator()
        
        # Crear Avatar por Defecto para la GUI
        self.default_avatar_path = self._generar_avatar_defecto()
        
        # Estado de la App
        self.selected_contact_ids = {} # {id: BooleanVar}
        self.editing_contact_id = None
        self.selected_photo_path = None # Ruta temporal de foto seleccionada en formulario
        
        self._build_ui()
        self.cargar_contactos()

    def _generar_avatar_defecto(self) -> str:
        """Genera dinámicamente un avatar por defecto en assets/ si no existe."""
        os.makedirs("assets", exist_ok=True)
        path = os.path.abspath(os.path.join("assets", "default_avatar.png"))
        if not os.path.exists(path):
            try:
                avatar = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
                draw = ImageDraw.Draw(avatar)
                # Círculo gris de fondo
                draw.ellipse((0, 0, 99, 99), fill=(100, 116, 139, 255))
                # Silueta (cabeza y hombros)
                draw.ellipse((35, 20, 65, 50), fill=(241, 245, 249, 255))
                draw.chord((15, 55, 85, 110), start=180, end=360, fill=(241, 245, 249, 255))
                avatar.save(path, "PNG")
            except Exception:
                pass
        return path

    def _build_ui(self):
        # Configurar cuadrícula principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Crear contenedor de pestañas
        self.tabview = ctk.CTkTabview(self, width=960, height=665)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.tab_directory = self.tabview.add("🔍 Directorio")
        self.tab_form = self.tabview.add("➕ Nuevo Contacto")
        self.tab_config = self.tabview.add("⚙️ Respaldos")
        
        self._build_directory_tab()
        self._build_form_tab()
        self._build_config_tab()

    # --- PESTAÑA 1: DIRECTORIO ---
    def _build_directory_tab(self):
        self.tab_directory.grid_columnconfigure(0, weight=1)
        self.tab_directory.grid_rowconfigure(1, weight=1)
        
        # Barra superior
        top_frame = ctk.CTkFrame(self.tab_directory, fg_color="transparent")
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Buscar por nombre, puesto o empresa...")
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda event: self.cargar_contactos())
        
        self.btn_gen_horiz = ctk.CTkButton(top_frame, text="Tarjeta H. (Seleccionados)", command=lambda: self.generar_tarjeta_seleccionados(horizontal=True))
        self.btn_gen_horiz.grid(row=0, column=1, padx=5, sticky="e")
        
        self.btn_gen_vert = ctk.CTkButton(top_frame, text="Tarjeta V. (Seleccionados)", command=lambda: self.generar_tarjeta_seleccionados(horizontal=False))
        self.btn_gen_vert.grid(row=0, column=2, padx=5, sticky="e")
        
        # Lista scrollable
        self.contacts_scroll = ctk.CTkScrollableFrame(self.tab_directory, label_text="Contactos Registrados")
        self.contacts_scroll.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.contacts_scroll.grid_columnconfigure(0, weight=1)

    # --- PESTAÑA 2: FORMULARIO ---
    def _build_form_tab(self):
        self.tab_form.grid_columnconfigure(0, weight=1)
        self.tab_form.grid_columnconfigure(1, weight=1)
        
        self.form_title_label = ctk.CTkLabel(self.tab_form, text="Registrar Nuevo Contacto", font=ctk.CTkFont(size=20, weight="bold"))
        self.form_title_label.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Grid de campos
        self.inputs = {}
        campos = [
            ("nombre", "Nombre Completo (Requerido)"),
            ("telefono", "Teléfono (Requerido)"),
            ("email", "Correo Electrónico"),
            ("empresa", "Empresa"),
            ("puesto", "Puesto / Cargo"),
            ("direccion", "Dirección Física"),
            ("web", "Sitio Web (URL)")
        ]
        
        for idx, (key, label_text) in enumerate(campos):
            row = (idx // 2) + 1
            col = idx % 2
            
            frame = ctk.CTkFrame(self.tab_form, fg_color="transparent")
            frame.grid(row=row, column=col, padx=20, pady=8, sticky="ew")
            frame.grid_columnconfigure(0, weight=1)
            
            lbl = ctk.CTkLabel(frame, text=label_text, anchor="w")
            lbl.grid(row=0, column=0, sticky="w", pady=(0, 3))
            
            entry = ctk.CTkEntry(frame, placeholder_text=f"Escribe {label_text.lower()}...")
            entry.grid(row=1, column=0, sticky="ew")
            
            self.inputs[key] = entry
            
        # Campo 8: Foto de Perfil (Colocado en fila 4 columna 1 para balancear la cuadrícula)
        photo_frame = ctk.CTkFrame(self.tab_form, fg_color="transparent")
        photo_frame.grid(row=4, column=1, padx=20, pady=8, sticky="ew")
        photo_frame.grid_columnconfigure(0, weight=1)
        
        lbl_photo = ctk.CTkLabel(photo_frame, text="Foto de Perfil (Opcional)", anchor="w")
        lbl_photo.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 3))
        
        self.btn_select_photo = ctk.CTkButton(photo_frame, text="Elegir Imagen...", width=110, command=self.seleccionar_foto)
        self.btn_select_photo.grid(row=1, column=0, padx=(0, 5), sticky="w")
        
        self.btn_clear_photo = ctk.CTkButton(photo_frame, text="Remover", width=70, fg_color="#991B1B", hover_color="#7F1D1D", command=self.remover_foto_formulario)
        # Mostrar el botón de remover
        self.btn_clear_photo.grid(row=1, column=1, padx=5, sticky="w")
        
        self.lbl_photo_status = ctk.CTkLabel(photo_frame, text="Sin foto seleccionada", text_color="gray", anchor="w")
        self.lbl_photo_status.grid(row=1, column=2, padx=10, sticky="ew")
        
        # Botones de guardado
        btn_frame = ctk.CTkFrame(self.tab_form, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=25)
        
        self.btn_save = ctk.CTkButton(btn_frame, text="Guardar Contacto", width=150, command=self.guardar_contacto)
        self.btn_save.grid(row=0, column=0, padx=10)
        
        self.btn_cancel_edit = ctk.CTkButton(btn_frame, text="Cancelar Edición", width=150, fg_color="gray", hover_color="#555555", command=self.cancelar_edicion)

    # --- PESTAÑA 3: CONFIGURACIÓN ---
    def _build_config_tab(self):
        self.tab_config.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(self.tab_config, text="Gestión de Respaldos", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_title.grid(row=0, column=0, pady=25)
        
        info_frame = ctk.CTkFrame(self.tab_config, width=600)
        info_frame.grid(row=1, column=0, padx=20, pady=20, sticky="n")
        
        lbl_db_info = ctk.CTkLabel(info_frame, text="Ruta de la Base de Datos Activa:", font=ctk.CTkFont(weight="bold"))
        lbl_db_info.pack(padx=20, pady=(15, 5), anchor="w")
        
        self.lbl_db_path = ctk.CTkLabel(info_frame, text=self.db.db_path, text_color="gray")
        self.lbl_db_path.pack(padx=20, pady=(0, 15), anchor="w")
        
        actions_frame = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        actions_frame.grid(row=2, column=0, pady=20)
        
        btn_export = ctk.CTkButton(actions_frame, text="Exportar Respaldo (.db)", width=200, height=45, command=self.exportar_db)
        btn_export.grid(row=0, column=0, padx=15)
        
        btn_import = ctk.CTkButton(actions_frame, text="Importar Respaldo (.db)", width=200, height=45, fg_color="#D97706", hover_color="#B45309", command=self.importar_db)
        btn_import.grid(row=0, column=1, padx=15)

    # --- LÓGICA DE FOTOS EN FORMULARIO ---
    def seleccionar_foto(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")],
            title="Seleccionar Foto de Perfil"
        )
        if filepath:
            self.selected_photo_path = filepath
            filename = os.path.basename(filepath)
            self.lbl_photo_status.configure(text=filename, text_color="green")

    def remover_foto_formulario(self):
        self.selected_photo_path = None
        self.lbl_photo_status.configure(text="Sin foto seleccionada", text_color="gray")

    # --- CARGAR CONTACTOS ---
    def cargar_contactos(self):
        for widget in self.contacts_scroll.winfo_children():
            widget.destroy()
            
        search_query = self.search_entry.get().strip().lower()
        contactos = self.db.obtener_contactos()
        
        if search_query:
            contactos = [
                c for c in contactos if
                search_query in c["nombre"].lower() or
                (c["puesto"] and search_query in c["puesto"].lower()) or
                (c["empresa"] and search_query in c["empresa"].lower())
            ]
            
        self.selected_contact_ids.clear()
        
        if not contactos:
            lbl_empty = ctk.CTkLabel(self.contacts_scroll, text="No se encontraron contactos.", text_color="gray")
            lbl_empty.grid(row=0, column=0, pady=20)
            return

        for idx, contacto in enumerate(contactos):
            c_id = contacto["id"]
            self.selected_contact_ids[c_id] = ctk.BooleanVar(value=False)
            
            # Fila de contacto como contenedor (se adapta automáticamente al tema claro/oscuro del sistema)
            row_frame = ctk.CTkFrame(self.contacts_scroll, height=90)
            row_frame.grid(row=idx, column=0, padx=5, pady=5, sticky="ew")
            
            # Grid interno de la fila para alinear
            row_frame.grid_columnconfigure(2, weight=1) # El contenedor de texto toma el espacio central y empuja los botones
            
            # 1. Checkbox (Col 0)
            chk = ctk.CTkCheckBox(row_frame, text="", variable=self.selected_contact_ids[c_id], width=20)
            chk.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")
            
            # 2. Avatar de Perfil (Col 1) - Tamaño 50x50
            foto_path = contacto.get("foto")
            if foto_path and not os.path.isabs(foto_path):
                foto_path = os.path.abspath(foto_path)
                
            path_imagen = foto_path if (foto_path and os.path.exists(foto_path)) else self.default_avatar_path
            
            try:
                pil_img = Image.open(path_imagen)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(50, 50))
                img_label = ctk.CTkLabel(row_frame, image=ctk_img, text="")
                img_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            except Exception:
                pass
            
            # 3. Contenedor de Textos (Col 2) - Todo alineado a la izquierda
            info_text = f"{contacto['nombre']}"
            sub_text = ""
            if contacto["puesto"] or contacto["empresa"]:
                sub_text = f"{contacto['puesto'] or ''} @ {contacto['empresa'] or ''}".strip(" @ ")
                
            text_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            text_frame.grid(row=0, column=2, padx=10, pady=5, sticky="w")
            
            lbl_name = ctk.CTkLabel(text_frame, text=info_text, font=ctk.CTkFont(weight="bold", size=16))
            lbl_name.grid(row=0, column=0, sticky="w")
            
            curr_row = 1
            if sub_text:
                lbl_sub = ctk.CTkLabel(text_frame, text=sub_text, text_color="gray", font=ctk.CTkFont(size=12))
                lbl_sub.grid(row=curr_row, column=0, sticky="w")
                curr_row += 1
                
            # Detalles de contacto (Teléfono y Email) - Color de texto adaptativo: slate gris en tema claro, gris claro brillante en tema oscuro
            details_text = f"📞 {contacto['telefono']}"
            if contacto["email"]:
                details_text += f"   •   📧 {contacto['email']}"
            lbl_details = ctk.CTkLabel(
                text_frame, 
                text=details_text, 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color=("#475569", "#CBD5E1")
            )
            lbl_details.grid(row=curr_row, column=0, sticky="w")
            
            # 4. Botones de Acción (Col 3) - Empujados al extremo derecho
            actions_subframe = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_subframe.grid(row=0, column=3, padx=15, sticky="e")
            
            btn_card = ctk.CTkButton(actions_subframe, text="📇 Tarjeta", width=70, command=lambda c=contacto: self.generar_tarjeta_individual(c))
            btn_card.grid(row=0, column=0, padx=2)
            
            btn_edit = ctk.CTkButton(actions_subframe, text="✏️", width=35, fg_color="#4B5563", hover_color="#374151", command=lambda c=contacto: self.iniciar_edicion(c))
            btn_edit.grid(row=0, column=1, padx=2)
            
            btn_del = ctk.CTkButton(actions_subframe, text="🗑️", width=35, fg_color="#DC2626", hover_color="#B91C1C", command=lambda c_id=c_id: self.eliminar_contacto(c_id))
            btn_del.grid(row=0, column=2, padx=2)

    # --- OPERACIONES CRUD ---
    def guardar_contacto(self):
        nombre = self.inputs["nombre"].get().strip()
        telefono = self.inputs["telefono"].get().strip()
        
        if not nombre or not telefono:
            messagebox.showerror("Error", "Los campos Nombre y Teléfono son obligatorios.")
            return

        datos = {k: entry.get().strip() or None for k, entry in self.inputs.items()}
        
        if self.editing_contact_id:
            # ACTUALIZAR CONTACTO
            # Manejo de copia de foto si cambió
            foto_final = self.selected_photo_path
            
            # Buscar el contacto original para ver si tenía foto anterior
            original = self.db.obtener_contacto_por_id(self.editing_contact_id)
            foto_original = original.get("foto") if original else None
            
            if self.selected_photo_path != foto_original:
                if self.selected_photo_path is None:
                    # Foto fue removida
                    foto_final = None
                    if foto_original and os.path.exists(foto_original):
                        try:
                            os.remove(foto_original)
                        except Exception:
                            pass
                else:
                    # Foto es nueva o modificada
                    try:
                        os.makedirs("profiles", exist_ok=True)
                        _, ext = os.path.splitext(self.selected_photo_path)
                        destino = f"profiles/foto_{self.editing_contact_id}{ext}"
                        
                        # Si no es ya el archivo destino
                        if os.path.abspath(self.selected_photo_path) != os.path.abspath(destino):
                            shutil.copy2(self.selected_photo_path, destino)
                        foto_final = destino
                    except Exception as e:
                        messagebox.showwarning("Advertencia", f"No se pudo guardar la imagen física: {str(e)}")
                        foto_final = None
            
            exito = self.db.actualizar_contacto(
                contacto_id=self.editing_contact_id,
                nombre=nombre,
                telefono=telefono,
                email=datos["email"],
                empresa=datos["empresa"],
                puesto=datos["puesto"],
                direccion=datos["direccion"],
                web=datos["web"],
                foto=foto_final
            )
            if exito:
                messagebox.showinfo("Éxito", "Contacto actualizado exitosamente.")
                self.cancelar_edicion()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el contacto.")
        else:
            # CREAR CONTACTO
            nuevo_id = self.db.crear_contacto(
                nombre=nombre,
                telefono=telefono,
                email=datos["email"],
                empresa=datos["empresa"],
                puesto=datos["puesto"],
                direccion=datos["direccion"],
                web=datos["web"],
                foto=None # Primero None para obtener el ID de archivo único
            )
            
            if nuevo_id > 0:
                if self.selected_photo_path:
                    try:
                        os.makedirs("profiles", exist_ok=True)
                        _, ext = os.path.splitext(self.selected_photo_path)
                        destino = f"profiles/foto_{nuevo_id}{ext}"
                        shutil.copy2(self.selected_photo_path, destino)
                        # Actualizar ruta en la BD
                        self.db.actualizar_contacto(
                            contacto_id=nuevo_id,
                            nombre=nombre,
                            telefono=telefono,
                            email=datos["email"],
                            empresa=datos["empresa"],
                            puesto=datos["puesto"],
                            direccion=datos["direccion"],
                            web=datos["web"],
                            foto=destino
                        )
                    except Exception as e:
                        messagebox.showwarning("Advertencia", f"No se pudo guardar la imagen: {str(e)}")
                
                messagebox.showinfo("Éxito", "Contacto guardado exitosamente.")
                self.limpiar_formulario()
                self.tabview.set("🔍 Directorio")
            else:
                messagebox.showerror("Error", "No se pudo guardar el contacto.")

        self.cargar_contactos()

    def eliminar_contacto(self, contacto_id: int):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este contacto?"):
            contacto = self.db.obtener_contacto_por_id(contacto_id)
            foto = contacto.get("foto") if contacto else None
            
            if self.db.eliminar_contacto(contacto_id):
                # Eliminar archivo físico de foto
                if foto and os.path.exists(foto):
                    try:
                        os.remove(foto)
                    except Exception:
                        pass
                self.cargar_contactos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el contacto.")

    def iniciar_edicion(self, contacto: Dict[str, Any]):
        self.editing_contact_id = contacto["id"]
        self.form_title_label.configure(text=f"Editar Contacto: {contacto['nombre']}")
        self.btn_save.configure(text="Actualizar Contacto")
        
        for key, entry in self.inputs.items():
            entry.delete(0, "end")
            valor = contacto.get(key)
            if valor:
                entry.insert(0, valor)
                
        # Cargar estado de la foto
        self.selected_photo_path = contacto.get("foto")
        if self.selected_photo_path:
            self.lbl_photo_status.configure(text=os.path.basename(self.selected_photo_path), text_color="green")
        else:
            self.lbl_photo_status.configure(text="Sin foto seleccionada", text_color="gray")
            
        self.btn_cancel_edit.grid(row=0, column=1, padx=10)
        self.tabview.set("➕ Nuevo Contacto")

    def cancelar_edicion(self):
        self.editing_contact_id = None
        self.selected_photo_path = None
        self.form_title_label.configure(text="Registrar Nuevo Contacto")
        self.btn_save.configure(text="Guardar Contacto")
        self.btn_cancel_edit.grid_forget()
        self.limpiar_formulario()
        self.lbl_photo_status.configure(text="Sin foto seleccionada", text_color="gray")
        self.tabview.set("🔍 Directorio")

    def limpiar_formulario(self):
        for entry in self.inputs.values():
            entry.delete(0, "end")
        self.selected_photo_path = None
        self.lbl_photo_status.configure(text="Sin foto seleccionada", text_color="gray")

    # --- GENERAR TARJETAS ---
    def generar_tarjeta_individual(self, contacto: Dict[str, Any]):
        orientacion = messagebox.askyesnocancel(
            "Seleccionar Orientación",
            "¿Desea la tarjeta en formato Horizontal?\n\n(Sí = Horizontal, No = Vertical / Móvil)"
        )
        if orientacion is None:
            return
            
        default_filename = f"tarjeta_{contacto['nombre'].replace(' ', '_')}.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imágenes PNG", "*.png")],
            initialfile=default_filename,
            title="Guardar Tarjeta de Contacto"
        )
        
        if filepath:
            try:
                self.card_gen.crear_tarjeta([contacto], filepath, horizontal=orientacion)
                messagebox.showinfo("Éxito", f"Tarjeta generada correctamente en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al generar tarjeta: {str(e)}")

    def generar_tarjeta_seleccionados(self, horizontal: bool = True):
        seleccionados_ids = [c_id for c_id, var in self.selected_contact_ids.items() if var.get()]
        
        if not seleccionados_ids:
            messagebox.showwarning("Advertencia", "Por favor, selecciona al menos un contacto en la lista.")
            return
            
        if len(seleccionados_ids) > 5:
            messagebox.showwarning("Límite superado", "El límite máximo es de 5 contactos por tarjeta.")
            return

        lista_contactos = []
        for c_id in seleccionados_ids:
            contacto = self.db.obtener_contacto_por_id(c_id)
            if contacto:
                lista_contactos.append(contacto)

        default_filename = f"directorio_{len(lista_contactos)}_contactos.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imágenes PNG", "*.png")],
            initialfile=default_filename,
            title="Guardar Directorio de Contactos"
        )
        
        if filepath:
            try:
                self.card_gen.crear_tarjeta(lista_contactos, filepath, horizontal=horizontal)
                messagebox.showinfo("Éxito", f"Tarjeta de contactos generada correctamente en:\n{filepath}")
                for var in self.selected_contact_ids.values():
                    var.set(False)
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al generar tarjeta: {str(e)}")

    # --- RESPALDOS ---
    def exportar_db(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Base de Datos SQLite", "*.db")],
            initialfile="directorio_respaldo.db",
            title="Exportar Respaldo de Base de Datos"
        )
        if filepath:
            exito, msg = exportar_respaldo(self.db.db_path, filepath)
            if exito:
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)

    def importar_db(self):
        if messagebox.askyesno("Confirmar Importación", "ADVERTENCIA: Importar un respaldo reemplazará TODOS los contactos actuales por los del archivo seleccionado. ¿Deseas continuar?"):
            filepath = filedialog.askopenfilename(
                filetypes=[("Base de Datos SQLite", "*.db")],
                title="Seleccionar Archivo de Respaldo"
            )
            if filepath:
                exito, msg = importar_respaldo(filepath, self.db.db_path)
                if exito:
                    messagebox.showinfo("Éxito", msg)
                    self.cargar_contactos()
                else:
                    messagebox.showerror("Error", msg)

if __name__ == "__main__":
    app = ContactCardProApp()
    app.mainloop()
