# Projeto de Agentes de IA - Bemobi

Este projeto demonstra a implementação e integração de dois agentes de IA, **Concierge** e **Guardian**, para aprimorar a jornada do cliente em uma plataforma de serviços.

## Arquitetura

O projeto é composto por três componentes principais:

1.  **Agente Concierge (`agent_concierge.py`)**:
    *   **Tecnologia**: LangChain com o modelo `gemini-1.5-pro-latest`.
    *   **Função**: É o ponto de contato principal com o usuário. Ele é projetado para ser um assistente proativo e prestativo, capaz de realizar tarefas de autoatendimento como consultar dados, atualizar informações e, crucialmente, identificar e agir sobre possíveis problemas (ex: um cartão de crédito prestes a expirar).
    *   **Integração**: O Concierge possui uma ferramenta que lhe permite invocar o Agente Guardian para analisar transações que o usuário reporte como suspeitas.

2.  **Agente Guardian (`agent_guardian.py`)**:
    *   **Tecnologia**: Lógica de negócios em Python (baseada em regras).
    *   **Função**: É um serviço especializado em análise de risco. Ele recebe os detalhes de uma transação e, com base no perfil e histórico do usuário, calcula um score de risco e identifica os motivos. Ele não interage diretamente com o usuário.

3.  **Orquestrador da Simulação (`main.py`)**:
    *   **Função**: Este script inicializa o ambiente, cria uma instância do Agente Concierge para um usuário simulado e conduz um diálogo que demonstra a colaboração entre os agentes.

4.  **Base de Dados Simulada (`customer_profile.json`)**:
    *   Um arquivo JSON que simula um banco de dados de clientes, contendo informações pessoais, métodos de pagamento, histórico de faturamento e dados comportamentais.

## Como Configurar e Executar

Siga os passos abaixo para rodar a simulação.

### Pré-requisitos

*   Python 3.9 ou superior.
*   Uma chave de API do Google para acesso aos modelos Gemini. Você pode obter uma no Google AI Studio.

### 1. Instalação das Dependências

Primeiro, instale as bibliotecas Python necessárias. É altamente recomendável usar um ambiente virtual (`venv`).

```bash
# Crie um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install langchain langchain-google-genai google-generativeai langchain-community duckduckgo-search python-dotenv
```

### 2. Configuração da Chave de API

A forma mais segura de gerenciar sua chave de API é através de variáveis de ambiente.

1.  Crie um arquivo chamado `.env` na raiz do projeto (`c:\bemobi_agent\.env`).
2.  Adicione a seguinte linha ao arquivo, substituindo `sua_chave_aqui` pela sua chave de API real:

    ```
    GOOGLE_API_KEY='sua_chave_aqui'
    ```

O script `main.py` carregará automaticamente esta variável.

### 3. Executando a Simulação

Com tudo configurado, execute o script `main.py` a partir do seu terminal:

```bash
python main.py
```

O script irá simular uma conversa entre um usuário e o Agente Concierge. Você verá no console os "pensamentos" do agente (as ferramentas que ele decide usar) e as respostas finais, incluindo o momento em que ele consulta o Agente Guardian para analisar uma transação.