import os
import logging
import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging ko enable karte hain
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- API Keys ---
# BEST PRACTICE: Hamesha environment variables use karo
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8482963758:AAG9XsJhAtz0MVxqRVMbOi1RZeaGhlSLRgs")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBdRvrWUyo92_ASnu4PSybtveBRtJ-CtJo")

if not TELEGRAM_BOT_TOKEN or not GOOGLE_API_KEY:
    raise ValueError("TELEGRAM_BOT_TOKEN ya GOOGLE_API_KEY environment variable set nahi hai! Bot nahi chal sakta.")

# --- Gemini AI Model Setup ---
genai.configure(api_key=GOOGLE_API_KEY)
# Hum latest 'gemini-2.0-flash' model use karenge jo text ke liye accha hai
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Jab user /start command run karta hai."""
    user = update.effective_user
    await update.message.reply_html(
        f"Assalam-o-Alaikum {user.mention_html()}! 🤖\n\n"
        f"Main aapka AI Assistant hoon. Mujhe koi bhi sawaal poochiye ya koi bhi baat kariye, main aapki madad karunga."
    )
    logger.info(f"User {user.full_name} ({user.id}) ne AI Assistant bot start kiya.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help message dikhata hai."""
    await update.message.reply_text("Mujhe seedha koi bhi message bhejiye, main apne AI dimaag se jawab dunga! 😉")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User ka message receive karke Gemini se jawab leta hai."""
    user_message = update.message.text
    user = update.effective_user
    
    # User ko ye pata lagaye ki bot soch raha hai (typing action)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    logger.info(f"Message from {user.full_name} ({user.id}): {user_message}")

    try:
        # Gemini se jawab mang rahe hain
        response = model.generate_content(user_message)
        ai_response = response.text
        
        # Jawab ko user ko bhej rahe hain
        await update.message.reply_text(ai_response)
        logger.info(f"AI Response to {user.full_name}: {ai_response[:100]}...") # Log mein sirf 100 characters

    except Exception as e:
        # Koi error aaye toh user ko bataayein
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text("Sorry, mujhe abhi jawab nahi mil paaya. Thori der baar phir try kijiye. 🙏")

def main() -> None:
    """Bot ko start karne ka main function."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers ko add karte hain
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Koi bhi text message ke liye (commands ko chhod kar)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bot ko polling mode mein start karte hain
    application.run_polling()

if __name__ == "__main__":
    main()