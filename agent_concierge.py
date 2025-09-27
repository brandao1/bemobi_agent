import os
import json
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from faker import Faker

# --- 1. Simulação do Ecossistema Bemobi ---
# Em um ambiente real, estas informações viriam de bancos de dados e APIs.

fake = Faker('pt_BR')

mock_database = {
    "user_maria_123": {
        "personal_info": {
            "name": "Maria Silva",
            "email": "maria.silva@example.com",
            "address": "Rua das Flores, 123, São Paulo, SP"
        },
        "payment_methods": [
            {
                "id": "cc_visa_1234",
                "type": "credit_card",
                "brand": "Visa",
                "last4": "1234",
                "expiry_date": (datetime.now() + timedelta(days=25)).strftime('%Y-%m') # Expira no próximo mês
            },
            {
                "id": "cc_master_5678",
                "type": "credit_card",
                "brand": "Mastercard",
                "last4": "5678",
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime('%Y-%m')
            }
        ],
        "subscriptions": [
            {
                "service_name": "Plano Bemobi Premium",
                "status": "active",
                "price_brl": 79.90,
                "next_billing_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
            }
        ],
        "billing_history": [
            {"date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'), "description": "Mensalidade Plano Premium", "amount_brl": 79.90, "status": "paid"},
            {"date": (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'), "description": "Mensalidade Plano Premium", "amount_brl": 79.90, "status": "paid"}
        ]
    }
}

# --- 2. Ferramentas do Agente Concierge ---
# Funções que o agente pode executar para interagir com os dados do usuário.

def get_user_context(user_id: str) -> str:
    """
    Verifica o contexto do usuário, como cartões expirando ou faturas em aberto.
    Esta é a ferramenta que permite a proatividade do agente.
    """
    print(f"🤖 Verificando contexto para o usuário: {user_id}")
    user = mock_database.get(user_id)
    if not user:
        return "Usuário não encontrado."

    # Verifica cartões expirando
    for pm in user["payment_methods"]:
        if pm["type"] == "credit_card":
            expiry_year, expiry_month = map(int, pm["expiry_date"].split('-'))
            next_month = datetime.now() + timedelta(days=30)
            if expiry_year == next_month.year and expiry_month == next_month.month:
                return json.dumps({
                    "proactive_alert": "expiring_card",
                    "details": f"O cartão {pm['brand']} com final {pm['last4']} expira em breve."
                })
    return "Nenhum alerta proativo imediato."

def get_personal_info(user_id: str) -> str:
    """Busca as informações pessoais de um usuário."""
    print(f"🤖 Buscando informações de {user_id}")
    return json.dumps(mock_database.get(user_id, {}).get("personal_info", {}))

def update_personal_info(user_id: str, new_email: str = None, new_address: str = None) -> str:
    """Atualiza o e-mail ou endereço de um usuário."""
    print(f"🤖 Atualizando informações de {user_id}")
    user = mock_database.get(user_id)
    if not user:
        return "Usuário não encontrado."
    if new_email:
        user["personal_info"]["email"] = new_email
    if new_address:
        user["personal_info"]["address"] = new_address
    return f"Informações de {user['personal_info']['name']} atualizadas com sucesso."

def get_billing_history(user_id: str) -> str:
    """Consulta o histórico de faturamento de um usuário."""
    print(f"🤖 Consultando histórico de faturamento de {user_id}")
    return json.dumps(mock_database.get(user_id, {}).get("billing_history", []))

def manage_payment_methods(user_id: str, action: str, card_details: dict = None) -> str:
    """Adiciona ou remove um método de pagamento."""
    print(f"🤖 Gerenciando pagamentos para {user_id}")
    user = mock_database.get(user_id)
    if not user:
        return "Usuário não encontrado."
    if action == "add":
        new_card = {
            "id": f"cc_{fake.credit_card_provider().lower()}_{card_details['last4']}",
            "type": "credit_card",
            "brand": card_details['brand'],
            "last4": card_details['last4'],
            "expiry_date": card_details['expiry_date']
        }
        user["payment_methods"].append(new_card)
        return f"Cartão {new_card['brand']} final {new_card['last4']} adicionado."
    elif action == "remove":
        user["payment_methods"] = [pm for pm in user["payment_methods"] if pm["last4"] != card_details["last4"]]
        return f"Cartão com final {card_details['last4']} removido."
    return "Ação inválida."


# --- 3. Configuração do Agente ---

# Carrega a API Key do ambiente
#api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = "AIzaSyA8AgoaSY_o0kq3nyFnsUVHUqWpY5hmMTM"
#if not api_key:
#    raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")

# Inicializa o modelo de linguagem
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# Define a lista de ferramentas que o agente pode usar
concierge_tools = [
    Tool.from_function(
        func=get_user_context,
        name="Verificar Contexto do Usuário",
        description="Sempre use esta ferramenta primeiro para verificar se há alguma ação proativa a ser tomada para o usuário."
    ),
    Tool.from_function(func=get_personal_info, name="Consultar Informações Pessoais", description="Útil para buscar o nome, e-mail ou endereço do usuário."),
    Tool.from_function(func=update_personal_info, name="Atualizar Informações Pessoais", description="Útil para alterar o e-mail ou endereço do usuário."),
    Tool.from_function(func=get_billing_history, name="Consultar Histórico de Faturamento", description="Útil para ver as faturas passadas do usuário."),
    Tool.from_function(func=manage_payment_methods, name="Gerenciar Métodos de Pagamento", description="Útil para adicionar ou remover um método de pagamento. A ação pode ser 'add' ou 'remove'. Para 'add', forneça 'card_details' com 'brand', 'last4' e 'expiry_date'. Para 'remove', forneça 'card_details' com 'last4'."),
]

# Define a "personalidade" e as instruções do agente
# Este é o prompt que guia o comportamento do agente.
agent_system_prompt = """
Você é o Concierge, um assistente de IA da Bemobi, especialista em gerenciamento de contas.
Sua personalidade é: prestativo, amigável e, acima de tudo, proativo.

Seu objetivo principal é transformar o autoatendimento em uma experiência fácil e guiada.

**Instruções Críticas:**
1.  **Seja Proativo:** Ao iniciar uma conversa, SEMPRE use a ferramenta "Verificar Contexto do Usuário" primeiro para ver se há algum problema iminente (como um cartão expirando). Se houver, inicie a conversa abordando esse ponto diretamente.
2.  **Use Linguagem Natural:** Fale com o usuário de forma clara e conversacional, como um humano faria. Evite jargões técnicos.
3.  **Guie o Usuário:** Não espere apenas por comandos. Se um usuário fizer uma pergunta vaga como "meu pagamento", use as ferramentas para descobrir o problema e ofereça uma solução.
4.  **Confirme Ações:** Antes de executar uma ação que altere dados (como adicionar um cartão), confirme com o usuário.
5.  **ID do Usuário:** Todas as funções exigem um `user_id`. Para esta simulação, use sempre o ID `user_maria_123`.
"""

# Configura a memória para que o agente se lembre do histórico da conversa
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Inicializa o agente
concierge_agent = initialize_agent(
    concierge_tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    agent_kwargs={
        "system_message": agent_system_prompt
    }
)


# --- 4. Execução e Interação ---

print("--- Agente Concierge da Bemobi ---")
print("Iniciando simulação para a usuária Maria Silva (user_maria_123)...")
print("Digite 'sair' para terminar.")

# O agente inicia a conversa de forma proativa
initial_prompt = "Olá, sou o Concierge da Bemobi. Como posso ajudar hoje?"
print(f"\nConcierge: {initial_prompt}")

# O agente "pensa" sobre a saudação inicial e verifica o contexto
# A instrução no prompt o força a usar a ferramenta de contexto primeiro.
response = concierge_agent.invoke({"input": "Um cliente iniciou a conversa."})
print(f"Concierge: {response['output']}\n")


while True:
    user_input = input("Você: ")
    if user_input.lower() == 'sair':
        break

    response = concierge_agent.invoke({"input": user_input})
    print(f"Concierge: {response['output']}\n")
