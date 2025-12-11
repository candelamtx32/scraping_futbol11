from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time 

# --- CONFIGURACIÓN DE SELECTORES ---
ID_BOTON_COOKIES = "accept-choices"
CLASE_BOTON_START = "startGame" 
CLASE_DATO_GRID = "groupTitle" # Clase que contiene los 9 títulos

def extraer_grid(dificultad_valor):
    """
    Extrae los 9 títulos de la cuadrícula del juego Grid (clase groupTitle).
    """
    
    URL = "https://futbol-11.com/futbol-grid"
    
    SELECTOR_INPUT_DIFICULTAD = f'input[value="{dificultad_valor}"]'
    SELECTOR_BOTON_START = 'button.searchButton.startGame' 
    
    print(f"\n>>>> INICIANDO GRID | DIFICULTAD: {dificultad_valor} | Buscando: .{CLASE_DATO_GRID} <<<<")
    
    opciones = Options()
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=opciones) 
    
    try:
        driver.get(URL)
        
        # 1. ACEPTAR COOKIES
        print("1. Aceptando cookies...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, ID_BOTON_COOKIES))).click()
        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, ID_BOTON_COOKIES))) 
        time.sleep(1) 

        # 2. SELECCIONAR DIFICULTAD (Forzado con JS)
        print(f"2. Forzando la selección de dificultad '{dificultad_valor}'...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_INPUT_DIFICULTAD)))
        driver.execute_script(f"document.querySelector('{SELECTOR_INPUT_DIFICULTAD}').click();")
        
        # 3. CLIC EN START GAME (Forzado con JS)
        print("3. Forzando el clic en 'Start Game'...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_BOTON_START)))
        driver.execute_script(f"document.querySelector('{SELECTOR_BOTON_START}').click();")
        
        # AÑADIMOS UN RETARDO para asegurar que la cuadrícula se ha renderizado
        print("⏳ Retardo de 2 segundos para asegurar la renderización del Grid...")
        time.sleep(2) 
        
        # 4. EXTRACCIÓN DEL DATO FINAL
        print(f"4. Esperando a que el dato ('{CLASE_DATO_GRID}') cargue...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, CLASE_DATO_GRID)))
        
        html_cargado = driver.page_source
        sopa = BeautifulSoup(html_cargado, 'html.parser')
        
        # Búsqueda de TODOS los 9 elementos con la clase
        elementos_encontrados = sopa.find_all(attrs={'class': CLASE_DATO_GRID})

        if elementos_encontrados:
            datos_extraidos = [e.get_text(strip=True).replace('\n', ' ').replace('\r', '').strip() for e in elementos_encontrados]
            
            print(f"✅ Éxito! Se extrajeron {len(datos_extraidos)} elementos.")
            return datos_extraidos
        else:
            print(f"❌ Error: No se encontraron elementos con la clase '{CLASE_DATO_GRID}'.")
            return None

    except Exception as e:
        print(f"❌ Ocurrió un error en el scraping: {e}")
        return None
    finally:
        driver.quit()

# -----------------------------------------------------------------------------
# |                      EJECUCIÓN DE LAS PRUEBAS DE GRIDS                      |
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    DIFICULTADES = ["easy", "normal", "hard", "legend"]
    resultados_finales = {}
    
    for dificultad in DIFICULTADES:
        nombre = f"Grid Game ({dificultad.capitalize()})"
        resultado = extraer_grid(dificultad)
        resultados_finales[nombre] = resultado
        
    print("\n================== RESUMEN DE EXTRACCIÓN GRID (RESULTADOS COMPLETOS) ==================")
    for nombre, resultado in resultados_finales.items():
        if isinstance(resultado, list):
            # 🚨 AQUÍ ESTÁ EL CAMBIO: Imprimimos la lista completa (los 9 elementos)
            print(f"[{nombre}]: {len(resultado)} elementos extraídos.")
            print(f"    ▶️ Datos: {resultado}")
        else:
            print(f"[{nombre}]: {resultado if resultado else 'FALLO'}")