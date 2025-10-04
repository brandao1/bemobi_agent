from .agent_oracle import OracleAgent

class AmbassadorAgent:
    """
    O braço executivo do Oracle, agindo com base na inteligência preditiva
    para gerenciar proativamente a relação com o cliente.
    """
    def __init__(self):
        self.oracle = OracleAgent()

    def create_proactive_retention_action(self, user_id: str) -> dict:
        """
        Verifica o risco de churn e, se for alto, cria uma ação de retenção personalizada.
        """
        print(f"🤖 Ambassador: Verificando necessidade de ação proativa para {user_id}.")

        churn_analysis = self.oracle.calculate_churn_risk(user_id)
        if churn_analysis.get("error"):
            return {"action_taken": False, "reason": churn_analysis["error"]}

        churn_prob = churn_analysis["churn_probability"]
        risk_level = churn_analysis["risk_level"]
        reasons = churn_analysis["reasons"]

        if risk_level in ["Alto", "Médio"]:
            print(f"🤖 Ambassador: Risco de churn '{risk_level}' ({churn_prob:.2%}) detectado. Gerando ação.")

            action_message = ""
            if any("Inatividade" in r for r in reasons):
                action_message = (
                    f"Olá! Sentimos sua falta. Notamos que você não tem aproveitado muito nossos serviços. "
                    f"Como incentivo, estamos oferecendo um upgrade de velocidade gratuito por 30 dias!"
                )
            elif any("falha(s) de pagamento" in r for r in reasons):
                 action_message = (
                    f"Olá, notamos que houve um problema com seu último pagamento. "
                    f"Não se preocupe, oferecemos opções flexíveis para regularizar. Que tal parcelar o valor em 2x sem juros?"
                )
            else:
                action_message = (
                    f"Olá! Como nosso cliente, queremos garantir que você tenha a melhor experiência. "
                    f"Temos uma oferta especial de 15% de desconto na sua próxima fatura."
                )

            return {
                "action_taken": True,
                "risk_level": risk_level,
                "churn_probability": churn_prob,
                "suggested_action": "Enviar notificação proativa de retenção.",
                "message_to_user": action_message
            }
        else:
            print(f"🤖 Ambassador: Risco de churn 'Baixo' ({churn_prob:.2%}). Nenhuma ação necessária.")
            return {
                "action_taken": False,
                "risk_level": risk_level,
                "reason": "O risco de churn do cliente é baixo."
            }


def create_ambassador_agent():
    return AmbassadorAgent()