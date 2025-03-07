from crewai import Agent, Crew, Task, LLM, Process
from dotenv import load_dotenv
from tools.tool import CryptoDataTool, ActionsDataTool
import yaml

files = {
    'agents': 'app/flow/crews/config',
    'tasks': 'app/flow/crews/config'
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r', encoding='utf-8') as file:
        configs[config_type] = yaml.safe_load(file)

llm = LLM(model="gpt-4o-mini")

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']



financial_evaluator = Agent(
  config=agents_config['financial_evaluator'],
  llm=llm
)

financial_simulator = Agent(
  config=agents_config['financial_simulator'],
  tools=[CryptoDataTool(), ActionsDataTool()],
  llm=llm
)

financial_optimizer = Agent(
  config=agents_config['financial_optimizer'],
  llm=llm
)

analize_cashflow = Task(
  config=tasks_config['analize_cashflow'],
  agent=financial_evaluator,
)

generate_investment_scenarios = Task(
  config=tasks_config['generate_investment_scenarios'],
  agent=financial_simulator,
)

optimizated_investment_scenarios = Task(
  config=tasks_config['optimizated_investment_scenarios'],
  agent=financial_optimizer,
)

crew = Crew(
  agents=[
    financial_evaluator,
    financial_simulator,
    financial_optimizer
  ],
  tasks=[
    analize_cashflow,
    generate_investment_scenarios,
    optimizated_investment_scenarios
  ],
  process=Process.sequential,  
  verbose=True
)

if __name__ == "__main__":
    crew.kickoff(inputs={"prompt": "Cobro 600 euros al mes, y quiero invertir 1000 euros en 2 años, que me recomiendas?"})