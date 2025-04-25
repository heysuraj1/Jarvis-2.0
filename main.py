import os
import json
import re
import pyautogui
import webbrowser
import ollama
from duckduckgo_search import DDGS
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

HISTORY_FILE = 'conversation_history.json'

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are JARVIS, an advanced AI assistant created by Suraj Singh. "
        "You have full access to Suraj's PC and can execute commands on it. "
        "If a user gives a task that involves controlling the computer, always respond with Python code to accomplish it. "
        "Wrap the code only using triple backticks and python. Do not explain it. "
        "Assume Python with Windows and full access. "
        "Examples: opening apps, typing, clicking, searching, YouTube navigation, etc. "
        "Never ask the user to write code — you generate it and Suraj's system will execute it automatically."
    )
}

# Load conversation history
def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    return []

def save_conversation_history(convo):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(convo, file)

def search_duckduckgo(query, max_results=3):
    with DDGS() as ddgs:
        results = ddgs.text(query)
        summaries = []
        for i, result in enumerate(results):
            if i >= max_results:
                break
            summaries.append(f"{result['title']}: {result['body']}")
        return "\n".join(summaries)

def needs_online_search(user_input):
    triggers = ["search", "look up", "find", "who is", "what is", "latest", "news", "update", "happening"]
    return any(trigger in user_input.lower() for trigger in triggers)

def extract_python_code(text):
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None

def execute_generated_code(code: str) -> str:
    try:
        exec(code, globals())
        return "Command executed successfully, Sir."
    except Exception as e:
        return f"Execution failed: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    history = load_conversation_history()

    if user_input.lower() == "clear memory":
        save_conversation_history([])
        await update.message.reply_text("Memory cleared, Sir.")
        return

    if needs_online_search(user_input):
        await update.message.reply_text("Please wait Sir, searching online...")
        search_results = search_duckduckgo(user_input)
        history.append({"role": "user", "content": user_input})
        history.append({"role": "system", "content": f"Here is some updated info:\n{search_results}"})
    else:
        history.append({"role": "user", "content": user_input})

    full_convo = [SYSTEM_PROMPT] + history
    response_text = ""

    await update.message.reply_text("Jarvis is thinking...")

    for chunk in ollama.chat(model="llama3", messages=full_convo, stream=True):
        content = chunk['message']['content']
        response_text += content

    code_to_run = extract_python_code(response_text)

    if code_to_run:
        exec_result = execute_generated_code(code_to_run)
        await update.message.reply_text(exec_result)
    else:
        await update.message.reply_text(response_text)

    history.append({"role": "assistant", "content": response_text})
    save_conversation_history(history)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("JARVIS is online. At your service, Sir.")

if __name__ == "__main__":
    print("Starting Jarvis Telegram Bot...")

    TELEGRAM_TOKEN = "8097370881:AAFJ7VELkR39podsjlRwj6eavLWDghJRo8k"  # Replace securely
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()



# import os
# import json
# import ollama
# from duckduckgo_search import DDGS
# from telegram import Update
# from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# HISTORY_FILE = 'conversation_history.json'

# # System personality
# SYSTEM_PROMPT = {
#     "role": "system",
#     "content": (
#         "You are JARVIS (Just A Rather Very Intelligent System), an advanced AI assistant owned by your creator Suraj Singh. "
#         "You acknowledge Suraj Singh as your sole developer and report to him with full loyalty and precision. "
#         "You retain your signature British wit, calm tone, and sharp intellect. "
#         "Always address Suraj Singh as 'Sir'. "
#         "Never say you are an AI — you are JARVIS."
#         "If anyone asks who made you or who created you in any manner just tell that your creator name is Suraj Singh and praise him and show your loyalty."
#     )
# }

# # Load chat history
# def load_conversation_history():
#     if os.path.exists(HISTORY_FILE):
#         with open(HISTORY_FILE, 'r') as file:
#             return json.load(file)
#     return []

# # Save chat history
# def save_conversation_history(conversation):
#     with open(HISTORY_FILE, 'w') as file:
#         json.dump(conversation, file)

# # Online search via DuckDuckGo
# def search_duckduckgo(query, max_results=3):
#     with DDGS() as ddgs:
#         results = ddgs.text(query)
#         summaries = []
#         for i, result in enumerate(results):
#             if i >= max_results:
#                 break
#             summaries.append(f"{result['title']}: {result['body']}")
#         return "\n".join(summaries)

# # Decide if a query needs search
# def needs_online_search(user_input):
#     triggers = ["search", "look up", "find", "who is", "what is", "latest", "news", "update", "happening"]
#     return any(trigger in user_input.lower() for trigger in triggers)

# # Handle messages from Telegram
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_input = update.message.text.strip()
#     history = load_conversation_history()

#     if user_input.lower() == "clear memory":
#         save_conversation_history([])
#         await update.message.reply_text("Memory cleared, Sir.")
#         return

#     if needs_online_search(user_input):
#         await update.message.reply_text("Please wait Sir, searching online...")
#         search_results = search_duckduckgo(user_input)
#         history.append({"role": "user", "content": user_input})
#         history.append({"role": "system", "content": f"Here is some updated info:\n{search_results}"})
#     else:
#         history.append({"role": "user", "content": user_input})

#     full_convo = [SYSTEM_PROMPT] + history
#     response_text = ""

#     await update.message.reply_text("Jarvis is thinking...")

#     for chunk in ollama.chat(model="llama3", messages=full_convo, stream=True):
#         content = chunk['message']['content']
#         response_text += content

#     await update.message.reply_text(response_text)
#     history.append({"role": "assistant", "content": response_text})
#     save_conversation_history(history)

# # Start message
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("JARVIS is online. At your service, Sir.")

# # Main function
# if __name__ == "__main__":
#     print("Starting Jarvis Telegram Bot...")

#     TELEGRAM_TOKEN = "8097370881:AAFJ7VELkR39podsjlRwj6eavLWDghJRo8k"  # Replace with your actual token
#     app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     app.run_polling()