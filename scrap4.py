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
CLASE_FORMACION_POSICION = "player-card card-front" 

# --- DEFINICIÓN DE URLS CORREGIDAS ---
URLS_FORMACION = {
    "Paises": "https://futbol-11.com/futbol11", # URL corregida: la base
    "Clubes": "https://futbol-11.com/futbol11-clubs" # URL corregida
}

# --------------------------------------------------------------------------------------
# |                              FUNCIÓN DE ANÁLISIS DE DATOS                           |
# --------------------------------------------------------------------------------------

def analizar_formacion(posiciones_extraidas):
    """
    Analiza una lista de posiciones y devuelve el conteo Defensas-Centrocampistas-Delanteros.
    """
    
    GRUPOS = {
        'DELANTEROS': ['ST', 'RW', 'LW', 'CF'],
        'CENTROCAMPISTAS': ['CM', 'CDM', 'CAM', 'RM', 'LM'], 
        'DEFENSAS': ['LB', 'RB', 'CB', 'LWB', 'RWB'] 
    }
    
    conteo = {'DEFENSAS': 0, 'CENTROCAMPISTAS': 0, 'DELANTEROS': 0}
    conteo_gk = 0
    
    for pos in posiciones_extraidas:
        pos = pos.upper() 
        if pos == 'GK':
            conteo_gk += 1
            continue
            
        elif pos in GRUPOS['DELANTEROS']:
            conteo['DELANTEROS'] += 1
        elif pos in GRUPOS['CENTROCAMPISTAS']:
            conteo['CENTROCAMPISTAS'] += 1
        elif pos in GRUPOS['DEFENSAS']:
            conteo['DEFENSAS'] += 1
            
    # Formato de la Formación: Defensas - Centrocampistas - Delanteros
    formacion_numerica = f"{conteo['DEFENSAS']}-{conteo['CENTROCAMPISTAS']}-{conteo['DELANTEROS']}"
    
    return {
        "posiciones": posiciones_extraidas,
        "conteo": conteo,
        "formacion": formacion_numerica,
        "porteros": conteo_gk
    }


# --------------------------------------------------------------------------------------
# |                              FUNCIÓN DE EXTRACCIÓN MAESTRA                          |
# --------------------------------------------------------------------------------------

def extraer_formacion_unificada(tipo_juego, dificultad_valor):
    """
    Extrae la formación (11 posiciones) para el juego de clubes o países.
    """
    
    url = URLS_FORMACION[tipo_juego]
    SELECTOR_INPUT_DIFICULTAD = f'input[value="{dificultad_valor}"]'
    SELECTOR_BOTON_START = 'button.searchButton.startGame' 

    print(f"\n>>>> INICIANDO FORMACIÓN | JUEGO: {tipo_juego} | DIFICULTAD: {dificultad_valor} | URL: {url} <<<<")
    
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

        # 2. SELECCIONAR DIFICULTAD
        print(f"2. Forzando la selección de dificultad '{dificultad_valor}'...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_INPUT_DIFICULTAD)))
        driver.execute_script(f"document.querySelector('{SELECTOR_INPUT_DIFICULTAD}').click();")
        
        # 3. CLIC EN START GAME
        print("3. Forzando el clic en 'Start Game'...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_BOTON_START)))
        driver.execute_script(f"document.querySelector('{SELECTOR_BOTON_START}').click();")
        
        # 4. EXTRACCIÓN DE POSICIONES
        print(f"4. Esperando a que las 11 posiciones ('{CLASE_FORMACION_POSICION}') carguen...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, CLASE_FORMACION_POSICION.replace(' ', '.'))))
        
        html_cargado = driver.page_source
        sopa = BeautifulSoup(html_cargado, 'html.parser')
        
        posiciones_encontradas = sopa.find_all(attrs={'class': CLASE_FORMACION_POSICION.split()})
        
        if len(posiciones_encontradas) >= 11:
            posiciones_texto = [e.get_text(strip=True) for e in posiciones_encontradas]
            return analizar_formacion(posiciones_texto)
        else:
            print(f"❌ Error: Solo se encontraron {len(posiciones_encontradas)} posiciones.")
            return None

    except Exception as e:
        print(f"❌ Ocurrió un error en el scraping: {e}")
        return None
    finally:
        driver.quit()

# -----------------------------------------------------------------------------
# |                      EJECUCIÓN DEL PROYECTO (CLUBES Y PAÍSES)               |
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    DIFICULTAD = "normal" 
    juegos = ["Clubes", "Paises"]
    resultados_finales = {}
    
    for juego in juegos:
        nombre = f"Formación por {juego} ({DIFICULTAD.capitalize()})"
        resultado = extraer_formacion_unificada(juego, DIFICULTAD)
        resultados_finales[nombre] = resultado
        
    print("\n================== RESUMEN DE ANÁLISIS DE FORMACIÓN ==================")
    for nombre, resultado in resultados_finales.items():
        print(f"\n--- {nombre} ---")
        if resultado and resultado.get('formacion'):
            print(f"✅ Formación Detectada: {resultado['formacion']}")
            print(f"   Posiciones (11): {resultado['posiciones']}")
            print(f"   Conteo: Defensas({resultado['conteo']['DEFENSAS']}) - Centrocampistas({resultado['conteo']['CENTROCAMPISTAS']}) - Delanteros({resultado['conteo']['DELANTEROS']})")
        else:
            print("❌ FALLO en la extracción de la Formación.")