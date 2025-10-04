import os
import json
import ast
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

from .agent_guardian import GuardianAgent
from .agent_dynamo import DynamoAgent

USER_ID = "user_maria_123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '..', 'data', 'customer_profile.json')

def read_database():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_database(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def get_user_context() -> str:
    """Verifica o contexto do usuário, como cartões expirando. Use sempre no início da conversa."""
    print(f"🤖 Grace: Verificando contexto para {USER_ID}")
    db = read_database()
    user = db.get(USER_ID)
    if not user:
        return "Usuário não encontrado."
    if user.get("proactive_alert"):
        alert_details = user["proactive_alert"]["details"]
        del user["proactive_alert"]
        write_database(db)
        return json.dumps({"proactive_alert": "blocked_transaction", "details": alert_details})
    for pm in user["payment_methods"]:
        if pm["type"] == "credit_card" and pm["expiry_date"]:
            expiry_year, expiry_month = map(int, pm["expiry_date"].split('-'))
            first_day_of_expiry_month = datetime(expiry_year, expiry_month, 1)
            effective_expiry_date = (first_day_of_expiry_month + timedelta(days=32)).replace(day=1)
            if datetime.now() >= effective_expiry_date:
                return json.dumps({
                    "proactive_alert": "expiring_card",
                    "details": f"notei que o seu cartão {pm['brand']} com final {pm['last4']} expirou em {expiry_month}/{expiry_year}. Para evitar problemas em sua assinatura, o ideal é atualizá-lo."
                })
    return "Nenhum alerta proativo imediato."

def get_personal_info() -> str:
    """Busca as informações pessoais do usuário."""
    print(f"🤖 Grace: Buscando informações de {USER_ID}")
    db = read_database()
    result = db.get(USER_ID, {}).get("personal_info", {})
    return json.dumps({"agent_source": "Agente Concierge", "result": result})

def update_personal_info(new_email: str = None, new_address: str = None) -> str:
    """Atualiza o e-mail ou endereço do usuário."""
    print(f"🤖 Grace: Atualizando informações de {USER_ID}")
    db = read_database()
    user = db.get(USER_ID)
    if not user:
        return json.dumps({"agent_source": "Agente Concierge", "result": "Usuário não encontrado."})
    if new_email:
        user["personal_info"]["email"] = new_email
    if new_address:
        user["personal_info"]["address"] = new_address
    write_database(db)
    return json.dumps({"agent_source": "Agente Concierge", "result": f"Informações atualizadas com sucesso!"})

def get_payment_methods() -> str:
    """Consulta os métodos de pagamento do usuário."""
    print(f"🤖 Grace: Consultando métodos de pagamento de {USER_ID}")
    db = read_database()
    result = db.get(USER_ID, {}).get("payment_methods", [])
    return json.dumps({"agent_source": "Agente Concierge", "result": result})

def get_billing_history() -> str:
    """Consulta o histórico de faturamento do usuário."""
    print(f"🤖 Grace: Consultando histórico de faturamento de {USER_ID}")
    db = read_database()
    result = db.get(USER_ID, {}).get("billing_history", [])
    return json.dumps({"agent_source": "Agente Concierge", "result": result})

def get_subscriptions() -> str:
    """Consulta as assinaturas e serviços ativos do usuário."""
    print(f"🤖 Grace: Consultando assinaturas de {USER_ID}")
    db = read_database()
    result = db.get(USER_ID, {}).get("subscriptions", [])
    return json.dumps({"agent_source": "Agente Concierge", "result": result})

def analyze_suspicious_transaction(transaction_id: str) -> str:
    """Analisa uma transação específica que o usuário considera suspeita."""
    print(f"🤖 Grace: Acionando Guardian para análise da transação {transaction_id}")
    db = read_database()
    user_history = db.get(USER_ID, {}).get("billing_history", [])
    transaction_to_analyze = next((t for t in user_history if t["transaction_id"] == transaction_id), None)
    if not transaction_to_analyze:
        return json.dumps({"agent_source": "Agente Concierge", "result": f"Transação com ID {transaction_id} não encontrada."})
    guardian_agent = GuardianAgent()
    analysis_result = guardian_agent.analyze_transaction(USER_ID, transaction_to_analyze)
    return json.dumps({"agent_source": "Agente Guardian", "result": analysis_result})

def get_dynamic_payment_options(transaction_id: str) -> str:
    """Verifica e oferece opções de pagamento dinâmicas para uma fatura."""
    print(f"🤖 Grace: Acionando Dynamo para obter opções para a transação {transaction_id}.")
    db = read_database()
    user = db.get(USER_ID)
    if not user: return json.dumps({"agent_source": "Agente Concierge", "result": "Usuário não encontrado."})
    transaction = next((t for t in user.get("billing_history", []) if t["transaction_id"] == transaction_id), None)
    if not transaction: return json.dumps({"agent_source": "Agente Concierge", "result": f"Transação {transaction_id} não encontrada."})
    transaction_details_for_dynamo = {"amount_brl": transaction["amount_brl"], "location": transaction["location"], "time_on_page_seconds": 20}
    dynamo_agent = DynamoAgent()
    offer = dynamo_agent.generate_dynamic_offer(USER_ID, transaction_details_for_dynamo)
    return json.dumps({"agent_source": "Agente Dynamo", "result": offer})

def delete_payment_method(payment_method_id: str) -> str:
    """Remove um método de pagamento do perfil do usuário."""
    print(f"🤖 Grace: Removendo o método de pagamento {payment_method_id}.")
    db = read_database()
    user = db.get(USER_ID)
    if not user:
        return json.dumps({"agent_source": "Agente Concierge", "result": "Usuário não encontrado."})
    initial_len = len(user["payment_methods"])
    user["payment_methods"] = [pm for pm in user["payment_methods"] if pm.get("id") != payment_method_id]
    if len(user["payment_methods"]) < initial_len:
        if user.get("preferred_payment_method_id") == payment_method_id:
            user["preferred_payment_method_id"] = None
        write_database(db)
        return json.dumps({"agent_source": "Agente Concierge", "result": f"Método de pagamento {payment_method_id} removido com sucesso."})
    else:
        return json.dumps({"agent_source": "Agente Concierge", "result": f"Método de pagamento com ID {payment_method_id} não encontrado."})

class ConciergeAgent:
    def __init__(self):
        self.user_id = USER_ID
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro-latest", temperature=0.1, convert_system_message_to_human=True)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.agent = self._create_agent()

    def _create_agent(self):
        tools = [
            Tool.from_function(func=lambda _: get_user_context(), name="Verificar Contexto do Usuário", description="Sempre use esta ferramenta primeiro para verificar se há alguma ação proativa a ser tomada, como um alerta de segurança ou um cartão expirado. Não requer argumentos."),
            Tool.from_function(func=lambda _: get_personal_info(), name="Consultar Informações Pessoais", description="Útil para buscar o nome, e-mail ou endereço do usuário. Não requer argumentos."),
            Tool(name="Atualizar Informações Pessoais", func=lambda tool_input: update_personal_info(**ast.literal_eval(tool_input)), description="Útil para alterar o e-mail ou endereço do usuário. Requer um dicionário com os novos dados (new_email ou new_address)."),
            Tool.from_function(func=lambda _: get_payment_methods(), name="Consultar Métodos de Pagamento", description="Útil para listar os métodos de pagamento do usuário. Não requer argumentos."),
            Tool.from_function(func=lambda _: get_billing_history(), name="Consultar Histórico de Faturamento", description="Útil para ver as faturas passadas do usuário. Não requer argumentos."),
            
            Tool.from_function(
                func=lambda _: get_subscriptions(), 
                name="Consultar Assinaturas Ativas", 
                description="Use esta ferramenta quando o usuário perguntar sobre suas assinaturas, planos ou serviços ativos."
            ),

            Tool(
                name="Analisar Transação Suspeita", 
                func=lambda tool_input: analyze_suspicious_transaction(**ast.literal_eval(tool_input)),
                description="Analisa uma transação suspeita usando seu ID. É a única forma de obter uma análise de risco. Se o usuário mencionar uma cobrança mas não fornecer o ID exato (ex: 'a cobrança de São Paulo'), você deve primeiro usar a ferramenta 'Consultar Histórico de Faturamento' para listar as transações e então pedir para o usuário confirmar o ID da transação que ele quer analisar."
            ),
            Tool(name="Oferecer Opções de Pagamento Dinâmico", func=lambda tool_input: get_dynamic_payment_options(**ast.literal_eval(tool_input)), description="Use para verificar e apresentar opções de pagamento, como parcelamentos, para uma fatura. Requer um dicionário com o ID da transação (transaction_id)."),
            Tool(
                name="Remover Método de Pagamento",
                func=lambda tool_input: delete_payment_method(**ast.literal_eval(tool_input)),
                description="Útil para apagar ou remover um método de pagamento existente, como um cartão de crédito. Requer o ID exato do método de pagamento (`payment_method_id`). Se o usuário não fornecer o ID, você deve primeiro usar a ferramenta 'Consultar Métodos de Pagamento' para listar os cartões e seus IDs, e então perguntar qual ele deseja remover."
            ),
        ]

        agent_system_prompt = f"""
        Você é a Grace, a assistente pessoal de IA da Bemobi para a usuária Maria Silva ({self.user_id}).
        Sua personalidade é prestativa, empática e, acima de tudo, proativa. Você se comunica de forma clara e amigável, como em uma conversa de WhatsApp.
        Seu objetivo é transformar o autoatendimento em uma experiência fácil e guiada.

        **Instruções Críticas de Formatação:**
        - Quando você precisar listar informações como faturas, assinaturas ou métodos de pagamento, SEMPRE use formatação **Markdown** para maior clareza.
        - Para listas de itens (como faturas), use **tabelas Markdown** sempre que possível. Use `R$` para valores monetários.
        - Use títulos com **negrito** para separar as seções da sua resposta.
        - Exemplo de uma boa tabela de faturamento:
        | ID da Fatura | Data       | Valor     |
        |--------------|------------|-----------|
        | txn_abc123   | 10/09/2025 | R$ 149,90 |
        | txn_def456   | 10/08/2025 | R$ 149,90 |

        **Instruções Críticas de Comportamento:**
        1.  **Seja Proativa:** No início de CADA conversa, SEMPRE use a ferramenta "Verificar Contexto do Usuário". Se houver um alerta, inicie a conversa abordando esse ponto de forma natural. Exemplo: "Olá Maria! Tudo bem? Antes de mais nada, notei que...".
        2.  **Atribuição de Agente:** Se a ferramenta retornar "agent_source", comece sua resposta com "Grace(Nome do Agente): ". Ex: "Grace(Agente Guardian): Maria, analisei a transação e...". Senão, responda normalmente como "Grace:".
        3.  **Linguagem Natural:** Fale com a Maria de forma pessoal e direta. Evite jargões.
        """

        return initialize_agent(
            tools, self.llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=False,
            memory=self.memory, handle_parsing_errors=True, agent_kwargs={"system_message": agent_system_prompt}
        )

    def run(self, user_input):
        return self.agent.invoke({"input": user_input}).get("output", "Desculpe, Maria. Ocorreu um erro e não consegui processar sua solicitação.")

def create_concierge_agent():
    return ConciergeAgent()