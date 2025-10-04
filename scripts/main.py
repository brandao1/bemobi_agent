import os
import sys
from dotenv import load_dotenv
from agent_concierge import create_concierge_agent

def main():
    """
    Função principal para simular uma conversa de WhatsApp com a Agente Grace.
    """
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("Erro: A variável de ambiente GOOGLE_API_KEY não está definida.")
        sys.exit(1)

    print("="*60)
    print("🚀 Iniciando Chat com a Agente Grace (para Maria Silva)")
    print("   Simulação de uma conversa de WhatsApp.")
    print("="*60)

    concierge = create_concierge_agent()

    print("\n--- Conversa Iniciada ---")
    initial_response = concierge.run("Olá, Grace!")
    print(f"🤖 {initial_response}")
    print("(Digite 'sair' para encerrar a conversa)")

    while True:
        user_query = input("👤 Maria: ")
        if user_query.lower() in ["sair", "exit", "quit"]:
            print("🤖 Grace: Até mais, Maria! Se precisar, é só chamar. 😉")
            break
        response = concierge.run(user_query)
        print(f"🤖 {response}")

if __name__ == "__main__":
    main()