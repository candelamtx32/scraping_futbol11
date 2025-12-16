import csv
import datetime
import os
# Importamos solo los scripts de dificultad 'Normal'
import scrapClubs2 as s_club_norm 
import scrapCountries2 as s_pais_norm

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

def ejecutar_guardado_dificil():
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    DIFICULTAD = "Normal"
    print(f"\n🚀 INICIANDO RECOLECCIÓN DE DATOS {DIFICULTAD} - {fecha_hoy}")

    # =========================================================================
    # 1. MONITOREO DE PAÍSES Y CLUBES (DIFICULTAD NORMAL)
    #    NOTA: Estas funciones tienen un tiempo de espera de 120s. 
    # =========================================================================
    archivo_monitoreo = "historial_dificil.csv" # <--- NOMBRE DE ARCHIVO ACTUALIZADO
    headers_monitoreo = ["FECHA", "JUEGO", "DIFICULTAD", "TOTAL_ENCONTRADOS", "ITEMS_ENCONTRADOS"]
    
    juegos_a_monitorizar = [
        # Clubes (Normal) - scrapClubs2
        { 
            "nombre": "Clubes", 
            "dificultad_texto": s_club_norm.NOMBRE_DIFICULTAD, # "Normal"
            "funcion": s_club_norm.extraer_clubes_jugando 
        },
        # Países (Normal) - scrapCountries2
        { 
            "nombre": "Países", 
            "dificultad_texto": s_pais_norm.NOMBRE_DIFICULTAD, # "Normal"
            "funcion": s_pais_norm.extraer_paises_normal 
        }
    ]

    for juego in juegos_a_monitorizar:
        print(f"\n--- Procesando {juego['nombre']} ({juego['dificultad_texto']}) ---")
        try:
            # La función devuelve una lista de clubes/países
            res = juego["funcion"]() 
            total = len(res) if res else 0
            # Los elementos de la lista se unen en un solo string para guardarlos en una celda
            items = ", ".join(res) if res else ""
            
            fila = [
                fecha_hoy,
                juego["nombre"],
                juego["dificultad_texto"],
                total,
                items
            ]
            guardar_en_csv(archivo_monitoreo, headers_monitoreo, fila)
        except Exception as e:
            print(f"   ⚠️ Error en Monitoreo {juego['nombre']} ({juego['dificultad_texto']}): {e}")

    print("\n🏁 PROCESO DIFÍCIL FINALIZADO.")

if __name__ == "__main__":
    ejecutar_guardado_dificil()