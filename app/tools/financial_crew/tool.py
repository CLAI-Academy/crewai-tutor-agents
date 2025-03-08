from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from crewai.tools import BaseTool
import random
from datetime import datetime, timedelta


class CryptoDataTool(BaseTool):
    name: str = "Crypto Data Tool"
    description: str = "Scrape de datos actuales e históricos de criptomonedas."

    def _run(self) -> dict:
        # Diccionario de criptomonedas
        cryptos = {
            1: "bitcoin",
            2: "ethereum",
            3: "crp",
            4: "bnb",
            5: "solana",
            6: "cardano",
            7: "dogecoin",
            8: "tron",
            9: "avalanche",
            10: "toncoin"
        }
        
        resultados = {}
        # Se realizan 3 ejecuciones
        for i in range(1, 3):
            # Seleccionar una criptomoneda al azar
            crypto = random.choice(list(cryptos.values()))
            
            # Calcular fechas a buscar a partir de la fecha actual
            fecha_actual = datetime.now()
            fechas = {
                "un_dia": (fecha_actual - timedelta(days=1)).strftime("%b %d, %Y"),
                "tres_dias": (fecha_actual - timedelta(days=3)).strftime("%b %d, %Y"),
                "una_semana": (fecha_actual - timedelta(days=7)).strftime("%b %d, %Y"),
                "dos_semanas": (fecha_actual - timedelta(days=14)).strftime("%b %d, %Y"),
                "un_mes": (fecha_actual - timedelta(days=30)).strftime("%b %d, %Y"),
                "un_mes_y_medio": (fecha_actual - timedelta(days=45)).strftime("%b %d, %Y")
            }
            
            # Obtener el precio actual
            datos_actuales = self.scrape_current(crypto)
            
            # Obtener los datos históricos para cada fecha
            datos_historicos = {}
            for key, fecha in fechas.items():
                datos_historicos[key] = self.scrape_historic(crypto, fecha)
            
            resultados[f"Ejecución {i} - {crypto}"] = {
                "datos_actuales": datos_actuales,
                "datos_historicos": datos_historicos
            }
        
        return resultados

    def scrape_current(self, moneda: str) -> dict:
        """
        Scrapea el precio actual de la criptomoneda.
        """
        class Scraper:
            def __init__(self, moneda: str):
                self.moneda = moneda.lower()
                self.url = f"https://coinmarketcap.com/es/currencies/{self.moneda}/"
                self.options = webdriver.ChromeOptions()
                self.options.add_argument("--headless")

            def run(self) -> str:
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=self.options
                )
                driver.get(self.url)
                try:
                    span = driver.find_element(By.CLASS_NAME, "sc-65e7f566-0.WXGwg.base-text")
                    resultado = span.text
                except Exception as e:
                    resultado = f"Error: {e}"
                driver.quit()
                return resultado

        resultado = Scraper(moneda).run()
        if resultado.startswith("Error:"):
            return {"error": resultado}
        return {"Precio": resultado}

    def scrape_historic(self, moneda: str, fecha: str) -> dict:
        """
        Scrapea los datos históricos de la criptomoneda para una fecha dada.
        """
        class Scraper:
            def __init__(self, moneda: str, fecha: str):
                self.moneda = moneda
                self.fecha = fecha
                self.url = f"https://coinmarketcap.com/es/currencies/{self.moneda}/historical-data/"
                self.options = webdriver.ChromeOptions()
                self.options.add_argument("--headless")

            def run(self) -> dict:
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=self.options
                )
                driver.get(self.url)
                wait = WebDriverWait(driver, 10)
                try:
                    fila = wait.until(
                        EC.visibility_of_element_located(
                            (By.XPATH, f"//tbody/tr[td[normalize-space(text())='{self.fecha}']]")
                        )
                    )
                    columnas = fila.find_elements(By.TAG_NAME, "td")
                    resultado = {
                        "Apertura": columnas[1].text,
                        "Alza": columnas[2].text,
                        "Baja": columnas[3].text,
                        "MarketCap": columnas[6].text
                    }
                except Exception as e:
                    resultado = {"error": str(e)}
                driver.quit()
                return resultado

        return Scraper(moneda, fecha).run()
    

import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ActionsDataTool(BaseTool):
    name: str = "Actions Data Tool"
    description: str = "Scrape de datos actuales e históricos de acciones."

    def _run(self) -> dict:
        actions = {
            1: "nvidia-corp",
            2: "apple-computer-inc",
            3: "nextera-energy-inc",
            4: "united-health-group",
            5: "mastercard-cl-a",
            6: "amazon-com-inc",
            7: "boeing-co",
            8: "nike",
            9: "pfizer"
        }
        
        resultados = {}
        for i in range(1, 3):
            action = random.choice(list(actions.values()))
            datos_actuales = self.scrape_current(action)
            datos_historicos = self.scrape_historic(action)
            
            resultados[f"Ejecución {i} - {action}"] = {
                "datos_actuales": datos_actuales,
                "datos_historicos": datos_historicos
            }
        
        return resultados
    
    def scrape_current(self, action: str) -> dict:
        url = f"https://www.investing.com/equities/{action}"
        options = webdriver.ChromeOptions()
        # Se eliminan las opciones de headless y tamaño de ventana.
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        try:
            wait = WebDriverWait(driver, 10)
            # Scroll para asegurar que se carga todo el contenido.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            precio_elemento = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@data-test='instrument-price-last']")
            ))
            precio = precio_elemento.text
        except Exception as e:
            precio = f"Error: {e}"
        driver.quit()
        return {"Precio": precio}
    
    def scrape_historic(self, action: str) -> dict:
        url = f"https://es.investing.com/equities/{action}-historical-data"
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
                
        # Declaración de las fechas para extraer datos históricos.
        fecha_actual = datetime.now()
        fechas = {
            "hoy": fecha_actual.strftime("%d.%m.%Y"),
            "una_semana": (fecha_actual - timedelta(weeks=1)).strftime("%d.%m.%Y"),
            "un_mes": (fecha_actual - relativedelta(months=1)).strftime("%d.%m.%Y")
        }
        
        resultados = {}
        # Se recorre la lista de fechas y se extrae la fila correspondiente para cada fecha.
        for key, fecha in fechas.items():
            try:
                fila = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//tr[td/time[@datetime='{fecha}']]")
                ))
                columnas = fila.find_elements(By.TAG_NAME, "td")
                resultados[key] = {
                    "Fecha": fecha,
                    "Apertura": columnas[2].text,
                    "Máximo": columnas[3].text,
                    "Mínimo": columnas[4].text,
                    "Variacion": columnas[6].text
                }
            except Exception as e:
                print(f"Error extrayendo datos para {key} ({fecha}): {e}")
                resultados[key] = {"error": str(e)}
                continue
        driver.quit()
        return resultados