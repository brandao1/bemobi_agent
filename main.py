import os
import sys
from dotenv import load_dotenv
from agent_concierge import create_concierge_agent

def main():
    """
    Função principal para simular a interação com o Agente Concierge.
    """
    # Carrega variáveis de ambiente do arquivo .env
    load_dotenv()

    # Verifica se a chave de API do Google está configurada
    if not os.getenv("GOOGLE_API_KEY"):
        print("Erro: A variável de ambiente GOOGLE_API_KEY não está definida.")
        print("Por favor, crie um arquivo .env e adicione a linha: GOOGLE_API_KEY='sua_chave_aqui'")
        sys.exit(1)

    # ID do usuário para a simulação
    user_id_sim = "user_maria_123"

    print("="*50)
    print(f"🚀 Iniciando Simulação com o Agente Concierge para o usuário: {user_id_sim}")
    print("="*50)

    # Cria uma instância do agente para o usuário específico
    concierge = create_concierge_agent(user_id=user_id_sim)

    # --- Simulação de Conversa ---

    # 1. O agente começa a conversa de forma proativa
    print("\n--- Início da Conversa ---")
    initial_response = concierge.run("Olá")
    print(f"🤖 Concierge: {initial_response}")
    print("(Digite 'sair' para encerrar a conversa)")

    # 2. Loop para conversa contínua
    while True:
        user_query = input("👤 Usuário: ")
        if user_query.lower() in ["sair", "exit", "quit"]:
            print("🤖 Concierge: Até logo! Fico à disposição se precisar de algo mais.")
            break
        response = concierge.run(user_query)
        print(f"🤖 Concierge: {response}")

if __name__ == "__main__":
    main()