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
CLASE_CONTENEDOR_PISTA = "nextTeam" # Contenedor de la pista (país actual)

# DIFICULTAD CONFIGURADA: Normal
VALOR_DIFICULTAD_INTERNO = "normal" 
NOMBRE_DIFICULTAD = "Normal"

URL_PAISES = "https://futbol-11.com/futbol11"
TIEMPO_MAXIMO_SEGUNDOS = 120 # 2 minutos de espera

def extraer_paises_normal():
    """
    Inicia el juego en modo 'Normal', espera hasta 120 segundos mientras el usuario juega,
    y monitorea la aparición de 11 nombres de países únicos.
    """
    
    SELECTOR_INPUT_DIFICULTAD = f'input[value="{VALOR_DIFICULTAD_INTERNO}"]'
    SELECTOR_BOTON_START = 'button.searchButton.startGame' 

    print(f"\n>>>> INICIANDO MONITOR FORMACIÓN PAÍSES | DIFICULTAD: {NOMBRE_DIFICULTAD} | URL: {URL_PAISES} <<<<")
    
    opciones = Options()
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=opciones) 
    
    paises_encontrados = set()
    
    try:
        driver.get(URL_PAISES)
        
        # 1. ACEPTAR COOKIES
        print("1. Aceptando cookies...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, ID_BOTON_COOKIES))).click()
        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, ID_BOTON_COOKIES))) 
        time.sleep(1) 

        # 2. SELECCIONAR DIFICULTAD
        print(f"2. Forzando la selección de dificultad '{NOMBRE_DIFICULTAD}'...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_INPUT_DIFICULTAD)))
        driver.execute_script(f"document.querySelector('{SELECTOR_INPUT_DIFICULTAD}').click();")
        
        # 3. CLIC EN START GAME
        print("3. Forzando el clic en 'Start Game'...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_BOTON_START)))
        driver.execute_script(f"document.querySelector('{SELECTOR_BOTON_START}').click();")
        
        # 4. MONITORIZACIÓN DE PISTAS (Juego manual)
        print(f"\n4. INICIO DE MONITOREO. Tienes {TIEMPO_MAXIMO_SEGUNDOS} segundos para jugar.")
        
        start_time = time.time()
        
        while time.time() - start_time < TIEMPO_MAXIMO_SEGUNDOS and len(paises_encontrados) < 11:
            
            try:
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, CLASE_CONTENEDOR_PISTA)))
                
                html_cargado = driver.page_source
                sopa = BeautifulSoup(html_cargado, 'html.parser')
                
                contenedor_pista = sopa.find('div', class_=CLASE_CONTENEDOR_PISTA)
                
                if contenedor_pista:
                    pais_element = contenedor_pista.find('p')
                    if pais_element:
                        pais_name = pais_element.get_text(strip=True)
                        
                        if pais_name and pais_name not in paises_encontrados:
                            paises_encontrados.add(pais_name)
                            print(f"   [País Encontrado]: '{pais_name}' | Total: {len(paises_encontrados)}/11")
                            
            except:
                pass
            
            time.sleep(1) 

        # 5. Cierre condicional
        if len(paises_encontrados) >= 11:
            print(f"\n✅ META CUMPLIDA: Se encontraron 11 países en {int(time.time() - start_time)} segundos. Cerrando navegador.")
        else:
            print(f"\n⏳ TIEMPO AGOTADO: Se encontraron {len(paises_encontrados)}/11 países. Cerrando navegador.")

        return list(paises_encontrados)

    except Exception as e:
        print(f"❌ Ocurrió un error en el scraping: {e}")
        return list(paises_encontrados)
    finally:
        driver.quit()

# -----------------------------------------------------------------------------
# |                      EJECUCIÓN DEL PROYECTO (ÚNICA VEZ)                     |
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    resultados_finales = extraer_paises_normal()
        
    print(f"\n================== RESUMEN FINAL DE PAÍSES ({NOMBRE_DIFICULTAD}) ==================")
    if resultados_finales:
        print(f"Total de países únicos extraídos: {len(resultados_finales)}")
        print("Lista de Países:")
        for i, pais in enumerate(resultados_finales, 1):
            print(f"  {i}. {pais}")
    else:
        print("❌ FALLO: No se pudo extraer ningún país.")