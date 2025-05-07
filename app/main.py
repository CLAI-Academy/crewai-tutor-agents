from typing import Any
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from app.crews.chill_crew.chill_crew import Chillcrew
from app.crews.financial_crew.financial_crew import FinanceCrew
from app.crews.diagno_crew.diagno_crew import DiagnosticCrew
import openai
from opik.integrations.crewai import track_crewai
import opik
from app.utils.websockets.manager import ws_manager

opik.configure(use_local=False)
track_crewai(project_name="CREWAI-TUTOR-AGENTS")

class InitialState(BaseModel):
    categoria: str = ""
    user_input: str = ""
    image: str = ""
    client_id: str = ""

class RouterFlow(Flow[InitialState]):    
    @start() 
    async def start_method(self):  
        self.diagnosticFlow = DiagnosticCrew(self.state.client_id)   
        self.chillflow = Chillcrew(self.state.client_id)   
        self.financialflow = FinanceCrew(self.state.client_id)   
         # Notificar status: pensando
    
        
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
    async def diagnostic_handler(self):
        # Establecer modo peluquería
        await ws_manager.send_to_client(self.state.client_id, {
                "mode": "peluqueria",
                "agents": self.diagnosticFlow.agents_list,
                "actual_agent": "hair_diagno"
            })
        finance_crew = self.diagnosticFlow.get_crew()
        result = await finance_crew.kickoff_async(inputs={'prompt': self.state.user_input, 'image': self.state.image})
        return result 

    @listen("finanzas_route")
    async def finanzas_handler(self):
        # Enviamos el estado por websocket  
        await ws_manager.send_to_client(self.state.client_id, {
                "mode": "finanzas",
                "agents": self.financialflow.agents_list,
                "actual_agent": "financial_evaluator"
            })
        
        print("Ejecutando flujo de finanzas")
        financial_crew = self.financialflow.get_crew()
        result = await financial_crew.kickoff_async(inputs={'prompt': self.state.user_input})
        return result

    @listen("chill_route")
    async def chill_handler(self):
        # Enviamos el estado por websocket
        await ws_manager.send_to_client(self.state.client_id, {
                "mode": "chill",
                "agents": self.chillflow.agents_list,
                "actual_agent": "agente_conversacional"
            })
        print("Ejecutando flujo chill")
        chill_crew = self.chillflow.get_crew()
        result = await chill_crew.kickoff_async(inputs={'message': self.state.user_input})
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