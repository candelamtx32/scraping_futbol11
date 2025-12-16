import csv
import datetime
import os

# --- IMPORTACIÓN DE TUS SCRIPTS ---
import scrap4 as s_formaciones      # Formaciones
import scrap3 as s_grid             # Grid
import scrap2 as s_connections      # Connections
import scrap1 as s_minijuegos       # Minijuegos

def guardar_en_csv(nombre_archivo, encabezados, fila_datos):
    archivo_existe = os.path.isfile(nombre_archivo)
    
    try:
        with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f, delimiter=';')
            
            # Si el archivo es nuevo, escribimos los encabezados
            if not archivo_existe:
                escritor.writerow(encabezados)
            
            escritor.writerow(fila_datos)
            print(f"   ✅ Guardado en {nombre_archivo}")
            
    except PermissionError:
        print(f"   ❌ ERROR: No se pudo escribir en '{nombre_archivo}'. ¡Ciérralo si lo tienes abierto!")

def ejecutar_guardado_diario():
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n🚀 INICIANDO RECOLECCIÓN DE DATOS (POR COLUMNAS) - {fecha_hoy}")

    # =========================================================================
    # 1. FORMACIONES (Clubes y Países) -> Archivo: historial_formaciones.csv
    # =========================================================================
    print("\n--- Procesando Formaciones ---")
    archivo_form = "historial_formaciones.csv"
    # Aquí ya lo teníamos separado, lo mantenemos igual
    headers_form = ["FECHA", "TIPO", "DIFICULTAD", "FORMACION", "POSICIONES", "PORTEROS", "DEF", "MED", "DEL"]
    
    for juego in ["Clubes", "Paises"]:
        try:
            res = s_formaciones.extraer_formacion_unificada(juego, "normal")
            if res:
                fila = [
                    fecha_hoy,
                    juego,
                    "Normal",
                    res['formacion'],
                    ", ".join(res['posiciones']), # Las posiciones individuales las dejamos en una celda para no ocupar 11 columnas extra
                    res['porteros'],
                    res['conteo']['DEFENSAS'],
                    res['conteo']['CENTROCAMPISTAS'],
                    res['conteo']['DELANTEROS']
                ]
                guardar_en_csv(archivo_form, headers_form, fila)
        except Exception as e:
            print(f"   ⚠️ Error en Formación {juego}: {e}")

    # =========================================================================
    # 2. GRID (9 Columnas) -> Archivo: historial_grid.csv
    # =========================================================================
    print("\n--- Procesando Grid ---")
    archivo_grid = "historial_grid.csv"
    
    # CAMBIO: Creamos 9 encabezados para los 9 títulos
    headers_grid = ["FECHA", "DIFICULTAD", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
    
    dificultades_grid = ["easy", "normal", "hard", "legend"]
    
    for dif in dificultades_grid:
        try:
            res = s_grid.extraer_grid(dif) # Esto devuelve una lista de 9 elementos
            if res and len(res) == 9:
                # CAMBIO: Sumamos la lista de datos a la lista de información inicial
                # [Fecha, Dif] + [Titulo1, Titulo2, ..., Titulo9]
                fila = [fecha_hoy, dif.capitalize()] + res
                guardar_en_csv(archivo_grid, headers_grid, fila)
            else:
                print(f"   ⚠️ Grid {dif}: Se esperaban 9 elementos, se encontraron {len(res) if res else 0}")
        except Exception as e:
            print(f"   ⚠️ Error en Grid {dif}: {e}")

    # =========================================================================
    # 3. CONNECTIONS (4 Columnas) -> Archivo: historial_connections.csv
    # =========================================================================
    print("\n--- Procesando Connections ---")
    archivo_conn = "historial_connections.csv"
    
    # CAMBIO: Creamos 4 encabezados para las categorías
    headers_conn = ["FECHA", "DIFICULTAD", "GRUPO_1", "GRUPO_2", "GRUPO_3", "GRUPO_4"]
    
    dificultades_conn = ["easy", "normal"]
    
    for dif in dificultades_conn:
        try:
            res = s_connections.extraer_connections(dif) # Esto devuelve una lista de 4 elementos
            if res and len(res) == 4:
                # CAMBIO: Desglosamos la lista en columnas
                fila = [fecha_hoy, dif.capitalize()] + res
                guardar_en_csv(archivo_conn, headers_conn, fila)
            else:
                print(f"   ⚠️ Connections {dif}: Se esperaban 4 elementos.")
        except Exception as e:
            print(f"   ⚠️ Error en Connections {dif}: {e}")

    # =========================================================================
    # 4. MINIJUEGOS -> Archivo: historial_minijuegos.csv
    # =========================================================================
    print("\n--- Procesando Otros Minijuegos ---")
    archivo_mini = "historial_minijuegos.csv"
    headers_mini = ["FECHA", "JUEGO", "DIFICULTAD", "DATO EXTRAIDO"]
    
    lista_minijuegos = [
        { "nombre": "Pyramid",  "url": "https://futbol-11.com/futbol11-pyramid", "dif": "easy",   "clase": "gameCategory" },
        { "nombre": "Impostor", "url": "https://futbol-11.com/futbol11-impostor", "dif": "normal", "clase": "textBox" },
        { "nombre": "Top 10",   "url": "https://futbol-11.com/futbol-top10",      "dif": "normal", "clase": "top10title" }
    ]

    for juego in lista_minijuegos:
        try:
            res = s_minijuegos.extraer_minijuego(juego["url"], juego["dif"], juego["clase"])
            if res:
                fila = [fecha_hoy, juego["nombre"], juego["dif"], res]
                guardar_en_csv(archivo_mini, headers_mini, fila)
        except Exception as e:
            print(f"   ⚠️ Error en {juego['nombre']}: {e}")

    print("\n🏁 PROCESO FINALIZADO.")

if __name__ == "__main__":
    ejecutar_guardado_diario()