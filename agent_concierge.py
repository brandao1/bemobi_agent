import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_community.tools import DuckDuckGoSearchRun
from faker import Faker

from langchain_google_genai import chat_models

# Lista os modelos disponíveis

print("Modelos disponíveis:", chat_models)

# --- Configuração do Cérebro (LLM) ---

# IMPORTANTE: Cole sua API key aqui. 
# A forma mais segura é usar variáveis de ambiente, mas para um teste simples, pode ser direto.
os.environ["GOOGLE_API_KEY"] = "" 

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

# Inicializa o gerador de dados fake
fake = Faker()

# --- Ferramentas do Concierge ---

def atualizar_informacoes_pessoais(nome, endereco, email):
    return f"Informações atualizadas: Nome: {nome}, Endereço: {endereco}, Email: {email}"

def gerenciar_metodos_pagamento(acao, metodo):
    return f"Método de pagamento {acao}: {metodo}"

def consultar_historico_faturamento():
    return "Histórico de faturamento: [Fatura 1, Fatura 2, Fatura 3]"

def configurar_pagamento_recorrente(acao, detalhes):
    return f"Pagamento recorrente {acao}: {detalhes}"

def iniciar_conversa_proativa(nome, cartao):
    return f"Olá, {nome}. Notei que seu cartão {cartao} expira em breve. Gostaria de atualizá-lo?"

# Ferramentas descritas para o agente
concierge_tools = [
    Tool(
        name="Atualizar Informações Pessoais",
        func=lambda: atualizar_informacoes_pessoais(
            fake.name(), fake.address(), fake.email()
        ),
        description="Atualiza informações pessoais, como endereço ou e-mail."
    ),
    Tool(
        name="Gerenciar Métodos de Pagamento",
        func=lambda: gerenciar_metodos_pagamento("adicionado", "Cartão de Crédito"),
        description="Adiciona, remove ou altera métodos de pagamento."
    ),
    Tool(
        name="Consultar Histórico de Faturamento",
        func=consultar_historico_faturamento,
        description="Consulta o histórico de faturamento e solicita envio de faturas."
    ),
    Tool(
        name="Configurar Pagamento Recorrente",
        func=lambda: configurar_pagamento_recorrente("configurado", "Cartão Visa"),
        description="Configura ou modifica agendamentos de pagamentos recorrentes."
    ),
    Tool(
        name="Iniciar Conversa Proativa",
        func=lambda: iniciar_conversa_proativa(fake.first_name(), "Visa com final 1234"),
        description="Inicia uma conversa proativa com base em dados contextuais."
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

# --- Criação do Agente Concierge ---
concierge_agent = initialize_agent(
    concierge_tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# --- Testando o Agente ---
print("\n--- TESTANDO O AGENTE CONCIERGE ---")
for tool in concierge_tools:
    print(f"\nExecutando ferramenta: {tool.name}")
    print(tool.func())