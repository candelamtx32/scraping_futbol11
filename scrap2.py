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
CLASE_ICONO_RENDICION = "flagGiveUp" 
CLASE_BOTON_YES_CONFIRMACION = "searchButton.buttonText.blue"
CLASE_BOTON_CERRAR_MODAL = "modalClose" 
# CLASE REAL Y ESTABLE del DIV contenedor de CADA respuesta
CLASE_DATO_CONEXIONES = "finishedConnection" 

def extraer_connections(dificultad_valor):
    """
    Extrae las 4 descripciones de respuesta del juego Connections,
    ejecutando el flujo de Aceptar Cookies -> Start Game -> Rendirse (3 pasos).
    """
    
    URL = "https://futbol-11.com/futbol11-connections"
    
    SELECTOR_INPUT_DIFICULTAD = f'input[value="{dificultad_valor}"]'
    SELECTOR_BOTON_START = 'button.searchButton.startGame' 
    
    print(f"\n>>>> INICIANDO CONNECTIONS | DIFICULTAD: {dificultad_valor} | Buscando contenedores: .{CLASE_DATO_CONEXIONES} <<<<")
    
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
        
        # --- PASOS DE RENDICIÓN (4a, 4b, 4c) ---
        
        # 4a. Clic en Bandera (Rendición) - Forzado con JS
        print("4a. Ejecutando flujo de rendición: Forzando clic en Bandera...")
        selector_bandera = f"i.{CLASE_ICONO_RENDICION}"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_bandera)))
        driver.execute_script(f"document.querySelector('{selector_bandera}').click();")
        
        # 4b. Clic en confirmar 'Yes' - Forzado con JS
        print("4b. Confirmando rendición con 'Yes'...")
        selector_yes = f"button.{CLASE_BOTON_YES_CONFIRMACION.replace(' ', '.')}"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_yes)))
        driver.execute_script(f"document.querySelector('{selector_yes}').click();")
        print("✅ Rendición confirmada.")

        # 4c. CERRAR VENTANA MODAL DE ESTADÍSTICAS - Forzado con JS
        print("4c. Cerrando ventana modal de estadísticas...")
        selector_modal_close = f"button.{CLASE_BOTON_CERRAR_MODAL.replace(' ', '.')}"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_modal_close)))
        driver.execute_script(f"document.querySelector('{selector_modal_close}').click();")
        
        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, selector_modal_close))) 
        print("✅ Modal cerrada.")
        
        # 5. EXTRACCIÓN DEL DATO FINAL
        print(f"5. Esperando a que el contenedor ('{CLASE_DATO_CONEXIONES}') cargue...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, CLASE_DATO_CONEXIONES)))
        
        html_cargado = driver.page_source
        sopa = BeautifulSoup(html_cargado, 'html.parser')
        
        # Búsqueda de TODOS los contenedores (div class="finishedConnection")
        contenedores_encontrados = sopa.find_all('div', attrs={'class': CLASE_DATO_CONEXIONES})

        if contenedores_encontrados:
            datos_extraidos = []
            for contenedor in contenedores_encontrados:
                # Dentro de cada contenedor, buscamos el primer <p> (que es la descripción)
                parrafo_descripcion = contenedor.find('p') 
                if parrafo_descripcion:
                    # Limpiamos el texto, eliminando el <br> y el espacio extra
                    texto_limpio = parrafo_descripcion.get_text(strip=True)
                    datos_extraidos.append(texto_limpio)
            
            print(f"✅ Éxito! Se extrajeron {len(datos_extraidos)} elementos.")
            return datos_extraidos
        else:
            print(f"❌ Error: No se encontraron elementos con la clase contenedora '{CLASE_DATO_CONEXIONES}'.")
            return None

    except Exception as e:
        print(f"❌ Ocurrió un error en el scraping: {e}")
        return None
    finally:
        driver.quit()

# -----------------------------------------------------------------------------
# |                      EJECUCIÓN DE LAS PRUEBAS DE CONNECTIONS                |
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    resultados_finales = {}
    
    # Prueba 1: Dificultad Easy
    resultados_finales["Connections Game (Easy)"] = extraer_connections("easy")
    
    # Prueba 2: Dificultad Normal
    resultados_finales["Connections Game (Normal)"] = extraer_connections("normal")
    
    print("\n================== RESUMEN DE EXTRACCIÓN CONNECTIONS ==================")
    for nombre, resultado in resultados_finales.items():
        if isinstance(resultado, list):
            print(f"[{nombre}]: {len(resultado)} elementos extraídos: {resultado}")
        else:
            print(f"[{nombre}]: {resultado if resultado else 'FALLO'}")