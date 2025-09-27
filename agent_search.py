import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_community.tools import DuckDuckGoSearchRun

from langchain_google_genai import chat_models

# Lista os modelos disponíveis

print("Modelos disponíveis:", chat_models)

# --- Configuração do Cérebro (LLM) ---

# IMPORTANTE: Cole sua API key aqui. 
# A forma mais segura é usar variáveis de ambiente, mas para um teste simples, pode ser direto.
os.environ["GOOGLE_API_KEY"] = "AIzaSyA8AgoaSY_o0kq3nyFnsUVHUqWpY5hmMTM" 

# Inicializa o modelo Gemini do Google. 
# A 'temperatura' controla a criatividade (0 = mais determinístico)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# --- Configuração das Ferramentas ---

# Instancia a ferramenta de busca da web do DuckDuckGo
search = DuckDuckGoSearchRun()

# Descrevemos as ferramentas em uma lista. O agente usará a descrição
# para decidir qual ferramenta usar.
tools = [
    Tool(
        name="Busca na Web",
        func=search.run,
        description="útil para pesquisar informações recentes na internet sobre qualquer tópico."
    )
]

# --- Criação e Execução do Agente ---

# 'initialize_agent' junta o cérebro (llm) com as ferramentas (tools).
# O AgentType.ZERO_SHOT_REACT_DESCRIPTION usa o ciclo ReAct que explicamos.
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True # 'verbose=True' nos mostra o "pensamento" do agente passo a passo
)

# A pergunta que queremos que o agente responda
pergunta = input("Digite sua pergunta para o agente: ")

# Executa o agente com a nossa pergunta
resultado = agent.invoke(pergunta)

# --- Apresentação do Resultado ---
print("\n\n--- RESPOSTA FINAL DO AGENTE ---")
print(resultado)