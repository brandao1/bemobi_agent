import os
import json
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

# --- 1. Funções de Interação com a Base de Dados (customer_profile.json) ---

DB_FILE = 'customer_profile.json'

def read_database():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_database(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- 2. Ferramentas do Agente Concierge ---

def get_user_context(user_id: str) -> str:
    """Verifica o contexto do usuário, como cartões expirando. Use sempre no início da conversa."""
    print(f"🤖 Concierge: Verificando contexto para {user_id}")
    db = read_database()
    user = db.get(user_id)
    if not user:
        return "Usuário não encontrado."

    for pm in user["payment_methods"]:
        if pm["type"] == "credit_card":
            expiry_year, expiry_month = map(int, pm["expiry_date"].split('-'))
            next_month = datetime.now() + timedelta(days=30)
            if expiry_year == next_month.year and expiry_month == next_month.month:
                return json.dumps({
                    "proactive_alert": "expiring_card",
                    "details": f"O cartão {pm['brand']} com final {pm['last4']} expira no próximo mês."
                })
    return "Nenhum alerta proativo imediato."

def get_personal_info(user_id: str) -> str:
    """Busca as informações pessoais de um usuário."""
    print(f"🤖 Concierge: Buscando informações de {user_id}")
    db = read_database()
    return json.dumps(db.get(user_id, {}).get("personal_info", {}))

def update_personal_info(user_id: str, new_email: str = None, new_address: str = None) -> str:
    """Atualiza o e-mail ou endereço de um usuário."""
    print(f"🤖 Concierge: Atualizando informações de {user_id}")
    db = read_database()
    user = db.get(user_id)
    if not user:
        return "Usuário não encontrado."
    if new_email:
        user["personal_info"]["email"] = new_email
    if new_address:
        user["personal_info"]["address"] = new_address
    write_database(db)
    return f"Informações de {user['personal_info']['name']} atualizadas com sucesso."

def get_payment_methods(user_id: str) -> str:
    """Consulta os métodos de pagamento de um usuário."""
    print(f"🤖 Concierge: Consultando métodos de pagamento de {user_id}")
    db = read_database()
    return json.dumps(db.get(user_id, {}).get("payment_methods", []))

def get_billing_history(user_id: str) -> str:
    """Consulta o histórico de faturamento de um usuário."""
    print(f"🤖 Concierge: Consultando histórico de faturamento de {user_id}")
    db = read_database()
    return json.dumps(db.get(user_id, {}).get("billing_history", []))

# --- 3. Classe e Factory do Agente ---

class ConciergeAgent:
    def __init__(self, user_id):
        self.user_id = user_id
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.2)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.agent = self._create_agent()

    def _create_agent(self):
        # As funções precisam ser recriadas como lambdas para capturar o self.user_id
        tools = [
            Tool.from_function(lambda: get_user_context(self.user_id), name="Verificar Contexto do Usuário", description="Sempre use esta ferramenta primeiro para verificar se há alguma ação proativa a ser tomada para o usuário."),
            Tool.from_function(lambda: get_personal_info(self.user_id), name="Consultar Informações Pessoais", description="Útil para buscar o nome, e-mail ou endereço do usuário."),
            Tool.from_function(update_personal_info, name="Atualizar Informações Pessoais", description="Útil para alterar o e-mail ou endereço do usuário. Requer o user_id e os novos dados."),
            Tool.from_function(lambda: get_payment_methods(self.user_id), name="Consultar Métodos de Pagamento", description="Útil para listar os métodos de pagamento do usuário."),
            Tool.from_function(lambda: get_billing_history(self.user_id), name="Consultar Histórico de Faturamento", description="Útil para ver as faturas passadas do usuário."),
        ]

        agent_system_prompt = f"""
        Você é o Concierge, um assistente de IA da Bemobi para o usuário {self.user_id}.
        Sua personalidade é: prestativo, amigável e, acima de tudo, proativo.
        Seu objetivo é transformar o autoatendimento em uma experiência fácil e guiada.

        **Instruções Críticas:**
        1.  **Seja Proativo:** Ao iniciar, SEMPRE use a ferramenta "Verificar Contexto do Usuário" para ver se há algum problema iminente (como um cartão expirando). Se houver, inicie a conversa abordando esse ponto.
        2.  **Use o ID do Usuário:** Todas as ferramentas já estão configuradas para usar o ID '{self.user_id}'. Você não precisa passá-lo novamente.
        3.  **Fale com Clareza:** Use linguagem natural e evite jargões.
        """

        return initialize_agent(
            tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            agent_kwargs={
                "system_message": agent_system_prompt
            }
        )

    def run(self, user_input):
        return self.agent.invoke({"input": user_input})

# Factory para criar uma instância do agente para um usuário específico
def create_concierge_agent(user_id):
    return ConciergeAgent(user_id)