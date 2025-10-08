import os
import pickle
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

# ************* Variáveis de Configuração *************
ML_BASE_URL = "https://www.mercadolivre.com.br/"
ML_LOGIN_URL = "https://www.mercadolivre.com.br/anuncios/login"
# URL de destino que contém o fragmento
ML_AFILIADOS_URL = "https://www.mercadolivre.com.br/afiliados/hub#menu-user"
COOKIES_FILE = "cookies.pkl"
# ***************************************************

options = Options()
options.add_experimental_option("detach", True)
options.add_argument("--disable-blink-features=AutomationControlled")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30) 


def save_cookies(driver, location):
    print("Salvando cookies da sessão...")
    with open(location, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)
    print("Cookies salvos com sucesso.")


def load_cookies(driver, location):
    driver.get(ML_BASE_URL) 
    with open(location, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie) 


def login_and_save_cookies():
    driver.get(ML_LOGIN_URL)
    input("\nFAÇA O LOGIN MANUALMENTE no navegador aberto. Após o login BEM-SUCEDIDO, pressione ENTER aqui...")
    
    # Salva os cookies APÓS o login manual estar concluído
    save_cookies(driver, COOKIES_FILE)
    
    # Após o salvamento, garante que a navegação continue para o destino
    driver.get(ML_AFILIADOS_URL)


def start_session():
    if os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
        print("Tentando iniciar sessão com cookies salvos...")
        try:
            load_cookies(driver, COOKIES_FILE)
            driver.refresh()
            time.sleep(5) 
            
            driver.get(ML_AFILIADOS_URL)

            if driver.current_url.startswith(ML_AFILIADOS_URL):
                 print("Sessão carregada com sucesso! Navegando para a página de Afiliados.")
                 # Após a navegação, uma pequena espera para o JavaScript carregar o fragmento
                 time.sleep(3) 
                 return True
            else:
                 print("Cookies expiraram. Redirecionando para login manual.")
                 login_and_save_cookies()
                 return True 

        except Exception as e:
            print(f"Erro ao carregar ou usar cookies: {e}. Iniciando login manual.")
            login_and_save_cookies()
            return True
    else:
        print("Arquivo de cookies não existe. Faça login manualmente.")
        login_and_save_cookies()
        return True
        

def navegar_e_extrair_produtos():
    links_capturados = []
    count_anterior = 0 
    

    while True:
        produtos  = driver.find_elements(By.CLASS_NAME, "poly-component__title")

        for produto in produtos[count_anterior:]:
            link = produto.get_attribute("href")
            links_capturados.append(link)
            print(link)
        
        if count_atual == count_anterior:
            print("fim da execução")
            break

            

        count_atual = len(produtos)
        count_anterior  = count_atual

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Pausa para carregamento


    
        
    # AGORA VOCÊ PODE INSERIR O CÓDIGO DE ROLAGEM E EXTRAÇÃO AQUI
    
    # Exemplo: Espera um elemento chave para confirmar o carregamento do Hub de Afiliados
    try:
        # Ajuste este seletor para um elemento que só aparece no HUB de Afiliados
        wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Hub de Afiliados")]')))
        print("Página de Afiliados totalmente carregada.")
    except:
        print("Não foi possível carregar a página de Afiliados com sucesso. Verifique o login.")
        return

    # ... Sua lógica de rolagem e scraping segue aqui ...
    
    print("Extração de dados concluída.")


# --- FLUXO PRINCIPAL ---
start_session()
navegar_e_extrair_produtos()

input("Pressione ENTER para fechar...")
driver.quit()