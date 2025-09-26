import google.generativeai as genai
import os
import json


# --- 1. Configuração Inicial e Banco de Dados Falso (Mock) ---

# Cole sua API Key aqui ou configure como uma variável de ambiente
# os.environ['GOOGLE_API_KEY'] = "SUA_API_KEY"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Simulação de um banco de dados de usuários e serviços.
# Em um sistema real, isso seria um banco de dados SQL, NoSQL, etc.
mock_user_database = {
    "user_123": {
        "name": "Victor",
        "email": "victor@email.com",
        "subscriptions": [
            {
                "service_name": "GamePass Ultimate",
                "plan": "Premium",
                "price_brl": 49.99,
                "next_billing_date": "2025-10-05",
                "payment_method": "Cartão final 4021"
            }
        ],
        "payment_history": [
            {"date": "2025-09-05", "description": "Cobrança mensal GamePass", "amount_brl": 49.99},
            {"date": "2025-09-15", "description": "Compra de item 'XP extra'", "amount_brl": 15.00}
        ]
    }
}

mock_service_providers_br = {
    "netflix": {"provider": "Netflix Brasil", "type": "Streaming de Vídeo"},
    "spotify": {"provider": "Spotify AB", "type": "Streaming de Música"},
    "gamepass": {"provider": "Microsoft", "type": "Serviço de Jogos"},
    "office 365": {"provider": "Microsoft", "type": "Software de Produtividade"},
    "aws": {"provider": "Amazon Web Services", "type": "Computação em Nuvem"}
}


# --- 2. Definição das Ferramentas (Tools) que o Gemini pode usar ---
# As descrições (docstrings) são MUITO importantes, pois é assim que o Gemini
# aprende o que cada ferramenta faz.

def search_service_providers(service_name: str) -> str:
    """
    Busca provedores para um serviço específico disponível no Brasil.
    Retorna o nome do provedor e o tipo de serviço.
    """
    print(f"🤖 Executando busca pelo serviço: {service_name}")
    service_key = service_name.lower().replace(" ", "")
    provider_info = mock_service_providers_br.get(service_key)
    if provider_info:
        return json.dumps(provider_info)
    else:
        return json.dumps({"error": "Serviço não encontrado."})

def get_user_account_status(user_id: str, service_name: str) -> str:
    """
    Verifica no banco de dados interno se um usuário já possui uma assinatura
    ativa para um serviço específico.
    """
    print(f"🤖 Verificando status da conta para {user_id} no serviço {service_name}")
    user = mock_user_database.get(user_id, {})
    for sub in user.get("subscriptions", []):
        if service_name.lower() in sub["service_name"].lower():
            return json.dumps({"status": "active", "details": sub})
    return json.dumps({"status": "inactive"})

def create_subscription(user_id: str, service_name: str, payment_method: str) -> str:
    """
    Cria uma nova assinatura para um usuário em um serviço específico,
    processando o primeiro pagamento. (Simulação)
    """
    print(f"🤖 Criando assinatura de {service_name} para {user_id} com {payment_method}")
    # Lógica para adicionar a assinatura ao mock_user_database aqui...
    return json.dumps({"status": "success", "message": f"Assinatura de {service_name} criada com sucesso!"})

def get_user_plan_details(user_id: str) -> str:
    """
    Consulta e retorna os detalhes do plano e assinaturas atuais do usuário.
    """
    print(f"🤖 Buscando detalhes do plano para {user_id}")
    user = mock_user_database.get(user_id, {})
    subscriptions = user.get("subscriptions", [])
    if subscriptions:
        return json.dumps(subscriptions)
    return json.dumps({"error": "Nenhuma assinatura ativa encontrada."})

def resolve_billing_issue(user_id: str, issue_description: str) -> str:
    """
    Analisa o histórico de pagamentos do usuário para resolver uma dúvida
    sobre cobrança.
    """
    print(f"🤖 Analisando problema de cobrança para {user_id}: '{issue_description}'")
    user = mock_user_database.get(user_id, {})
    history = user.get("payment_history", [])
    # IA do Gemini analisará o histórico junto com a pergunta para dar a resposta
    return json.dumps(history)

# --- 3. Inicialização do Modelo Gemini e do Chat ---

# Habilita o "Function Calling" automático
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    tools=[
        search_service_providers,
        get_user_account_status,
        create_subscription,
        get_user_plan_details,
        resolve_billing_issue
    ]
)

# Inicia o chat
chat = model.start_chat(enable_automatic_function_calling=True)

print("--- Protótipo do Agente Grace (Conectado à Bemobi) ---")
print("Para simular, você é o usuário 'user_123'. Digite 'sair' para terminar.")

# --- 4. Loop de Conversa (Simulação do WhatsApp) ---

while True:
    prompt = input("Você: ")
    if prompt.lower() == 'sair':
        break

    # Adiciona o ID do usuário ao prompt para o agente saber quem está falando
    # Numa integração real, o ID viria do número do WhatsApp
    contextual_prompt = f"O usuário 'user_123' diz: {prompt}"

    response = chat.send_message(contextual_prompt)

    print(f"Agente Grace: {response.text}\n")