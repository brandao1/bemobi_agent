from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from dotenv import load_dotenv
load_dotenv()

from src.agents.agent_concierge import create_concierge_agent

try:
    with open('src/data/customer_profile.json', 'r', encoding='utf-8') as f:
        ORIGINAL_USER_PROFILE = json.load(f)
except FileNotFoundError:
    print("ERRO: Arquivo 'src/data/customer_profile.json' não encontrado. Verifique o caminho.")
    exit()

def write_database(data):
    with open('src/data/customer_profile.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

app = Flask(__name__)
CORS(app)

print("🤖 Inicializando a Agente Grace... Por favor, aguarde.")
concierge_agent = create_concierge_agent()
print("✅ Agente Pronta!")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    print(f"👤 Mensagem recebida da interface: {user_message}")

    if user_message == "Olá":
        print("🔄 Detectada nova sessão, restaurando o perfil do usuário para o padrão.")
        write_database(ORIGINAL_USER_PROFILE)

    agent_response = concierge_agent.run(user_message)
    print(f"🤖 Resposta gerada pela agente: {agent_response}")

    return jsonify({'reply': agent_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)