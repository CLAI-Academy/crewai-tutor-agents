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
import time
import concurrent.futures


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
    risk: str = Field(..., description="Nivel de riesgo a asumir: low/medium/high")

class TickerFinderTool(BaseTool):
    name: str = "Ticker Finder Tool"
    description: str = "Filtra tickers basados en datos financieros y nivel de riesgo."
    args_schema = TickerFinderToolInput

    min_dividend_yield: float = 3.0
    max_pe: float = 20.0
    usar_media_50: bool = True

    def __init__(self):
        """Inicializa la herramienta con valores predeterminados."""
        # Primero inicializamos los atributos obligatorios

        
        # Después llamamos al constructor de la clase padre
        super().__init__()
    

    def _run(self, risk: str) -> dict:
        """
        Método principal que recibe el nivel de riesgo y ejecuta la búsqueda.
        
        Paso 0: Configura los parámetros basados en el riesgo.
        Paso 1: Extrae la lista de tickers desde Wikipedia.
        Paso 2: Pasa la lista a un método que los procesa y filtra.
        Paso 3: Devuelve 3 tickers aleatorios de entre los resultados que cumplan los criterios.
        """
        # Paso 0: Configurar los parámetros según el nivel de riesgo
        risk_lower = risk.lower()
        if risk_lower in ["low", "bajo"]:
            self.min_dividend_yield = 4.0  # Más restrictivo para riesgo bajo
            self.max_pe = 15.0
            self.usar_media_50 = True
        elif risk_lower in ["medium", "medio"]:
            self.min_dividend_yield = 3.0
            self.max_pe = 20.0
            self.usar_media_50 = True
        elif risk_lower in ["high", "alto"]:
            self.min_dividend_yield = 1.5  # Más permisivo para riesgo alto
            self.max_pe = 30.0
            self.usar_media_50 = False
        else:
            self.min_dividend_yield = 3.0
            self.max_pe = 20.0
            self.usar_media_50 = True
        
        # Paso 1: Obtener los tickers del S&P 500.
        tickers = self.obtener_tickers_sp500()
        
        # Paso 2: Procesar la lista de tickers para aplicar los filtros definidos.
        resultados = self.procesar_tickers(tickers, debug=True)
        
        # Paso 3: Seleccionar 3 tickers aleatorios (si hay más de 3 resultados)
        if len(resultados) > 3:
            resultados = random.sample(resultados, 3)
        
        return {"results": resultados}

    def obtener_tickers_sp500(self):
        """
        Extrae la lista de tickers del S&P 500 desde Wikipedia.
        
        Retorna:
          Una lista de símbolos bursátiles.
        """
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        try:
            df = pd.read_html(url, header=0)[0]
            tickers = df['Symbol'].tolist()
            return tickers
        except Exception as e:
            print(f"Error al obtener tickers del S&P 500: {e}")
            return []

    def procesar_tickers(self, tickers, debug=False, max_workers=5):
        """
        Procesa la lista de tickers de forma concurrente y aplica los filtros.
        
        Paso 1: Se envían tareas concurrentes para procesar cada ticker.
        Paso 2: Se recogen los resultados a medida que cada tarea finaliza.
        
        Retorna:
          Una lista de diccionarios con la información de cada ticker que cumple los criterios.
        """
        resultados = []
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Se envía una tarea por cada ticker usando el método procesar_ticker.
                # El diccionario 'futures' mapea cada tarea (future) con el ticker correspondiente.
                futures = {
                    executor.submit(self.procesar_ticker, ticker, debug): ticker 
                    for ticker in tickers
                }
                # Se itera sobre las tareas a medida que van finalizando.
                for future in concurrent.futures.as_completed(futures):
                    try:
                        res = future.result()
                    except TickerFinderTool.RateLimitedException as rle:
                        print("Rate limited detectado. Se detiene la búsqueda.")
                        break
                    except Exception as e:
                        if debug:
                            print(f"Error en ticker {futures[future]}: {e}")
                        continue
                    if res:
                        resultados.append(res)
        except Exception as e:
            if debug:
                print(f"Error en el procesamiento concurrente: {e}")
        return resultados

    def procesar_ticker(self, ticker, debug=False):
        """
        Procesa un ticker utilizando yfinance y aplica los filtros basados en:
          - Comparación del precio actual con la media de 50 días (si aplica).
          - Rendimiento mínimo por dividendos.
          - Ratio P/E máximo permitido.
        
        Retorna:
          Un diccionario con los datos del ticker si cumple los criterios, o None en caso contrario.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            precio_actual = info.get('regularMarketPrice')
            media_50 = info.get('fiftyDayAverage')
            dividend_yield = info.get('dividendYield')
            pe_ratio = info.get('trailingPE')
            dividend_yield_pct = dividend_yield * 100 if dividend_yield is not None else 0.0

            if debug:
                print(f"Ticker: {ticker}")
                print(f"  Precio actual: {precio_actual}")
                print(f"  Media 50 días: {media_50}")
                print(f"  Dividend Yield (%): {dividend_yield_pct}")
                print(f"  P/E Ratio: {pe_ratio}")

            cumple = True

            # Se aplica el filtro de precio en relación con la media de 50 días si es requerido.
            if self.usar_media_50:
                if precio_actual is not None and media_50 is not None:
                    if precio_actual >= media_50:
                        cumple = False
                        if debug:
                            print("  Falla: Precio actual no está por debajo de la media de 50 días.")
                else:
                    cumple = False
                    if debug:
                        print("  Falla: Datos insuficientes para comparar precio y media de 50 días.")

            # Se aplica el filtro del rendimiento por dividendos.
            if dividend_yield_pct < self.min_dividend_yield:
                cumple = False
                if debug:
                    print(f"  Falla: Dividend yield {dividend_yield_pct}% es menor que el mínimo requerido {self.min_dividend_yield}%.")

            # Se aplica el filtro del ratio P/E.
            if pe_ratio is None or pe_ratio > self.max_pe:
                cumple = False
                if debug:
                    print(f"  Falla: P/E Ratio {pe_ratio} no cumple el máximo permitido {self.max_pe}.")

            if cumple:
                if debug:
                    print("  Cumple todos los criterios.")
                return {
                    "ticker": ticker,
                    "precio_actual": precio_actual,
                    "media_50": media_50,
                    "dividend_yield_pct": dividend_yield_pct,
                    "pe_ratio": pe_ratio
                }
        except Exception as e:
            if "Too Many Requests" in str(e) or "Rate limited" in str(e):
                raise TickerFinderTool.RateLimitedException(str(e))
            if debug:
                print(f"Error procesando {ticker}: {e}")
        return None

    class RateLimitedException(Exception):
        """Excepción para indicar que se ha excedido el límite de peticiones."""
        pass


# Ejecución para probar las tool
if __name__ == "__main__":
    tool = TickerFinderTool(risk="low")
    print(tool._run())
