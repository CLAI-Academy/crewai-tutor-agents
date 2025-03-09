from crewai.tools import BaseTool
import yfinance as yf
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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

    


class ActionsDataTool(BaseTool):
    name: str = "Actions Data Tool"
    description: str = "Scrape de datos actuales e históricos de acciones."

    def _run(self) -> dict:
        actions = {
            1: "NVDA", #nvidia
            2: "AAPL",  #apple
            3: "NEE", # nextera energy
            4: "REP.MC", # Repsol
            6: "AMZN", # amazon
            7: "NFLX", # netflix
            8: "nke", # nike
            9: "MSFT" # microsoft
        }
        
        resultados = {}
        today = datetime.today()
        fechas = {
            "1_dia": today - timedelta(days=1),
            "1_semana": today - timedelta(weeks=1),
            "1_mes": today - timedelta(days=30),      # Aproximación de 1 mes
            "3_meses": today - timedelta(days=90),      # Aproximación de 3 meses
            "6_meses": today - timedelta(days=180),     # Aproximación de 6 meses
            "1_año": today - timedelta(days=365),
            "2_años": today - timedelta(days=730)
        }

        for i in range(1, 3):
            ticker = random.choice(list(actions.values()))
            print(ticker)
            datos_historicos = self.obtener_datos_en_fechas(ticker, fechas)
            
            resultados[f"Ejecución {i} - {ticker}"] = {
                "datos_historicos": datos_historicos
            }
        
        return resultados
    

   

    def obtener_datos_en_fechas(self, ticker, fechas):
        """
        Obtiene para cada fecha los datos relevantes:
        apertura, máximo, mínimo, cierre, cierre ajustado, volumen, dividendos y splits.
        Si la fecha exacta no se encuentra (por ejemplo, en fin de semana),
        se toma el último registro disponible anterior a esa fecha.
        """
        # Determinar el rango de fechas a descargar
        fecha_inicio = min(fechas.values()).strftime('%Y-%m-%d')
        fecha_fin = datetime.today().strftime('%Y-%m-%d')
        
        # Descargar datos históricos
        datos = yf.Ticker(ticker).history(start=fecha_inicio, end=fecha_fin)
        
        datos_resultado = {}
        for label, fecha in fechas.items():
            fecha_str = fecha.strftime('%Y-%m-%d')
            try:
                # Se intenta obtener la fila exacta
                fila = datos.loc[fecha_str]
            except KeyError:
                # Si no existe, se toma el último registro disponible anterior a la fecha
                fila = datos.loc[:fecha_str].iloc[-1]
            
            # Se extraen los datos relevantes y se guardan en un diccionario
            datos_resultado[label] = {
                "Open": float(fila.get("Open", 0) or 0),
                "High": float(fila.get("High", 0) or 0),
                "Low": float(fila.get("Low", 0) or 0),
                "Close": float(fila.get("Close", 0) or 0),
                "Adj Close": float(fila.get("Adj Close", 0) or 0) if fila.get("Adj Close") is not None else None,
                "Volume": float(fila.get("Volume", 0) or 0)
                }

        return datos_resultado

if __name__ == "__main__":
    tool = CryptoDataTool()
    print(tool._run())
