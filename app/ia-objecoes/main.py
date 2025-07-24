# main.py
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from config import OPENAI_API_KEY

# 1) Carrega todo o prompt de sistema (sua “Agente de Objeções Inteligente”)
with open("prompts/base_prompt_dificil.txt", "r", encoding="utf-8") as f:
    base_prompt = f.read()

# 2) Instancia o ChatOpenAI
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=0.7,
    model="gpt-4"
)

# 3) Inicia o histórico com a mensagem de sistema + primeira instrução do vendedor  # noqa: E501
messages: list[SystemMessage | HumanMessage | AIMessage] = [
    SystemMessage(content=base_prompt),
    HumanMessage(content="Inicie agora com uma objeção de dificuldade fácil no setor de transporte.")  # noqa: E501
]

# 4) Chama o LLM usando .invoke() e imprime a resposta
initial_response: AIMessage = llm.invoke(messages)
print("\n--- AGENTE ---\n", initial_response.content)
messages.append(initial_response)

# 5) Loop de chat
while True:
    user_input = input("\nVocê: ")
    if user_input.strip().lower() in {"sair", "exit", "quit"}:
        print("Encerrando o chat. Até mais!")
        break

    # 5.1) Anexa a mensagem do usuário
    messages.append(HumanMessage(content=user_input))

    # 5.2) Gera a próxima resposta
    response: AIMessage = llm.invoke(messages)
    print("\n--- AGENTE ---\n", response.content)

    # 5.3) Armazena no histórico
    messages.append(response)  # noqa: W292