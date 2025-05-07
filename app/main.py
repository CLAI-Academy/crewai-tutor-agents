from typing import Any
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from app.crews.chill_crew.chill_crew import Chillcrew
from app.crews.financial_crew.financial_crew import FinanceCrew
from app.crews.diagno_crew.diagno_crew import DiagnosticCrew
import openai
from opik.integrations.crewai import track_crewai
import opik

opik.configure(use_local=False)
track_crewai(project_name="CREWAI-TUTOR-AGENTS")

class InitialState(BaseModel):
    categoria: str = ""
    user_input: str = ""
    image: str = ""

class RouterFlow(Flow[InitialState]):    
    @start() 
    def start_method(self):  
        self.diagnosticFlow = DiagnosticCrew()   
        self.chillflow = Chillcrew()   
        self.financialflow = FinanceCrew()   
        print(f"Mensaje del usuario: {self.state.user_input}")
        
        # Clasificar el mensaje
        client = openai.Client()
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un agente experto en detectar la categoria de una consulta. Debes responder solo la categoria de la consulta. Las categorias de la consulta pueden ser: Peluqueria, Finanzas, Neutro"},
                {"role": "user", "content": self.state.user_input}
            ]
        )
        categoria = respuesta.choices[0].message.content.strip()
        print(f"Categoría detectada: {categoria}")
        self.state.categoria = categoria
        
        return self.state

    @router(start_method)
    def route_to_crew(self):
        print(f"Enrutando a la categoría: {self.state.categoria}")
        # Simplificar las condiciones para reducir posibles errores
        if self.state.categoria == "Peluqueria":
            return "diagnostic_router"
        elif self.state.categoria == "Finanzas":
            return "finanzas_route"
        else:  # Por defecto incluyendo "Neutro"
            return "chill_route"

    @listen("diagnostic_router")
    def diagnostic_handler(self):
        result = self.diagnosticFlow.crew().kickoff(inputs={'prompt': self.state.user_input, 'image': self.state.image})
        return result 

    @listen("finanzas_route")
    def finanzas_handler(self):
        print("Ejecutando flujo de finanzas")
        result = self.financialflow.crew().kickoff(inputs={'prompt': self.state.user_input})
        return result

    @listen("chill_route")
    def chill_handler(self):
        print("Ejecutando flujo chill")
        result = self.chillflow.crew().kickoff(inputs={'message': self.state.user_input})
        return result

if __name__ == "__main__":
    # Inicializar estado
    mensaje = "Hola, ¿cómo estás hoy?"

    # Crear y ejecutar el flujo
    flow = RouterFlow()
    flow.state.user_input = mensaje
    resultado = flow.kickoff()
    
    # Imprimir resultado final
    print("\nResultado final del flujo:")
    print(resultado)