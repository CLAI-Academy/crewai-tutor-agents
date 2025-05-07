from crewai import Agent, Crew, Task, LLM, Process
from app.tools.financial_crew.tool import CryptoDataTool, ActionsDataTool, TickerFinderTool
from crewai.project import CrewBase, agent, crew, task
import yaml
import os
from app.utils.list_agents import list_agents
import asyncio
#import websocket manager
from app.utils.websockets.manager import ws_manager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@CrewBase
class FinanceCrew():
    agents_config = os.path.join(BASE_DIR, 'config/finances_config/agents.yaml')
    tasks_config = os.path.join(BASE_DIR, 'config/finances_config/tasks.yaml')

    llm = LLM(model="gpt-4o-mini")

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.agents_list = list_agents(self.agents_config)
        self._crew_instance = None  # <— cache seguro

        
    def get_crew(self):
        if self._crew_instance is None:
            self._crew_instance = self.crew()   # llama al método decorado
        return self._crew_instance

        
    def create_callback(self, agent_name: str):
        payload = {
            "mode":   "finanzas",
            "agents": self.agents_list,
            "actual_agent": agent_name
        }

        # función *síncrona* (CrewAI la invoca dentro de un hilo worker)
        def _callback(_):
            # en ese hilo NO hay event-loop → podemos usar asyncio.run()
            asyncio.run(ws_manager.send_to_client(self.client_id, payload))

        return _callback

    @agent
    def financial_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_evaluator'],
            llm=self.llm
        )

    @agent
    def ticker_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['ticker_finder'],
            tools=[TickerFinderTool()],
            llm=self.llm
        )

    @agent
    def financial_simulator(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_simulator'],
            tools=[CryptoDataTool(), ActionsDataTool()],
            llm=self.llm
        )

    @agent
    def financial_optimizer(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_optimizer'],
            llm=self.llm
        )

    @task
    def analize_cashflow(self) -> Task:
        return Task(
            config=self.tasks_config['analize_cashflow'],
            agent=self.financial_evaluator(),
            callback=self.create_callback("ticker_finder")
        )

    @task
    def find_tickers(self) -> Task:
        return Task(
            config=self.tasks_config['find_tickers'],
            agent=self.ticker_finder(),
            callback=self.create_callback("financial_simulator")
        )

    @task
    def generate_investment_scenarios(self) -> Task:
        return Task(
            config=self.tasks_config['generate_investment_scenarios'],
            agent=self.financial_simulator(),
            callback=self.create_callback("financial_optimizer")
        )

    @task
    def optimizated_investment_scenarios(self) -> Task:
        return Task(
            config=self.tasks_config['optimizated_investment_scenarios'],
            agent=self.financial_optimizer(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.financial_evaluator(),
                self.ticker_finder(),
                self.financial_simulator(),
                self.financial_optimizer()
            ],
            tasks=[
                self.analize_cashflow(),
                self.find_tickers(),
                self.generate_investment_scenarios(),
                self.optimizated_investment_scenarios()
            ],
            process=Process.sequential,
            verbose=True
        )

if __name__ == '__main__':
    finance_crew_instance = FinanceCrew()
    crew_instance = finance_crew_instance.crew()
    inputs = {'prompt': "Cobro 5000 euros al mes, puedo invertir 1000 euros al mes, estoy harto de que mi dinero solo pierda valor, ¡quiero ganar dinero como sea, quiero riesgo!"}
    result = crew_instance.kickoff(inputs=inputs)
    print(result)
