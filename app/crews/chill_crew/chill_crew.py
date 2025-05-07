# # Warning control
# import warnings
# warnings.filterwarnings('ignore')

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

import os
import yaml
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from app.utils.list_agents import list_agents
#import websocket manager
from app.utils.websockets.manager import ws_manager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@CrewBase
class Chillcrew():
    agents_config=os.path.join(BASE_DIR, 'config/chill_config/agents.yaml')
    tasks_config=os.path.join(BASE_DIR, 'config/chill_config/tasks.yaml')

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.agents_list = list_agents(self.agents_config)
        self._crew_instance = None
    
    def get_crew(self):
        if self._crew_instance is None:
            self._crew_instance = self.crew()   # llama al método decorado
        return self._crew_instance
    
    @agent
    def agente_conversacional(self) -> Agent:
        return Agent(
            config=self.agents_config['agente_conversacional']
        )
    
    @task
    def mantener_conversacion(self) -> Task:
        return Task(
            config=self.tasks_config['mantener_conversacion'],
            agent=self.agente_conversacional()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True
        )
