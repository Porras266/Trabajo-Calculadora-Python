from fractions import Fraction
import math
import numpy as np
import re
# ============================================================================
#  SECCIÓN 1: FUNCIONES AUXILIARES (UTILIDADES)
#  Estas funciones son pequeñas ayudas usadas en TODA la lógica posterior.
#  Hacen tareas repetitivas: copiar matrices, formatear números, detectar ceros, etc.
# ============================================================================

def es_casi_cero(numero, tolerancia=1e-9):
    """
    Verifica si un número es prácticamente cero.
    Esto es importante por los errores de punto flotante (ej: 0.000000001).
    """
    return abs(numero) < tolerancia


def formatea_num(numero, tolerancia=1e-9):
    """
    Formatea un número para impresión clara en pantalla.
    - Si es casi cero → muestra "0"
    - Si es entero → muestra sin decimales
    - Si es decimal → lo limita a 4 decimales
    """
    if es_casi_cero(numero, tolerancia):
        return "0"
    entero = int(round(numero))
    if abs(numero - entero) < tolerancia:
        return str(entero)
    return f"{numero:.4f}"


def copia_profunda(matriz):
    """
    Crea una copia PROFUNDA de la matriz.
    Se usa para no modificar la matriz original que dio el usuario.
    """
    return [fila[:] for fila in matriz]


def matriz_a_string(matriz, is_system=False):
    """
    Convierte una matriz en un texto legible.
    
    Si is_system = True → se asume que la última columna es el resultado
    y se muestra con un separador (|) como sistema de ecuaciones.
    
    Ejemplo:
    [ a b c | d ]
    """
    if not matriz:
        return "[ ]"
        
    filas = len(matriz)
    columnas = len(matriz[0])
    salida = []

    for i in range(filas):
        if is_system and columnas > 1:
            # Parte izquierda (coeficientes)
            izquierda = " ".join(formatea_num(matriz[i][j]) for j in range(columnas - 1))
            # Parte derecha (resultado)
            derecha = formatea_num(matriz[i][columnas - 1])
            salida.append(f"[ {izquierda} | {derecha} ]")
        else:
            # Solo matriz normal
            fila_str = " ".join(formatea_num(matriz[i][j]) for j in range(columnas))
            salida.append(f"[ {fila_str} ]")

    return "\n".join(salida)


def convertir_valor(texto):
        """
        Convierte un texto a número, aceptando fracciones como '1/2'
        """
        texto = texto.strip()
        
        # Si es fracción tipo a/b
        if "/" in texto:
            try:
                numerador, denominador = texto.split("/")
                return float(numerador) / float(denominador)
            except:
                raise ValueError(f"Fracción inválida: {texto}")
        
        # Si es número normal
        try:
            return float(texto)
        except:
            raise ValueError(f"Valor inválido: {texto}")

# ============================================================================
#  SECCIÓN 2: OPERACIONES ENTRE MATRICES
#  Aquí se implementan las operaciones básicas entre matrices:
#   - Suma
#   - Multiplicación
#   - Transpuesta
#  Nota: Esta función recibe la operación como texto ("suma", "multiplicacion", "transpuesta")
#        y ejecuta el bloque correspondiente.
# ============================================================================

def calcular_operaciones_matrices(matriz_a, matriz_b, operacion):
    """
    Realiza la suma, multiplicación o transpuesta de matrices.
    Además, en el caso de transpuesta devuelve pasos explicativos.

    Parámetros:
      - matriz_a: primera matriz (o matriz principal en transpuesta)
      - matriz_b: segunda matriz (solo aplica en suma y multiplicación)
      - operacion: "suma", "multiplicacion" o "transpuesta"

    Retorno:
      - En suma o multiplicación → matriz resultado o mensaje de error
      - En transpuesta → diccionario {"resultado": matriz, "pasos": [...]} o error
    """

    # ================== SUMA ==================
    if operacion == "suma":
        # Ambas matrices deben tener las mismas dimensiones
        if len(matriz_a) != len(matriz_b) or len(matriz_a[0]) != len(matriz_b[0]):
            return "Error: Las matrices deben tener las mismas dimensiones para la suma."

        filas = len(matriz_a)
        columnas = len(matriz_a[0])

        # Se suma elemento a elemento
        resultado = [
            [matriz_a[i][j] + matriz_b[i][j] for j in range(columnas)]
            for i in range(filas)
        ]
        return resultado

    # ================== MULTIPLICACIÓN ==================
    elif operacion == "multiplicacion":
        # Regla: columnas de A = filas de B
        if len(matriz_a[0]) != len(matriz_b):
            return "Error: El número de columnas de A debe ser igual al número de filas de B."

        filas_a = len(matriz_a)
        columnas_a = len(matriz_a[0])
        columnas_b = len(matriz_b[0])

        # Fórmula clásica: (A x B)[i][j] = sumatoria(A[i][k] * B[k][j])
        resultado = [
            [
                sum(matriz_a[i][k] * matriz_b[k][j] for k in range(columnas_a))
                for j in range(columnas_b)
            ]
            for i in range(filas_a)
        ]
        return resultado

    # ================== TRANSPUESTA ==================
    elif operacion == "transpuesta":
        # En este caso solo necesitamos una matriz (matriz_a)
        if matriz_a is None or not matriz_a:
            return "Error: Debes proporcionar una matriz válida para calcular la transpuesta."

        filas = len(matriz_a)
        columnas = len(matriz_a[0])

        pasos = []
        pasos.append("Matriz original A:\n" + matriz_a_string(matriz_a))
        pasos.append("Regla: (Las filas de A se convierten en columnas).")

        # Crear matriz transpuesta: cambiar filas por columnas
        transpuesta = [[matriz_a[j][i] for j in range(filas)] for i in range(columnas)]

        # Explicar paso a paso qué fila se convirtió en qué columna
        for i in range(columnas):
            fila_original = [matriz_a[j][i] for j in range(filas)]
            pasos.append(f"Fila {i+1} = Columna {i+1} de A → {fila_original}")

        pasos.append("Resultado final:\n" + matriz_a_string(transpuesta))

        # Devolvemos tanto el resultado como los pasos explicativos
        return {"resultado": transpuesta, "pasos": pasos}

    # ================== OPERACIÓN NO RECONOCIDA ==================
    else:
        return "Error: Operación no reconocida."


# ============================================================================
#  SECCIÓN 3: MÉTODO DE ELIMINACIÓN DE FILAS (Forma escalonada)
#  Este método lleva la matriz a forma ESCALONADA (Echelon)
#  Paso a paso:
#    1. Buscar pivote en cada columna
#    2. Hacer 1 el pivote (si es necesario)
#    3. Eliminar hacia ABAJO (hacer ceros debajo del pivote)
#    4. Determinar tipo de solución:
#        - Única
#        - Infinita
#        - Inconsistente
# ============================================================================

def resolver_eliminacion_filas(matriz_entrada):
    """Resuelve un sistema de ecuaciones por eliminación de filas con todos sus pasos."""
    matriz = copia_profunda(matriz_entrada)      # Trabajamos con copia
    filas = len(matriz)
    columnas = len(matriz[0]) - 1                # Última columna = término independiente
    pasos = [f"Matriz original:\n{matriz_a_string(matriz, is_system=True)}"]

    fila_pivote = 0  # Marca la fila donde colocaremos el siguiente pivote

    # Recorremos cada columna de coeficientes
    for indice_columna in range(columnas):
        if fila_pivote >= filas:
            break

        # 1) Buscar una fila que tenga un pivote (valor != 0) en esta columna
        mejor_fila = fila_pivote
        while mejor_fila < filas and es_casi_cero(matriz[mejor_fila][indice_columna]):
            mejor_fila += 1

        # Si todas son cero, no hay pivote en esta columna → variable libre
        if mejor_fila == filas:
            pasos.append(f"Paso: La columna {indice_columna+1} es cero. Se salta.")
            continue

        # 2) Si la mejor fila no es la actual, intercambiamos
        if mejor_fila != fila_pivote:
            matriz[fila_pivote], matriz[mejor_fila] = matriz[mejor_fila], matriz[fila_pivote]
            pasos.append(f"Paso: F{fila_pivote+1} <-> F{mejor_fila+1}")
            pasos.append(matriz_a_string(matriz, is_system=True))

        # 3) Normalizamos el pivote a 1 (F = F / pivote)
        pivote = matriz[fila_pivote][indice_columna]
        if not es_casi_cero(pivote) and not es_casi_cero(pivote - 1):
            pasos.append(f"Paso: F{fila_pivote+1} := F{fila_pivote+1} / {formatea_num(pivote)}")
            for j in range(indice_columna, columnas + 1):
                matriz[fila_pivote][j] /= pivote
            pasos.append(matriz_a_string(matriz, is_system=True))

        # 4) Eliminar hacia ABAJO (hacer ceros debajo del pivote)
        for indice_fila in range(fila_pivote + 1, filas):
            if es_casi_cero(matriz[indice_fila][indice_columna]):
                continue
            factor = matriz[indice_fila][indice_columna]
            if not es_casi_cero(factor):
                signo = "-" if factor >= 0 else "+"
                factor_absoluto = formatea_num(abs(factor))
                pasos.append(f"Paso: F{indice_fila+1} := F{indice_fila+1} {signo} {factor_absoluto} * F{fila_pivote+1}")
                for indice_j in range(indice_columna, columnas + 1):
                    matriz[indice_fila][indice_j] -= factor * matriz[fila_pivote][indice_j]
                pasos.append(matriz_a_string(matriz, is_system=True))

        fila_pivote += 1

    # Terminamos la forma escalonada
    pasos.append("\nMatriz en forma escalonada (Echelon):\n" + matriz_a_string(matriz, is_system=True))

    # ======================================================
    #  Evaluamos si el sistema es inconsistente
    #  (una fila con 0 0 0 | b   y b ≠ 0)
    # ======================================================
    inconsistente = False
    for indice_fila in range(filas):
        fila_ceros = all(es_casi_cero(matriz[indice_fila][indice_columna]) for indice_columna in range(columnas))
        if fila_ceros and not es_casi_cero(matriz[indice_fila][columnas]):
            inconsistente = True
            break

    if inconsistente:
        return {"tipo_solucion": "Inconsistente", "solucion": None, "pasos": pasos}

    # ======================================================
    #  Contamos pivotes para saber si hay solución única o infinita
    # ======================================================
    conteo_pivotes = 0
    for indice_fila in range(filas):
        # Si una fila tiene algún número != 0 en las columnas de coeficientes => cuenta como pivote
        if any(not es_casi_cero(matriz[indice_fila][indice_columna]) for indice_columna in range(columnas)):
            conteo_pivotes += 1

    # Si hay menos pivotes que columnas, hay variables libres → infinitas soluciones
    if conteo_pivotes < columnas:
        return {"tipo_solucion": "Infinita", "solucion": None, "pasos": pasos}

    # Si llegamos aquí, tiene solución única → hacemos sustitución hacia atrás
    solucion = [0.0] * columnas
    for i in range(columnas - 1, -1, -1):
        solucion[i] = matriz[i][columnas]
        for j in range(i + 1, columnas):
            solucion[i] -= matriz[i][j] * solucion[j]
        solucion[i] /= matriz[i][i]

    return {"tipo_solucion": "Única", "solucion": [formatea_num(s) for s in solucion], "pasos": pasos}


# ============================================================================
#  SECCIÓN 4: MÉTODO GAUSS-JORDAN (Forma reducida por filas - RREF)
#  Este método es más completo que la eliminación de filas.
#  Lleva la matriz a FORMA ESCALONADA REDUCIDA (RREF):
#     - Los pivotes son 1
#     - Hay ceros ARRIBA y ABAJO del pivote
#     - Permite leer la solución directamente
#  Además:
#     - Detecta variables libres
#     - Indica solución única, infinita o inconsistente
# ============================================================================

def resolver_gauss_jordan(matriz_entrada):
    """Resuelve un sistema por Gauss-Jordan enseñando sus pasos."""
    matriz = copia_profunda(matriz_entrada)
    filas = len(matriz)
    columnas = len(matriz[0]) - 1   # Última columna = término independiente
    pasos = [f"Matriz original:\n{matriz_a_string(matriz, is_system=True)}"]
    columnas_pivote = []            # Guardará las columnas donde hay pivote

    fila_pivote = 0  # Marca en qué fila colocaremos el próximo pivote

    # Recorremos cada columna de coeficientes
    for indice_columna in range(columnas):
        if fila_pivote >= filas:
            break

        # 1) Buscar la mejor fila para el pivote (la de mayor valor absoluto)
        mejor_fila = fila_pivote
        maximo_absoluto = abs(matriz[mejor_fila][indice_columna])
        for indice_fila in range(fila_pivote + 1, filas):
            if abs(matriz[indice_fila][indice_columna]) > maximo_absoluto:
                maximo_absoluto = abs(matriz[indice_fila][indice_columna])
                mejor_fila = indice_fila

        # Si toda la columna es cero → variable libre
        if es_casi_cero(maximo_absoluto):
            pasos.append(f"\nColumna {indice_columna+1}: No hay pivote (todos ceros). Variable libre: x{indice_columna+1}.")
            continue

        # 2) Si la fila con mejor pivote no es la actual, intercambiamos
        if mejor_fila != fila_pivote:
            pasos.append(f"\nPaso: F{fila_pivote+1} <-> F{mejor_fila+1}")
            matriz[fila_pivote], matriz[mejor_fila] = matriz[mejor_fila], matriz[fila_pivote]
            pasos.append(matriz_a_string(matriz, is_system=True))

        # 3) Normalizar el pivote a 1
        pivote = matriz[fila_pivote][indice_columna]
        if not es_casi_cero(pivote - 1):
            pasos.append(f"\nPaso: F{fila_pivote+1} := (1/{formatea_num(pivote)}) * F{fila_pivote+1}")
            for j in range(indice_columna, columnas + 1):
                matriz[fila_pivote][j] /= pivote
            pasos.append(matriz_a_string(matriz, is_system=True))

        # 4) Eliminar TODAS las otras entradas de la columna (arriba y abajo)
        pasos.append(f"\nPaso: Anulando otras entradas en la columna {indice_columna+1}.")
        for indice_fila in range(filas):
            if indice_fila == fila_pivote:
                continue
            factor = matriz[indice_fila][indice_columna]
            if not es_casi_cero(factor):
                signo = "-" if factor >= 0 else "+"
                factor_absoluto = formatea_num(abs(factor))
                pasos.append(f"  F{indice_fila+1} := F{indice_fila+1} {signo} {factor_absoluto} * F{fila_pivote+1}")
                for indice_j in range(indice_columna, columnas + 1):
                    matriz[indice_fila][indice_j] -= factor * matriz[fila_pivote][indice_j]
        pasos.append(matriz_a_string(matriz, is_system=True))

        # Guardamos qué columna tiene pivote
        columnas_pivote.append(indice_columna)
        fila_pivote += 1

    # Limpiar ceros pequeños (por errores de punto flotante)
    for indice_fila in range(filas):
        for indice_columna in range(columnas + 1):
            if es_casi_cero(matriz[indice_fila][indice_columna]):
                matriz[indice_fila][indice_columna] = 0.0

    # ======================================================
    #  Ahora determinamos el TIPO DE SOLUCIÓN
    # ======================================================

    # 1) Verificar si el sistema es INCONSISTENTE
    inconsistente = any(
        all(es_casi_cero(matriz[indice_fila][indice_columna]) for indice_columna in range(columnas))
        and not es_casi_cero(matriz[indice_fila][columnas])
        for indice_fila in range(filas)
    )

    if inconsistente:
        tipo = "Inconsistente"
        solucion = None

    # 2) Si hay pivotes en TODAS las columnas → solución única
    elif len(columnas_pivote) == columnas:
        tipo = "Única"
        solucion = [formatea_num(matriz[indice_fila][columnas]) for indice_fila in range(columnas)]

    # 3) Si faltan pivotes → variables libres → infinitas soluciones
    else:
        tipo = "Infinita"
        solucion = None

    return {
        "matriz_rref": matriz,                   
        "pasos": pasos,                             
        "columnas_pivote": [c + 1 for c in columnas_pivote],  
        "variables_libres": [f"x{c+1}" for c in range(columnas) if c not in columnas_pivote],
        "tipo_solucion": tipo,
        "solucion": solucion,                        
    }
    
    
# ============================================================================
#  SECCIÓN 5: RESOLVER SISTEMA HOMOGÉNEO (Ax = 0)
#  Un sistema homogéneo SIEMPRE tiene al menos la solución trivial (x = 0).
#  Usamos Gauss-Jordan para:
#     - Identificar variables pivote y libres
#     - Ver si hay solo solución trivial o infinitas soluciones
#     - Construir la solución general con parámetros t1, t2, ...
#
#  IMPORTANTE:
#     La matriz de entrada YA VIENE con la columna de ceros al final.
#     Ejemplo: [a b c | 0]
# ============================================================================

def resolver_sistema_homogeneo(matriz_entrada):
    """
    Resuelve un sistema homogéneo Ax = 0 usando Gauss-Jordan.
    La matriz_entrada debe incluir la columna de ceros al final.

    Retorna SIEMPRE un diccionario con:
        - tipo_solucion: "Única (trivial)" o "Infinitas"
        - pasos: lista con cada paso del proceso
        - variables_libres: lista con nombres de variables libres (x2, x3, ...)
        - pivotes: lista con índices de variables pivote (1-based)
        - solucion_parametrica: lista de vectores que representan cada parámetro
        - parametros: nombres de parámetros (t1, t2, ...)
        - matriz_rref: la matriz final en forma reducida
    """
    # ===============================
    # Validación inicial
    # ===============================
    if not matriz_entrada or not isinstance(matriz_entrada, list):
        return {
            "tipo_solucion": "Error",
            "pasos": ["La matriz está vacía o no es válida."],
            "variables_libres": [],
            "pivotes": [],
            "solucion_parametrica": [],
            "parametros": [],
            "matriz_rref": []
        }

    matriz = copia_profunda(matriz_entrada)
    filas = len(matriz)
    columnas_totales = len(matriz[0])

    if columnas_totales < 1:
        return {
            "tipo_solucion": "Error",
            "pasos": ["La matriz no tiene columnas."],
            "variables_libres": [],
            "pivotes": [],
            "solucion_parametrica": [],
            "parametros": [],
            "matriz_rref": matriz
        }

    columnas = columnas_totales - 1  # Última columna = 0
    pasos = [f"Matriz original (sistema homogéneo):\n{matriz_a_string(matriz, is_system=True)}"]

    fila_pivote = 0
    columnas_pivote = []

    # ============================================================================
    #    PROCESO GAUSS-JORDAN (similar al método general, pero adaptado)
    # ============================================================================
    for col in range(columnas):
        if fila_pivote >= filas:
            break

        # Buscar fila con pivote en esta columna
        mejor_fila = fila_pivote
        while mejor_fila < filas and es_casi_cero(matriz[mejor_fila][col]):
            mejor_fila += 1

        # Si no se encontró pivote → variable libre
        if mejor_fila == filas:
            pasos.append(f"Columna {col+1}: Sin pivote, variable libre: x{col+1}")
            continue

        # Intercambiar filas si es necesario
        if mejor_fila != fila_pivote:
            pasos.append(f"Paso: F{fila_pivote+1} <-> F{mejor_fila+1}")
            matriz[fila_pivote], matriz[mejor_fila] = matriz[mejor_fila], matriz[fila_pivote]
            pasos.append(matriz_a_string(matriz, is_system=True))

        # Normalizar el pivote a 1
        pivote = matriz[fila_pivote][col]
        if not es_casi_cero(pivote - 1):
            pasos.append(f"Paso: F{fila_pivote+1} := F{fila_pivote+1} / {formatea_num(pivote)}")
            for j in range(col, columnas + 1):
                matriz[fila_pivote][j] /= pivote
            pasos.append(matriz_a_string(matriz, is_system=True))

        # Eliminar hacia arriba y abajo
        for f in range(filas):
            if f != fila_pivote and not es_casi_cero(matriz[f][col]):
                factor = matriz[f][col]
                pasos.append(f"Paso: F{f+1} := F{f+1} - {formatea_num(factor)} * F{fila_pivote+1}")
                for j in range(col, columnas + 1):
                    matriz[f][j] -= factor * matriz[fila_pivote][j]
                pasos.append(matriz_a_string(matriz, is_system=True))

        columnas_pivote.append(col)
        fila_pivote += 1

    pasos.append("\nMatriz en RREF:\n" + matriz_a_string(matriz, is_system=True))

    pivotes = columnas_pivote
    libres = [c for c in range(columnas) if c not in pivotes]

    # ============================================================================
    #   CASO 1: NO hay variables libres → Solo solución trivial x = 0
    # ============================================================================
    if not libres:
        pasos.append("\nNo hay variables libres → solución única (trivial): x = 0")
        return {
            "tipo_solucion": "Única (trivial)",
            "pasos": pasos,
            "variables_libres": [],
            "pivotes": [p+1 for p in pivotes],
            "solucion_parametrica": [],
            "parametros": [],
            "matriz_rref": matriz
        }

    # ============================================================================
    #   CASO 2: Hay variables libres → Infinitas soluciones
    #   Construimos solución general en función de parámetros t1, t2, ...
    # ============================================================================
    pasos.append(f"\nVariables pivote: {', '.join('x'+str(p+1) for p in pivotes)}")
    pasos.append(f"Variables libres: {', '.join('x'+str(l+1) for l in libres)}")

    coeficientes = []   # Cada vector corresponde a una solución base
    parametros = []     # Ej: t1, t2, ...

    for idx, col_libre in enumerate(libres):
        t = f"t{idx+1}"
        parametros.append(t)
        
        # Vector inicial: la variable libre = 1, las demás = 0
        vector_param = [0] * columnas
        vector_param[col_libre] = 1

        # Ahora resolvemos para las variables pivote usando la RREF
        for i, p in enumerate(pivotes):
            valor = matriz[i][col_libre]
            vector_param[p] = -valor if not es_casi_cero(valor) else 0

        coeficientes.append(vector_param)

    # Mostrar solución general en pasos
    pasos.append("\nSolución general:")
    for idx, vec in enumerate(coeficientes):
        t = parametros[idx]
        for var_index, coef in enumerate(vec):
            if not es_casi_cero(coef):
                pasos.append(f"x{var_index+1} = {formatea_num(coef)} * {t}")

    return {
        "tipo_solucion": "Infinitas",
        "pasos": pasos,
        "variables_libres": [f"x{l+1}" for l in libres],
        "pivotes": [p+1 for p in pivotes],
        "solucion_parametrica": coeficientes,
        "parametros": parametros,
        "matriz_rref": matriz
    }


# ============================================================================
#  CALCULAR INVERSA DE UNA MATRIZ CUADRADA
#
#  Existen dos formas (según el tamaño):
#
#  Caso 1: Matriz 2x2 → Se aplica fórmula directa (primer teorema)
#        A = [a b]
#            [c d]
#        inv(A) = (1/det) * [ d -b
#                            -c  a ]
#
#  Caso 2: Matriz n >= 3 → Usamos Gauss-Jordan sobre [A | I]
#        - Verificamos que tenga n pivotes (es invertible)
#        - Construimos la aumentada [A | I]
#        - Aplicamos Gauss-Jordan
#        - Obtenemos [I | A⁻¹]
#
# ============================================================================

def calcular_inversa(matriz_original):
    """
    Calcula la inversa de una matriz cuadrada A.

    - Si es 2x2: usa la fórmula (primer teorema).
    - Si es de tamaño >=3: usa Gauss-Jordan con [A|I] (segundo teorema).
    """
    pasos = []
    A = copia_profunda(matriz_original)
    n = len(A)

    # =====================================================
    # Verificar que sea cuadrada
    # =====================================================
    if any(len(fila) != n for fila in A):
        pasos.append("La matriz no es cuadrada, por lo tanto no es invertible.")
        return {
            "es_invertible": False,
            "inversa": None,
            "motivo": "La matriz no es cuadrada.",
            "pasos": pasos
        }

    pasos.append("Matriz original A:")
    pasos.append(matriz_a_string(A))

    # =====================================================
    # CASO 1: MATRIZ 2x2 → USAR FÓRMULA DIRECTA
    # =====================================================
    if n == 2:
        pasos.append("Matriz 2x2: se aplica el PRIMER TEOREMA (fórmula de la inversa).")

        a, b = A[0][0], A[0][1]
        c, d = A[1][0], A[1][1]
        det = a * d - b * c

        pasos.append(f"Determinante = ad - bc = {formatea_num(a)}*{formatea_num(d)} - {formatea_num(b)}*{formatea_num(c)}")
        pasos.append(f"Determinante = {formatea_num(det)}")

        if es_casi_cero(det):
            pasos.append("El determinante es 0 → la matriz es singular, NO es invertible.")
            return {
                "es_invertible": False,
                "inversa": None,
                "motivo": "Determinante = 0 en matriz 2x2.",
                "pasos": pasos
            }

        inv_det = 1 / det
        inversa = [
            [ d * inv_det, -b * inv_det],
            [-c * inv_det,  a * inv_det]
        ]

        pasos.append("Se aplica (1/det) * [d, -b; -c, a]:")
        pasos.append(matriz_a_string(inversa))

        return {
            "es_invertible": True,
            "inversa": inversa,
            "motivo": "",
            "pasos": pasos
        }

    # =====================================================
    # CASO 2: MATRIZ n>=3 → USAR GAUSS-JORDAN (TEOREMA 2)
    # =====================================================
    pasos.append("Matriz de tamaño >= 3: se aplica el SEGUNDO TEOREMA (Gauss-Jordan con [A|I]).")

    # 1) Primero verificar invertibilidad usando Gauss-Jordan en A|0
    matriz_temp = [fila[:] + [0.0] for fila in A]  # Aumentamos con columna de ceros
    rref_info = resolver_gauss_jordan(matriz_temp)
    pivotes = rref_info["columnas_pivote"]
    num_pivotes = len(pivotes)

    pasos.append("Verificando número de pivotes:")
    pasos.append(f"Pivotes encontrados: {num_pivotes} de {n}")

    # Si no hay n pivotes → no es invertible
    if num_pivotes < n:
        pasos.append("La matriz NO es invertible porque no tiene pivotes en todas las columnas.")
        pasos.append("Equivalente a: Ax=0 tiene infinitas soluciones / columnas dependientes.")
        # Añadimos pasos del Gauss-Jordan para mostrar el proceso
        pasos.extend(rref_info["pasos"])
        return {
            "es_invertible": False,
            "inversa": None,
            "motivo": "No tiene n pivotes (es singular).",
            "pasos": pasos
        }

    pasos.append("La matriz SÍ tiene n pivotes → es invertible.")
    pasos.append("=== Ahora se construye [A | I] y se aplica Gauss-Jordan ===")

    # 2) Construir [A | I]
    identidad = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    aumentada = [A[i] + identidad[i] for i in range(n)]

    pasos.append("Matriz aumentada [A | I]:")
    pasos.append(matriz_a_string(aumentada))

    # 3) Aplicar Gauss-Jordan a la matriz aumentada
    matriz = copia_profunda(aumentada)
    fila_pivote = 0
    columnas_totales = len(matriz[0])

    for col in range(n):
        # Buscar fila con mejor pivote
        mejor = fila_pivote
        for f in range(fila_pivote + 1, n):
            if abs(matriz[f][col]) > abs(matriz[mejor][col]):
                mejor = f

        if es_casi_cero(matriz[mejor][col]):
            continue

        if mejor != fila_pivote:
            pasos.append(f"F{fila_pivote+1} <-> F{mejor+1}")
            matriz[fila_pivote], matriz[mejor] = matriz[mejor], matriz[fila_pivote]
            pasos.append(matriz_a_string(matriz))

        pivote = matriz[fila_pivote][col]
        if not es_casi_cero(pivote - 1):
            pasos.append(f"F{fila_pivote+1} := F{fila_pivote+1} / {formatea_num(pivote)}")
            for j in range(col, columnas_totales):
                matriz[fila_pivote][j] /= pivote
            pasos.append(matriz_a_string(matriz))

        # Eliminar hacia arriba y abajo
        for f in range(n):
            if f != fila_pivote:
                factor = matriz[f][col]
                if not es_casi_cero(factor):
                    pasos.append(f"F{f+1} := F{f+1} - {formatea_num(factor)} * F{fila_pivote+1}")
                    for j in range(col, columnas_totales):
                        matriz[f][j] -= factor * matriz[fila_pivote][j]
                    pasos.append(matriz_a_string(matriz))
        fila_pivote += 1

    # Limpiar errores numéricos pequeños
    for i in range(n):
        for j in range(columnas_totales):
            if es_casi_cero(matriz[i][j]):
                matriz[i][j] = 0.0

    # Extraer la parte derecha como la inversa
    inversa = [fila[n:] for fila in matriz]
    
    
    # Convertir cada elemento de la inversa a fracción simplificada
    inversa_frac = [[str(Fraction(x).limit_denominator()) for x in fila] for fila in inversa]


    pasos.append("Matriz final [I | A⁻¹]:")
    pasos.append(matriz_a_string(matriz))
    pasos.append("Inversa A⁻¹:")
    pasos.append(matriz_a_string(inversa))

    return {
        "es_invertible": True,
        "inversa": inversa,
        "motivo": "",
        "pasos": pasos
    }

# ============================================================================
#  SECCIÓN 7: CONSTRUIR MATRIZ DE TRANSFORMACIÓN T(x) = A·x
#
#
# ============================================================================

def construir_matriz_transformacion(expresiones, num_variables):
    """
    Construye la matriz A de una transformación T(x)=A·x a partir de expresiones tipo '3x1 - 2x2 + 5x3'.

    Devuelve una tupla: (pasos, matriz_A)
       - pasos: lista de strings explicando el proceso
       - matriz_A: lista de listas con los coeficientes
    """

    pasos = []
    pasos.append("Construyendo la matriz de la transformación T(x) = A·x")

    matriz_A = []

    # Procesamos cada expresión, que representa una fila de A
    for idx, expr in enumerate(expresiones):
        pasos.append(f"\nAnalizando ecuacion {idx+1}: '{expr}'")

        # Reemplazar signos para hacer más fácil el split
        # Convertimos "-" en "+-" para luego separar por "+"
        expr = expr.replace("-", "+-")

        # Eliminamos espacios en blanco
        tokens = expr.split("+")
        coeficientes = [0.0] * num_variables

        pasos.append(f"Tokens obtenidos: {tokens}")

        # Ahora analizamos cada token (ej: "3x1", "-2x2", "x3", "-x1")
        for token in tokens:
            token = token.strip()
            if token == "":
                continue

            # Buscar si hay 'x' en el token
            if "x" not in token:
                pasos.append(f"   Ignorando token sin 'x': {token}")
                continue

            # Separar coeficiente y variable
            # Posibles casos:
            #   "3x2"   → coef = 3,  var = 2
            #   "-x1"   → coef = -1, var = 1
            #   "x3"    → coef = 1,  var = 3
            #   "-4x1"  → coef = -4, var = 1
            partes = token.split("x")
            coef_str = partes[0]  # Parte antes de la x
            var_str = partes[1]   # Parte después de la x (número de variable)

            # Determinar coeficiente numérico
            if coef_str == "" or coef_str == "+":
                coef = 1.0
            elif coef_str == "-":
                coef = -1.0
            else:
                coef = float(coef_str)

            # Determinar índice de variable
            var_index = int(var_str) - 1

            if 0 <= var_index < num_variables:
                coeficientes[var_index] += coef
                pasos.append(f"   Termino '{token}' → coef = {coef}, var = x{var_index+1}")
            else:
                pasos.append(f"   Variable fuera de rango en '{token}', se ignora.")

        pasos.append(f"Coeficientes finales de la ecuacion {idx+1}: {coeficientes}")
        matriz_A.append(coeficientes)

    pasos.append("\nMatriz A resultante:")
    pasos.append(matriz_a_string(matriz_A))

    return pasos, matriz_A

# ============================================================================
#  SECCIÓN 8: VERIFICAR INDEPENDENCIA LINEAL
#
#  Objetivo:
#     Determinar si un conjunto de vectores es linealmente independiente.
#
#  ¿Qué hace?
#     1. Construye una matriz donde cada fila es un vector.
#     2. Aplica Gauss-Jordan para obtener la forma reducida (RREF).
#     3. Cuenta los pivotes (filas no nulas).
#     4. Si el número de pivotes = número de vectores → Independientes.
#        Si hay menos pivotes → Dependientes.
#
#  Retorna:
#     {
#         "independientes": True/False,
#         "pasos": [...],
#         "matriz_rref": [...],
#         "pivotes": [...],
#         "dependientes": [... indices o variables dependientes ...]
#     }
# ============================================================================

def verificar_independencia_lineal(vectores):
    """
    Verifica si un conjunto de vectores es linealmente independiente.
    Cada vector se asume como una lista de números.
    Todos deben tener la misma longitud.

    - Se arma una matriz con los vectores (cada vector = fila).
    - Se aplica Gauss-Jordan.
    - Se cuentan los pivotes.
    """
    pasos = []
    pasos.append("Verificando independencia lineal de los vectores...")

    # Validar que haya vectores
    if not vectores:
        pasos.append("No se proporcionaron vectores.")
        return {
            "independientes": False,
            "pasos": pasos,
            "matriz_rref": [],
            "pivotes": [],
            "dependientes": []
        }

    # Copiamos la matriz de vectores
    matriz = copia_profunda(vectores)
    filas = len(matriz)
    columnas = len(matriz[0])

    pasos.append("Matriz inicial formada por los vectores (cada fila es un vector):")
    pasos.append(matriz_a_string(matriz))

    # Aplicamos Gauss-Jordan adaptado (sin columna extra)
    fila_pivote = 0
    columnas_pivote = []

    for col in range(columnas):
        if fila_pivote >= filas:
            break

        # Encontrar fila con mejor pivote en esta columna
        mejor_fila = fila_pivote
        max_abs = abs(matriz[mejor_fila][col])
        for f in range(fila_pivote + 1, filas):
            if abs(matriz[f][col]) > max_abs:
                max_abs = abs(matriz[f][col])
                mejor_fila = f

        # Si toda la columna es 0 → no hay pivote
        if es_casi_cero(max_abs):
            pasos.append(f"Columna {col+1}: no hay pivote.")
            continue

        # Intercambio si es necesario
        if mejor_fila != fila_pivote:
            pasos.append(f"F{fila_pivote+1} <-> F{mejor_fila+1}")
            matriz[fila_pivote], matriz[mejor_fila] = matriz[mejor_fila], matriz[fila_pivote]
            pasos.append(matriz_a_string(matriz))

        # Normalizar pivote a 1
        pivote = matriz[fila_pivote][col]
        if not es_casi_cero(pivote - 1):
            pasos.append(f"F{fila_pivote+1} := F{fila_pivote+1} / {formatea_num(pivote)}")
            for j in range(col, columnas):
                matriz[fila_pivote][j] /= pivote
            pasos.append(matriz_a_string(matriz))

        # Eliminar arriba y abajo del pivote
        for f in range(filas):
            if f != fila_pivote and not es_casi_cero(matriz[f][col]):
                factor = matriz[f][col]
                pasos.append(f"F{f+1} := F{f+1} - {formatea_num(factor)} * F{fila_pivote+1}")
                for j in range(col, columnas):
                    matriz[f][j] -= factor * matriz[fila_pivote][j]
                pasos.append(matriz_a_string(matriz))

        columnas_pivote.append(col)
        fila_pivote += 1

    # Redondear ceros pequeños
    for i in range(filas):
        for j in range(columnas):
            if es_casi_cero(matriz[i][j]):
                matriz[i][j] = 0.0

    pasos.append("Matriz en RREF:")
    pasos.append(matriz_a_string(matriz))

    # Contar pivotes
    num_pivotes = len(columnas_pivote)
    pasos.append(f"Cantidad de pivotes: {num_pivotes}")

    # Si pivotes == cantidad de vectores (filas) → independientes
    if num_pivotes == filas:
        pasos.append("Todos los vectores son linealmente independientes.")
        return {
            "independientes": True,
            "pasos": pasos,
            "matriz_rref": matriz,
            "pivotes": [p+1 for p in columnas_pivote],
            "dependientes": []
        }
    else:
        pasos.append("Hay menos pivotes que vectores → los vectores son dependientes.")
        # Las filas sin pivote corresponden a vectores dependientes
        dependientes = [i+1 for i in range(filas) if i >= num_pivotes]
        return {
            "independientes": False,
            "pasos": pasos,
            "matriz_rref": matriz,
            "pivotes": [p+1 for p in columnas_pivote],
            "dependientes": dependientes
        }
        
# ========================================================================
#  SECCIÓN 7: CÁLCULO DE DETERMINANTES (MÉTODOS VARIOS)
#  Incluye:
#     - Determinante 2x2 (fórmula directa)
#     - Regla de Sarrus (3x3)
#     - Desarrollo por Cofactores (n x n)
#     - Método por Propiedades (operaciones de fila -> triangular)
# ========================================================================

def det_2x2(matriz):
    """
    Calcula el determinante de una matriz 2x2 usando la fórmula:
       |a b|
       |c d|  =  ad - bc
    Retorna un diccionario con:
       - resultado: valor del determinante
       - pasos: lista de pasos explicativos
       - metodo: nombre del método
    """
    pasos = []
    a = matriz[0][0]
    b = matriz[0][1]
    c = matriz[1][0]
    d = matriz[1][1]

    pasos.append(f"Usando la fórmula: det(A) = a·d - b·c")
    pasos.append(f"a = {a}, d = {d}, b = {b}, c = {c}")
    pasos.append(f"det(A) = ({a} * {d}) - ({b} * {c})")
    resultado = a*d - b*c
    pasos.append(f"det(A) = {resultado}")

    return {
        "resultado": resultado,
        "pasos": pasos,
        "metodo": "Determinante 2x2 (fórmula directa)"
    }

def det_sarrus(matriz):
    """
    Calcula el determinante de una matriz 3x3 usando la Regla de Sarrus.
    
    Regla:
      |a b c|
      |d e f|  =  a·e·i + b·f·g + c·d·h  -  c·e·g - a·f·h - b·d·i
      |g h i|
    
    Retorna un diccionario:
      - resultado: valor del determinante
      - pasos: lista de pasos explicativos
      - metodo: nombre del método
    """
    pasos = []
    a, b, c = matriz[0]
    d, e, f = matriz[1]
    g, h, i = matriz[2]

    pasos.append("Aplicando la Regla de Sarrus:")
    pasos.append("det(A) = (a·e·i + b·f·g + c·d·h) - (c·e·g + a·f·h + b·d·i)")
    pasos.append(f"= ({a}*{e}*{i} + {b}*{f}*{g} + {c}*{d}*{h}) - ({c}*{e}*{g} + {a}*{f}*{h} + {b}*{d}*{i})")

    parte1 = a*e*i + b*f*g + c*d*h
    parte2 = c*e*g + a*f*h + b*d*i

    pasos.append(f"= ({parte1}) - ({parte2})")

    resultado = parte1 - parte2
    pasos.append(f"det(A) = {resultado}")

    return {
        "resultado": resultado,
        "pasos": pasos,
        "metodo": "Regla de Sarrus (3x3)"
    }
    
def det_cofactor(matriz, nivel=0):
    """
    Calcula el determinante de una matriz n×n usando
    desarrollo por cofactores (recursivo).
    
    Retorna un diccionario:
      - resultado: valor del determinante
      - pasos: lista de pasos explicativos
      - metodo: nombre del método
    """

    pasos = []
    n = len(matriz)

    # Caso base 1x1
    if n == 1:
        pasos.append(f"{'  '*nivel}Matriz 1x1: det = {matriz[0][0]}")
        return {
            "resultado": matriz[0][0],
            "pasos": pasos,
            "metodo": "Cofactores"
        }

    # Caso base 2x2 → reutilizamos la función anterior
    if n == 2:
        aux = det_2x2(matriz)
        for p in aux["pasos"]:
            pasos.append(f"{'  '*nivel}{p}")
        return {
            "resultado": aux["resultado"],
            "pasos": pasos,
            "metodo": "Cofactores"
        }

    # Desarrollo por la primera fila (i = 0)
    det_total = 0
    pasos.append(f"{'  '*nivel}Desarrollando por la primera fila:")

    for j in range(n):
        elemento = matriz[0][j]
        
        if elemento == 0:
            pasos.append(f"{'  '*nivel}a(0,{j}) = 0 → se omite")
            continue

        # Signo = (-1)^(i+j) = (-1)^j porque i=0
        signo = (-1) ** j
        pasos.append(f"{'  '*nivel}Cofactor C(0,{j}): signo = {signo}, elemento = {elemento}")

        # Crear la submatriz menor
        submatriz = []
        for fila in range(1, n):
            subfila = []
            for col in range(n):
                if col != j:
                    subfila.append(matriz[fila][col])
            submatriz.append(subfila)

        pasos.append(f"{'  '*nivel}Submatriz eliminando fila 0 y columna {j}:")
        for sf in submatriz:
            pasos.append(f"{'  '*nivel}{sf}")

        # Llamada recursiva para determinante del menor
        resultado_sub = det_cofactor(submatriz, nivel + 1)
        det_sub = resultado_sub["resultado"]

        # Agregar los pasos del cálculo interno
        for p in resultado_sub["pasos"]:
            pasos.append(p)

        # Sumar al determinante total
        valor = signo * elemento * det_sub
        pasos.append(f"{'  '*nivel}Aporte = {signo} * {elemento} * {det_sub} = {valor}")
        det_total += valor

    pasos.append(f"{'  '*nivel}Determinante final (cofactores) = {det_total}")

    return {
        "resultado": det_total,
        "pasos": pasos,
        "metodo": "Cofactores (n×n)"
    }

def det_propiedades(matriz):
    """
    Calcula el determinante de una matriz cuadrada usando
    operaciones de fila (propiedades del determinante)
    para reducirla a forma triangular superior.

    Retorna un diccionario con:
        - resultado: valor del determinante
        - pasos: lista de pasos explicativos
        - metodo: nombre del método
    """
    pasos = []
    A = copia_profunda(matriz)
    n = len(A)
    det = 1
    intercambios = 0  # Para contar cuántas veces se intercambian filas

    pasos.append("Usando propiedades y reducción a forma triangular superior.")
    pasos.append("Propiedades usadas:")
    pasos.append("  • Intercambio de filas → det cambia de signo")
    pasos.append("  • Multiplicar una fila por k → det * k")
    pasos.append("  • Sumar múltiplos de filas → det no cambia\n")

    for i in range(n):
        # Si el pivote es 0, buscamos una fila inferior con un pivote no 0
        if es_casi_cero(A[i][i]):
            encontrado = False
            for k in range(i + 1, n):
                if not es_casi_cero(A[k][i]):
                    pasos.append(f"F{i+1} ↔ F{k+1} (intercambio de filas)")
                    A[i], A[k] = A[k], A[i]
                    intercambios += 1
                    pasos.append(matriz_a_string(A))
                    encontrado = True
                    break
            if not encontrado:
                pasos.append("Toda la columna es cero → det = 0")
                return {
                    "resultado": 0,
                    "pasos": pasos,
                    "metodo": "Propiedades / Triangular"
                }

        # Normalizamos el pivote
        pivote = A[i][i]
        if es_casi_cero(pivote):
            pasos.append("Pivote cero → det = 0")
            return {
                "resultado": 0,
                "pasos": pasos,
                "metodo": "Propiedades / Triangular"
            }

        det *= pivote
        pasos.append(f"Pivote en (F{i+1},C{i+1}) = {formatea_num(pivote)}")

        # Hacemos cero las entradas debajo del pivote
        for k in range(i + 1, n):
            factor = A[k][i] / pivote
            if not es_casi_cero(factor):
                pasos.append(f"F{k+1} := F{k+1} - ({formatea_num(factor)}) * F{i+1}")
                for j in range(i, n):
                    A[k][j] -= factor * A[i][j]
                pasos.append(matriz_a_string(A))

    # Ajustar por los intercambios de filas
    if intercambios % 2 == 1:
        pasos.append(f"Hubo {intercambios} intercambios de filas → det final = -{det}")
        det = -det
    else:
        pasos.append(f"Hubo {intercambios} intercambios de filas (par) → det no cambia signo")

    pasos.append(f"Determinante final = {formatea_num(det)}")

    return {
        "resultado": det,
        "pasos": pasos,
        "metodo": "Propiedades / Triangular"
    }

# ============================================================================
#  SECCIÓN 6: DETERMINANTES AUTOMÁTICOS (con PASO A PASO detallado)
#     - 2x2 → Fórmula directa
#     - 3x3 → Regla de Sarrus
#     - 4x4–5x5 → Cofactores (expansión recursiva con pasos)
#     - n ≥ 6 → Propiedades / Triangularización (operaciones de fila)
# ============================================================================

def calcular_determinante_auto(matriz):
    """
    Calcula el determinante automáticamente eligiendo el mejor método.
    Retorna un diccionario con: determinante, pasos, metodo, razon
    """
    n = len(matriz)
    
    pasos = []
    pasos.append("=== CÁLCULO DE DETERMINANTE ===")
    pasos.append(f"Matriz {n}x{n} ingresada:")
    pasos.append(matriz_a_string(matriz))
    
    # Elegir método según el tamaño
    if n == 1:
        metodo = "1x1 (elemento único)"
        razon = "Para matrices 1x1: det(A) = a₁₁"
        resultado = matriz[0][0]
        pasos.append(f"det(A) = {matriz[0][0]}")
        
    elif n == 2:
        metodo = "Fórmula 2x2"
        razon = "Para matrices 2x2: det(A) = a·d - b·c"
        a, b, c, d = matriz[0][0], matriz[0][1], matriz[1][0], matriz[1][1]
        resultado = a*d - b*c
        pasos.append(f"Fórmula: ({a}×{d}) - ({b}×{c})")
        pasos.append(f"det(A) = {a*d} - {b*c} = {resultado}")
        
    elif n == 3:
        metodo = "Regla de Sarrus"
        razon = "Para matrices 3x3: Regla de Sarrus"
        resultado = det_sarrus(matriz)["resultado"]
        sarrus_pasos = det_sarrus(matriz)["pasos"]
        pasos.extend(sarrus_pasos)
        
    elif n <= 5:
        metodo = "Desarrollo por Cofactores"
        razon = f"Para matrices {n}x{n} (n≤5): Desarrollo por cofactores"
        cofactor_result = det_cofactor(matriz)
        resultado = cofactor_result["resultado"]
        pasos.extend(cofactor_result["pasos"])
        
    else:
        metodo = "Propiedades/Triangularización"
        razon = f"Para matrices {n}x{n} (n≥6): Método eficiente por propiedades"
        prop_result = det_propiedades(matriz)
        resultado = prop_result["resultado"]
        pasos.extend(prop_result["pasos"])
    
    pasos.append(f"\n🎯 DETERMINANTE FINAL: {formatea_num(resultado)}")
    
    return {
        "determinante": resultado,
        "resultado": resultado,  # Duplicado para compatibilidad
        "pasos": pasos,
        "metodo": metodo,
        "razon": razon
    }



# ============================================================================
#  MÉTODO DE CRAMER (Regla de Cramer para sistemas lineales)
#  Solo aplica para matrices cuadradas (n×n) y un vector b en Rⁿ.
# ============================================================================

def resolver_cramer(A, b):
    """
    Resuelve un sistema lineal Ax = b usando la Regla de Cramer.
    Devuelve los pasos explicativos y la solución en fracciones y decimales.
    """
    pasos = []
    n = len(A)

    # ---------------------- VALIDACIONES ----------------------
    if any(len(fila) != n for fila in A):
        return {"error": "La matriz A no es cuadrada.", "pasos": []}
    if len(b) != n:
        return {"error": "El vector b debe tener la misma dimensión que A.", "pasos": []}

    pasos.append("=== MÉTODO DE CRAMER ===")
    pasos.append(f"Matriz A:\n{matriz_a_string(A)}")
    pasos.append(f"Vector b:\n{b}")

    # ---------------------- DETERMINANTE PRINCIPAL ----------------------
    detA_data = calcular_determinante_auto(A)
    detA = detA_data.get("determinante") or detA_data.get("resultado", 0)

    pasos.append(f"\nDeterminante de A = {formatea_num(detA)}")

    if es_casi_cero(detA):
        pasos.append("El determinante es 0 → El sistema NO tiene solución única.")
        return {
            "tipo_solucion": "No única (det(A)=0)",
            "solucion": None,
            "solucion_fraccion": None,
            "pasos": pasos
        }

    # ---------------------- CÁLCULO DE x_i ----------------------
    from copy import deepcopy
    from fractions import Fraction
    soluciones_decimal = []
    soluciones_fraccion = []

    for i in range(n):
        Ai = deepcopy(A)
        for fila in range(n):
            Ai[fila][i] = b[fila]  # Reemplazar columna i por b

        detAi_data = calcular_determinante_auto(Ai)
        detAi = detAi_data.get("determinante") or detAi_data.get("resultado", 0)

        xi_decimal = detAi / detA
        
        # Convertir a fracción de manera más robusta
        try:
            # Usar Fraction directamente con el valor decimal
            xi_fraccion = Fraction(xi_decimal).limit_denominator(1000000)
            
            # Simplificar la representación
            if xi_fraccion.denominator == 1:
                fraccion_str = str(xi_fraccion.numerator)
            else:
                fraccion_str = f"{xi_fraccion.numerator}/{xi_fraccion.denominator}"
                
        except Exception as e:
            # Si hay error en la conversión, mostrar el decimal como fallback
            fraccion_str = formatea_num(xi_decimal)

        soluciones_decimal.append(formatea_num(xi_decimal))
        soluciones_fraccion.append(fraccion_str)

        pasos.append(f"\nMatriz A{i+1}(b):\n{matriz_a_string(Ai)}")
        pasos.append(f"det(A{i+1}(b)) = {formatea_num(detAi)}")
        pasos.append(f"x{i+1} = det(A{i+1}(b)) / det(A) = {formatea_num(detAi)} / {formatea_num(detA)}")
        pasos.append(f"x{i+1} = {fraccion_str} ≈ {formatea_num(xi_decimal)}")

    pasos.append("\n=== SOLUCIÓN FINAL ===")
    for i, (fraccion, decimal) in enumerate(zip(soluciones_fraccion, soluciones_decimal)):
        pasos.append(f"x{i+1} = {fraccion} = {decimal}")

    return {
        "tipo_solucion": "Única",
        "solucion": soluciones_decimal,
        "solucion_fraccion": soluciones_fraccion,
        "pasos": pasos

    }
def _safe_eval_f(funcion_str: str, x_val: float) -> float:
    """
    Evalúa de forma segura una función matemática de una variable 'x'.
    """
    # Funciones permitidas
    funciones_seguras = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "log": math.log, "log10": math.log10, "ln": math.log,
        "exp": math.exp, "sqrt": math.sqrt,
        "pi": math.pi, "e": math.e,
        "pow": pow,
    }
    # Variables permitidas
    variables_seguras = {
        "x": x_val
    }
    
    try:
        # Evalúa la expresión usando solo las funciones y variables seguras
        return eval(funcion_str, {"__builtins__": None}, {**funciones_seguras, **variables_seguras})
    except Exception as e:
        raise ValueError(f"Error al evaluar f(x): {e}")
#========================================================================================#
# ================================================================#
# ================================================================
# LÓGICA DE PARSEO DE FUNCIONES
# ================================================================

def normalize_funcion(expr: str) -> str:
    """Normaliza/expande la expresión de usuario para permitir escritura flexible."""
    if expr is None:
        return ""
    expr = str(expr).strip()
    
    # Caracteres especiales y unicode math
    expr = (expr.replace("π", "pi").replace("√", "sqrt")
            .replace("×", "*").replace("÷", "/").replace("−", "-").replace("·", "*"))
    expr = expr.replace("^", "**")
    expr = expr.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    expr = re.sub(r"[\u00A0\u2007\u202F\u2009\u200A\u200B\u200C\u200D]", "", expr)
    
    # Superíndices
    supers = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
    
    def _sup_to_pow(match):
        base = match.group(1)
        sup = match.group(2).translate(supers)
        return f"{base}**{sup}"
    
    expr = re.sub(r"([A-Za-z0-9\)])([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", _sup_to_pow, expr)
    
    # Funciones sin paréntesis
    expr = re.sub(r'\bsqrt\s+([A-Za-z0-9_.]+)', r'sqrt(\1)', expr)
    
    funcs = ["sin","cos","tan","asin","acos","atan","sinh","cosh","tanh","ln","log","log10","log2","exp",
             "abs", "floor", "ceil"]
    for f in funcs:
        expr = re.sub(rf'\b{f}\s+([A-Za-z0-9_.]+)', rf'{f}(\1)', expr)
    
    # Multiplicación implícita
    expr = re.sub(r'(?<=\d)\s*(?=[x(pi)(e)(sin)(cos)(tan)(ln)(log)(sqrt)(abs)])', '*', expr)
    expr = re.sub(r'(?<=x)\s*(?=[0-9(pi)(e)(sin)(cos)(tan)(ln)(log)(sqrt)(abs)])', '*', expr)
    expr = re.sub(r'\bpi\s*(?=[0-9x(])', 'pi*', expr)
    expr = re.sub(r'(?<!\d)\be\s*(?=[0-9x(])', 'e*', expr)
    expr = re.sub(r'\)\s*(?=[(x0-9pi(e)(sin)(cos)(tan)(ln)(log)(sqrt)(abs)])', ')*', expr)
    
    func_group = r'(?:sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|exp|ln|log|log10|log2|sqrt|floor|ceil|abs)'
    expr = re.sub(rf'(?<=[0-9x\)])\s*(?={func_group}\s*\()', '*', expr)
    expr = re.sub(r'(?<=x)\s*(?=[A-Za-z])', '*', expr)
    
    return expr

def eval_funcion_escalar(expr_str: str, x_val: float):
    """Evalúa la expresión normalizada para un solo valor 'x'."""
    expr = normalize_funcion(expr_str)
    if not expr.strip():
        raise ValueError("Ingrese una función f(x).")
    
    env = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "log": math.log, "ln": math.log, "log10": math.log10, "log2": math.log2,
        "exp": math.exp, "sqrt": math.sqrt, "abs": abs, "pow": pow,
        "pi": math.pi, "e": math.e, "floor": math.floor, "ceil": math.ceil,
        "degrees": math.degrees, "radians": math.radians, "x": x_val,
        "math": math
    }
    
    return eval(expr, {"__builtins__": None}, env)

def eval_funcion_vectorial(expr_str: str, xs: np.ndarray):
    """Evalúa la expresión normalizada para un vector 'x' (para gráficas)."""
    expr = normalize_funcion(expr_str)
    if not expr.strip():
        raise ValueError("Ingrese una función f(x).")
    
    env = {
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "log": np.log, "ln": np.log, "log10": np.log10, "log2": np.log2,
        "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs, "pow": np.power,
        "pi": np.pi, "e": np.e, "floor": np.floor, "ceil": np.ceil,
        "degrees": np.degrees, "radians": np.radians, "x": xs,
        "np": np
    }
    
    try:
        with np.errstate(divide='ignore', invalid='ignore'):
            return eval(expr, {"__builtins__": None}, env)
    except Exception:
        return np.full_like(xs, np.nan)

def convertir_valor(valor_str: str):
    """Convierte un string a número, manejando notación científica."""
    try:
        return float(valor_str)
    except ValueError:
        # Manejar notación científica como "1e-5"
        if 'e' in valor_str.lower():
            base, exp = valor_str.lower().split('e')
            return float(base) * (10 ** float(exp))
        raise
def normalize_funcion(expr: str) -> str:
    """
    Normaliza/expande la expresión de usuario para permitir escritura flexible.
    (Lógica del 'BiseccionApp' de tu amigo)
    """
    if expr is None:
        return ""
    expr = expr.strip()

    # 0) caracteres y potencias / unicode math
    #   - π → pi, √ → sqrt, × → *, ÷ → /, − (minus) → -, · → *
    expr = (expr.replace("π", "pi").replace("√", "sqrt")
                .replace("×", "*").replace("÷", "/").replace("−", "-").replace("·", "*"))
    expr = expr.replace("^", "**")

    #   - Dashes and minus variants: – — −   → -
    expr = expr.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    #   - Non-breaking / thin / zero-width spaces → remove
    expr = re.sub(r"[\u00A0\u2007\u202F\u2009\u200A\u200B\u200C\u200D]", "", expr)
    
    #   - Superíndices: x²,x³ → x**2, x**3 (y secuencias como x¹⁰ → x**10)
    supers = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
    def _sup_to_pow(match):
        base = match.group(1)
        sup = match.group(2).translate(supers)
        return f"{base}**{sup}"
    expr = re.sub(r"([A-Za-z0-9\)])([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", _sup_to_pow, expr)

    # 1) sqrt sin paréntesis: sqrt x -> sqrt(x)
    expr = re.sub(r'\bsqrt\s+([A-Za-z0-9_.]+)', r'sqrt(\1)', expr)

    # 2) funciones sin paréntesis: sin x -> sin(x) (y similares)
    funcs = ["sin","cos","tan","asin","acos","atan","sinh","cosh","tanh","ln","log","log10","log2","exp"]
    for f in funcs:
        expr = re.sub(rf'\b{f}\s+([A-Za-z0-9_.]+)', rf'{f}(\1)', expr)

    # 3) multiplicación implícita (varias reglas). Orden importa.
    # a) número seguido de x o (   -> 2x, 3(x
    expr = re.sub(r'(?<=\d)\s*(?=[x(])', '*', expr)

    # b) x seguido de número o (   -> x2, x(
    expr = re.sub(r'(?<=x)\s*(?=[0-9(])', '*', expr)

    # c) pi/e seguidos de número/x/(   -> pi x, e(x, e2
    expr = re.sub(r'\bpi\s*(?=[0-9x(])', 'pi*', expr)
    # 'e' es especial, no queremos 'exp'
    expr = re.sub(r'(?<![a-zA-Z])\be\s*(?=[0-9x(])', 'e*', expr) 

    # d) ) seguido de (, x o número -> )(, )x, )2
    expr = re.sub(r'\)\s*(?=[(x0-9])', ')*', expr)

    # e) número, x o ) seguidos de función que abre paréntesis -> 2sin(  /  xsin(
    func_group = r'(?:sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|exp|ln|log|log10|log2|sqrt|floor|ceil)'
    expr = re.sub(rf'(?<=[0-9x\)])\s*(?={func_group}\s*\()', '*', expr)

    # f) x seguido de letras (por ejemplo xk o xsin(x)) -> x*k / x*sin(
    expr = re.sub(r'(?<=x)\s*(?=[A-Za-z])', '*', expr)

    return expr

def eval_funcion_escalar(expr_str: str, x_val):
    """
    Evalúa la expresión normalizada para un solo valor 'x'.
    (Lógica del 'BiseccionApp' de tu amigo)
    """
    expr = normalize_funcion(expr_str)
    if not expr.strip():
        raise ValueError("Ingrese una función f(x).")
    
    # Entorno seguro para eval()
    env = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "log": math.log, "ln": math.log, "log10": math.log10, "log2": math.log2,
        "exp": math.exp, "sqrt": math.sqrt, "abs": abs, "pow": pow,
        "pi": math.pi, "e": math.e, "floor": math.floor, "ceil": math.ceil,
        "degrees": math.degrees, "radians": math.radians,
        "x": x_val
    }
    
    try:
        return eval(expr, {"__builtins__": None}, env)
    except Exception as e:
        raise ValueError(f"Error al evaluar f({x_val}): {e}\nExpresión normalizada: '{expr}'")

def eval_funcion_vectorial(expr_str: str, xs: np.ndarray):
    """
    Evalúa la expresión normalizada para un vector 'x' (para gráficas).
    (Lógica del 'BiseccionApp' de tu amigo)
    """
    expr = normalize_funcion(expr_str)
    if not expr.strip():
        raise ValueError("Ingrese una función f(x).")
    
    # Entorno seguro para eval() usando numpy
    env = {
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "log": np.log, "ln": np.log, "log10": np.log10, "log2": np.log2,
        "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs, "pow": np.power,
        "pi": np.pi, "e": np.e, "floor": np.floor, "ceil": np.ceil,
        "degrees": np.degrees, "radians": np.radians,
        "x": xs,
        "np": np
    }
    
    try:
        with np.errstate(divide='ignore', invalid='ignore'):
            resultado = eval(expr, {"__builtins__": None}, env)
            if isinstance(resultado, (int, float)):
                return np.full_like(xs, resultado, dtype=float)
            return np.asarray(resultado, dtype=float)
    except Exception as e:
        raise ValueError(f"Error al evaluar vector: {e}\nExpresión normalizada: '{expr}'")

def resolver_biseccion(expr_str: str, a_val: float, b_val: float, tol: float, itmax: int):
    """
    Resuelve una función por el método de Bisección.
    (Lógica extraída de los archivos de tu amigo)
    """
    try:
        fa = eval_funcion_escalar(expr_str, a_val)
        fb = eval_funcion_escalar(expr_str, b_val)
    except Exception as e:
        return {'error_msg': f"Error evaluando f(x):\n{e}"}

    if fa * fb > 0:
        return {'error_msg': f"f(a) y f(b) deben tener signos opuestos.\nf({a_val}) = {fa:.6f}\nf({b_val}) = {fb:.6f}"}

    pasos = []
    header = f"{'Iter':<5}{'a':>14}{'b':>14}{'c':>14}{'f(a)':>16}{'f(b)':>16}{'f(c)':>16}\n"
    pasos.append(header)
    pasos.append("-" * (5+14*3+16*3) + "\n")

    it = 1
    error = abs(b_val - a_val)
    convergido = False
    c = a_val

    while error > tol and it <= itmax:
        c = (a_val + b_val) / 2.0
        fa = eval_funcion_escalar(expr_str, a_val) 
        fb = eval_funcion_escalar(expr_str, b_val)
        fc = eval_funcion_escalar(expr_str, c)
        line = f"{it:<5}{a_val:>14.8f}{b_val:>14.8f}{c:>14.8f}{fa:>16.8f}{fb:>16.8f}{fc:>16.8f}\n"
        pasos.append(line)

        if fa * fc > 0:
            a_val = c
        else:
            b_val = c
        error = abs(b_val - a_val)
        it += 1

    if error <= tol:
        convergido = True
        
    pasos.append("-" * (5+14*3+16*3) + "\n")
    pasos.append(f"Iteraciones: {it-1}\n")
    pasos.append(f"x ≈ {c:.10f}\n")
    pasos.append(f"Error (|b-a|): {error:.10e}\n")
    if not convergido and it > itmax:
         pasos.append("⚠️  Máximo de iteraciones alcanzado\n")
            
    return {
        'pasos': pasos,
        'solucion': c,
        'iter': it-1,
        'error': error,
        'convergido': convergido,
        'error_msg': None
    }

def resolver_falsa_posicion_avanzado(expr_str: str, a_val: float, b_val: float, tol: float, itmax: int):
    """
    Resuelve una función por el método de Falsa Posición.
    (Lógica extraída del 'BiseccionFalsaPosicionApp' de tu amigo)
    """
    try:
        fa = eval_funcion_escalar(expr_str, a_val)
        fb = eval_funcion_escalar(expr_str, b_val)
    except Exception as e:
        return {'error_msg': f"Error evaluando f(x):\n{e}"}

    if fa * fb > 0:
        return {'error_msg': f"f(a) y f(b) deben tener signos opuestos.\nf({a_val}) = {fa:.6f}\nf({b_val}) = {fb:.6f}"}

    pasos = []
    header = f"{'Iter':<5}{'a':>14}{'b':>14}{'xr':>14}{'f(a)':>16}{'f(b)':>16}{'f(xr)':>16}\n"
    pasos.append(header)
    pasos.append("-" * (5+14*3+16*3) + "\n")

    it = 1
    xr = a_val
    xr_prev = a_val
    fxr = fa
    convergido = False

    while it <= itmax:
        fa = eval_funcion_escalar(expr_str, a_val)
        fb = eval_funcion_escalar(expr_str, b_val)
        
        try:
            xr = (a_val * fb - b_val * fa) / (fb - fa)
        except ZeroDivisionError:
             return {'error_msg': f"División por cero en la iteración {it} (fb - fa = 0)"}
             
        fxr = eval_funcion_escalar(expr_str, xr)

        line = f"{it:<5}{a_val:>14.8f}{b_val:>14.8f}{xr:>14.8f}{fa:>16.8f}{fb:>16.8f}{fxr:>16.8f}\n"
        pasos.append(line)

        if abs(fxr) < tol:
            convergido = True
            break

        if fa * fxr < 0:
            b_val = xr
        else:
            a_val = xr

        if it > 1 and abs(xr - xr_prev) < tol:
            convergido = True
            break

        xr_prev = xr
        it += 1

    pasos.append("-" * (5+14*3+16*3) + "\n")
    pasos.append(f"Iteraciones: {it}\n")
    pasos.append(f"x ≈ {xr:.10f}\n")
    pasos.append(f"f(x) ≈ {fxr:.10e}\n")
    if not convergido and it > itmax:
        pasos.append("⚠️  Máximo de iteraciones alcanzado\n")
            
    return {
        'pasos': pasos,
        'solucion': xr,
        'iter': it,
        'error_fx': fxr,
        'convergido': convergido,
        'error_msg': None
    }