import customtkinter as ctk

from tkinter import (
    messagebox, scrolledtext,     # Módulos
    
    # --- VARIABLES DE CONTROL ---
    StringVar, DoubleVar, BooleanVar, 
    
    # --- WIDGETS NO REEMPLAZADOS ---
    Listbox, 
    
    # --- CONSTANTES ---
    END, INSERT, NSEW, W, N, S, E, LEFT, RIGHT, # ¡¡AÑADÍ 'INSERT' Y MÁS!!
    
    TclError
)

# --- Tus otras librerías (estas estaban bien) ---
import math
import unicodedata
import inspect
import difflib
from fractions import Fraction
import re  # <-- ¡NUEVO! Para la lógica de normalización

# --- ¡NUEVAS LIBRERÍAS PARA GRÁFICAS! ---
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from logica_calculadora import (
    convertir_valor,
    resolver_falsa_posicion_avanzado,
    resolver_gauss_jordan,
    resolver_eliminacion_filas,
    matriz_a_string,
    calcular_operaciones_matrices,
    verificar_independencia_lineal,
    resolver_sistema_homogeneo,
    calcular_inversa,
    calcular_determinante_auto,
    resolver_cramer,
    formatea_num,
    es_casi_cero,
    normalize_funcion,
    eval_funcion_escalar,
    eval_funcion_vectorial,
    resolver_biseccion
)

# ================================================================
#              CALCULADORA CIENTIFICA — MODO OSCURO
#                    Estilo WebApp Neumorfico
# ================================================================
# ================================================================
#              CALCULADORA CIENTIFICA — MODO MODERNO
# ================================================================
class CalculadoraApp(ctk.CTk):  # <-- HEREDAMOS DE CTK
    def __init__(self):
        super().__init__() # <-- LLAMAMOS AL PADRE

        # ===========================================================
        # ¡¡AQUÍ ESTÁ LA SOLUCIÓN!!
        # Define TODAS tus variables de color ANTES de usarlas.
        # ===========================================================
        self.COLOR_BG = "#1e1e1e"
        self.COLOR_CARD = "#2b2b2b"
        self.COLOR_PRIMARY = "#00C8FF"
        self.COLOR_ACCENT = "#FF8C42"
        self.COLOR_DANGER = "#D9534F"
        
        # --- ESTAS ERAN LAS QUE FALTABAN (y causan el error) ---
        self.COLOR_TEXT = "#f2f2f2"      # <-- La que causó el error
        self.COLOR_SUB = "#bfbfbf"        # <-- La que causaría el próximo error
        self.COLOR_LIGHT = "#3a3a3a"      # (Por si la usas)
        self.COLOR_DARK = "#141414"       # (Por si la usas)
        
        
        # --- Ahora que los colores existen, configura la app ---
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue") 
        self.configure(fg_color=self.COLOR_BG)

        self.title("MatrixScholar — Proyecto Universitario")
        self.geometry("1080x720")
        self.minsize(980, 620)
        
        # --- Variables globales ---
        self.metodo_actual = ""
        self.entradas_matriz = []
        self.entradas_matriz_a = []
        self.entradas_matriz_b = []
        self.entradas_matriz_t = []
        self.vars_biseccion = {}
        self.canvas_biseccion = None
        self.ax_biseccion = None
        self.fig_biseccion = None
        self.vars_falsa_posicion = {}
        self.canvas_falsa_posicion = None
        self.ax_falsa_posicion = None
        self.fig_falsa_posicion = None
        self.entry_func_falsa_posicion = None
        self.txt_proc_falsa_posicion = None
        self.entry_func_biseccion = None
        self.txt_proc_biseccion = None
        self.filas_a = self.columnas_a = self.filas_b = self.columnas_b = 0

        # --- Construccion visual ---
        # (Ahora esto funcionará, porque self.COLOR_TEXT ya existe)
        self._construir_shell()
        self.vista_menu()
    # ================================================================
    #                  ESTRUCTURA PRINCIPAL (SHELL)
    # ================================================================
    def _construir_shell(self):
        """Crea la estructura general: barra superior + sidebar + contenido + búsqueda."""
        
        # ====== BARRA SUPERIOR ======
        # Nota: Usamos fg_color para el color de fondo en CTk
        topbar = ctk.CTkFrame(self, fg_color="#242424", height=60, corner_radius=0)
        topbar.pack(side="top", fill="x")

        # Contenedor del título
        topbar_left = ctk.CTkFrame(topbar, fg_color="transparent")
        topbar_left.pack(side="left", fill="x", expand=True, padx=20)

        # Contenedor del buscador
        topbar_right = ctk.CTkFrame(topbar, fg_color="transparent")
        topbar_right.pack(side="right", padx=20)

        # --- Título del proyecto ---
        ctk.CTkLabel(topbar_left, text="MatrixScholar — Proyecto Universitario",
                    text_color=self.COLOR_PRIMARY,
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=12)

        # ====== BARRA DE BÚSQUEDA CON AUTOCOMPLETADO ======
        self.search_var = StringVar() # Mantenemos tk.StringVar
        search_frame = ctk.CTkFrame(topbar_right, fg_color="transparent")
        search_frame.pack(anchor="e", pady=10)

        # Campo de entrada (¡MUCHO MÁS LIMPIO!)
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            fg_color="#1E1E1E",
            border_color="#00C8FF", # Borde neón
            placeholder_text="Buscar herramienta...",
            width=280
        )
        search_entry.pack(side="left")

        # --- Listbox de sugerencias flotante ---
        # NOTA: Listbox es un widget complejo. Por ahora, mantenemos el tk.Listbox
        # pero lo estilizamos para que encaje.
        self.suggestion_box = Listbox(
            self,
            bg="#1E1E1E",
            fg="#00C8FF",
            font=("Segoe UI", 10),
            relief="flat",
            highlightthickness=1, # Borde
            highlightbackground="#00C8FF", # Color del borde
            selectbackground=self.COLOR_PRIMARY,
            selectforeground="black",
            height=0
        )
        self.suggestion_box.place_forget() 

        # Eventos (ESTOS SE QUEDAN IGUAL - ¡Bien hecho!)
        self.search_var.trace("w", lambda *args: self._actualizar_sugerencias())
        search_entry.bind("<Down>", lambda e: self._mover_seleccion("down"))
        search_entry.bind("<Up>", lambda e: self._mover_seleccion("up"))
        search_entry.bind("<Return>", lambda e: self._confirmar_sugerencia())
        self.suggestion_box.bind("<ButtonRelease-1>", lambda e: self._confirmar_sugerencia())

        # Botón de búsqueda (¡MÁS LIMPIO!)
        btn_search = ctk.CTkButton(
            search_frame,
            text="🔍",
            font=("Segoe UI", 14),
            fg_color="#242424", # Transparente al fondo
            hover_color="#00A8E8",
            width=40,
            command=self.buscar_herramienta
        )
        btn_search.pack(side="left", padx=(8, 0))

        # ====== CONTENEDOR PRINCIPAL ======
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # Sidebar lateral
        self.sidebar = ctk.CTkScrollableFrame(main_frame, fg_color="#252525", width=320, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Contenido central (¡AQUÍ USAMOS EL SCROLL!)
        # Reemplazamos tu ctk.CTkFrame por un CTkScrollableFrame
        self.content_scrollable = ctk.CTkScrollableFrame(main_frame, fg_color=self.COLOR_BG, corner_radius=0)
        self.content_scrollable.pack(side="left", fill="both", expand=True)

        # ====== FOOTER (opcional o limpio) ======
        footer = ctk.CTkFrame(self, fg_color="transparent", height=10)
        footer.pack(side="bottom", fill="x", pady=5)

        # ====== CONSTRUIR SIDEBAR ======
        self._construir_sidebar()
            # ================================================================
        #                  FUNCIONALIDAD DE BÚSQUEDA
        # ================================================================

    def buscar_herramienta(self):
        """Búsqueda inteligente y estable para todas las herramientas de MatrixScholar."""
        consulta_original = self.search_var.get().strip()
        consulta = consulta_original.lower()

        # --- Normalizar texto (quita tildes) ---
        def normalizar(txt):
            import unicodedata
            return ''.join(
                c for c in unicodedata.normalize('NFD', txt)
                if unicodedata.category(c) != 'Mn'
            ).lower()

        consulta = normalizar(consulta)
        if not consulta:
            return

        # --- Diccionario de herramientas con nombres REALES de tu app ---
        herramientas = {
            # Métodos verificados
            "gauss": lambda: self.preparar_matriz_unica("Gauss-Jordan"),
            "gauss-jordan": lambda: self.preparar_matriz_unica("Gauss-Jordan"),

            # Eliminación por filas
            "eliminacion": lambda: self.preparar_matriz_unica("Eliminacion"),
            "filas": lambda: self.preparar_matriz_unica("Eliminacion"),

            # Método de Cramer
            "cramer": getattr(self, "preparar_cramer", None),

            # Sistema homogéneo
            "homogeneo": getattr(self, "preparar_matriz_homogeneo", None),
            "sistema": getattr(self, "preparar_matriz_homogeneo", None),

            # Suma y multiplicación de matrices
            "suma": getattr(self, "preparar_matrices_operaciones", None),
            "multiplicacion": getattr(self, "preparar_matrices_operaciones", None),
            "operaciones": getattr(self, "preparar_matrices_operaciones", None),

            # Transpuesta
            "transpuesta": getattr(self, "preparar_matriz_transpuesta", None),
            "traspuesta": getattr(self, "preparar_matriz_transpuesta", None),

            # Inversa
            "inversa": getattr(self, "preparar_inversa_matriz", None),

            # Determinante
            "determinante": getattr(self, "preparar_determinante", None),

            # Independencia y linealidad
            "independencia": getattr(self, "preparar_linealidad", None),
            "linealidad": getattr(self, "preparar_linealidad", None),

            # Método de Bisección (nuevo)
            "biseccion": getattr(self, "abrir_biseccion", None),
            "método de bisección": getattr(self, "abrir_biseccion", None),
            "metodo de biseccion": getattr(self, "abrir_biseccion", None),
            "metodo numerico": getattr(self, "abrir_biseccion", None),
            "método numérico": getattr(self, "abrir_biseccion", None),
            "raiz": getattr(self, "abrir_biseccion", None),
            "raices": getattr(self, "abrir_biseccion", None),
            "raíz": getattr(self, "abrir_biseccion", None),
            "raices de ecuaciones": getattr(self, "abrir_biseccion", None),

            # Cerrar aplicación
            "cerrar": self.root.quit,
            "salir": self.root.quit
        }

        # --- Buscar coincidencias ---
        for palabra, funcion in herramientas.items():
            if palabra in consulta and funcion:
                funcion()
                return

        # --- Si no encuentra coincidencia ---
        from tkinter import messagebox
        messagebox.showinfo(
            "Sin resultados",
            f"No se encontró ninguna herramienta que coincida con '{consulta_original}'."
        )


    def _actualizar_sugerencias(self):
        """Actualiza las sugerencias de autocompletado en tiempo real (flotantes)."""
        texto = self.search_var.get().lower()
        sugerencias = []

        # Lista de nombres visibles en el autocompletado
        herramientas = [
            "Gauss-Jordan",
            "Eliminación de Filas",
            "Método de Cramer",
            "Sistema Homogéneo",
            "Suma y Multiplicación",
            "Transpuesta",
            "Inversa",
            "Determinante",
            "Independencia Lineal",
            "Probar Linealidad",
            "Método de Bisección",     
            "Cerrar Aplicación"
        ]

        if texto:
            sugerencias = [h for h in herramientas if texto in h.lower()]

        self.suggestion_box.delete(0, END)

        if sugerencias:
            for item in sugerencias:
                self.suggestion_box.insert(END, item)

            # Calcular posición del campo para ubicar la lista justo debajo
            widget = self.root.focus_get()
            if widget:
                x = widget.winfo_rootx() - self.root.winfo_rootx()
                y = widget.winfo_rooty() - self.root.winfo_rooty() + widget.winfo_height()
                self.suggestion_box.place(x=x, y=y, width=widget.winfo_width())
                self.suggestion_box.lift()
                self.suggestion_box.config(height=min(len(sugerencias), 5))
        else:
            self.suggestion_box.place_forget()


    def _mover_seleccion(self, direccion):
        """Permite navegar con flechas ↑ y ↓ dentro del Listbox."""
        size = self.suggestion_box.size()
        if size == 0:
            return

        seleccion = self.suggestion_box.curselection()
        if not seleccion:
            index = 0 if direccion == "down" else size - 1
        else:
            index = seleccion[0] + (1 if direccion == "down" else -1)
            index %= size  # ciclo

        self.suggestion_box.selection_clear(0, END)
        self.suggestion_box.selection_set(index)
        self.suggestion_box.activate(index)


    def _confirmar_sugerencia(self):
        """Inserta la sugerencia seleccionada y ejecuta la búsqueda."""
        seleccion = self.suggestion_box.curselection()
        if seleccion:
            texto = self.suggestion_box.get(seleccion[0])
            self.search_var.set(texto)
        self.suggestion_box.place_forget()
        self.buscar_herramienta()

# ================================================================
    #      SIDEBAR DE NAVEGACION (Híbrido: Acordeón + Scroll)
    # ================================================================
    def _construir_sidebar(self):
        """Sidebar scrollable con acordeones colapsables."""

        # --- FUNCIÓN DE BOTÓN (Se queda igual, es perfecta) ---
        def crear_boton_nav(parent, texto, comando, icono="•", hover_color=None):
            hover_color = hover_color or self.COLOR_PRIMARY
            btn = ctk.CTkButton(
                parent,
                text=f" {icono}   {texto}",
                command=comando,
                font=("Segoe UI", 11),
                text_color=self.COLOR_TEXT,
                fg_color="transparent",
                hover_color=hover_color,
                anchor="w",
                height=44
            )
            btn.pack(fill="x", padx=15, pady=3)
            return btn

        # --- ¡NUEVA FUNCIÓN DE ACORDEÓN (CORREGIDA)! ---
        def crear_acordeon(parent, titulo, items, empezar_abierto=False):
            
            acordeon = ctk.CTkFrame(parent, fg_color="transparent")
            acordeon.pack(fill="x", pady=(10, 0))

            # --- 1. El Header Clickeable ---
            # Usamos un Frame normal para el header, no un botón
            header_frame = ctk.CTkFrame(acordeon, fg_color="#2c2c2c", height=35, corner_radius=4, cursor="hand2")
            header_frame.pack(fill="x", padx=15)
            header_frame.pack_propagate(False) # Forzar altura

            # Icono (flecha)
            icono_texto = "▲" if empezar_abierto else "▼"
            icon = ctk.CTkLabel(header_frame, text=icono_texto, text_color=self.COLOR_PRIMARY, font=("Segoe UI", 10))
            icon.pack(side="right", padx=10)

            # Título
            lbl_titulo = ctk.CTkLabel(header_frame, text=titulo, font=("Segoe UI", 9, "bold"), text_color=self.COLOR_SUB)
            lbl_titulo.pack(side="left", fill="x", expand=True, padx=15)

            # --- 2. El Contenido Colapsable ---
            contenido = ctk.CTkFrame(acordeon, fg_color="transparent")
            if empezar_abierto:
                contenido.pack(fill="x", pady=(5,0)) # Empezar visible
            
            abierto = BooleanVar(value=empezar_abierto)

            # --- 3. La Lógica de Toggle ---
            def toggle(event=None): # event=None es importante para binds
                if abierto.get():
                    contenido.pack_forget()
                    icon.configure(text="▼")
                    abierto.set(False)
                else:
                    contenido.pack(fill="x", pady=(5,0))
                    icon.configure(text="▲")
                    abierto.set(True)

            # --- 4. Los Efectos (Hover y Clic) ---
            # ¡La verdadera solución! Bindeamos a todos los widgets del header.
            widgets_clickeables = [header_frame, lbl_titulo, icon]

            def on_enter(event):
                header_frame.configure(fg_color="#3a3a3a") # Color hover
            def on_leave(event):
                header_frame.configure(fg_color="#2c2c2c") # Color normal

            for w in widgets_clickeables:
                w.bind("<Button-1>", toggle)
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)

            # --- 5. Llenar el contenido ---
            for texto, comando, icono_btn in items:
                crear_boton_nav(contenido, texto, comando, icono_btn)

        # = = = = = = = = = = = = = = = = = = = = = = = = = = =
        # --- CONSTRUYENDO EL SIDEBAR (¡Ahora dentro del scroll!) ---
        # = = = = = = = = = = = = = = = = = = = = = = = = = = =

        # Header del sidebar (igual que antes)
        # IMPORTANTE: El padre es 'self.sidebar' (que ya es scrollable)
        header = ctk.CTkFrame(self.sidebar, fg_color="#1a1a1a", height=90, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="HERRAMIENTAS", text_color="#7f7f7f", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=25, pady=(18, 2))
        ctk.CTkLabel(header, text="Álgebra Lineal", text_color=self.COLOR_TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=25)
        ctk.CTkFrame(self.sidebar, fg_color="#303030", height=2).pack(fill="x", pady=(5, 8))

        # Botón de Inicio (igual)
        crear_boton_nav(self.sidebar, "Inicio", self.vista_menu, "🏠")

        # --- ¡Llamando a los NUEVOS Acordeones! ---
        
        # Grupo 1 (Empezará abierto)
        crear_acordeon(self.sidebar, "SISTEMAS LINEALES", [
            ("Gauss-Jordan", lambda: self.preparar_matriz_unica("Gauss-Jordan"), "⚡"),
            ("Eliminación de Filas", lambda: self.preparar_matriz_unica("Eliminacion"), "🔍"),
            ("Método de Cramer", self.preparar_cramer, "🧮"),
            ("Sistema Homogéneo", self.preparar_matriz_homogeneo, "⚖️"),
        ], empezar_abierto=True) # <-- ¡Este empieza abierto!

        # Grupo 2
        crear_acordeon(self.sidebar, "OPERACIONES MATRICIALES", [
            ("Suma y Multiplicación", self.preparar_matrices_operaciones, "➕"),
            ("Transpuesta", self.preparar_matriz_transpuesta, "🔄"),
            ("Inversa", self.preparar_inversa_matriz, "🔺"),
            ("Determinantes", self.preparar_determinante, "📐"),
        ])

        # Grupo 3
        crear_acordeon(self.sidebar, "VECTORES Y TRANSFORMACIONES", [
            ("Independencia Lineal", self.preparar_vectores_independencia, "📊"),
            ("Probar Linealidad", self.preparar_linealidad, "📈"),
        ])
        
        # Grupo 4
        crear_acordeon(self.sidebar, "MÉTODOS NUMÉRICOS", [
            ("Método de Bisección", self._mostrar_vista_biseccion, "📉"),
            ("Método Falsa Posición", self._mostrar_vista_falsa_posicion, "📈")
        ])
        
        # --- FIN DE LOS ACORDEONES ---

        # Botón de Cierre
        ctk.CTkFrame(self.sidebar, fg_color="#303030", height=1).pack(fill="x", pady=(15, 10))
        crear_boton_nav(self.sidebar, "Cerrar Aplicación", self.destroy, "🚪", hover_color=self.COLOR_DANGER)

        version = ctk.CTkLabel(self.sidebar, text="v2.0 Moderna • Proyecto Académico",
                               text_color="#7f7f7f", font=("Segoe UI", 8))
        version.pack(side="bottom", pady=(10, 10))
    # ================================================================
    #               UTILIDADES VISUALES
    # ================================================================
    def clear_content(self):
        """Limpia todo el contenido del area central scrollable."""
        # Ahora limpiamos el 'content_scrollable' que creamos en _construir_shell
        for w in self.content_scrollable.winfo_children():
            w.destroy()
        # Devolvemos el frame scrollable para que las vistas se construyan DENTRO de él
        return self.content_scrollable

    def card(self, parent=None, pad=20):
        """Crea una tarjeta CTk moderna."""
        parent = parent or self.content_scrollable # Usamos el scrollable
        
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.COLOR_CARD,
            corner_radius=10, # ¡Esquinas redondeadas!
            border_width=1,
            border_color="#3a3a3a" # Borde sutil
        )
        frame.pack(padx=20, pady=10, fill="x")
        return frame

    def grid_inputs(self, parent, filas, columnas, width=8):
        """Crea una cuadricula de entradas con estilo CTk."""
        entradas = []
        g = ctk.CTkFrame(parent, fg_color="transparent")
        g.pack()
        
        for i in range(filas):
            row = []
            for j in range(columnas):
                e = ctk.CTkEntry(
                    g, 
                    width=width * 10, # CTk usa un 'width' diferente
                    justify="center",
                    font=("Consolas", 12),
                    fg_color="#3a3a3a",
                    border_color="#4a4a4a"
                )
                e.grid(row=i, column=j, padx=4, pady=4)
                row.append(e)
            entradas.append(row)
        return entradas
        
    # ================================================================
    #               MENU PRINCIPAL
    # ================================================================
    
    def vista_menu(self):
        """Pantalla inicial con tarjetas CTk."""
        content = self.clear_content() # Obtenemos el frame scrollable
        
        # Header principal
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", padx=22, pady=(25, 15))
        
        ctk.CTkLabel(header_frame, text="Panel Principal", text_color=self.COLOR_PRIMARY,
                     font=("Segoe UI", 28, "bold")).pack(anchor="w", pady=(0, 4))
        
        # Subtítulo
        sub_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        sub_frame.pack(anchor="w", fill="x")
        
        ctk.CTkLabel(sub_frame,
                     text="Selecciona una opción en la barra lateral o desde las tarjetas inferiores",
                     text_color=self.COLOR_SUB, font=("Segoe UI", 11)).pack(side="left")

        # --- ¡ARREGLADO! ---
        # Rellené la lista 'cards' con los datos de tu archivo original.
        cards = [
            ("Método Gauss-Jordan", "Resuelve sistemas y muestra pasos detallados", "⚡",
             lambda: self.preparar_matriz_unica("Gauss-Jordan")),
            ("Eliminación de Filas", "Aplica transformaciones elementales a matrices", "🔍",
             lambda: self.preparar_matriz_unica("Eliminacion")),
            ("Suma y Multiplicación", "Opera entre dos matrices con validación dimensional", "➕",
             self.preparar_matrices_operaciones),
            ("Independencia Lineal", "Analiza vectores y determina su independencia", "📊",
             self.preparar_vectores_independencia),
            ("Transpuesta de Matriz", "Calcula la transpuesta y muestra el proceso", "🔄",
             self.preparar_matriz_transpuesta),
            ("Sistema Homogéneo", "Resuelve sistemas Ax=0 con solución paramétrica", "⚖️",
             self.preparar_matriz_homogeneo),
        ]
        # --- FIN DEL ARREGLO ---

        # Contenedor de columnas (¡MÁS SIMPLE!)
        columns_frame = ctk.CTkFrame(content, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=12, pady=10)
        
        # Configuramos el grid para 2 columnas
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.columnconfigure(1, weight=1)

        # Bucle para crear tarjetas
        for i, (titulo, desc, icono, comando) in enumerate(cards):
            # Alternar entre columnas 0 y 1
            col = i % 2
            
            c = ctk.CTkFrame(columns_frame, fg_color=self.COLOR_CARD, corner_radius=10)
            c.grid(row=i//2, column=col, padx=8, pady=8, sticky="nsew")
            
            # Header de tarjeta con icono
            card_header = ctk.CTkFrame(c, fg_color="transparent")
            card_header.pack(fill="x", padx=15, pady=(12, 8))
            
            icon_label = ctk.CTkLabel(card_header, text=icono, text_color=self.COLOR_PRIMARY,
                                      font=("Segoe UI", 20))
            icon_label.pack(side="left", padx=(0, 10))
            
            # Título
            title_frame = ctk.CTkFrame(card_header, fg_color="transparent")
            title_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(title_frame, text=titulo, font=("Segoe UI", 14, "bold")).pack(anchor="w")
            ctk.CTkLabel(title_frame, text=desc, text_color=self.COLOR_SUB,
                         font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 0))
            
            # Botón de acción
            btn_frame = ctk.CTkFrame(c, fg_color="transparent")
            btn_frame.pack(fill="x", padx=15, pady=(8, 12))
            
            ctk.CTkButton(
                btn_frame, 
                text="Abrir herramienta", 
                fg_color=self.COLOR_PRIMARY,
                text_color="black",
                hover_color="#33D1FF",
                font=("Segoe UI", 11, "bold"),
                command=comando
            ).pack(side="right")
        
        # --- ¡ARREGLADO! ---
        # Footer del dashboard
        # Usamos 'content' como padre, no 'self.content' (que ya no existe)
        footer_card = self.card(content) 
        footer_frame = ctk.CTkFrame(footer_card, fg_color=self.COLOR_CARD)
        footer_frame.pack(fill="x", padx=20, pady=15)
        
        # Corregí el 'style=' por 'text_color='
        ctk.CTkLabel(footer_frame, 
                     text="💡 Tip: Usa el menú lateral para acceder a todas las herramientas disponibles",
                     text_color=self.COLOR_SUB, 
                     font=("Segoe UI", 10, "italic")).pack(side="left")
        
        # Corregí el 'style=' por 'text_color='
        ctk.CTkLabel(footer_frame, 
                     text=f"{len(cards)} herramientas disponibles", 
                     text_color=self.COLOR_SUB,
                     font=("Segoe UI", 10)).pack(side="right")
    # ================================================================
    #               METODOS DE MATRICES (CORREGIDOS)
    # ================================================================
    def preparar_matriz_unica(self, metodo):
        """Pantalla inicial para ingresar dimensiones del sistema."""
        self.metodo_actual = metodo
        content = self.clear_content() # <-- ARREGLO 1: Capturar 'content'

        ctk.CTkLabel(content, text=f"{metodo}", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8)) # <-- ARREGLO 2: 'content'

        c = self.card(content) # <-- ARREGLO 3: Pasar 'content'
        ctk.CTkLabel(
            c,
            text="Dimensiones de la matriz aumentada (m x n)",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="center", pady=(10, 15))

        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO 4: 'fg_color' en lugar de 'bg'
        f.pack(pady=15)

        ctk.CTkLabel(
            f, text="Filas:", text_color=self.COLOR_TEXT, # <-- ARREGLO 5: 'text_color'
            font=("Segoe UI", 13)
        ).grid(row=0, column=0, padx=10)

        self.entrada_filas = ctk.CTkEntry(
            f, width=100, font=("Segoe UI", 13), # (Ajustado el 'width')
            justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT, # <-- ARREGLO 6: 'fg_color', 'text_color'
            border_width=0 # <-- ARREGLO 7: Quitar 'relief'
        )
        self.entrada_filas.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(
            f, text="Columnas:", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 13)
        ).grid(row=0, column=2, padx=10)

        self.entrada_columnas = ctk.CTkEntry(
            f, width=100, font=("Segoe UI", 13),
            justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
            border_width=0
        )
        self.entrada_columnas.grid(row=0, column=3, padx=10)

        ctk.CTkButton(
            c, text="Crear Matriz", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.crear_interfaz_matriz_unica
        ).pack(anchor="center", pady=(20, 10))

    def preparar_matriz_homogeneo(self):
        """Pantalla inicial para sistemas homogeneos (solo coeficientes)."""
        self.metodo_actual = "Sistema Homogeneo"
        content = self.clear_content() # <-- ARREGLO

        ctk.CTkLabel(content, text="Sistema Homogeneo (Ax = 0)", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8)) # <-- ARREGLO

        c = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(
            c,
            text="Dimensiones de la matriz de coeficientes (m x n)",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="center", pady=(10, 15))

        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO
        f.pack(pady=15)

        ctk.CTkLabel(f, text="Filas (ecuaciones):", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=0, padx=10)
        self.entrada_filas = ctk.CTkEntry(f, width=100, font=("Segoe UI", 13),
                                          justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
                                          border_width=0)
        self.entrada_filas.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(f, text="Columnas (variables):", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=2, padx=10)
        self.entrada_columnas = ctk.CTkEntry(f, width=100, font=("Segoe UI", 13),
                                             justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
                                             border_width=0)
        self.entrada_columnas.grid(row=0, column=3, padx=10)

        ctk.CTkButton(
            c, text="Crear Matriz", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.crear_interfaz_matriz_homogeneo
        ).pack(anchor="center", pady=(20, 10))


    def crear_interfaz_matriz_unica(self):
        """Crea la cuadricula para ingresar un sistema de ecuaciones."""
        try:
            filas = int(self.entrada_filas.get())
            columnas = int(self.entrada_columnas.get())
            if filas <= 0 or columnas <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores validos para filas y columnas.")
            return

        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Ingrese los valores de la matriz aumentada", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8)) # <-- ARREGLO

        c = self.card(content) # <-- ARREGLO
        self.entradas_matriz = self.grid_inputs(c, filas, columnas)

        a = self.card(content) # <-- ARREGLO
        ctk.CTkButton(a, text="Resolver Sistema", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", command=self.resolver_sistema).pack(side="left", padx=8)
        ctk.CTkButton(a, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", command=lambda: self.preparar_matriz_unica(self.metodo_actual)).pack(side="left")

    def crear_interfaz_matriz_homogeneo(self):
        """Crea la cuadricula para ingresar solo los coeficientes del sistema homogeneo."""
        try:
            filas = int(self.entrada_filas.get())
            columnas = int(self.entrada_columnas.get())
            if filas <= 0 or columnas <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores validos para filas y columnas.")
            return

        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Ingrese los coeficientes de la matriz (Ax = 0)", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8)) # <-- ARREGLO

        c = self.card(content) # <-- ARREGLO
        self.entradas_matriz = self.grid_inputs(c, filas, columnas)

        a = self.card(content) # <-- ARREGLO
        ctk.CTkButton(a, text="Resolver Sistema Homogeneo", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", command=self.resolver_sistema_homogeneo_visual).pack(side="left", padx=8)
        ctk.CTkButton(a, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", command=self.preparar_matriz_homogeneo).pack(side="left")

    def resolver_sistema(self):
        """Llama al metodo correspondiente (Gauss-Jordan o Eliminacion)."""
        try:
            datos = [[float(e.get()) for e in fila] for fila in self.entradas_matriz]
        except ValueError:
            messagebox.showerror("Error", "Solo se permiten numeros.")
            return

        if self.metodo_actual == "Gauss-Jordan":
            resultados = resolver_gauss_jordan(datos)
            self.mostrar_resultados_gauss_jordan(resultados, datos)
        else:
            resultados = resolver_eliminacion_filas(datos)
            self.mostrar_resultados_eliminacion(resultados)

    def resolver_sistema_homogeneo_visual(self):
        """Lee la matriz de coeficientes, agrega columna de ceros y resuelve el sistema homogeneo."""
        try:
            matriz_coef = [[float(e.get()) for e in fila] for fila in self.entradas_matriz]
        except ValueError:
            messagebox.showerror("Error", "Solo se permiten numeros.")
            return

        matriz_aumentada = [fila + [0.0] for fila in matriz_coef]

        from logica_calculadora import resolver_sistema_homogeneo
        resultados = resolver_sistema_homogeneo(matriz_aumentada)

        self.mostrar_resultados_homogeneo(resultados, matriz_coef)
        
    # ------------------- Eliminacion de Filas -------------------
    def mostrar_resultados_eliminacion(self, resultados):
        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Resultado — Eliminación de Filas", 
                     font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        pasos_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(pasos_card, text="🔄 Proceso de eliminación:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        
        box = ctk.CTkTextbox(pasos_card, height=18*10, font=("Consolas", 11), # (Ajustada altura)
                             fg_color="#2a2a2a", text_color="#E0E0E0", border_width=0)
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for paso in resultados["pasos"]:
            if "Paso:" in paso:
                box.insert(END, f"🎯 {paso}\n", "paso")
            elif "Matriz en forma escalonada" in paso:
                box.insert(END, f"📊 {paso}\n", "importante")
            else:
                box.insert(END, paso + "\n")
        
        box.tag_configure("paso", foreground="#FF9800")
        box.tag_configure("importante", foreground="#4FC3F7")
        box.configure(state="disabled") # <-- ARREGLO: 'configure' en lugar de 'config'

        resumen_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(resumen_card, text="📈 Conclusión:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        
        tipo = resultados['tipo_solucion']
        if tipo == "Única":
            color = "#4CAF50"
            icon = "✅"
            info = f"{icon} SOLUCIÓN ÚNICA\n\n"
            info += "Solución del sistema:\n" + "\n".join(f"• x{i+1} = {v}" for i, v in enumerate(resultados['solucion']))
        elif tipo == "Infinita":
            color = "#FF9800"
            icon = "🔶"
            info = f"{icon} INFINITAS SOLUCIONES\n\nEl sistema tiene infinitas soluciones"
        else:
            color = "#F44336"
            icon = "❌"
            info = f"{icon} SISTEMA INCONSISTENTE\n\nEl sistema no tiene solución"
        
        ctk.CTkLabel(resumen_card, text=info, fg_color="#333333", text_color=color, # <-- ARREGLO
                     font=("Consolas", 12, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

    # ------------------- Gauss-Jordan -------------------
    def mostrar_resultados_gauss_jordan(self, resultados, matriz_original):
        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Resultado — Método Gauss-Jordan", 
                     font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        matriz_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(matriz_card, text="Matriz original del sistema:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        matriz_str = matriz_a_string(matriz_original, is_system=True)
        ctk.CTkLabel(matriz_card, text=matriz_str, fg_color="#333333", text_color="#4FC3F7", # <-- ARREGLO
                     font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO

        pasos_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(pasos_card, text="Proceso de resolución:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        box = ctk.CTkTextbox(pasos_card, height=18*10, font=("Consolas", 11), # (Ajustada altura)
                             fg_color="#2a2a2a", text_color="#E0E0E0", border_width=0)
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for p in resultados["pasos"]:
            if "Paso:" in p:
                box.insert(END, f"{p}\n", "paso")
            elif "Columna" in p and "Variable libre" in p:
                box.insert(END, f"{p}\n", "libre")
            else:
                box.insert(END, p + "\n")
        
        box.tag_configure("paso", foreground="#FF9800")
        box.tag_configure("libre", foreground="#4CAF50")
        box.configure(state="disabled") # <-- ARREGLO: 'configure'

        resumen_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(resumen_card, text="Conclusión:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        
        info = f"Tipo de Solución: {resultados['tipo_solucion']}\n"
        info += f"Columnas Pivote: {', '.join(map(str, resultados['columnas_pivote']))}\n"
        info += f"Variables Libres: {', '.join(resultados['variables_libres']) if resultados['variables_libres'] else 'No hay'}\n\n"
        
        if resultados['solucion'] is not None:
            info += "Solución del sistema:\n" + "\n".join(f"x{i+1} = {v}" for i, v in enumerate(resultados['solucion']))
        elif resultados['tipo_solucion'] == "Infinita":
            info += "El sistema tiene infinitas soluciones (variables libres presentes)"
        else:
            info += "El sistema no tiene solución única"
        
        color = "#4CAF50" if resultados['tipo_solucion'] == "Única" else "#FF9800" if resultados['tipo_solucion'] == "Infinita" else "#F44336"
        
        ctk.CTkLabel(resumen_card, text=info, fg_color="#333333", text_color=color, # <-- ARREGLO
                     font=("Consolas", 12, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO
        
        ctk.CTkButton(content, text="Resolver otro sistema", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", # <-- ARREGLO
            command=lambda: self.preparar_matriz_unica("Gauss-Jordan")).pack(side="left", padx=8, pady=20)
        ctk.CTkButton(content, text="Volver al Inicio", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", # <-- ARREGLO
            command=self.vista_menu).pack(side="left", padx=8, pady=20)
            
        
    def mostrar_resultados_homogeneo(self, resultados, matriz_original):
        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Resultado — Sistema Homogéneo (Ax = 0)", 
                     font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        matriz_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(matriz_card, text="Matriz original de coeficientes:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        matriz_str = matriz_a_string(matriz_original)
        ctk.CTkLabel(matriz_card, text=matriz_str, fg_color="#333333", text_color="#4FC3F7", # <-- ARREGLO
                     font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO

        pasos_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(pasos_card, text="Proceso de resolución:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        box = ctk.CTkTextbox(pasos_card, height=18*10, font=("Consolas", 11), # (Ajustada altura)
                             fg_color="#2a2a2a", text_color="#E0E0E0", border_width=0)
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for p in resultados["pasos"]:
            if "Paso:" in p:
                box.insert(END, f"{p}\n", "paso")
            elif "Variable libre" in p:
                box.insert(END, f"{p}\n", "libre")
            else:
                box.insert(END, p + "\n")
        
        box.tag_configure("paso", foreground="#FF9800")
        box.tag_configure("libre", foreground="#4CAF50")
        box.configure(state="disabled") # <-- ARREGLO

        resumen_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(resumen_card, text="Conclusión:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

        if resultados["tipo_solucion"] == "Única (trivial)":
            color = "#4CAF50"
            texto = "SOLUCIÓN ÚNICA (TRIVIAL)\n\n"
            texto += "x = 0 (solución trivial)\n"
            texto += f"Variables pivote: {', '.join(map(str, resultados['pivotes']))}"
        else:
            color = "#FF9800"
            texto = "INFINITAS SOLUCIONES\n\n"
            texto += f"Variables libres: {', '.join(resultados['variables_libres'])}\n"
            texto += f"Variables pivote: {', '.join(map(str, resultados['pivotes']))}\n\n"
            texto += "Solución general paramétrica:\n"
            
            for i in range(len(resultados["solucion_parametrica"])):
                vec = resultados["solucion_parametrica"][i]
                t = resultados["parametros"][i]
                texto += f"\nPara {t}:\n"
                for idx, coef in enumerate(vec):
                    if not es_casi_cero(coef):
                        texto += f"    x{idx+1} = {formatea_num(coef)} * {t}\n"

        ctk.CTkLabel(resumen_card, text=texto, fg_color="#333333", text_color=color, # <-- ARREGLO
                     font=("Consolas", 12, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO
        
        ctk.CTkButton(content, text="Resolver otro sistema", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", # <-- ARREGLO
            command=self.preparar_matriz_homogeneo).pack(side="left", padx=8, pady=20)
        ctk.CTkButton(content, text="Volver al Inicio", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", # <-- ARREGLO
            command=self.vista_menu).pack(side="left", padx=8, pady=20)
        
    # ------------------- Transpuesta -------------------
    def preparar_matriz_transpuesta(self):
        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Transpuesta de una Matriz", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8)) # <-- ARREGLO

        c = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c, text="Dimensiones de la matriz (m x n)", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        
        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO
        f.pack(pady=15)

        ctk.CTkLabel(f, text="Filas:", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=0, padx=10)
        self.entrada_filas_t = ctk.CTkEntry(f, width=100, font=("Segoe UI", 13), justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT, border_width=0)
        self.entrada_filas_t.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(f, text="Columnas:", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=2, padx=10)
        self.entrada_columnas_t = ctk.CTkEntry(f, width=100, font=("Segoe UI", 13), justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT, border_width=0)
        self.entrada_columnas_t.grid(row=0, column=3, padx=10)

        ctk.CTkButton(c, text="Crear Matriz", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", command=self.crear_interfaz_matriz_transpuesta).pack(anchor="center", pady=(20, 10))

    def preparar_linealidad(self):
        """Pantalla inicial para probar si T(x)=Ax+b es lineal."""
        content = self.clear_content() # <-- ARREGLO
        self.metodo_actual = "Linealidad"

        ctk.CTkLabel(
            content, # <-- ARREGLO
            text="Probar Linealidad de T(x) = A·x + b",
            font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY
        ).pack(anchor="w", padx=22, pady=(18, 8))

        c = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(
            c,
            text="Dimensiones de la matriz A (m × n)",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="center", pady=(10, 15))

        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO
        f.pack(pady=15)

        # FILAS (m)
        ctk.CTkLabel(
            f, text="Filas (m):", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 13)
        ).grid(row=0, column=0, padx=10)
        self.entrada_filas_lineal = ctk.CTkEntry(
            f, width=100, font=("Segoe UI", 13),
            justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
            border_width=0
        )
        self.entrada_filas_lineal.grid(row=0, column=1, padx=10)

        # COLUMNAS (n)
        ctk.CTkLabel(
            f, text="Columnas (n):", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 13)
        ).grid(row=0, column=2, padx=10)
        self.entrada_columnas_lineal = ctk.CTkEntry(
            f, width=100, font=("Segoe UI", 13),
            justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
            border_width=0
        )
        self.entrada_columnas_lineal.grid(row=0, column=3, padx=10)

        ctk.CTkButton(
            c, text="Crear Matrices A y b",
            fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.crear_interfaz_linealidad
        ).pack(anchor="center", pady=(20, 10))

    ''' (Tu código comentado se queda comentado) '''
        
    def preparar_inversa_matriz(self):
        """Pantalla inicial para ingresar dimensión de la matriz (n x n)."""
        self.metodo_actual = "Inversa"
        content = self.clear_content() # <-- ARREGLO

        ctk.CTkLabel(content, text="Inversa de una Matriz", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack( # <-- ARREGLO
            anchor="w", padx=22, pady=(18, 8)
        )

        c = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c, text="Dimensión de la matriz (n × n)", font=("Segoe UI", 14, "bold")).pack(
            anchor="center", pady=(10, 15)
        )

        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO
        f.pack(pady=15)

        ctk.CTkLabel(
            f, text="n:", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 13)
        ).grid(row=0, column=0, padx=10)

        self.entrada_n_inversa = ctk.CTkEntry(
            f, width=100, font=("Segoe UI", 13),
            justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
            border_width=0
        )
        self.entrada_n_inversa.grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            c, text="Crear Matriz", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.crear_interfaz_inversa
        ).pack(anchor="center", pady=(20, 10))
        
    def preparar_determinante(self):
        """Pantalla inicial para ingresar dimensión de la matriz (n x n)."""
        self.metodo_actual = "Determinante"
        content = self.clear_content() # <-- ARREGLO

        ctk.CTkLabel(content, text="Determinante de una Matriz", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack( # <-- ARREGLO
            anchor="w", padx=22, pady=(18, 8)
        )

        c = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(
            c,
            text="Dimensión de la matriz (n × n)",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="center", pady=(10, 15))

        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO
        f.pack(pady=15)

        ctk.CTkLabel(
            f, text="n:", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 13)
        ).grid(row=0, column=0, padx=10)

        self.entrada_n_det = ctk.CTkEntry(
            f, width=100, font=("Segoe UI", 13),
            justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
            border_width=0
        )
        self.entrada_n_det.grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            c, text="Crear Matriz", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.crear_interfaz_determinante
        ).pack(anchor="center", pady=(20, 10))
        
    def preparar_cramer(self):
        """Pantalla inicial para ingresar un sistema Ax=b (Regla de Cramer)."""
        self.metodo_actual = "Cramer"
        content = self.clear_content() # <-- ARREGLO

        ctk.CTkLabel(content, text="Método de Cramer", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack( # <-- ARREGLO
            anchor="w", padx=22, pady=(18, 8)
        )

        c = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c, text="Dimensión de la matriz A (n × n)", font=("Segoe UI", 14, "bold")).pack(
            anchor="center", pady=(10, 15)
        )

        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO
        f.pack(pady=15)

        ctk.CTkLabel(f, text="n:", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=0, padx=10)
        self.entrada_n_cramer = ctk.CTkEntry(f, width=100, font=("Segoe UI", 13),
                                             justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
                                             border_width=0)
        self.entrada_n_cramer.grid(row=0, column=1, padx=10)

        ctk.CTkButton(c, text="Crear Matrices A y b", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
                      command=self.crear_interfaz_cramer).pack(anchor="center", pady=(20, 10))

    def crear_interfaz_cramer(self):
        """Permite ingresar la matriz A y el vector b."""
        try:
            n = int(self.entrada_n_cramer.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor válido para n.")
            return

        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text=f"Ingrese los valores de A ({n}×{n}) y el vector b", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack( # <-- ARREGLO
            anchor="w", padx=22, pady=(18, 8)
        )

        c1 = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c1, text="Matriz A:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        self.matriz_A = self.grid_inputs(c1, n, n)

        c2 = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c2, text="Vector b:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        self.vector_b = self.grid_inputs(c2, n, 1)

        a = self.card(content) # <-- ARREGLO
        ctk.CTkButton(a, text="Resolver por Cramer", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", command=self.resolver_cramer_visual).pack(side="left", padx=8)
        ctk.CTkButton(a, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", command=self.preparar_cramer).pack(side="left", padx=8)

    def resolver_cramer_visual(self):
        
        from logica_calculadora import resolver_cramer, convertir_valor

        try:
            A = []
            for fila in self.matriz_A:
                A.append([convertir_valor(e.get()) for e in fila])

            b = [convertir_valor(self.vector_b[i][0].get()) for i in range(len(self.vector_b))]

        except Exception as e:
            messagebox.showerror("Error", f"Error en los datos ingresados: {str(e)}\n\nUse números o fracciones válidas (Ej: 1/2, -3/4)")
            return

        resultado = resolver_cramer(A, b)

        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Resultado — Regla de Cramer", # <-- ARREGLO
                     font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        pasos_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(pasos_card, text="Pasos del método",
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        box = ctk.CTkTextbox(pasos_card, height=20*10, font=("Consolas", 12), # (Ajustada altura)
                             fg_color="#2a2a2a", text_color="#E0E0E0", border_width=0)
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if "pasos" in resultado and resultado["pasos"]:
            for p in resultado["pasos"]:
                if "det(A)" in p:
                    box.insert(END, f"{p}\n", "detA")
                elif ("x" in p and "=" in p) or "Solución" in p:
                    box.insert(END, f"{p}\n", "solucion")
                elif "SOLUCIÓN FINAL" in p:
                    box.insert(END, f"{p}\n", "final")
                else:
                    box.insert(END, p + "\n")

            box.tag_configure("detA", foreground="#FF9800")
            box.tag_configure("solucion", foreground="#4CAF50")
            box.tag_configure("final", foreground="#4FC3F7")
        else:
            box.insert(END, "No hay pasos disponibles para mostrar.\n")

        box.configure(state="disabled") # <-- ARREGLO

        sol_decimal = resultado.get("solucion") or resultado.get("soluciones") or []
        sol_fraccion = resultado.get("solucion_fraccion") or resultado.get("soluciones_fraccion") or []

        if sol_decimal:
            sol_decimal_card = self.card(content) # <-- ARREGLO
            ctk.CTkLabel(sol_decimal_card, text="Solución en Decimal",
                         font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

            for i, decimal in enumerate(sol_decimal):
                texto_sol = f"x{i+1} = {decimal}"
                ctk.CTkLabel(sol_decimal_card, text=texto_sol,
                             text_color="#4CAF50", # <-- ARREGLO
                             font=("Consolas", 12, "bold")).pack(anchor="w", padx=20, pady=2)

        if sol_fraccion:
            sol_fraccion_card = self.card(content) # <-- ARREGLO
            ctk.CTkLabel(sol_fraccion_card, text="Solución en Fracciones",
                         font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
            for i, fraccion in enumerate(sol_fraccion):
                texto_frac = f"x{i+1} = {fraccion}"
                ctk.CTkLabel(sol_fraccion_card, text=texto_frac,
                        style="CardText.TLabel", foreground="#FFEB3B",
                        font=("Consolas", 12, "bold")).pack(anchor="w", padx=20, pady=2)


    def resolver_determinante_visual(self):
            from logica_calculadora import calcular_determinante_auto

            try:
                matriz = []
                for fila in self.entradas_matriz:
                    nueva_fila = []
                    for e in fila:
                        txt = e.get().strip()
                        if "/" in txt:
                            num, den = txt.split("/")
                            nueva_fila.append(int(num) / int(den))
                        else:
                            nueva_fila.append(float(txt))
                    matriz.append(nueva_fila)
            except:
                messagebox.showerror("Error", "Solo números y fracciones como 1/2")
                return

            resultado = calcular_determinante_auto(matriz)

            self.clear_content()
            ctk.CTkLabel(self.content, text="Determinante — Paso a Paso", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

            card = self.card()
            box = ctk.CTkTextbox(
                card, height=20, font=("Consolas", 11),
                bg="#2a2a2a", fg="white", bd=0, relief="flat"
            )
            box.pack(fill="both", expand=True, padx=10, pady=10)

            for p in resultado["pasos"]:
                box.insert("end", p + "\n")

            box.insert("end", f"\nRESULTADO FINAL: det(A) = {resultado['determinante']}\n")
            box.config(state="disabled")

    def mostrar_resultados_determinante(self, resultados, matriz_original):
        self.clear_content()
        ctk.CTkLabel(self.content, text=f"Resultado — {resultados['metodo']}", 
                font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        # ======== MATRIZ ORIGINAL ========
        matriz_card = self.card()
        ctk.CTkLabel(matriz_card, text="📊 Matriz original:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        matriz_str = matriz_a_string(matriz_original)
        ctk.CTkLabel(matriz_card, text=matriz_str, bg="#333333", fg="#4FC3F7",
                font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # ======== MÉTODO USADO ========
        metodo_card = self.card()
        ctk.CTkLabel(metodo_card, text="🎯 Método aplicado:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        ctk.CTkLabel(metodo_card, text=resultados["metodo"], bg="#333333", fg="#FF9800",
                font=("Consolas", 11, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # ======== PROCESO ========
        pasos_card = self.card()
        ctk.CTkLabel(pasos_card, text="🔄 Proceso de cálculo:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        box = ctk.CTkTextbox(pasos_card, height=18, font=("Consolas", 11),
                                        bg="#2a2a2a", fg="#E0E0E0", bd=0, relief="flat")
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for p in resultados["pasos"]:
            if "det(A)" in p or "Determinante" in p:
                box.insert(END, f"🎯 {p}\n", "importante")
            elif "=" in p and any(op in p for op in ["+", "-", "*"]):
                box.insert(END, f"🧮 {p}\n", "calculo")
            else:
                box.insert(END, p + "\n")
        
        box.tag_configure("importante", foreground="#4CAF50")
        box.tag_configure("calculo", foreground="#FF9800")
        box.config(state="disabled")

        # ======== RESULTADO FINAL ========
        res_card = self.card()
        ctk.CTkLabel(res_card, text="Resultado final:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        
        resultado_text = f"det(A) = {formatea_num(resultados['resultado'])}"
        if abs(resultados['resultado']) < 1e-9:
            resultado_text += "\n\nLa matriz es SINGULAR (no invertible)"
            color = "#F44336"
        else:
            resultado_text += "\n\nLa matriz es NO SINGULAR (invertible)"
            color = "#4CAF50"
        
        ctk.CTkLabel(res_card, text=resultado_text, bg="#333333", fg=color,
                font=("Consolas", 14, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=10)
    
    def crear_interfaz_inversa(self):
        try:
            n = int(self.entrada_n_inversa.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor valido para n.")
            return
        
        self.clear_content()
        ctk.CTkLabel(
            self.content,
            text="Ingrese los valores de la matriz A (n × n)",
            font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY
        ).pack(anchor="w", padx=22, pady=(18, 8))

        c = self.card()
        self.entradas_matriz_inversa = self.grid_inputs(c, n, n)

        a = self.card()
        ctk.CTkButton(
            a, text="Calcular Inversa", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.resolver_inversa_visual
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            a, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
            command=self.preparar_inversa_matriz
        ).pack(side="left")
        
        
    def crear_interfaz_determinante(self):
        """Crea la interfaz para ingresar una matriz cuadrada y calcular su determinante."""
        try:
            n = int(self.entrada_n_det.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor válido para n.")
            return

        self.clear_content()
        ctk.CTkLabel(
            self.content,
            text=f"Ingrese los valores de la matriz ({n}×{n})",
            font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY
        ).pack(anchor="w", padx=22, pady=(18, 8))

        c = self.card()
        self.entradas_matriz = self.grid_inputs(c, n, n)

        a = self.card()
        ctk.CTkButton(
            a, text="Calcular Determinante", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.resolver_determinante
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            a, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
            command=self.preparar_determinante
        ).pack(side="left", padx=8)

    def resolver_determinante(self):
        """Calcula el determinante de la matriz ingresada."""
        try:
            matriz = []
            for fila in self.entradas_matriz:
                nueva_fila = []
                for e in fila:
                    txt = e.get().strip()
                    if "/" in txt:
                        num, den = txt.split("/")
                        nueva_fila.append(float(num) / float(den))
                    else:
                        nueva_fila.append(float(txt))
                matriz.append(nueva_fila)
        except Exception as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}\n\nUse números o fracciones como: 1, 2.5, 1/2, -3/4")
            return

        # Verificar que sea cuadrada
        if len(matriz) != len(matriz[0]):
            messagebox.showerror("Error", "La matriz debe ser cuadrada para calcular el determinante.")
            return

        resultado = calcular_determinante_auto(matriz)
        self.mostrar_resultados_determinante(resultado, matriz)
        
    def crear_interfaz_transformacion(self):
        """Crea la interfaz para ingresar las expresiones de T(x)."""
        try:
            n = int(self.entrada_n_vars.get())   # Numero de variables
            m = int(self.entrada_m_ecuaciones.get())  # Numero de ecuaciones
            if n <= 0 or m <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores validos para n y m.")
            return
    
        self.num_variables = n
        self.num_ecuaciones = m
    
        self.clear_content()
        ctk.CTkLabel(
            self.content,
            text="Ingrese cada componente de T(x) (una por fila):",
            font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY
        ).pack(anchor="w", padx=22, pady=(18, 8))
    
        c = self.card()
        # Lista para guardar las entradas de expresiones
        self.entradas_expresiones = []
    
        for i in range(m):
            frame = ctk.CTkFrame(c, fg_color=self.COLOR_CARD)
            frame.pack(fill="x", pady=5, padx=10)
    
            etiqueta = ctk.CTkLabel(
                frame,
                text=f"Ecuacion {i+1}:",
                fg_color=self.COLOR_CARD,
                fg=self.COLOR_TEXT,
                font=("Segoe UI", 12)
            )
            etiqueta.pack(side="left", padx=10)
    
            entrada = ctk.CTkEntry(
                frame,
                width=50,
                font=("Segoe UI", 12),
                bg="#3a3a3a",
                fg=self.COLOR_TEXT,
                insertbackground=self.COLOR_PRIMARY,
                justify="left",
                relief="flat"
            )
            entrada.pack(side="left", padx=10, ipady=6, fill="x", expand=True)
    
            self.entradas_expresiones.append(entrada)
    
        # Botones inferiores
        a = self.card()
        ctk.CTkButton(
            a,
            text="Construir Matriz",
            fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.resolver_transformacion  # ESTE METODO VA EN EL BLOQUE 3
        ).pack(side="left", padx=8)
    
        ctk.CTkButton(
            a,
            text="Volver",
            fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
            command=self.preparar_construir_transformacion
        ).pack(side="left", padx=8)

    def resolver_transformacion(self):
        """Lee las expresiones, llama a la logica y muestra el resultado."""
        # Leer expresiones
        expresiones = []
        for entrada in self.entradas_expresiones:
            texto = entrada.get().strip()
            if not texto:
                messagebox.showerror("Error", "Todas las ecuaciones deben tener contenido.")
                return
            expresiones.append(texto)
    
        # Llamar a la logica (la implementaremos en logica_calculadora.py)
        try:
            from logica_calculadora import construir_matriz_transformacion
            pasos, matriz_A = construir_matriz_transformacion(expresiones, self.num_variables)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrio un problema: {str(e)}")
            return
    
        # Mostrar resultado
        self.mostrar_resultado_transformacion(pasos, matriz_A)
        
        
    def resolver_inversa_visual(self):
        try:
            matriz = [[float(e.get()) for e in fila] for fila in self.entradas_matriz_inversa]
        except ValueError:
            messagebox.showerror("Error", "Solo se permiten numeros en la matriz.")
            return
        resultado = calcular_inversa(matriz)

        self.mostrar_resultado_inversa(resultado, matriz)
        
        
    def mostrar_resultado_inversa(self, resultado, matriz_original):
        self.clear_content()
        ctk.CTkLabel(self.content, text="Resultado — Inversa de Matriz", 
                font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        # MATRIZ ORIGINAL
        matriz_card = self.card()
        ctk.CTkLabel(matriz_card, text="Matriz original:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        matriz_str = matriz_a_string(matriz_original)
        ctk.CTkLabel(matriz_card, text=matriz_str, bg="#333333", fg="#4FC3F7",
                font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # SEPARADOR
        ctk.CTkFrame(self.content, bg="#303030", height=1).pack(fill="x", padx=20, pady=10)

        # PROCESO
        pasos_card = self.card()
        ctk.CTkLabel(pasos_card, text="Pasos del proceso", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        box = ctk.CTkTextbox(pasos_card, height=18, font=("Consolas", 11),
                                        bg="#2a2a2a", fg="#E0E0E0", bd=0, relief="flat")
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for p in resultado.get("pasos", []):
            if "Pivotes encontrados" in p:
                box.insert(END, f"{p}\n", "importante")
            elif "NO es invertible" in p:
                box.insert(END, f"{p}\n", "error")
            elif "SÍ tiene n pivotes" in p:
                box.insert(END, f"{p}\n", "exito")
            elif "Matriz 2x2:" in p or "Determinante =" in p or "Se aplica" in p:
                box.insert(END, f"{p}\n", "naranja")
            else:
                box.insert(END, p + "\n")
        
        box.tag_configure("importante", foreground="#FF9800")
        box.tag_configure("error", foreground="#F44336")
        box.tag_configure("exito", foreground="#4CAF50")
        box.tag_configure("naranja", foreground="#FF9800")  # Color naranja para fórmulas
        box.config(state="disabled")

        # SEPARADOR
        ctk.CTkFrame(self.content, bg="#303030", height=1).pack(fill="x", padx=20, pady=10)

        # CONCLUSIÓN
        resumen_card = self.card()
        ctk.CTkLabel(resumen_card, text="Conclusión", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

        if not resultado["es_invertible"]:
            mensaje = "La matriz NO es invertible\n\n"
            mensaje += "Motivo:\n" + resultado.get("motivo", "No tiene n pivotes.")
            color = "#F44336"
        else:
            inversa = resultado.get("inversa", [])
            mensaje = "La matriz SÍ es invertible\n\n"
            mensaje += f"Matriz Original:\n{matriz_a_string(matriz_original)}\n\n"
            mensaje += f"Inversa A⁻¹:\n{matriz_a_string(inversa)}"
            color = "#4CAF50"

        ctk.CTkLabel(resumen_card, text=mensaje, bg="#333333", fg=color,
                font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # BOTONES
        ctk.CTkFrame(self.content, bg="#303030", height=1).pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(self.content, text="Calcular otra inversa", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
                command=self.preparar_inversa_matriz).pack(side="left", padx=8, pady=20)
        ctk.CTkButton(self.content, text="Volver al Inicio", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
                command=self.vista_menu).pack(side="left", padx=8, pady=20)


    def mostrar_resultado_transformacion(self, pasos, matriz_A):
        self.clear_content()
        ctk.CTkLabel(self.content, text="Resultado — Matriz de Transformación T(x)=A·x",
                font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        # PASOS
        pasos_card = self.card()
        ctk.CTkLabel(pasos_card, text="Pasos del proceso", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

        box = ctk.CTkTextbox(pasos_card, height=18, font=("Consolas", 12),
                                        bg="#2a2a2a", fg="#E0E0E0", bd=0, relief="flat")
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for p in pasos:
            if "Analizando" in p:
                box.insert(END, f"{p}\n", "analisis")  # <-- ARREGLADO
            elif "Coeficientes finales" in p:
                 box.insert(END, f"{p}\n", "resultado") # <-- ARREGLADO
            elif "Matriz A resultante" in p:
                box.insert(END, f"{p}\n", "final")     # <-- ARREGLADO
            else:
                box.insert(END, p + "\n")              # <-- ARREGLADO
        
        box.tag_configure("analisis", foreground="#FF9800")
        box.tag_configure("resultado", foreground="#4CAF50")
        box.tag_configure("final", foreground="#4FC3F7")
        box.config(state="disabled")

        # MATRIZ FINAL
        matriz_card = self.card()
        ctk.CTkLabel(matriz_card, text="Matriz A resultante", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

        texto_matriz = matriz_a_string(matriz_A)
        ctk.CTkLabel(matriz_card, text=texto_matriz, bg="#333333", fg="#4FC3F7",
                font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.content, text="Volver al Menu Principal",
            fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", command=self.vista_menu
        ).pack(anchor="center", pady=20) 

    def crear_interfaz_linealidad(self):
        """Crea la interfaz para ingresar A y b."""
        try:
            m = int(self.entrada_filas_lineal.get())
            n = int(self.entrada_columnas_lineal.get())
            if m <= 0 or n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos para m y n.")
            return

        self.clear_content()
        ctk.CTkLabel(
            self.content,
            text="Ingrese los valores de A y b",
            font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY
        ).pack(anchor="w", padx=22, pady=(18, 8))

        # ---- Card principal ----
        c = self.card()

        # Contenedor de A y b
        cont = ctk.CTkFrame(c, fg_color=self.COLOR_CARD)
        cont.pack(pady=10)

        # ===== MATRIZ A =====
        frameA = ctk.CTkFrame(cont, fg_color=self.COLOR_CARD)
        frameA.pack(side="left", padx=20)
        ctk.CTkLabel(frameA, text="Matriz A", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.entradas_matriz_a = self.grid_inputs(frameA, m, n)

        # ===== VECTOR b (columna m×1) =====
        frameB = ctk.CTkFrame(cont, fg_color=self.COLOR_CARD)
        frameB.pack(side="left", padx=20)
        ctk.CTkLabel(frameB, text="Vector b (m×1)", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        self.entradas_vector_b = []
        for i in range(m):
            e = ctk.CTkEntry(
                frameB, width=8, justify="center", bd=0,
                font=("Segoe UI", 12),
                bg="#3a3a3a", fg=self.COLOR_TEXT,
                insertbackground=self.COLOR_PRIMARY
            )
            e.pack(padx=4, pady=4, ipady=6)  
            self.entradas_vector_b.append(e)
       

        # ---- Botones inferior ----
        a = self.card()
        ctk.CTkButton(
            a, text="Probar Linealidad",
            fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.resolver_linealidad
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            a, text="Volver",
            fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
            command=self.preparar_linealidad
        ).pack(side="left", padx=8)

    def resolver_linealidad(self):
        """Calcula T(0) = A·0 + b y determina si es lineal."""
        try:
            A = [[float(e.get()) for e in fila] for fila in self.entradas_matriz_a]
            b = [float(e.get()) for e in self.entradas_vector_b]
        except ValueError:
            messagebox.showerror("Error", "Solo se permiten números en A y b.")
            return

        m = len(A)      # Filas
        n = len(A[0])   # Columnas

        # Vector cero de tamaño n (x en R^n)
        x0 = [0.0] * n

        # Calcular A·x0 (que debe dar vector cero de tamaño m)
        Ax0 = [sum(A[i][j] * x0[j] for j in range(n)) for i in range(m)]

        # T(0) = A·0 + b = b
        T0 = [Ax0[i] + b[i] for i in range(m)]

        # PASO A PASO
        pasos = []
        pasos.append("Definimos T(x) = A·x + b")
        pasos.append(f"\nVector 0 en R^{n}: {x0}")
        pasos.append(f"\n1) Calculamos A·0:")
        pasos.append(f"A·0 = {Ax0}")
        pasos.append(f"\n2) Ahora T(0) = A·0 + b:")
        pasos.append(f"T(0) = {Ax0} + {b} = {T0}")

        # Verificar si T(0) = 0
        es_lineal = all(abs(val) < 1e-9 for val in T0)

        if es_lineal:
            pasos.append("\nComo T(0) = 0, T ES transformación lineal ✅")
        else:
            pasos.append("\nComo T(0) ≠ 0, T NO es transformación lineal ❌")

        # Mostrar resultado final
        self.mostrar_resultado_linealidad(pasos, es_lineal)

    def mostrar_resultado_linealidad(self, pasos, es_lineal):
        self.clear_content()
        ctk.CTkLabel(self.content, text="Resultado — Linealidad de T(x) = A·x + b",
                font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        # PASOS
        pasos_card = self.card()
        ctk.CTkLabel(pasos_card, text="Pasos del proceso",
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

        box = ctk.CTkTextbox(pasos_card, height=18, font=("Consolas", 12),
                                        bg="#2a2a2a", fg="#E0E0E0", bd=0, relief="flat")
        box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for p in pasos:
            if "T(0)" in p and "=" in p:
                box.insert(END, f"{p}\n", "importante")
            elif "ES transformación lineal" in p:
                box.insert(END, f"{p}\n", "exito")
            elif "NO es transformación lineal" in p:
                box.insert(END, f"{p}\n", "error")
            else:
                box.insert(END, p + "\n")
        
        box.tag_configure("importante", foreground="#FF9800")
        box.tag_configure("exito", foreground="#4CAF50")
        box.tag_configure("error", foreground="#F44336")
        box.config(state="disabled")

        # CONCLUSIÓN
        resumen_card = self.card()
        ctk.CTkLabel(resumen_card, text="Conclusión",
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

        if es_lineal:
            conclusion = "T ES transformación lineal (b = 0)"
            color = "#4CAF50"
        else:
            conclusion = "T NO es transformación lineal (b ≠ 0)"
            color = "#F44336"

        ctk.CTkLabel(resumen_card, text=conclusion, bg="#333333", fg=color,
                font=("Consolas", 13, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.content, text="Volver al Menú Principal",
            fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", command=self.vista_menu
        ).pack(anchor="center", pady=20)
        
    # ------------------- Matriz Transpuesta -------------------
    def crear_interfaz_matriz_transpuesta(self):
        try:
            filas = int(self.entrada_filas_t.get())
            cols = int(self.entrada_columnas_t.get())
            if filas <= 0 or cols <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese numeros enteros positivos.")
            return
        self.clear_content()
        ctk.CTkLabel(self.content, text="Valores de la Matriz", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))
        c = self.card()
        self.entradas_matriz_t = self.grid_inputs(c, filas, cols)
        a = self.card()
        ctk.CTkButton(a, text="Calcular Transpuesta", fg_color=self.COLOR_ACCENT, text_color="black", hover_color="#FF9F5E", command=self.resolver_transpuesta).pack(side="left", padx=8)
        ctk.CTkButton(a, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", command=self.preparar_matriz_transpuesta).pack(side="left")

    def resolver_transpuesta(self):
        try:
            matriz = [[float(e.get()) for e in fila] for fila in self.entradas_matriz_t]
        except ValueError:
            messagebox.showerror("Error", "Solo se permiten números.")
            return
            
        resultado = calcular_operaciones_matrices(matriz, None, "transpuesta")
        self.mostrar_resultado_transpuesta(matriz, resultado)

    def mostrar_resultado_transpuesta(self, matriz, resultado):
        self.clear_content()
        ctk.CTkLabel(self.content, text="Resultado — Transpuesta", 
                font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))
        
        if isinstance(resultado, str):
            # Si hay error
            c = self.card()
            ctk.CTkLabel(c, text=resultado, font=("Segoe UI", 14, "bold"), foreground="#F44336").pack(anchor="w", padx=15)
            ctk.CTkButton(c, text="Volver al Menu Principal", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", 
                    command=self.vista_menu).pack(anchor="e", pady=8)
            return

        pasos = resultado.get("pasos", [])
        transpuesta = resultado.get("resultado", [])

        # MATRIZ ORIGINAL
        matriz_card = self.card()
        ctk.CTkLabel(matriz_card, text="Matriz original:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        matriz_str = matriz_a_string(matriz)
        ctk.CTkLabel(matriz_card, text=matriz_str, bg="#333333", fg="#4FC3F7",
                font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # SEPARADOR
        ctk.CTkFrame(self.content, bg="#303030", height=1).pack(fill="x", padx=20, pady=10)

        # PROCESO
        pasos_card = self.card()
        ctk.CTkLabel(pasos_card, text="Proceso de cálculo:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        box = ctk.CTkTextbox(pasos_card, height=14, font=("Consolas", 12), 
                                        bg="#2a2a2a", fg="#E0E0E0", bd=0, relief="flat")
        box.pack(fill="both", expand=True, padx=10, pady=6)
        
        for p in pasos:
            if "Fila" in p and "Columna" in p:
                box.insert(END, f"{p}\n", "conversion")
            elif "Resultado final" in p:
                box.insert(END, f"{p}\n", "final")
            else:
                box.insert(END, p + "\n")
        
        box.tag_configure("conversion", foreground="#FF9800")
        box.tag_configure("final", foreground="#4CAF50")
        box.config(state="disabled")

        # SEPARADOR
        ctk.CTkFrame(self.content, bg="#303030", height=1).pack(fill="x", padx=20, pady=10)

        # RESULTADO
        resumen_card = self.card()
        ctk.CTkLabel(resumen_card, text="Matriz transpuesta:", 
                font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        
        texto = f"Matriz Original ({len(matriz)}×{len(matriz[0])}):\n{matriz_a_string(matriz)}\n\n"
        texto += f"Matriz Transpuesta ({len(transpuesta)}×{len(transpuesta[0])}):\n{matriz_a_string(transpuesta)}"
        
        ctk.CTkLabel(resumen_card, text=texto, bg="#333333", fg="#4CAF50",
                font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # BOTONES
        ctk.CTkFrame(self.content, bg="#303030", height=1).pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(self.content, text="Calcular otra transpuesta", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
                command=self.preparar_matriz_transpuesta).pack(side="left", padx=8, pady=20)
        ctk.CTkButton(self.content, text="Volver al Inicio", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
                command=self.vista_menu).pack(side="left", padx=8, pady=20)

# ================================================================
    #           OPERACIONES (SUMA/MULTIPLICACION) (CORREGIDO)
    # ================================================================
    
    def preparar_matrices_operaciones(self):
        """Pantalla inicial para ingresar dimensiones de Matriz A y Matriz B."""
        self.metodo_actual = "Operaciones"
        content = self.clear_content() # <-- ARREGLO 1: Capturar 'content'

        ctk.CTkLabel(content, text="Operaciones con Matrices (A y B)", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8)) # <-- ARREGLO 2: 'content'

        # --- Tarjeta para Matriz A ---
        c_a = self.card(content) # <-- ARREGLO 3: Pasar 'content'
        ctk.CTkLabel(c_a, text="Dimensiones de la Matriz A (m x n)", font=("Segoe UI", 14, "bold")).pack(anchor="center", pady=(10, 15))
        
        f_a = ctk.CTkFrame(c_a, fg_color="transparent") # <-- ARREGLO 4: 'fg_color'
        f_a.pack(pady=15)

        ctk.CTkLabel(f_a, text="Filas (m):", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=0, padx=10) # <-- ARREGLO 5: 'text_color'
        self.entrada_filas_a = ctk.CTkEntry(f_a, width=100, font=("Segoe UI", 13),
                                          justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT, # <-- ARREGLO 6: 'fg_color', 'text_color'
                                          border_width=0) # <-- ARREGLO 7: Quitar 'relief'
        self.entrada_filas_a.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(f_a, text="Columnas (n):", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=2, padx=10)
        self.entrada_columnas_a = ctk.CTkEntry(f_a, width=100, font=("Segoe UI", 13),
                                             justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
                                             border_width=0)
        self.entrada_columnas_a.grid(row=0, column=3, padx=10)

        # --- Tarjeta para Matriz B ---
        c_b = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c_b, text="Dimensiones de la Matriz B (p x q)", font=("Segoe UI", 14, "bold")).pack(anchor="center", pady=(10, 15))
        
        f_b = ctk.CTkFrame(c_b, fg_color="transparent") # <-- ARREGLO
        f_b.pack(pady=15)

        ctk.CTkLabel(f_b, text="Filas (p):", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=0, padx=10)
        self.entrada_filas_b = ctk.CTkEntry(f_b, width=100, font=("Segoe UI", 13),
                                          justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
                                          border_width=0)
        self.entrada_filas_b.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(f_b, text="Columnas (q):", text_color=self.COLOR_TEXT, font=("Segoe UI", 13)).grid(row=0, column=2, padx=10)
        self.entrada_columnas_b = ctk.CTkEntry(f_b, width=100, font=("Segoe UI", 13),
                                             justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT,
                                             border_width=0)
        self.entrada_columnas_b.grid(row=0, column=3, padx=10)

        # --- Botón de Creación ---
        c_btn = self.card(content) # <-- ARREGLO
        ctk.CTkButton(
            c_btn, text="Crear Matrices", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.crear_interfaz_matrices_operaciones
        ).pack(anchor="center", pady=(20, 10))


    def crear_interfaz_matrices_operaciones(self):
        """Crea las cuadrículas para ingresar Matriz A y Matriz B."""
        try:
            self.filas_a = int(self.entrada_filas_a.get())
            self.columnas_a = int(self.entrada_columnas_a.get())
            self.filas_b = int(self.entrada_filas_b.get())
            self.columnas_b = int(self.entrada_columnas_b.get())
            
            if self.filas_a <= 0 or self.columnas_a <= 0 or self.filas_b <= 0 or self.columnas_b <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos para todas las dimensiones.")
            return

        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Ingrese los valores para A y B", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8)) # <-- ARREGLO

        # --- Matriz A ---
        c1 = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c1, text=f"Matriz A ({self.filas_a} x {self.columnas_a}):", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        self.entradas_matriz_a = self.grid_inputs(c1, self.filas_a, self.columnas_a)

        # --- Matriz B ---
        c2 = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c2, text=f"Matriz B ({self.filas_b} x {self.columnas_b}):", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        self.entradas_matriz_b = self.grid_inputs(c2, self.filas_b, self.columnas_b)

        # --- Botones de Acción ---
        a = self.card(content) # <-- ARREGLO
        
        # Validación de Suma/Resta
        if self.filas_a == self.filas_b and self.columnas_a == self.columnas_b:
            ctk.CTkButton(a, text="Sumar (A + B)", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", 
                          command=lambda: self.resolver_operaciones_visual("Suma")).pack(side="left", padx=8)
            ctk.CTkButton(a, text="Restar (A - B)", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
                          command=lambda: self.resolver_operaciones_visual("Resta")).pack(side="left", padx=8)
        else:
            ctk.CTkLabel(a, text=" (Suma/Resta deshabilitada: dimensiones no coinciden) ", text_color=self.COLOR_SUB).pack(side="left", padx=8)

        # Validación de Multiplicación
        if self.columnas_a == self.filas_b:
            ctk.CTkButton(a, text="Multiplicar (A * B)", fg_color=self.COLOR_ACCENT, text_color="black", hover_color="#FF9F5E",
                          command=lambda: self.resolver_operaciones_visual("Multiplicacion")).pack(side="left", padx=8)
        else:
            ctk.CTkLabel(a, text=" (Multiplicación deshabilitada: n != p) ", text_color=self.COLOR_SUB).pack(side="left", padx=8)

        ctk.CTkButton(a, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", 
                      command=self.preparar_matrices_operaciones).pack(side="right", padx=8)

    def resolver_operaciones_visual(self, operacion):
        """Lee los datos de las matrices A y B, llama a la lógica y muestra el resultado."""
        
        # Usar convertir_valor desde logica_calculadora para leer fracciones
        from logica_calculadora import calcular_operaciones_matrices, convertir_valor
        
        try:
            matriz_a = [[convertir_valor(e.get()) for e in fila] for fila in self.entradas_matriz_a]
            matriz_b = [[convertir_valor(e.get()) for e in fila] for fila in self.entradas_matriz_b]
        except Exception as e:
            messagebox.showerror("Error", f"Error en los datos ingresados: {str(e)}\n\nUse números o fracciones válidas (Ej: 1/2, -3/4)")
            return

        # Llamar a la lógica
        resultado = calcular_operaciones_matrices(matriz_a, matriz_b, operacion)
        
        # --- Mostrar Resultados ---
        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text=f"Resultado — {operacion} de Matrices", # <-- ARREGLO
                     font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        # --- Matriz A ---
        card_a = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(card_a, text="Matriz A:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        matriz_str_a = matriz_a_string(matriz_a)
        ctk.CTkLabel(card_a, text=matriz_str_a, fg_color="#333333", text_color="#4FC3F7", # <-- ARREGLO
                     font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # --- Matriz B ---
        card_b = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(card_b, text="Matriz B:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        matriz_str_b = matriz_a_string(matriz_b)
        ctk.CTkLabel(card_b, text=matriz_str_b, fg_color="#333333", text_color="#4FC3F7", # <-- ARREGLO
                     font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        # Separador
        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO

        # --- Resultado ---
        card_res = self.card(content) # <-- ARREGLO
        
        if resultado.get("error"):
            # Mostrar error
            ctk.CTkLabel(card_res, text="❌ Error en la Operación", font=("Segoe UI", 14, "bold"), text_color=self.COLOR_DANGER).pack(anchor="w", padx=15, pady=(5, 3))
            ctk.CTkLabel(card_res, text=resultado["error"], fg_color="#333333", text_color=self.COLOR_DANGER, # <-- ARREGLO
                         font=("Consolas", 12, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)
        else:
            # Mostrar resultado
            ctk.CTkLabel(card_res, text="✅ Resultado de la Operación (Decimal):", font=("Segoe UI", 14, "bold"), text_color="#4CAF50").pack(anchor="w", padx=15, pady=(5, 3))
            matriz_str_res = matriz_a_string(resultado["resultado"])
            ctk.CTkLabel(card_res, text=matriz_str_res, fg_color="#333333", text_color="#4CAF50", # <-- ARREGLO
                         font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)
            
            # Mostrar resultado en Fracciones (si existe)
            if "resultado_fraccion" in resultado:
                ctk.CTkLabel(card_res, text="✅ Resultado de la Operación (Fracción):", font=("Segoe UI", 14, "bold"), text_color="#4CAF50").pack(anchor="w", padx=15, pady=(15, 3))
                matriz_str_frac = matriz_a_string(resultado["resultado_fraccion"])
                ctk.CTkLabel(card_res, text=matriz_str_frac, fg_color="#333333", text_color="#4CAF50", # <-- ARREGLO
                             font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)
            
            # Mostrar pasos (si existen)
            if "pasos" in resultado and resultado["pasos"]:
                ctk.CTkLabel(card_res, text="📋 Pasos (Multiplicación):", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 3))
                box = ctk.CTkTextbox(card_res, height=15*10, font=("Consolas", 11), # (Ajustada altura)
                                     fg_color="#2a2a2a", text_color="#E0E0E0", border_width=0)
                box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
                for paso in resultado["pasos"]:
                    box.insert(END, paso + "\n")
                box.configure(state="disabled") # <-- ARREGLO

        # --- Botones ---
        btn_card = self.card(content) # <-- ARREGLO
        ctk.CTkButton(btn_card, text="Volver", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
                      command=self.preparar_matrices_operaciones).pack(side="left", padx=8, pady=20)

# ================================================================
    #           INDEPENDENCIA LINEAL (CORREGIDO)
    # ================================================================
    
    def preparar_vectores_independencia(self):
        """Interfaz para verificar independencia lineal con entrada matricial."""
        content = self.clear_content() # <-- ARREGLO 1: Capturar 'content'

        ctk.CTkLabel(
            content, # <-- ARREGLO 2: Usar 'content'
            text="Independencia Lineal",
            font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY
        ).pack(anchor="w", padx=22, pady=(18, 8))

        c = self.card(content) # <-- ARREGLO 3: Pasar 'content'
        ctk.CTkLabel(
            c,
            text="Dimensiones de la matriz de vectores (m x n)",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="center", pady=(10, 15))

        f = ctk.CTkFrame(c, fg_color="transparent") # <-- ARREGLO 4: 'fg_color'
        f.pack(pady=15)

        ctk.CTkLabel(f, text="Número de vectores (m):", text_color=self.COLOR_TEXT, # <-- ARREGLO 5: 'text_color'
                     font=("Segoe UI", 13)).grid(row=0, column=0, padx=10)
        self.entrada_filas_indep = ctk.CTkEntry(f, width=100, font=("Segoe UI", 13), # (Ajustado width)
                                              justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT, # <-- ARREGLO 6
                                              border_width=0) # <-- ARREGLO 7: (quitado 'relief')
        self.entrada_filas_indep.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(f, text="Dimensión de vectores (n):", text_color=self.COLOR_TEXT, # <-- ARREGLO
                     font=("Segoe UI", 13)).grid(row=0, column=2, padx=10)
        self.entrada_columnas_indep = ctk.CTkEntry(f, width=100, font=("Segoe UI", 13),
                                                   justify="center", fg_color="#3a3a3a", text_color=self.COLOR_TEXT, # <-- ARREGLO
                                                   border_width=0) # <-- ARREGLO
        self.entrada_columnas_indep.grid(row=0, column=3, padx=10)

        ctk.CTkButton(
            c, text="Crear Matriz de Vectores", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.crear_interfaz_independencia
        ).pack(anchor="center", pady=(20, 10))
        
        
    def crear_interfaz_independencia(self):
        """Crea la interfaz para ingresar la matriz de vectores."""
        try:
            filas = int(self.entrada_filas_indep.get()) 
            columnas = int(self.entrada_columnas_indep.get())
            if filas <= 0 or columnas <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos para filas y columnas.")
            return

        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(
            content, # <-- ARREGLO
            text=f"Ingrese los vectores (cada fila es un vector en R^{columnas})",
            font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY
        ).pack(anchor="w", padx=22, pady=(18, 8))

        c = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(c, text="Matriz de vectores (cada fila = un vector):", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 10))
        
        self.entradas_matriz_indep = self.grid_inputs(c, filas, columnas)

        a = self.card(content) # <-- ARREGLO
        ctk.CTkButton(
            a, text="Verificar Independencia", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF",
            command=self.resolver_independencia
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            a, text="Volver al Inicio", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A",
            command=self.vista_menu
        ).pack(side="left", padx=8)
        
    def resolver_independencia(self):
        """Resuelve la independencia lineal con la matriz ingresada."""
        # Esta función es pura lógica, no tiene errores de 'content' o estilo.
        # ¡Tu código original aquí es perfecto!
        try:
            vectores = []
            for fila in self.entradas_matriz_indep:
                vector_fila = []
                for entrada in fila:
                    valor = entrada.get().strip()
                    if not valor:
                        messagebox.showerror("Error", "Todos los campos deben estar llenos.")
                        return
                    if "/" in valor:
                        try:
                            num, den = valor.split("/")
                            vector_fila.append(float(num) / float(den))
                        except:
                            raise ValueError(f"Fracción inválida: {valor}")
                    else:
                        vector_fila.append(float(valor))
                vectores.append(vector_fila)
        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}\n\nUse números o fracciones como: 1, 2.5, 1/2, -3/4")
            return

        resultado = verificar_independencia_lineal(vectores)
        self.mostrar_resultado_independencia(vectores, resultado)
        
    def mostrar_resultado_independencia(self, vectores_originales, resultado):
        content = self.clear_content() # <-- ARREGLO
        ctk.CTkLabel(content, text="Resultado — Independencia Lineal", # <-- ARREGLO
                     font=("Segoe UI", 22, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w", padx=22, pady=(18, 8))

        matriz_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(matriz_card, text="Matriz original de vectores:", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
        
        matriz_str = matriz_a_string(vectores_originales)
        ctk.CTkLabel(matriz_card, text=matriz_str, fg_color="#333333", text_color="#4FC3F7", # <-- ARREGLO (fg_color, text_color)
                     font=("Consolas", 12), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO

        if "pasos" in resultado and resultado["pasos"]:
            pasos_card = self.card(content) # <-- ARREGLO
            ctk.CTkLabel(pasos_card, text="Proceso de verificación:", 
                         font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))
            
            box = ctk.CTkTextbox(pasos_card, height=12*10, font=("Consolas", 11), # (Ajustada altura)
                                 fg_color="#2a2a2a", text_color="#E0E0E0", border_width=0) # <-- ARREGLO (estilos)
            box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            for paso in resultado["pasos"]:
                if "Verificando independencia lineal" in paso:
                    box.insert(END, f"{paso}\n", "naranja")
                elif "Matriz inicial" in paso:
                    box.insert(END, f"{paso}\n", "importante")
                elif "Matriz en RREF" in paso:
                    box.insert(END, f"{paso}\n", "importante")
                elif "Cantidad de pivotes" in paso:
                    box.insert(END, f"{paso}\n", "naranja")
                elif "linealmente independientes" in paso.lower() or "linealmente dependientes" in paso.lower():
                    box.insert(END, f"{paso}\n", "conclusion")
                else:
                    box.insert(END, paso + "\n")
            
            box.tag_configure("naranja", foreground="#FF9800")
            box.tag_configure("importante", foreground="#4FC3F7")
            box.tag_configure("conclusion", foreground="#4CAF50")
            box.configure(state="disabled") # <-- ARREGLO ('configure')

        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO

        resumen_card = self.card(content) # <-- ARREGLO
        ctk.CTkLabel(resumen_card, text="Conclusión", 
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 3))

        if resultado.get("independientes", False):
            mensaje = "Los vectores son LINEALMENTE INDEPENDIENTES\n\n"
            mensaje += f"Se encontraron {len(resultado.get('pivotes', []))} pivotes\n"
            mensaje += "Todos los vectores son base del espacio generado"
            color = "#4CAF50"
        else:
            mensaje = "Los vectores son LINEALMENTE DEPENDIENTES\n\n"
            mensaje += f"Se encontraron {len(resultado.get('pivotes', []))} pivotes\n"
            mensaje += f"Vectores dependientes: {resultado.get('dependientes', [])}\n"
            mensaje += f"Vectores pivote (independientes): {resultado.get('pivotes', [])}"
            color = "#F44336"
        
        ctk.CTkLabel(resumen_card, text=mensaje, fg_color="#333333", text_color=color, # <-- ARREGLO
                     font=("Consolas", 12, "bold"), justify="left", anchor="w").pack(fill="x", padx=10, pady=5)

        ctk.CTkFrame(content, fg_color="#303030", height=1).pack(fill="x", padx=20, pady=10) # <-- ARREGLO
        
        ctk.CTkButton(content, text="Analizar otros vectores", fg_color=self.COLOR_PRIMARY, text_color="black", hover_color="#33D1FF", # <-- ARREGLO
            command=self.preparar_vectores_independencia
        ).pack(side="left", padx=8, pady=20)
        
        ctk.CTkButton(content, text="Volver al Inicio", fg_color=self.COLOR_DANGER, text_color="white", hover_color="#E46A6A", # <-- ARREGLO
            command=self.vista_menu
        ).pack(side="left", padx=8, pady=20)

# ============================================================================
#  NUEVO: VISTA MÉTODO DE BISECCIÓN (VERSIÓN CORREGIDA)
#  REEMPLAZA LA VERSIÓN ANTERIOR CON ESTA.
# ============================================================================

    def _mostrar_vista_biseccion(self):
        """Crea la interfaz para el método de Bisección usando CustomTkinter."""
        
        # --- ¡CORRECCIÓN CLAVE! ---
        # 1. Llama a TU función 'clear_content' (que usa 'content_scrollable')
        # 2. Guarda el frame que devuelve en la variable 'content'
        content = self.clear_content()
        # ----------------------------------------
        
        # Paleta de colores (basada en la de tu amigo, pero usando tus colores)
        COLOR_PRIMARY = self.COLOR_PRIMARY
        COLOR_ACCENT = self.COLOR_DANGER
        COLOR_SUCCESS = "#4caf50" # (O tu self.COLOR_SUCCESS si lo tienes)
        COLOR_MUTED = "#2a3442"   # (O tu self.COLOR_WARNING si lo tienes)
        
        # --- Variables de Control ---
        # (Usamos self.vars_biseccion que ya definiste en __init__)
        self.vars_biseccion = {
            'funcion': ctk.StringVar(value="x**3 - x - 2"), # Ejemplo
            'a': ctk.DoubleVar(value=1.0),
            'b': ctk.DoubleVar(value=2.0),
            'tol': ctk.DoubleVar(value=1e-4),
            'itmax': ctk.IntVar(value=100),
            'resultado': ctk.StringVar(value="")
        }

        # --- Card Superior: Entradas y Acciones ---
        # Dibuja en 'content', NO en 'self.content_frame'
        top_card = ctk.CTkFrame(content, corner_radius=10)
        top_card.pack(fill="x", padx=20, pady=(20, 10))

        # --- Fila 1: Función f(x) ---
        ctk.CTkLabel(top_card, text="f(x) =", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="e")
        
        self.entry_func_biseccion = ctk.CTkEntry(
            top_card, 
            textvariable=self.vars_biseccion['funcion'], 
            font=("Consolas", 16),
            height=40
        )
        self.entry_func_biseccion.grid(row=0, column=1, columnspan=7, padx=(0, 20), pady=(20, 10), sticky="ew")
        top_card.grid_columnconfigure(1, weight=1)

        # --- Fila 2: Parámetros ---
        params = [("a =", 'a'), ("b =", 'b'), ("ε =", 'tol'), ("Iter máx =", 'itmax')]
        col_idx = 0
        for label, key in params:
            ctk.CTkLabel(top_card, text=label, font=("Segoe UI", 12)).grid(
                row=1, column=col_idx, padx=(20, 5), pady=10, sticky="e")
            
            entry = ctk.CTkEntry(
                top_card, 
                textvariable=self.vars_biseccion[key], 
                font=("Consolas", 12),
                width=120
            )
            entry.grid(row=1, column=col_idx+1, padx=(0, 15), pady=10, sticky="w")
            col_idx += 2 # Siguiente par label/entry

        # --- Fila 3: Botones de Acción ---
        action_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        action_frame.grid(row=2, column=0, columnspan=8, padx=20, pady=(10, 20), sticky="w")
        
        ctk.CTkButton(
            action_frame, text="Calcular (Bisección)", 
            fg_color=COLOR_PRIMARY, text_color="white",
            command=self._on_biseccion_calcular
        ).pack(side="left", padx=(0, 8))
        
        # (Ya que tu app tiene Falsa Posición, puedes añadir el botón aquí si quieres)
        # ctk.CTkButton(
        #     action_frame, text="Calcular (Falsa Posición)", 
        #     fg_color=COLOR_SUCCESS, text_color="white",
        #     command=self._on_falsa_posicion_calcular # (Tendrías que crear esta)
        # ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_frame, text="Graficar", 
            fg_color=COLOR_ACCENT, text_color="white",
            command=self._on_biseccion_graficar
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_frame, text="Limpiar", 
            fg_color=COLOR_MUTED, text_color="white",
            command=self._on_biseccion_limpiar
        ).pack(side="left", padx=(0, 8))

        # --- Teclado Científico ---
        # Dibuja en 'content', NO en 'self.content_frame'
        kbd_card = ctk.CTkFrame(content, corner_radius=10)
        kbd_card.pack(fill="x", padx=20, pady=10)

        kbd_frame = ctk.CTkScrollableFrame(kbd_card, orientation="horizontal", height=60)
        kbd_frame.pack(fill="x", padx=10, pady=10)

        # Tokens para el teclado (de tu amigo)
        tokens_row1 = [("x", "x"), ("x²", "**2"), ("x³", "**3"), ("^", "**"), ("(", "("), (")", ")"),
                    ("|x|", "abs(x)"), ("√", "sqrt("), ("exp", "exp("), ("ln", "ln("), ("log", "log("),
                    ("sin(", "sin("), ("cos(", "cos("), ("tan(", "tan("), ("π", "pi"), ("e", "e")]
        
        for txt, ins in tokens_row1:
            btn = ctk.CTkButton(
                kbd_frame, text=txt, font=("Segoe UI", 11, "bold"), width=40,
                command=lambda t=ins: self._biseccion_insert_token(t)
            )
            btn.pack(side="left", padx=3)

        # --- Área de Resultados (Izquierda/Derecha) ---
        # Dibuja en 'content', NO en 'self.content_frame'
        middle_frame = ctk.CTkFrame(content, fg_color="transparent")
        middle_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        middle_frame.grid_columnconfigure(0, weight=1) # Izquierda crece
        middle_frame.grid_columnconfigure(1, weight=1) # Derecha crece
        middle_frame.grid_rowconfigure(0, weight=1)

        # --- Lado Izquierdo: Procedimiento y Resultado ---
        left_frame = ctk.CTkFrame(middle_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_frame.grid_rowconfigure(0, weight=1) # Procedimiento crece
        left_frame.grid_columnconfigure(0, weight=1)

        # Card Procedimiento
        proc_card = ctk.CTkFrame(left_frame, corner_radius=10)
        proc_card.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(proc_card, text="Procedimiento", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=15, pady=(10, 5))
        
        self.txt_proc_biseccion = ctk.CTkTextbox(
            proc_card, 
            font=("Consolas", 12), 
            wrap="none",
            state="disabled"
        )
        self.txt_proc_biseccion.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Card Resultado
        res_card = ctk.CTkFrame(left_frame, corner_radius=10)
        res_card.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ctk.CTkLabel(res_card, text="Resultado", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            res_card, 
            textvariable=self.vars_biseccion['resultado'],
            font=("Consolas", 14, "bold"),
            text_color="#a6ffea", # Color de éxito
            anchor="w", justify="left"
        ).pack(fill="x", padx=15, pady=(0, 15))


        # --- Lado Derecho: Gráfica ---
        graf_card = ctk.CTkFrame(middle_frame, corner_radius=10)
        graf_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(graf_card, text="Gráfica de f(x)", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=15, pady=(10, 5))

        # Configuración de Matplotlib para CustomTkinter
        # Configuración de Matplotlib para CustomTkinter
        bg_color = self.COLOR_CARD      # Tu color "#2b2b2b"
        text_color = self.COLOR_TEXT      # Tu color "#f2f2f2"
        plot_bg_color = self.COLOR_BG     # Tu color "#1e1e1e"
        
        self.fig_biseccion = Figure(figsize=(5, 4), dpi=100, facecolor=bg_color)
        self.ax_biseccion = self.fig_biseccion.add_subplot(111)
        
        self.ax_biseccion.set_facecolor(plot_bg_color)
        self.ax_biseccion.tick_params(axis='x', colors=text_color)
        self.ax_biseccion.tick_params(axis='y', colors=text_color)
        self.ax_biseccion.spines['left'].set_color(text_color)
        self.ax_biseccion.spines['right'].set_color(text_color)
        self.ax_biseccion.spines['top'].set_color(text_color)
        self.ax_biseccion.spines['bottom'].set_color(text_color)
        self.ax_biseccion.set_title("f(x)", color=text_color)
        self.ax_biseccion.grid(True, linestyle='--', alpha=0.3)
        
        self.fig_biseccion.tight_layout()

        self.canvas_biseccion = FigureCanvasTkAgg(self.fig_biseccion, master=graf_card)
        self.canvas_biseccion.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.canvas_biseccion.draw()


    def _biseccion_insert_token(self, token: str):
        """Inserta texto del teclado en el entry de función."""
        if not self.entry_func_biseccion: return
        self.entry_func_biseccion.insert(ctk.END, token)
        self.entry_func_biseccion.focus_set()


    def _on_biseccion_calcular(self):
        """Manejador para el botón 'Calcular' de Bisección."""
        try:
            expr = self.vars_biseccion['funcion'].get()
            a = self.vars_biseccion['a'].get()
            b = self.vars_biseccion['b'].get()
            tol = self.vars_biseccion['tol'].get()
            itmax = self.vars_biseccion['itmax'].get()

            # --- Llamada a la Lógica ---
            resultado = resolver_biseccion(expr, a, b, tol, itmax)
            # ---------------------------
            
            # Limpiar y mostrar procedimiento
            self.txt_proc_biseccion.configure(state="normal")
            self.txt_proc_biseccion.delete("1.0", ctk.END)
            
            if resultado['error_msg']:
                messagebox.showerror("Error de Cálculo", resultado['error_msg'])
                self.vars_biseccion['resultado'].set("")
                return
            
            self.txt_proc_biseccion.insert("1.0", "".join(resultado['pasos']))
            self.txt_proc_biseccion.configure(state="disabled")

            # Mostrar resultado
            sol = resultado['solucion']
            iters = resultado['iter']
            err = resultado['error']
            self.vars_biseccion['resultado'].set(
                f"BISECCIÓN: x ≈ {sol:.8f} | Iter: {iters} | Error: {err:.2e}"
            )
            
            # Graficar con la raíz marcada
            self._on_biseccion_graficar(marcar_raiz=sol)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")


    def _on_biseccion_graficar(self, marcar_raiz=None):
        """Manejador para el botón 'Graficar' de Bisección."""
        try:
            expr = self.vars_biseccion['funcion'].get()
            a = self.vars_biseccion['a'].get()
            b = self.vars_biseccion['b'].get()

            if a == b:
                messagebox.showerror("Error", "El intervalo [a, b] no puede ser cero.")
                return
            if a > b:
                a, b = b, a # Asegurar a < b
                
            # Ampliar un poco el rango para que se vea mejor
            rango = b - a
            xs = np.linspace(a - rango * 0.1, b + rango * 0.1, 500)
            
            # --- Llamada a la Lógica ---
            ys = eval_funcion_vectorial(expr, xs)
            # ---------------------------

            # Limpiar y dibujar
            self.ax_biseccion.cla()
            
            text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"][1]
            self.ax_biseccion.set_title(f"f(x) en [{a:g}, {b:g}]", color=text_color)
            self.ax_biseccion.grid(True, linestyle='--', alpha=0.3)
            
            # Graficar función
            self.ax_biseccion.plot(xs, ys, linewidth=2, color=self.COLOR_PRIMARY, label='f(x)')
            
            # Línea de y=0
            self.ax_biseccion.axhline(0, color=text_color, linewidth=1, alpha=0.5, linestyle='--')
            
            # Marcar la raíz si se pasó como argumento
            if marcar_raiz is not None:
                try:
                    y_raiz = eval_funcion_escalar(expr, marcar_raiz)
                    self.ax_biseccion.plot(
                        [marcar_raiz], [y_raiz], 'o', # Marcador
                        color=self.COLOR_DANGER, 
                        markersize=8, 
                        label=f'Raíz ≈ {marcar_raiz:.6f}'
                    )
                    self.ax_biseccion.axvline(marcar_raiz, color=self.COLOR_DANGER, linestyle=':', alpha=0.7)
                    
                    legend = self.ax_biseccion.legend(facecolor=self.fig_biseccion.get_facecolor(), labelcolor=text_color)
                    legend.get_frame().set_edgecolor("none")

                except Exception:
                    pass # No fallar si la raíz no se puede evaluar

            self.canvas_biseccion.draw()
            
        except Exception as e:
            messagebox.showerror("Error al Graficar", f"{e}")


    def _on_biseccion_limpiar(self):
        """Limpia la vista de Bisección."""
        self.vars_biseccion['resultado'].set("")
        
        self.txt_proc_biseccion.configure(state="normal")
        self.txt_proc_biseccion.delete("1.0", ctk.END)
        self.txt_proc_biseccion.configure(state="disabled")
        
        # Limpiar gráfica
        self.ax_biseccion.cla()
        text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"][1]
        self.ax_biseccion.set_title("f(x)", color=text_color)
        self.ax_biseccion.grid(True, linestyle='--', alpha=0.3)
        self.canvas_biseccion.draw()
# ============================================================================
#  FIN DE LA VISTA DE BISECCIÓN
# ============================================================================


#=========================================================#
# ============================================================================
#  INICIO: VISTA MÉTODO DE FALSA POSICIÓN
#  Pega todo este bloque (6 funciones) dentro de tu 'CalculadoraApp'
# ============================================================================

    def _mostrar_vista_falsa_posicion(self):
        """Crea la interfaz para el método de Falsa Posición."""
        
        content = self.clear_content() # ¡Usa tu función de limpiar!
        
        COLOR_PRIMARY = self.COLOR_PRIMARY
        COLOR_ACCENT = self.COLOR_DANGER
        COLOR_SUCCESS = "#4caf50" # O tu self.COLOR_SUCCESS
        COLOR_MUTED = self.COLOR_LIGHT # O tu self.COLOR_LIGHT

        # Usa las nuevas variables de instancia
        self.vars_falsa_posicion = {
            'funcion': ctk.StringVar(value="x**3 - x - 2"), # Ejemplo
            'a': ctk.DoubleVar(value=1.0),
            'b': ctk.DoubleVar(value=2.0),
            'tol': ctk.DoubleVar(value=1e-4),
            'itmax': ctk.IntVar(value=100),
            'resultado': ctk.StringVar(value="")
        }

        # --- Card Superior: Entradas y Acciones ---
        top_card = ctk.CTkFrame(content, corner_radius=10, fg_color=self.COLOR_CARD)
        top_card.pack(fill="x", padx=20, pady=(20, 10))

        # --- Fila 1: Función f(x) ---
        ctk.CTkLabel(top_card, text="f(x) =", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="e")
        
        self.entry_func_falsa_posicion = ctk.CTkEntry(
            top_card, 
            textvariable=self.vars_falsa_posicion['funcion'], 
            font=("Consolas", 16),
            height=40
        )
        self.entry_func_falsa_posicion.grid(row=0, column=1, columnspan=7, padx=(0, 20), pady=(20, 10), sticky="ew")
        top_card.grid_columnconfigure(1, weight=1)

        # --- Fila 2: Parámetros ---
        params = [("a =", 'a'), ("b =", 'b'), ("ε =", 'tol'), ("Iter máx =", 'itmax')]
        col_idx = 0
        for label, key in params:
            ctk.CTkLabel(top_card, text=label, font=("Segoe UI", 12)).grid(
                row=1, column=col_idx, padx=(20, 5), pady=10, sticky="e")
            entry = ctk.CTkEntry(
                top_card, 
                textvariable=self.vars_falsa_posicion[key], 
                font=("Consolas", 12),
                width=120
            )
            entry.grid(row=1, column=col_idx+1, padx=(0, 15), pady=10, sticky="w")
            col_idx += 2

        # --- Fila 3: Botones de Acción ---
        action_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        action_frame.grid(row=2, column=0, columnspan=8, padx=20, pady=(10, 20), sticky="w")
        
        ctk.CTkButton(
            action_frame, text="Calcular (Falsa Posición)", # <-- Título cambiado
            fg_color=COLOR_PRIMARY, text_color="white",
            command=self._on_falsa_posicion_calcular # <-- Función cambiada
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_frame, text="Graficar", 
            fg_color=COLOR_ACCENT, text_color="white",
            command=self._on_falsa_posicion_graficar # <-- Función cambiada
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_frame, text="Limpiar", 
            fg_color=COLOR_MUTED, text_color="white",
            command=self._on_falsa_posicion_limpiar # <-- Función cambiada
        ).pack(side="left", padx=(0, 8))

        # --- Teclado Científico ---
        kbd_card = ctk.CTkFrame(content, corner_radius=10, fg_color=self.COLOR_CARD)
        kbd_card.pack(fill="x", padx=20, pady=10)
        kbd_frame = ctk.CTkScrollableFrame(kbd_card, orientation="horizontal", height=60, fg_color="transparent")
        kbd_frame.pack(fill="x", padx=10, pady=10)

        tokens_row1 = [("x", "x"), ("x²", "**2"), ("x³", "**3"), ("^", "**"), ("(", "("), (")", ")"),
                    ("|x|", "abs(x)"), ("√", "sqrt("), ("exp", "exp("), ("ln", "ln("), ("log", "log("),
                    ("sin(", "sin("), ("cos(", "cos("), ("tan(", "tan("), ("π", "pi"), ("e", "e")]
        
        for txt, ins in tokens_row1:
            btn = ctk.CTkButton(
                kbd_frame, text=txt, font=("Segoe UI", 11, "bold"), width=40,
                command=lambda t=ins: self._falsa_posicion_insert_token(t) # <-- Función cambiada
            )
            btn.pack(side="left", padx=3)

        # --- Área de Resultados (Izquierda/Derecha) ---
        middle_frame = ctk.CTkFrame(content, fg_color="transparent")
        middle_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=1)
        middle_frame.grid_rowconfigure(0, weight=1)

        # --- Lado Izquierdo: Procedimiento y Resultado ---
        left_frame = ctk.CTkFrame(middle_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        proc_card = ctk.CTkFrame(left_frame, corner_radius=10, fg_color=self.COLOR_CARD)
        proc_card.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(proc_card, text="Procedimiento", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=15, pady=(10, 5))
        
        self.txt_proc_falsa_posicion = ctk.CTkTextbox(
            proc_card, 
            font=("Consolas", 12), 
            wrap="none",
            state="disabled",
            fg_color="#1e1e1e"
        )
        self.txt_proc_falsa_posicion.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        res_card = ctk.CTkFrame(left_frame, corner_radius=10, fg_color=self.COLOR_CARD)
        res_card.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ctk.CTkLabel(res_card, text="Resultado", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            res_card, 
            textvariable=self.vars_falsa_posicion['resultado'],
            font=("Consolas", 14, "bold"),
            text_color="#a6ffea",
            anchor="w", justify="left"
        ).pack(fill="x", padx=15, pady=(0, 15))


        # --- Lado Derecho: Gráfica ---
        graf_card = ctk.CTkFrame(middle_frame, corner_radius=10, fg_color=self.COLOR_CARD)
        graf_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(graf_card, text="Gráfica de f(x)", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=15, pady=(10, 5))

        bg_color = self.COLOR_CARD
        text_color = self.COLOR_TEXT
        plot_bg_color = self.COLOR_BG
        
        self.fig_falsa_posicion = Figure(figsize=(5, 4), dpi=100, facecolor=bg_color)
        self.ax_falsa_posicion = self.fig_falsa_posicion.add_subplot(111)
        
        self.ax_falsa_posicion.set_facecolor(plot_bg_color)
        self.ax_falsa_posicion.tick_params(axis='x', colors=text_color)
        self.ax_falsa_posicion.tick_params(axis='y', colors=text_color)
        self.ax_falsa_posicion.spines['left'].set_color(text_color)
        self.ax_falsa_posicion.spines['right'].set_color(text_color)
        self.ax_falsa_posicion.spines['top'].set_color(text_color)
        self.ax_falsa_posicion.spines['bottom'].set_color(text_color)
        self.ax_falsa_posicion.set_title("f(x)", color=text_color)
        self.ax_falsa_posicion.grid(True, linestyle='--', alpha=0.3, color="#555555")
        self.fig_falsa_posicion.tight_layout()

        self.canvas_falsa_posicion = FigureCanvasTkAgg(self.fig_falsa_posicion, master=graf_card)
        self.canvas_falsa_posicion.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.canvas_falsa_posicion.draw()


    def _falsa_posicion_insert_token(self, token: str):
        """Inserta texto del teclado en el entry de función."""
        if not self.entry_func_falsa_posicion: return
        self.entry_func_falsa_posicion.insert(ctk.END, token)
        self.entry_func_falsa_posicion.focus_set()


    def _on_falsa_posicion_calcular(self):
        """Manejador para el botón 'Calcular' de Falsa Posición."""
        try:
            expr = self.vars_falsa_posicion['funcion'].get()
            a = self.vars_falsa_posicion['a'].get()
            b = self.vars_falsa_posicion['b'].get()
            tol = self.vars_falsa_posicion['tol'].get()
            itmax = self.vars_falsa_posicion['itmax'].get()

            # --- ¡¡CAMBIO IMPORTANTE!! ---
            # Llamamos a la función de lógica correcta
            resultado = resolver_falsa_posicion_avanzado(expr, a, b, tol, itmax)
            # ---------------------------
            
            self.txt_proc_falsa_posicion.configure(state="normal")
            self.txt_proc_falsa_posicion.delete("1.0", ctk.END)
            
            if resultado['error_msg']:
                messagebox.showerror("Error de Cálculo", resultado['error_msg'])
                self.vars_falsa_posicion['resultado'].set("")
                self.txt_proc_falsa_posicion.configure(state="disabled")
                return
            
            self.txt_proc_falsa_posicion.insert("1.0", "".join(resultado['pasos']))
            self.txt_proc_falsa_posicion.configure(state="disabled")

            sol = resultado['solucion']
            iters = resultado['iter']
            fx = resultado['error_fx'] # <-- El diccionario devuelve 'error_fx'
            
            self.vars_falsa_posicion['resultado'].set(
                f"FALSA POSICIÓN: x ≈ {sol:.8f} | Iter: {iters} | f(x) = {fx:.2e}"
            )
            
            self._on_falsa_posicion_graficar(marcar_raiz=sol)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")


    def _on_falsa_posicion_graficar(self, marcar_raiz=None):
        """Manejador para el botón 'Graficar' de Falsa Posición."""
        try:
            expr = self.vars_falsa_posicion['funcion'].get()
            a = self.vars_falsa_posicion['a'].get()
            b = self.vars_falsa_posicion['b'].get()

            if a == b:
                messagebox.showerror("Error", "El intervalo [a, b] no puede ser cero.")
                return
            if a > b:
                a, b = b, a
                
            rango = b - a
            xs = np.linspace(a - rango * 0.1, b + rango * 0.1, 500)
            
            ys = eval_funcion_vectorial(expr, xs) # ¡Usa la lógica global!

            self.ax_falsa_posicion.cla()
            self.ax_falsa_posicion.set_title(f"f(x) en [{a:g}, {b:g}]", color=self.COLOR_TEXT)
            self.ax_falsa_posicion.grid(True, linestyle='--', alpha=0.3, color="#555555")
            
            self.ax_falsa_posicion.plot(xs, ys, linewidth=2, color=self.COLOR_PRIMARY, label='f(x)')
            self.ax_falsa_posicion.axhline(0, color=self.COLOR_TEXT, linewidth=1, alpha=0.5, linestyle='--')
            
            if marcar_raiz is not None:
                try:
                    y_raiz = eval_funcion_escalar(expr, marcar_raiz) # ¡Usa la lógica global!
                    self.ax_falsa_posicion.plot(
                        [marcar_raiz], [y_raiz], 'o',
                        color=self.COLOR_DANGER, 
                        markersize=8, 
                        label=f'Raíz ≈ {marcar_raiz:.6f}'
                    )
                    self.ax_falsa_posicion.axvline(marcar_raiz, color=self.COLOR_DANGER, linestyle=':', alpha=0.7)
                    
                    legend = self.ax_falsa_posicion.legend(facecolor=self.COLOR_CARD, labelcolor=self.COLOR_TEXT)
                    legend.get_frame().set_edgecolor(self.COLOR_LIGHT)

                except Exception:
                    pass

            self.canvas_falsa_posicion.draw()
            
        except Exception as e:
            messagebox.showerror("Error al Graficar", f"{e}")


    def _on_falsa_posicion_limpiar(self):
        """Limpia la vista de Falsa Posición."""
        self.vars_falsa_posicion['resultado'].set("")
        
        self.txt_proc_falsa_posicion.configure(state="normal")
        self.txt_proc_falsa_posicion.delete("1.0", ctk.END)
        self.txt_proc_falsa_posicion.configure(state="disabled")
        
        self.ax_falsa_posicion.cla()
        self.ax_falsa_posicion.set_title("f(x)", color=self.COLOR_TEXT)
        self.ax_falsa_posicion.grid(True, linestyle='--', alpha=0.3, color="#555555")
        self.canvas_falsa_posicion.draw()

    # ============================================================================
    #  FIN: VISTA MÉTODO DE FALSA POSICIÓN
    # ============================================================================








# ================================================================
#                        EJECUCION PRINCIPAL
# ================================================================
if __name__ == "__main__":
    app = CalculadoraApp()  # 1. Crea la aplicación (que ahora ES la ventana)
    app.mainloop()         # 2. Ejecútala