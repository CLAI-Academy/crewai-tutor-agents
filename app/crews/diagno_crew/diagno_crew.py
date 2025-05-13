from dotenv import load_dotenv
load_dotenv()

import os
import yaml
import json
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from app.tools.diagnostic_crew.tools import analyze_image
from app.utils.list_agents import list_agents
import asyncio
#import websocket manager
from app.utils.websockets.manager import ws_manager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@CrewBase
class DiagnosticCrew():
    agents_config = os.path.join(BASE_DIR, 'config/hair_diagno_config/agents.yaml')
    tasks_config = os.path.join(BASE_DIR, 'config/hair_diagno_config/tasks.yaml')
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.agents_list = list_agents(self.agents_config)
        self._crew_instance = None
        self.diagno_results = None

    def get_crew(self):
        if self._crew_instance is None:
            self._crew_instance = self.crew()   # llama al método decorado
        return self._crew_instance

    def parse_json_output(self, output: str) -> dict:
        """
        Parse the JSON output from the agents' responses.
        Extracts JSON from the string if it contains other text.
        """
        try:
            # First try to parse the entire string as JSON
            return json.loads(output)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from within the string
            try:
                # Look for JSON between triple backticks
                json_pattern = r'```json\s*([\s\S]*?)\s*```'
                import re
                match = re.search(json_pattern, output)
                
                if match:
                    json_str = match.group(1)
                    return json.loads(json_str)
                
                # If no JSON found between backticks, look for { } brackets
                json_pattern = r'(\{[\s\S]*\})'
                match = re.search(json_pattern, output)
                
                if match:
                    json_str = match.group(1)
                    return json.loads(json_str)
                
                raise ValueError("No valid JSON found in output")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(f"Original output: {output}")
                # Return a simple error object if parsing fails
                return {"error": "Failed to parse JSON output", "raw_output": output}
    
    def create_callback(self, agent_name: str):
        payload = {
            "mode":   "peluqueria",
            "agents": self.agents_list,
            "actual_agent": agent_name
        }

        # función *síncrona* (CrewAI la invoca dentro de un hilo worker)
        def _callback(output):
            # Parse the JSON output and store it for the next agent
            if agent_name == "hair_diagno":
                self.diagno_results = self.parse_json_output(output)
                # Add the parsed JSON to the payload
                payload["diagno_results"] = self.diagno_results
            
            # en ese hilo NO hay event-loop → podemos usar asyncio.run()
            asyncio.run(ws_manager.send_to_client(self.client_id, payload))

        return _callback
    
    # Creating LLM instances with specific configurations
    diagnostic_llm = LLM(
        model="gpt-4.1-mini",
        temperature=0.7,
        max_tokens=1000
    )
    
    suggestion_llm = LLM(
        model="gpt-4.1-mini",
        temperature=0.8,
        max_tokens=1500
    )

    @agent
    def hair_diagno(self) -> Agent:
        return Agent(
            config=self.agents_config['hair_diagno'],
            llm=self.diagnostic_llm,
            tools=[analyze_image],
            verbose=True
        )
    
    @agent
    def color_suggestion(self) -> Agent:
        return Agent(
            config=self.agents_config['color_suggestion'],
            llm=self.suggestion_llm,
            tools=[analyze_image],
            verbose=True
        )
    
    @task
    def hair_diagno_generation(self) -> Task:
        return Task(
            config=self.tasks_config['hair_diagno_generation'],
            agent=self.hair_diagno(),
            callback=self.create_callback("hair_diagno")
        )
    
    @task
    def color_suggestion_generation(self) -> Task:
        return Task(
            config=self.tasks_config['color_suggestion_generation'],
            agent=self.color_suggestion(),
            callback=self.create_callback("color_suggestion")
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential
        )