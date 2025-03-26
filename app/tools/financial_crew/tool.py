from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import yfinance as yf
from datetime import datetime, timedelta
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import requests
from typing import List, Dict, Any

class CryptoDataTool(BaseTool):
    name: str = "Crypto Data Tool"
    description: str = "Scrape de datos actuales e históricos de criptomonedas."

    def _run(self) -> dict:
        # Diccionario de criptomonedas
        cryptos = {
            1: "bitcoin",
            2: "ethereum",
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
            
            # Obtener los datos históricos en una sola ejecución del webdriver
            datos_historicos = self.scrape_historic(crypto, fechas)
            
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
 
    def scrape_historic(self, moneda: str, fechas: dict) -> dict:
        """
        Scrapea los datos históricos de la criptomoneda para las fechas dadas en una sola ejecución del webdriver.
        """
        resultados = {}
        url = f"https://coinmarketcap.com/es/currencies/{moneda}/historical-data/"
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        for key, fecha in fechas.items():
            try:
                fila = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//tbody/tr[td[normalize-space(text())='{fecha}']]")
                    )
                )
                columnas = fila.find_elements(By.TAG_NAME, "td")
                resultados[key] = {
                    "Apertura": columnas[1].text,
                    "Alza": columnas[2].text,
                    "Baja": columnas[3].text,
                    "MarketCap": columnas[6].text
                }
            except Exception as e:
                resultados[key] = {"error": str(e)}
        
        driver.quit()
        return resultados
    
class ActionsDataToolInput(BaseModel):
    ticker: str = Field(..., description="Ticker de la acción a analizar")

class ActionsDataTool(BaseTool):
    name: str = "Actions Data Tool"
    description: str = "Scrape de datos actuales e históricos de acciones."
    args_schema = ActionsDataToolInput

    def _run(self, ticker: str) -> dict:
        today = datetime.today()
        fechas = {
            "1_dia": today - timedelta(days=1),
            "1_semana": today - timedelta(weeks=1),
            "1_mes": today - timedelta(days=30),    
            "3_meses": today - timedelta(days=90),    
            "6_meses": today - timedelta(days=180),   
            "1_año": today - timedelta(days=365),
            "2_años": today - timedelta(days=730)
        }
        
        datos_historicos = self.obtener_datos_en_fechas(ticker, fechas)
        return datos_historicos
    


    def obtener_datos_en_fechas(self, ticker, fechas):
        """
        Obtiene para cada fecha los datos relevantes:
        apertura, máximo, mínimo, cierre, cierre ajustado, volumen.
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

class TickerFinderToolInput(BaseModel):
    """Esquema de entrada para la herramienta Ticker Finder Tool."""
    risk: str = Field(..., description="Nivel de riesgo a asumir: very_high/high/medium/low")

class TickerFinderTool(BaseTool):
    name: str = "Ticker Finder Tool"
    description: str = "Filtra tickers basados en nivel de riesgo desde un archivo CSV."
    args_schema = TickerFinderToolInput

    csv_url: str = "https://storage.googleapis.com/bucket-tickers-madrid/ticker_results.csv"
    csv_filename: str = "ticker_results.csv"

    def __init__(self):
        """Inicializa la herramienta con valores predeterminados."""
        super().__init__()

    def _run(self, risk: str) -> dict:
        """
        Método principal que recibe el nivel de riesgo y ejecuta la búsqueda.
        
        Paso 1: Descarga el archivo CSV con los tickers y sus datos.
        Paso 2: Filtra los tickers según el nivel de riesgo.
        Paso 3: Devuelve 3 tickers aleatorios de entre los resultados que cumplan los criterios.
        """
        try:
            # Paso 1: Descargar el CSV con los tickers y sus datos
            self.descargar_csv()
            
            # Paso 2: Filtrar los tickers según el nivel de riesgo
            resultados = self.filtrar_tickers_por_riesgo(risk.lower())
            
            # Paso 3: Seleccionar 3 tickers aleatorios (si hay más de 3 resultados)
            if len(resultados) > 3:
                resultados = random.sample(resultados, 3)
            
            # Paso 4: Eliminar el archivo CSV descargado
            self.eliminar_csv()
            
            return {"results": resultados}
        except Exception as e:
            # En caso de error, asegurarse de eliminar el CSV si existe
            self.eliminar_csv()
            raise e

    def descargar_csv(self) -> None:
        """
        Descarga el archivo CSV con los tickers y sus datos.
        """
        try:
            response = requests.get(self.csv_url)
            response.raise_for_status()
            
            with open(self.csv_filename, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error al descargar el CSV: {e}")
            raise e

    def eliminar_csv(self) -> None:
        """
        Elimina el archivo CSV descargado.
        """
        try:
            if os.path.exists(self.csv_filename):
                os.remove(self.csv_filename)
        except Exception as e:
            print(f"Error al eliminar el CSV: {e}")

    def filtrar_tickers_por_riesgo(self, risk: str) -> List[Dict[str, Any]]:
        """
        Filtra los tickers del CSV según el nivel de riesgo especificado.
        
        Retorna:
          Una lista de diccionarios con la información de cada ticker que cumple el criterio de riesgo.
        """
        resultados = []
        try:
            # Leer el CSV descargado
            df = pd.read_csv(self.csv_filename)
            
            # Filtrar por el nivel de riesgo
            df_filtrado = df[df['risk'] == risk]
            
            # Convertir a lista de diccionarios
            for _, row in df_filtrado.iterrows():
                resultados.append({
                    "ticker": row.get('ticker'),
                    "precio_actual": row.get('precio_actual'),
                    "media_50": row.get('media_50'),
                    "dividend_yield_pct": row.get('dividend_yield_pct'),
                    "pe_ratio": row.get('pe_ratio'),
                    "risk": row.get("risk")
                })
        except Exception as e:
            print(f"Error al filtrar tickers por riesgo: {e}")
            raise e
        
        return resultados


# Ejecución para probar las tool
if __name__ == "__main__":
    tool = TickerFinderTool(risk="low")
    print(tool._run())