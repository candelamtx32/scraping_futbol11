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
CLASE_CONTENEDOR_PISTA = "nextTeam" 

# DIFICULTAD CONFIGURADA: Normal
VALOR_DIFICULTAD_INTERNO = "normal" 
NOMBRE_DIFICULTAD = "Normal"

URL_CLUBES = "https://futbol-11.com/futbol11-clubs"
TIEMPO_MAXIMO_SEGUNDOS = 120 # 2 minutos de espera

def extraer_clubes_jugando():
    """
    Inicia el juego en modo 'Normal', espera hasta 120 segundos mientras el usuario juega,
    y monitorea la aparición de 11 nombres de clubes únicos.
    """
    
    SELECTOR_INPUT_DIFICULTAD = f'input[value="{VALOR_DIFICULTAD_INTERNO}"]'
    SELECTOR_BOTON_START = 'button.searchButton.startGame' 

    print(f"\n>>>> INICIANDO MONITOR FORMACIÓN CLUBES | DIFICULTAD: {NOMBRE_DIFICULTAD} | URL: {URL_CLUBES} <<<<")
    
    opciones = Options()
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=opciones) 
    
    clubes_encontrados = set()
    
    try:
        driver.get(URL_CLUBES)
        
        # 1. ACEPTAR COOKIES
        print("1. Aceptando cookies...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, ID_BOTON_COOKIES))).click()
        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, ID_BOTON_COOKIES))) 
        time.sleep(1) 

        # 2. SELECCIONAR DIFICULTAD (Usamos 'normal')
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
        
        while time.time() - start_time < TIEMPO_MAXIMO_SEGUNDOS and len(clubes_encontrados) < 11:
            
            try:
                # Esperamos brevemente a que el contenedor de la pista aparezca o se actualice
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, CLASE_CONTENEDOR_PISTA)))
                
                html_cargado = driver.page_source
                sopa = BeautifulSoup(html_cargado, 'html.parser')
                
                # Extraemos el texto del club (del tag <p> dentro del div.nextTeam)
                contenedor_pista = sopa.find('div', class_=CLASE_CONTENEDOR_PISTA)
                
                if contenedor_pista:
                    club_element = contenedor_pista.find('p')
                    if club_element:
                        club_name = club_element.get_text(strip=True)
                        
                        # Si es un nombre nuevo y válido, lo añadimos al set
                        if club_name and club_name not in clubes_encontrados:
                            clubes_encontrados.add(club_name)
                            print(f"   [Club Encontrado]: '{club_name}' | Total: {len(clubes_encontrados)}/11")
                            
            except:
                # Si el elemento no está visible temporalmente, continuamos
                pass
            
            time.sleep(1) # Esperamos 1 segundo antes de volver a escanear

        # 5. Cierre condicional
        if len(clubes_encontrados) >= 11:
            print(f"\n✅ META CUMPLIDA: Se encontraron 11 clubes en {int(time.time() - start_time)} segundos. Cerrando navegador.")
        else:
            print(f"\n⏳ TIEMPO AGOTADO: Se encontraron {len(clubes_encontrados)}/11 clubes. Cerrando navegador.")

        return list(clubes_encontrados)

    except Exception as e:
        print(f"❌ Ocurrió un error en el scraping: {e}")
        return list(clubes_encontrados)
    finally:
        driver.quit()

# -----------------------------------------------------------------------------
# |                      EJECUCIÓN DEL PROYECTO (ÚNICA VEZ)                     |
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    resultados_finales = extraer_clubes_jugando()
        
    print(f"\n================== RESUMEN FINAL DE CLUBES ({NOMBRE_DIFICULTAD}) ==================")
    if resultados_finales:
        print(f"Total de clubes únicos extraídos: {len(resultados_finales)}")
        print("Lista de Clubes:")
        for i, club in enumerate(resultados_finales, 1):
            print(f"  {i}. {club}")
    else:
        print("❌ FALLO: No se pudo extraer ningún club.")