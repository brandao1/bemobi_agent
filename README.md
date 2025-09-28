# Projeto Aegis

O Projeto Aegis é um ecossistema multiagente de IA projetado para revolucionar a jornada do cliente para a Bemobi. Este protótipo, desenvolvido para um hackathon, demonstra como agentes de IA especializados podem orquestrar de forma inteligente todo o ciclo de vida do cliente, desde o onboarding até a retenção.

## Sobre

Aegis atua como uma camada de orquestração inteligente sobre a infraestrutura existente da Bemobi, com a missão de fortalecer a segurança das transações e apoiar proativamente o cliente em cada etapa de sua jornada. A visão é elevar a Bemobi de um provedor de ferramentas de pagamento para um orquestrador autônomo e preditivo do ciclo de vida do cliente.

## Os Agentes

O ecossistema é composto por seis agentes especializados:

*   **Gatekeeper:** Automatiza o processo de onboarding de novos clientes com verificação de identidade segura e instantânea.
*   **Concierge:** Uma IA conversacional para autoatendimento e gerenciamento de contas.
*   **Guardian:** Um motor de detecção de fraude em tempo real que opera em segundo plano.
*   **Dynamo:** Otimiza as taxas de sucesso de pagamento e oferece opções de pagamento dinâmicas.
*   **Oracle:** Um agente de análise preditiva que calcula a probabilidade de churn e prevê possíveis falhas de pagamento.
*   **Ambassador:** Atua com base na inteligência preditiva do Oracle para gerenciar proativamente o relacionamento com o cliente.

## Começando

Estas instruções permitirão que você tenha uma cópia do projeto em funcionamento em sua máquina local para fins de desenvolvimento e teste.

### Pré-requisitos

*   Python 3.9 ou superior
*   Pip (gerenciador de pacotes do Python)

### Instalação

1.  **Clone o repositório:**
    ```sh
    git clone <url-do-repositorio>
    cd <diretorio-do-projeto>
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```sh
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure suas variáveis de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave da API do Google:
    ```
    GOOGLE_API_KEY='sua_chave_de_api_aqui'
    ```

## Uso

Para iniciar a simulação, execute o arquivo `main.py`. Isso iniciará uma interação de linha de comando com o Agente Concierge.

```sh
python main.py
```

Você poderá então conversar com o agente no seu terminal. Para encerrar a conversa, digite `sair`.

Segue o diagrama com as funcionalidades totais
<img width="1415" height="1409" alt="Diagrama" src="https://github.com/user-attachments/assets/9ba3bf92-181e-4d5f-baa8-7aa45bcb82af" />
