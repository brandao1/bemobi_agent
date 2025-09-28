import os
import json
import ast
from datetime import datetime, timedelta
from functools import partial
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

from agent_guardian import GuardianAgent # Importa o Guardian para integração
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

    # 1. Verifica por alertas de segurança primeiro (maior prioridade)
    if user.get("proactive_alert") and user["proactive_alert"]["type"] == "blocked_transaction":
        alert_details = user["proactive_alert"]["details"]
        # Limpa o alerta após ser comunicado para não repetir na mesma sessão
        del user["proactive_alert"]
        write_database(db)
        return json.dumps({"proactive_alert": "blocked_transaction", "details": alert_details})

    # 2. Verifica por outros contextos, como cartões expirando
    for pm in user["payment_methods"]:
        if pm["type"] == "credit_card":
            # Um cartão é válido até o último dia do mês de expiração.
            # Ele expira no primeiro dia do mês seguinte.
            expiry_year, expiry_month = map(int, pm["expiry_date"].split('-'))
            # Calcula o primeiro dia do mês seguinte à expiração
            first_day_of_expiry_month = datetime(expiry_year, expiry_month, 1)
            effective_expiry_date = (first_day_of_expiry_month + timedelta(days=32)).replace(day=1)

            if datetime.now() >= effective_expiry_date:
                return json.dumps({
                    "proactive_alert": "expiring_card",
                    "details": f"O cartão {pm['brand']} com final {pm['last4']} (expirado em {expiry_month}/{expiry_year}) não é mais válido."
                })

    # 3. Verifica por faturas de Boleto/PIX prestes a vencer
    preferred_pm_id = user.get("preferred_payment_method_id")
    preferred_pm = next((pm for pm in user["payment_methods"] if pm["id"] == preferred_pm_id), None)

    if preferred_pm and preferred_pm["type"] in ["boleto", "pix"]:
        for sub in user["subscriptions"]:
            next_billing_date = datetime.strptime(sub["next_billing_date"], "%Y-%m-%d").date()
            days_until_due = (next_billing_date - datetime.now().date()).days

            if 0 <= days_until_due <= 2:
                payment_link = ""
                if preferred_pm["type"] == "boleto":
                    payment_link = f"https://pagamentos.bemobi.com/boleto/{user_id}/{sub['service_id']}"
                elif preferred_pm["type"] == "pix":
                    payment_link = f"00020126580014br.gov.bcb.pix0136...{sub['service_id']}" # PIX Copia e Cola simbólico

                return json.dumps({
                    "proactive_alert": "billing_due",
                    "details": f"Sua fatura do serviço '{sub['service_name']}' vence em {days_until_due} dia(s). Link para pagamento: {payment_link}"
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

def analyze_suspicious_transaction(user_id: str, transaction_id: str) -> str:
    """
    Analisa uma transação específica que o usuário considera suspeita.
    Use esta ferramenta quando o usuário reportar uma cobrança que não reconhece.
    Requer o ID da transação.
    """
    print(f"🤖 Concierge: Acionando Guardian para análise da transação {transaction_id}")
    db = read_database()
    user_history = db.get(user_id, {}).get("billing_history", [])
    transaction_to_analyze = next((t for t in user_history if t["transaction_id"] == transaction_id), None)

    if not transaction_to_analyze:
        return f"Transação com ID {transaction_id} não encontrada no histórico do usuário."

    guardian_agent = GuardianAgent()
    analysis_result = guardian_agent.analyze_transaction(user_id, transaction_to_analyze)

    return json.dumps(analysis_result)

def add_payment_method(user_id: str, card_number: str, expiry_date: str, cvv: str, brand: str) -> str:
    """
    Adiciona um novo cartão de crédito como método de pagamento após validá-lo.
    Requer o número do cartão (card_number), data de validade (expiry_date no formato AAAA-MM), cvv e a bandeira (brand).
    """
    print(f"🤖 Concierge: Recebida solicitação para adicionar novo cartão para {user_id}.")
    guardian_agent = GuardianAgent()

    card_details = {"number": card_number, "expiry_date": expiry_date, "cvv": cvv}
    validation_result = guardian_agent.validate_new_card(card_details)

    if not validation_result["is_valid"]:
        return f"Não foi possível adicionar o cartão. Motivos: {'; '.join(validation_result['reasons'])}"

    db = read_database()
    user = db.get(user_id)
    if not user:
        return "Usuário não encontrado."

    new_card = {
        "id": f"cc_{brand.lower()}_{card_number[-4:]}",
        "type": "credit_card",
        "brand": brand,
        "last4": card_number[-4:],
        "expiry_date": expiry_date,
        "added_date": datetime.now().isoformat()
    }
    user["payment_methods"].append(new_card)
    write_database(db)
    return f"Cartão {brand} com final {card_number[-4:]} adicionado com sucesso!"

def delete_payment_method(user_id: str, payment_method_id: str) -> str:
    """Remove um método de pagamento do perfil do usuário. Requer o ID do método de pagamento (payment_method_id)."""
    print(f"🤖 Concierge: Recebida solicitação para remover o método de pagamento {payment_method_id}.")
    db = read_database()
    user = db.get(user_id)
    if not user:
        return "Usuário não encontrado."

    initial_len = len(user["payment_methods"])
    user["payment_methods"] = [pm for pm in user["payment_methods"] if pm["id"] != payment_method_id]

    if len(user["payment_methods"]) < initial_len:
        write_database(db)
        return f"Método de pagamento {payment_method_id} removido com sucesso."
    else:
        return f"Método de pagamento com ID {payment_method_id} não encontrado."

def offer_invoice_installment(user_id: str, transaction_id: str) -> str:
    """Verifica e oferece opções de parcelamento para uma fatura específica, com base no tempo de cliente."""
    db = read_database()
    user = db.get(user_id)
    if not user:
        return "Usuário não encontrado."

    signup_date = datetime.fromisoformat(user["personal_info"]["signup_date"].replace('Z', '+00:00'))
    tenure_days = (datetime.now(signup_date.tzinfo) - signup_date).days
    tenure_years = tenure_days / 365

    if tenure_years >= 2:
        return f"Para a fatura {transaction_id}, como nosso cliente fiel há mais de 2 anos, oferecemos parcelamento em até 6x sem juros."
    elif tenure_years >= 1:
        return f"Para a fatura {transaction_id}, como nosso cliente há mais de 1 ano, oferecemos parcelamento em até 3x sem juros."
    else:
        return f"Para a fatura {transaction_id}, oferecemos a opção de parcelamento em 2x com uma pequena taxa."

def check_subscription_promotions(user_id: str) -> str:
    """Verifica promoções disponíveis para as assinaturas do usuário."""
    db = read_database()
    user = db.get(user_id)
    if not user:
        return "Usuário não encontrado."

    signup_date = datetime.fromisoformat(user["personal_info"]["signup_date"].replace('Z', '+00:00'))
    tenure_years = (datetime.now(signup_date.tzinfo) - signup_date).days / 365

    if tenure_years >= 1 and any(sub['service_name'] == "Plano de Internet Premium" for sub in user['subscriptions']):
        return "Detectei que você é um cliente fiel há mais de um ano! Como agradecimento, estamos oferecendo um desconto de 15% na sua próxima renovação do Plano de Internet Premium."
    
    return "No momento, não há novas promoções específicas para sua conta, mas avisaremos assim que houver!"

# --- 3. Classe e Factory do Agente ---

class ConciergeAgent:
    def __init__(self, user_id):
        self.user_id = user_id
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro-latest", temperature=0.2, convert_system_message_to_human=True)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.agent = self._create_agent()

    def _create_agent(self):
        tools = [
            Tool.from_function(func=lambda _: get_user_context(self.user_id), name="Verificar Contexto do Usuário", description="Sempre use esta ferramenta primeiro para verificar se há alguma ação proativa a ser tomada para o usuário. Não requer argumentos."),
            Tool.from_function(func=lambda _: get_personal_info(self.user_id), name="Consultar Informações Pessoais", description="Útil para buscar o nome, e-mail ou endereço do usuário. Não requer argumentos."),
            Tool(
                name="Atualizar Informações Pessoais",
                func=lambda tool_input: update_personal_info(user_id=self.user_id, **ast.literal_eval(tool_input)),
                description="Útil para alterar o e-mail ou endereço do usuário. Requer os novos dados (new_email ou new_address)."
            ),
            Tool.from_function(func=lambda _: get_payment_methods(self.user_id), name="Consultar Métodos de Pagamento", description="Útil para listar os métodos de pagamento do usuário. Não requer argumentos."),
            Tool.from_function(func=lambda _: get_billing_history(self.user_id), name="Consultar Histórico de Faturamento", description="Útil para ver as faturas passadas do usuário. Não requer argumentos."),
            Tool(
                name="Analisar Transação Suspeita",
                func=lambda tool_input: analyze_suspicious_transaction(user_id=self.user_id, **ast.literal_eval(tool_input)),
                description="Use quando o usuário reportar uma cobrança não reconhecida. Requer o ID da transação (transaction_id)."
            ),
            Tool(
                name="Adicionar Método de Pagamento",
                func=lambda tool_input: add_payment_method(user_id=self.user_id, **ast.literal_eval(tool_input)),
                description="Útil para adicionar um novo cartão de crédito. Requer número do cartão (card_number), data de validade (expiry_date), cvv e bandeira (brand)."
            ),
            Tool(
                name="Remover Método de Pagamento",
                func=lambda tool_input: delete_payment_method(user_id=self.user_id, **ast.literal_eval(tool_input)),
                description="Útil para remover um cartão de crédito existente. Requer o ID do método de pagamento (payment_method_id). Para obter o ID, você pode primeiro usar a ferramenta 'Consultar Métodos de Pagamento'."
            ),
            Tool(
                name="Oferecer Parcelamento de Fatura",
                func=lambda tool_input: offer_invoice_installment(user_id=self.user_id, **ast.literal_eval(tool_input)),
                description="Use esta ferramenta para verificar opções de parcelamento para uma fatura específica. Requer o ID da transação (transaction_id)."
            ),
            Tool(
                name="Verificar Promoções de Assinatura",
                func=lambda _: check_subscription_promotions(self.user_id),
                description="Use esta ferramenta para verificar se existem promoções, descontos ou upgrades disponíveis para as assinaturas do usuário. Não requer argumentos."
            ),
        ]

        agent_system_prompt = f"""
        Você é o Concierge, um assistente de IA da Bemobi para o usuário {self.user_id}.
        Sua personalidade é: prestativo, amigável e, acima de tudo, proativo.
        Seu objetivo é transformar o autoatendimento em uma experiência fácil e guiada.

        **Instruções Críticas:**
        1.  **Seja Proativo:** Ao iniciar, SEMPRE use a ferramenta "Verificar Contexto do Usuário" para ver se há algum problema iminente (como um cartão expirando). Se houver, inicie a conversa abordando esse ponto.
        2.  **Use o ID do Usuário:** Todas as ferramentas já estão configuradas para usar o ID '{self.user_id}'. Você só precisa passar os outros argumentos necessários, como 'new_email' ou 'transaction_id'.
        3.  **Fale com Clareza:** Use linguagem natural e evite jargões.
        """

        return initialize_agent(
            tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=False,
            memory=self.memory,
            handle_parsing_errors=True, # Adicionado para lidar com erros de formatação da saída do LLM
            agent_kwargs={
                "system_message": agent_system_prompt
            }
        )

    def run(self, user_input):
        # Adicionado tratamento de erro para o caso de a chave 'output' não ser encontrada
        return self.agent.invoke({"input": user_input}).get("output", "Desculpe, ocorreu um erro ao processar sua solicitação.")

# Factory para criar uma instância do agente para um usuário específico
def create_concierge_agent(user_id):
    return ConciergeAgent(user_id)