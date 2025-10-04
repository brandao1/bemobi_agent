import json
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '..', 'data', 'customer_profile.json')

def read_database():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

class OracleAgent:
    """
    Agente de análise preditiva que opera nos bastidores para
    calcular a probabilidade de churn de cada cliente.
    """
    def calculate_churn_risk(self, user_id: str) -> dict:
        """
        Simula o cálculo de risco de churn baseado em dados do perfil do usuário.
        Em um cenário real, isso seria um modelo de ML treinado.
        """
        print(f"🤖 Oracle: Calculando risco de churn para o usuário {user_id}.")
        db = read_database()
        user = db.get(user_id)
        if not user:
            return {"error": "Usuário não encontrado."}

        base_score = 0.05
        reasons = ["Pontuação base inicial."]

        last_activity_str = user["behavioral_data"].get("last_activity_date")
        if last_activity_str:
            last_activity = datetime.fromisoformat(last_activity_str)
            days_inactive = (datetime.now() - last_activity).days
            if days_inactive > 30:
                base_score += 0.25
                reasons.append(f"Inatividade por mais de {days_inactive} dias.")
            elif days_inactive > 15:
                base_score += 0.10
                reasons.append(f"Inatividade por mais de {days_inactive} dias.")

        failed_payments = [p for p in user.get("billing_history", []) if p["status"] == "failed"]
        if len(failed_payments) > 0:
            base_score += 0.15 * len(failed_payments)
            reasons.append(f"{len(failed_payments)} falha(s) de pagamento no histórico.")

        signup_date_str = user["personal_info"].get("signup_date")
        if signup_date_str:
            try:
                signup_date = datetime.fromisoformat(signup_date_str)
                months_as_customer = (datetime.now() - signup_date).days / 30
                if months_as_customer > 12:
                    base_score -= 0.05
                    reasons.append("Cliente há mais de 1 ano (bônus de lealdade).")
            except ValueError:
                reasons.append("Não foi possível calcular o tempo de cliente (data de cadastro inválida).")
        else:
            reasons.append("Não foi possível calcular o tempo de cliente (data de cadastro não preenchida).")


        final_score = max(0.01, min(base_score, 0.95))

        print(f"🤖 Oracle: Cálculo concluído para {user_id}. Risco de Churn: {final_score:.2%}")

        return {
            "user_id": user_id,
            "churn_probability": final_score,
            "risk_level": self._classify_risk(final_score),
            "reasons": reasons,
            "last_calculated_date": datetime.now().isoformat()
        }

    def _classify_risk(self, score: float) -> str:
        if score > 0.6:
            return "Alto"
        if score > 0.3:
            return "Médio"
        return "Baixo"

def create_oracle_agent():
    return OracleAgent()