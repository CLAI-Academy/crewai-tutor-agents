from crewai.tools import BaseTool
import yfinance as yf
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
import random

class CryptoDataTool(BaseTool):
    name: str = "Crypto Data Tool"
    description: str = "Obtiene datos actuales e históricos de criptomonedas usando la API de CoinGecko."

    def _run(self) -> dict:
        cg = CoinGeckoAPI()
        # Diccionario de criptomonedas con coin IDs válidos en CoinGecko
        cryptos = {
            1: "bitcoin",
            2: "ethereum",
            3: "crypto-com-chain",  # reemplaza "crp" por su id correcto
            4: "binancecoin",       # reemplaza "bnb" por su id correcto
            5: "solana",
            6: "cardano",
            7: "dogecoin",
            8: "tron",
            9: "avalanche-2",       # id para Avalanche en CoinGecko
            10: "toncoin"
        }
        
        resultados = {}
        # Se realizan 2 ejecuciones (iteraciones 1 y 2)
        for i in range(1, 3):
            # Seleccionar una criptomoneda al azar
            crypto = random.choice(list(cryptos.values()))
            
            # Calcular fechas a buscar a partir de la fecha actual
            fecha_actual = datetime.now()
            fechas = {
                "un_dia": (fecha_actual - timedelta(days=1)),
                "tres_dias": (fecha_actual - timedelta(days=3)),
                "una_semana": (fecha_actual - timedelta(days=7)),
                "dos_semanas": (fecha_actual - timedelta(days=14)),
                "un_mes": (fecha_actual - timedelta(days=30)),
                "un_mes_y_medio": (fecha_actual - timedelta(days=45))
            }
            # CoinGecko requiere la fecha en formato "dd-mm-yyyy"
            fechas_formateadas = { key: fecha.strftime("%d-%m-%Y") for key, fecha in fechas.items() }
            
            # Obtener el precio actual usando la API
            datos_actuales = self.get_current(cg, crypto)
            
            # Obtener los datos históricos para cada fecha
            datos_historicos = {}
            for key, fecha in fechas_formateadas.items():
                datos_historicos[key] = self.get_historic(cg, crypto, fecha)
            
            resultados[f"Ejecución {i} - {crypto}"] = {
                "datos_actuales": datos_actuales,
                "datos_historicos": datos_historicos
            }
        
        return resultados

    def get_current(self, cg: CoinGeckoAPI, moneda: str) -> dict:
        """
        Obtiene el precio actual de la criptomoneda en USD.
        """
        try:
            price_data = cg.get_price(ids=moneda, vs_currencies='usd')
            if moneda in price_data:
                return {"Precio": price_data[moneda]['usd']}
            else:
                return {"error": "Datos no encontrados"}
        except Exception as e:
            return {"error": str(e)}

    def get_historic(self, cg: CoinGeckoAPI, moneda: str, fecha: str) -> dict:
        """
        Obtiene datos históricos de la criptomoneda para una fecha dada usando CoinGecko.
        La fecha debe estar en formato "dd-mm-yyyy".
        Nota: La API histórica de CoinGecko no provee datos de apertura, alza o baja, por lo que se retornan como 'N/A'.
        """
        try:
            historic_data = cg.get_coin_history_by_id(id=moneda, date=fecha)
            market_data = historic_data.get('market_data', {})
            if market_data:
                precio = market_data.get('current_price', {}).get('usd', 'N/A')
                market_cap = market_data.get('market_cap', {}).get('usd', 'N/A')
                return {
                    "Apertura": "N/A",
                    "Alza": "N/A",
                    "Baja": "N/A",
                    "MarketCap": market_cap,
                    "Precio": precio
                }
            else:
                return {"error": "Datos históricos no encontrados"}
        except Exception as e:
            return {"error": str(e)}

    


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
            action = random.choice(list(actions.values()))
            datos_actuales = self.scrape_current(action)
            datos_historicos = self.scrape_historic(action, fechas)
            
            resultados[f"Ejecución {i} - {action}"] = {
                "datos_actuales": datos_actuales,
                "datos_historicos": datos_historicos
            }
        
        return resultados
    

   

    def obtener_datos_en_fechas(ticker, fechas):
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
                "Open": fila.get("Open"),
                "High": fila.get("High"),
                "Low": fila.get("Low"),
                "Close": fila.get("Close"),
                "Adj Close": fila.get("Adj Close"),
                "Volume": fila.get("Volume"),
                "Dividends": fila.get("Dividends"),
                "Stock Splits": fila.get("Stock Splits")
            }
        return datos_resultado

if __name__ == "__main__":
    tool = ActionsDataTool()
    print(tool._run())
