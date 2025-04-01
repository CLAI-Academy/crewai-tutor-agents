from dotenv import load_dotenv
load_dotenv()

import os
import yaml
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from app.tools.diagnostic_crew.tools import analyze_image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@CrewBase
class DiagnosticCrew():
    agents_config = os.path.join(BASE_DIR, 'config/hair_diagno_config/agents.yaml')
    tasks_config = os.path.join(BASE_DIR, 'config/hair_diagno_config/tasks.yaml')
    
    # Creating LLM instances with specific configurations
    diagnostic_llm = LLM(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=1000
    )
    
    suggestion_llm = LLM(
        model="gpt-4o-mini",
        temperature=0.8,
        max_tokens=1500
    )

    @agent
    def hair_diagno(self) -> Agent:
        return Agent(
            config=self.agents_config['hair_diagno'],
            llm=self.diagnostic_llm,
            tools=[analyze_image],
            multimodal=True,
            verbose=True
        )
    
    @agent
    def color_suggestion(self) -> Agent:
        return Agent(
            config=self.agents_config['color_suggestion'],
            llm=self.suggestion_llm,
            multimodal=True,
            verbose=True
        )
    
    @task
    def hair_diagno_generation(self) -> Task:
        return Task(
            config=self.tasks_config['hair_diagno_generation'],
            agent=self.hair_diagno()
        )
    
    @task
    def color_suggestion_generation(self) -> Task:
        return Task(
            config=self.tasks_config['color_suggestion_generation'],
            agent=self.color_suggestion()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential
        )