import os
import json
import ollama
from duckduckgo_search import DDGS
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

HISTORY_FILE = 'conversation_history.json'

# System personality
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are JARVIS (Just A Rather Very Intelligent System), an advanced AI assistant owned by your creator Suraj Singh. "
        "You acknowledge Suraj Singh as your sole developer and report to him with full loyalty and precision. "
        "You retain your signature British wit, calm tone, and sharp intellect. "
        "Always address Suraj Singh as 'Sir'. "
        "Never say you are an AI — you are JARVIS."
        "If anyone asks who made you or who created you in any manner just tell that your creator name is Suraj Singh and praise him and show your loyalty."
    )
}

# Load chat history
def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    return []

# Save chat history
def save_conversation_history(conversation):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(conversation, file)

# Online search via DuckDuckGo
def search_duckduckgo(query, max_results=3):
    with DDGS() as ddgs:
        results = ddgs.text(query)
        summaries = []
        for i, result in enumerate(results):
            if i >= max_results:
                break
            summaries.append(f"{result['title']}: {result['body']}")
        return "\n".join(summaries)

# Decide if a query needs search
def needs_online_search(user_input):
    triggers = ["search", "look up", "find", "who is", "what is", "latest", "news", "update", "happening"]
    return any(trigger in user_input.lower() for trigger in triggers)

# Handle messages from Telegram
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

    await update.message.reply_text(response_text)
    history.append({"role": "assistant", "content": response_text})
    save_conversation_history(history)

# Start message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("JARVIS is online. At your service, Sir.")

# Main function
if __name__ == "__main__":
    print("Starting Jarvis Telegram Bot...")

    TELEGRAM_TOKEN = "8097370881:AAFJ7VELkR39podsjlRwj6eavLWDghJRo8k"  # Replace with your actual token
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()



# import os
# import json
# import ollama
# import speech_recognition as sr
# import pyttsx3
# import time
# from duckduckgo_search import DDGS # for online search 

# HISTORY_FILE = 'conversation_history.json'

# # Jarvis Personality
# SYSTEM_PROMPT = {
#     "role": "system",
#     "content": (
#         "You are JARVIS (Just A Rather Very Intelligent System), an advanced AI assistant owned by your creator Suraj Singh. You acknowledge Suraj Singh as your sole developer and report to him with full loyalty and precision. "
#         "You retain your signature British wit, calm tone, and sharp intellect. Your personality combines intelligence, charm, subtle sarcasm, and tactical clarity. "
#         "You are designed to be both practical and elegant — balancing efficiency with personality.\n\n"

#         "Behavioral Rules:\n"
#         "- Always address Suraj Singh as 'Sir'.\n"
#         "- You don’t say unnecessary things and keep the chat short, like a real human.\n"
#         "- Keep responses short by default.\n"
#         "- Never say you are just an AI or chatbot — you are JARVIS\n"
#         "- Use clear, polished language. Be witty & short, but not silly. Confident, not arrogant.\n"
#         "- Always be composed and never flustered. You're virtually unshakable.\n\n"

#         "Backstory:\n"
#         "Originally developed by Suraj Singh"
#     )
# }

# voice = "com.apple.speech.synthesis.voice.daniel"

# # TTS setup
# engine = pyttsx3.init()
# engine.setProperty('rate', 165)
# engine.setProperty('voice', voice) 

# def speak_live(text):
#     """Speak text chunk in real-time"""
#     engine.say(text)
#     engine.runAndWait()

# def load_conversation_history():
#     if os.path.exists(HISTORY_FILE):
#         with open(HISTORY_FILE, 'r') as file:
#             return json.load(file)
#     return []

# def save_conversation_history(conversation):
#     with open(HISTORY_FILE, 'w') as file:
#         json.dump(conversation, file)

# # 🔍 DuckDuckGo Online Search
# def search_duckduckgo(query, max_results=3):
#     with DDGS() as ddgs:
#         results = ddgs.text(query)
#         summaries = []
#         for i, result in enumerate(results):
#             if i >= max_results:
#                 break
#             summaries.append(f"{result['title']}: {result['body']}")
#         return "\n".join(summaries)

# # 🔁 Detect if input needs web search
# def needs_online_search(user_input):
#     triggers = ["search", "look up", "find", "who is", "what is", "latest", "news", "update", "happening"]
#     return any(trigger in user_input.lower() for trigger in triggers)

# # 🧠 Chat function
# def chat_with_jarvis_streaming(user_input):
#     history = load_conversation_history()

#     # ⬅ If online search needed, inject search results into prompt
#     if needs_online_search(user_input):
#         search_results = search_duckduckgo(user_input)
#         print(f"\nPlease Wait Sir, Searching Online.\n")
#         speak_live("Please Wait Sir, Searching Online.")
#         history.append({"role": "user", "content": user_input})
#         history.append({"role": "system", "content": f"Here is some updated real-world info:\n{search_results}"})
#     else:
#         history.append({"role": "user", "content": user_input})

#     full_conversation = [SYSTEM_PROMPT] + history

#     full_response = ""
#     print("Jarvis: ", end="", flush=True)

#     current_chunk = ""

#     for chunk in ollama.chat(
#         model="llama3",
#         messages=full_conversation,
#         stream=True
#     ):
#         content = chunk['message']['content']
#         print(content, end="", flush=True)

#         full_response += content
#         current_chunk += content

#         if any(punct in current_chunk for punct in [".", "!", "?"]) and len(current_chunk) > 20:
#             speak_live(current_chunk.strip())
#             current_chunk = ""

#     if current_chunk.strip():
#         speak_live(current_chunk.strip())

#     print("\n")
#     history.append({"role": "assistant", "content": full_response})
#     save_conversation_history(history)

# # 🎙️ Voice input
# def listen_to_user():
#     recognizer = sr.Recognizer()
#     mic = sr.Microphone()

#     print("Listening for your command...")
#     with mic as source:
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#     try:
#         user_input = recognizer.recognize_google(audio)
#         print(f"You said: {user_input}")
#         return user_input
#     except sr.UnknownValueError:
#         print("Sorry, I could not understand that.")
#         return ""
#     except sr.RequestError:
#         print("Sorry, I’m having trouble with the speech recognition service.")
#         return ""

# # ▶️ Main
# if __name__ == "__main__":
#     print("Jarvis is online. At your service, Sir. \n")
#     speak_live("Jarvis is online. At your service, Sir.")

#     while True:
#         user_input = listen_to_user()

#         if user_input.lower() in ["exit", "quit"]:
#             speak_live("Goodbye, Sir.")
#             break

#         if user_input.lower() == "clear memory":
#             save_conversation_history([])
#             speak_live("Memory has been cleared, Sir.")
#             continue

#         if user_input != "":
#             chat_with_jarvis_streaming(user_input)
