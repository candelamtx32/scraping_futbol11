from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time 

# --- CONFIGURACIÓN DE SELECTORES COMUNES ---
# Estos selectores son suficientes para el flujo NORMAL
ID_BOTON_COOKIES = "accept-choices"
CLASE_BOTON_START = "startGame" 

def extraer_minijuego(url, dificultad_valor, clase_dato_final):
    """
    Extrae un dato específico (clase_dato_final) de un minijuego con flujo NORMAL.
    """
    
    SELECTOR_INPUT_DIFICULTAD = f'input[value="{dificultad_valor}"]'
    SELECTOR_BOTON_START = 'button.searchButton.startGame' 

    print(f"\n>>>> Iniciando scraping | FLUJO: NORMAL | DIFICULTAD: {dificultad_valor} | URL: {url} <<<<")
    
    opciones = Options()
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=opciones) 
    
    try:
        driver.get(url)
        
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
        
        # 4. EXTRACCIÓN DEL DATO FINAL
        print(f"4. Esperando a que el dato ('{clase_dato_final}') cargue...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, clase_dato_final)))
        
        html_cargado = driver.page_source
        sopa = BeautifulSoup(html_cargado, 'html.parser')
        
        # Búsqueda genérica
        elementos_encontrados = sopa.find_all(attrs={'class': clase_dato_final})

        if elementos_encontrados:
            datos_extraidos = [e.get_text(strip=True) for e in elementos_encontrados]
            
            # Devolvemos solo el primer elemento, ya que solo se espera uno en estos juegos
            return datos_extraidos[0]
        else:
            print(f"❌ Error: No se encontraron elementos con la clase '{clase_dato_final}'.")
            return None

    except Exception as e:
        print(f"❌ Ocurrió un error en el scraping: {e}")
        return None
    finally:
        driver.quit()

# -----------------------------------------------------------------------------
# |             EJECUCIÓN DE LAS PRUEBAS PYRAMID, IMPOSTOR Y TOP10              |
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    # Definición de las 3 páginas
    PAGINAS_A_RASPAR = [
        # 1. PYRAMID: Flujo NORMAL
        { "url": "https://futbol-11.com/futbol11-pyramid", "dificultad": "easy", "clase_dato": "gameCategory", "nombre": "Pyramid Game" },
        # 2. IMPOSTOR: Flujo NORMAL
        { "url": "https://futbol-11.com/futbol11-impostor", "dificultad": "normal", "clase_dato": "textBox", "nombre": "Impostor Game" },
        # 3. TOP 10: Flujo NORMAL
        { "url": "https://futbol-11.com/futbol-top10", "dificultad": "normal", "clase_dato": "top10title", "nombre": "Top 10 Game" }
    ]

    resultados_finales = {}
    
    for pagina in PAGINAS_A_RASPAR:
        resultado = extraer_minijuego(
            pagina["url"], 
            pagina["dificultad"], 
            pagina["clase_dato"]
        )
        resultados_finales[pagina["nombre"]] = resultado
        
    print("\n================== RESUMEN FINAL DE EXTRACCIÓN ==================")
    for nombre, resultado in resultados_finales.items():
        print(f"[{nombre}]: {resultado if resultado else 'FALLO'}")