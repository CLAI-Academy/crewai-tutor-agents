from typing import Any
from crewai.flow.flow import Flow, listen, start
from crewai.flow.persistence.base import FlowPersistence
from app.crews.chill_crew.chill_crew import Chillcrew





class ChillFlow(Flow):    
    chill_crew=Chillcrew()

    @start()
    def empezar_conversacion(self):
        result=self.chill_crew.crew().kickoff(inputs={'message': self.state['user_input']})
        return result
        

if __name__ == "__main__":
    # Crea una instancia del flow
    flow = ChillFlow()
    # Establece el valor de entrada en el estado
    flow.state['user_input'] = "hola, cual es tu color favorito?"
    # Inicia el flujo
    flow.kickoff()
