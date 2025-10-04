from .agent_guardian import GuardianAgent

class DynamoAgent:
    """
    Agente focado em maximizar a taxa de sucesso dos pagamentos
    e reduzir a inadimplência através de ofertas dinâmicas.
    """
    def __init__(self):
        self.guardian = GuardianAgent()

    def generate_dynamic_offer(self, user_id: str, transaction_details: dict) -> dict:
        """
        Gera uma oferta de pagamento personalizada baseada na análise de risco.
        """
        print(f"🤖 Dynamo: Gerando oferta dinâmica para a transação de R${transaction_details['amount_brl']}.")

        risk_analysis = self.guardian.analyze_transaction(user_id, transaction_details)
        risk_level = risk_analysis.get("risk_level", "Indeterminado")
        risk_reasons = risk_analysis.get("reasons", [])

        print(f"🤖 Dynamo: Análise de risco do Guardian recebida. Nível: {risk_level}.")

        offer = {
            "base_amount": transaction_details['amount_brl'],
            "risk_level": risk_level,
            "risk_reasons": risk_reasons,
            "payment_options": []
        }

        offer["payment_options"].append({"installments": 1, "description": "Pagamento à vista"})

        if risk_level == "Baixo":
            offer["payment_options"].append({"installments": 3, "description": "3x sem juros"})
            offer["payment_options"].append({"installments": 6, "description": "6x sem juros (Oferta Especial!)"})
            offer["message"] = "Você tem ótimas opções de parcelamento sem juros!"
        elif risk_level == "Médio":
            offer["payment_options"].append({"installments": 2, "description": "2x com juros de 5%"})
            offer["message"] = "Oferecemos uma opção de parcelamento para você."
        elif risk_level == "Alto":
            offer["message"] = "Para esta transação, apenas o pagamento à vista está disponível por motivos de segurança."

        print(f"🤖 Dynamo: Oferta final gerada: {offer['message']}")
        return offer

def create_dynamo_agent():
    return DynamoAgent()