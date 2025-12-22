import csv
import datetime
import os
# Importamos el script encargado del Grid
import scrap3 as s_grid

def guardar_en_csv(nombre_archivo, encabezados, fila_datos):
    """Función de utilidad para guardar datos en un CSV."""
    archivo_existe = os.path.isfile(nombre_archivo)
    
    try:
        with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f, delimiter=';')
            
            # Si el archivo es nuevo, escribimos los encabezados
            if not archivo_existe:
                escritor.writerow(encabezados)
            
            escritor.writerow(fila_datos)
            print(f" Guardado en {nombre_archivo}")
            
    except PermissionError:
        print(f" ERROR: No se pudo escribir en '{nombre_archivo}'. ¡Ciérralo si lo tienes abierto!")

def ejecutar_guardado_grid():
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n🚀 INICIANDO RECOLECCIÓN DE DATOS GRID (6 TÍTULOS + 9 CONEXIONES) - {fecha_hoy}")

    archivo_grid = "historial_grid.csv"
    
    # Encabezados: Fecha, Dificultad, los 6 títulos y las 9 conexiones resultantes
    headers_grid = [
        "FECHA", "DIFICULTAD", 
        "T1", "T2", "T3", "T4", "T5", "T6",
        "T1_T4", "T2_T4", "T3_T4", 
        "T1_T5", "T2_T5", "T3_T5", 
        "T1_T6", "T2_T6", "T3_T6"
    ]
    
    dificultades_grid = ["easy", "normal", "hard", "legend"]
    
    for dif in dificultades_grid:
        print(f"\n--- Procesando Grid ({dif.capitalize()}) ---")
        try:
            # Extraer los 6 títulos usando scrap3.py
            titulos = s_grid.extraer_grid(dif) 
            
            if titulos and len(titulos) == 6:
                # Separamos para mayor claridad:
                # T1, T2, T3 suelen ser Columnas
                # T4, T5, T6 suelen ser Filas
                t1, t2, t3, t4, t5, t6 = titulos
                
                # Generamos las 9 conexiones combinando Columnas (1-3) con Filas (4-6)
                conexiones = [
                    f"{t1}_{t4}", f"{t2}_{t4}", f"{t3}_{t4}",
                    f"{t1}_{t5}", f"{t2}_{t5}", f"{t3}_{t5}",
                    f"{t1}_{t6}", f"{t2}_{t6}", f"{t3}_{t6}"
                ]
                
                # Preparamos la fila final: info básica + 6 títulos + 9 conexiones
                fila = [fecha_hoy, dif.capitalize()] + titulos + conexiones
                guardar_en_csv(archivo_grid, headers_grid, fila)
            else:
                print(f"   ⚠️ Grid {dif}: Se esperaban 6 títulos, se encontraron {len(titulos) if titulos else 0}")
                
        except Exception as e:
            print(f"   ⚠️ Error en Grid {dif}: {e}")

    print("\n🏁 PROCESO DE GRID FINALIZADO.")

if __name__ == "__main__":
    ejecutar_guardado_grid()