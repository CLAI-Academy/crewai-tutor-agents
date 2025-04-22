from typing import Any
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from app.crews.chill_crew.chill_crew import Chillcrew
from app.crews.financial_crew.financial_crew import FinanceCrew
import openai

class InitialState(BaseModel):
    categorias: str = ""
    user_input: str = ""

class RouterFlow(Flow[InitialState]):    
    @start()
    def start_method(self):
        self.financialflow = FinanceCrew()  
        self.chillflow = Chillcrew()   
        print(self.state.user_input)
        client = openai.Client()
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un agente experto en detectar la categoria de una consulta. Debes responder solo la categoria de la consulta. Las categorias de la consulta pueden ser: Peluqueria, Finanzas, Neutro"},
                {"role": "user", "content": self.state.user_input}
            ]
        )
        categoria = respuesta.choices[0].message.content.strip()
        print(categoria)
        self.state.categorias = categoria
        return self.state

    @router(start_method)
    def route_to_crew(self):
        if self.state.categorias == "Peluqueria":
            return "peluqueria"
        elif self.state.categorias == "Finanzas":
            return "finanzas"
        elif self.state.categorias == "Neutro":
            return "chill"

    @listen("peluqueria")
    def peluqueria(self):
        print("Crew peluqueria")
        return ("Crewdddd")

    @listen("finanzas")
    def finanzas(self):
        result = self.financialflow.crew().kickoff(inputs={'prompt': self.state.user_input})
        return result

    @listen("chill")
    def chill(self):
        result = self.chillflow.crew().kickoff(inputs={'message': self.state.user_input})
        return result


if __name__ == "__main__":
    mensaje = "HOLAAA!"
    flow = RouterFlow()
    flow.state.user_input = mensaje
    flow.kickoff()