# MatrixScholar 📐 — Calculadora Avanzada

> Una potente calculadora de escritorio enfocada en Álgebra Lineal y Métodos Numéricos. Construida en Python, destaca por su arquitectura limpia (lógica separada de la interfaz) y su moderna interfaz de usuario creada con CustomTkinter.

Este proyecto fue desarrollado como una herramienta de estudio y demostración, combinando un robusto motor de cálculo (`logica_calculadora.py`) con una interfaz de usuario fluida y atractiva (`app_principal.py`).

## 🚀 Características Principales

* **Interfaz Gráfica Moderna:** Construida con **CustomTkinter**, ofreciendo un look & feel oscuro, limpio y profesional.
* **Navegación Eficiente:** Incluye una **barra de búsqueda** inteligente y una **barra lateral con menús acordeón** colapsables.
* **Graficación Integrada:** Utiliza **Matplotlib** para graficar funciones de métodos numéricos directamente dentro de la aplicación.
* **Parser de Funciones Inteligente:** Acepta escritura de funciones matemáticas de forma natural (ej. `2x^3 - x`, `sqrt(x) * sin(x)`) gracias a un normalizador de expresiones.
* **Arquitectura Separada:** El código está limpiamente dividido entre la lógica de cálculo (`logica_calculadora.py`) y la interfaz (`app_principal.py`).

---

## 🧮 Funcionalidades de Cálculo

### Álgebra Lineal
* **Resolución de Sistemas:**
    * Eliminación por Gauss-Jordan
    * Método de Eliminación de Filas (Forma Escalonada)
    * Regla de Cramer
    * Sistemas Homogéneos (Ax=0)
* **Operaciones con Matrices:**
    * Suma, Multiplicación (con validación de dimensiones)
    * Transpuesta
    * Cálculo de Inversa
    * Cálculo de Determinante
* **Análisis Vectorial:**
    * Verificación de Independencia Lineal

### Métodos Numéricos
* **Búsqueda de Raíces:**
    * Método de Bisección (con gráficas)
    * Método de Falsa Posición (con gráficas)

---

## 🛠️ Tecnologías Utilizadas

* **Python 3**
* **CustomTkinter:** Para la interfaz gráfica de usuario.
* **Matplotlib:** Para la incrustación de gráficas 2D.
* **NumPy:** Para el manejo eficiente de vectores en la graficación.
* **Tkinter:** Como base del sistema de ventanas.
