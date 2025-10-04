from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from src.agents.agent_concierge import create_concierge_agent

app = Flask(__name__)
CORS(app)

print("🤖 Inicializando a Agente Grace... Por favor, aguarde.")
concierge_agent = create_concierge_agent()
print("✅ Agente Pronta!")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    print(f"👤 Mensagem recebida da interface: {user_message}")

    agent_response = concierge_agent.run(user_message)
    print(f"🤖 Resposta gerada pela agente: {agent_response}")

    return jsonify({'reply': agent_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)