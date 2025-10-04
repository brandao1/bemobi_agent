import json
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '..', 'data', 'customer_profile.json')

def read_database():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_database(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

class GatekeeperAgent:
    """
    Agente responsável por simular o onboarding de novos clientes.
    """
    def simulate_onboarding(self, document_image_path: str, new_user_data: dict):
        """
        Simula o processo completo de onboarding: OCR, verificação e criação de perfil.
        """
        print(f"🤖 Gatekeeper: Iniciando onboarding com o documento '{document_image_path}'.")

        time.sleep(1.5)
        print("🤖 Gatekeeper: Processando imagem com OCR... Dados extraídos.")
        extracted_name = new_user_data["personal_info"]["name"]
        extracted_email = new_user_data["personal_info"]["email"]

        time.sleep(2)
        print(f"🤖 Gatekeeper: Realizando verificação biométrica e KYC para '{extracted_name}'...")
        print("🤖 Gatekeeper: Verificação concluída com sucesso. Nenhuma pendência encontrada.")

        db = read_database()
        user_id = new_user_data["user_id"]
        if user_id in db:
            return {"status": "error", "message": f"Usuário com ID {user_id} já existe."}

        new_user_data["personal_info"]["signup_date"] = datetime.now().isoformat()
        new_user_data["aegis_scores"] = {
            "churn_probability": 0.05,
            "last_calculated_date": datetime.now().isoformat()
        }
        new_user_data["behavioral_data"]["last_activity_date"] = datetime.now().isoformat()


        db[user_id] = new_user_data
        write_database(db)
        print(f"🤖 Gatekeeper: Perfil para o usuário '{user_id}' criado com sucesso no sistema.")

        return {
            "status": "success",
            "user_id": user_id,
            "message": f"Onboarding de {extracted_name} ({extracted_email}) concluído."
        }

def create_gatekeeper_agent():
    return GatekeeperAgent()