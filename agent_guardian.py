import json
from datetime import datetime, timedelta

# --- 1. Funções de Interação com a Base de Dados (customer_profile.json) ---

DB_FILE = 'customer_profile.json'

def read_database():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 2. Lógica do Agente Guardian ---

class GuardianAgent:
    def __init__(self):
        self.db = read_database()

    def analyze_transaction(self, user_id: str, transaction_details: dict) -> dict:
        """Analisa uma transação e retorna um perfil de risco."""
        print(f"🤖 Guardian: Analisando transação para {user_id}")
        user_profile = self.db.get(user_id)
        if not user_profile:
            return {"risk_score": 100, "reason": "Usuário não encontrado."}

        risk_score = 0
        risk_reasons = []

        # 1. Análise de Anomalia de Valor
        risk_score, risk_reasons = self._check_value_anomaly(user_profile, transaction_details, risk_score, risk_reasons)

        # 2. Análise de Rede e Localização
        risk_score, risk_reasons = self._check_network_anomaly(user_profile, transaction_details, risk_score, risk_reasons)
        
        # 3. Análise Comportamental (Simulada)
        risk_score, reasons = self._check_behavioral_anomaly(transaction_details, risk_score, risk_reasons)

        final_risk = self._classify_risk(risk_score)
        print(f"🤖 Guardian: Análise concluída. Risco: {final_risk} (Score: {risk_score})")

        return {
            "risk_score": risk_score,
            "risk_level": final_risk,
            "reasons": risk_reasons
        }

    def _check_value_anomaly(self, profile, transaction, score, reasons):
        avg_value = profile["behavioral_data"]["avg_transaction_value"]
        if transaction["amount_brl"] > avg_value * 3:
            score += 40
            reasons.append(f"Valor da transação (R${transaction['amount_brl']}) é significativamente maior que a média do usuário (R${avg_value}).")
        return score, reasons

    def _check_network_anomaly(self, profile, transaction, score, reasons):
        last_location = profile["behavioral_data"]["login_locations"][-1]["city"]
        if transaction["location"] != last_location:
            score += 30
            reasons.append(f"Transação originada em '{transaction['location']}', mas a última localização conhecida do usuário é '{last_location}'.")
        return score, reasons

    def _check_behavioral_anomaly(self, transaction, score, reasons):
        # Simulação: tempo de preenchimento muito rápido pode indicar bot
        if transaction["time_on_page_seconds"] < 5:
            score += 30
            reasons.append("Tempo de preenchimento da página de pagamento suspeitosamente baixo.")
        return score, reasons

    def _classify_risk(self, score):
        if score >= 70:
            return "Alto"
        if score >= 40:
            return "Médio"
        return "Baixo"

    def _luhn_check(self, card_number: str) -> bool:
        """Verifica se um número de cartão é válido usando o Algoritmo de Luhn."""
        try:
            digits = [int(d) for d in card_number]
            checksum = 0
            for i, digit in enumerate(reversed(digits)):
                if i % 2 == 1:
                    doubled_digit = digit * 2
                    if doubled_digit > 9:
                        doubled_digit -= 9
                    checksum += doubled_digit
                else:
                    checksum += digit
            return checksum % 10 == 0
        except (ValueError, TypeError):
            return False

    def validate_new_card(self, card_details: dict) -> dict:
        """Valida um novo cartão de crédito usando verificações simuladas."""
        print("🤖 Guardian: Validando novo cartão.")
        card_number = card_details.get("number", "").replace(" ", "")
        expiry_date = card_details.get("expiry_date") # "YYYY-MM"
        cvv = card_details.get("cvv")

        reasons = []
        is_valid = True

        # 1. Verificação do Algoritmo de Luhn
        if not self._luhn_check(card_number):
            is_valid = False
            reasons.append("O número do cartão é inválido (falha na verificação do algoritmo de Luhn).")

        # 2. Verificação da Data de Validade
        if expiry_date:
            try:
                expiry_year, expiry_month = map(int, expiry_date.split('-'))
                first_day_of_expiry_month = datetime(expiry_year, expiry_month, 1)
                effective_expiry_date = (first_day_of_expiry_month + timedelta(days=32)).replace(day=1)
                if datetime.now() >= effective_expiry_date:
                    is_valid = False
                    reasons.append("O cartão informado já está expirado.")
            except (ValueError, IndexError):
                is_valid = False
                reasons.append("Formato da data de validade inválido. Use AAAA-MM.")
        else:
            is_valid = False
            reasons.append("Data de validade não fornecida.")

        # 3. Verificação do CVV (simples)
        if not (cvv and 3 <= len(cvv) <= 4 and cvv.isdigit()):
            is_valid = False
            reasons.append("CVV inválido.")

        if is_valid:
            print("🤖 Guardian: Cartão validado com sucesso.")
            return {"is_valid": True, "message": "Cartão validado com sucesso."}
        else:
            print(f"🤖 Guardian: Falha na validação do cartão. Motivos: {reasons}")
            return {"is_valid": False, "reasons": reasons}

# Factory para criar uma instância do agente
def create_guardian_agent():
    return GuardianAgent()
