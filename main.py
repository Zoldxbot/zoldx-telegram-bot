from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ✅ BOT TOKEN DIRECTLY ADDED
BOT_TOKEN = "8065897916:AAEirR0VhKkCiYurHD2p_NW75oqMXCGKqBU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Welcome to ZoldX Coin Bot\n\n"
        "Available Commands:\n"
        "/balance - Check your balance\n"
        "/airdrop - Get free coins"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Your balance: 100 ZOLDX")

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎁 Airdrop successful! +50 ZOLDX")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("airdrop", airdrop))

app.run_polling()
