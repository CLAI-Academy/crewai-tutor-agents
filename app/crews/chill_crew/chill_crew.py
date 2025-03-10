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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@CrewBase
class Chillcrew():
    agents_config=os.path.join(BASE_DIR, 'config/chill_config/agents.yaml')
    tasks_config=os.path.join(BASE_DIR, 'config/chill_config/tasks.yaml')

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
