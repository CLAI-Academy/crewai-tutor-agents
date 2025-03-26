from typing import Any
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from crewai.flow.persistence.base import FlowPersistence
from app.crews.chill_crew.chill_crew import Chillcrew
from app.crews.financial_crew.financial_crew import FinanceCrew
import openai


class ExampleState(BaseModel):
    categorias: str = ""

class RouterFlow(Flow[ExampleState]):
    
    @start()
    def start_method(self):
        self.financialflow = FinanceFlow()  # Instancia para el flujo financiero
        self.chillflow = ChillFlow()   
        print("Starting the structured flow")
        client = openai.Client()
        respuesta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un agente experto en detectar la categoria de una consulta. Debes responder solo la categoria de la consulta. Las categorias de la consulta pueden ser: Peluqueria, Finanzas, Neutro"},
            {"role": "user", "content": mensaje}
        ]
        )
        categoria = respuesta.choices[0].message.content.strip()
        print(categoria)
        self.state.categorias = categoria

    @router(start_method)
    def second_method(self):
        if self.state.categorias == "Peluqueria":
            return("peluqueria")
        elif self.state.categorias == "Finanzas":
            return("finanzas")
        elif self.state.categorias == "Neutro":
            return("chill")

    @listen("peluqueria")
    def peluqueria(self):
        print("Crew peluqueria")

    @listen("finanzas")
    def finanzas(self):
        self.financialflow.state['user_input'] = mensaje
        self.financialflow.kickoff()

    @listen("chill")
    def chill(self):
        self.chillflow.state['user_input'] = mensaje
        self.chillflow.kickoff()


class FinanceFlow(Flow):
    finance_crew=FinanceCrew()

    @start()
    def empezar_conversacion(self):
        result=self.finance_crew.crew().kickoff(inputs={'prompt': self.state['user_input']})
        return result
    
class ChillFlow(Flow):    
    chill_crew=Chillcrew()

    @start()
    def empezar_conversacion(self):
        result=self.chill_crew.crew().kickoff(inputs={'message': self.state['user_input']})
        return result
        

if __name__ == "__main__":
    # Crea una instancia del flow
    mensaje = "Cobro 5000 euros al mes, puedo invertir 1000 euros al mes, estoy harto que mi dinero solo pierda valor, quiero ganar dinero como sea, quiero riesgo!"
    flow = RouterFlow()
    flow.kickoff()
