import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔴 BOT TOKEN (Already Added)
BOT_TOKEN = "8065897916:AAEirR0VhKkCiYurHD2p_NW75oqMXCGKqBU"

DATA_FILE = "users.json"

# ---------- DATABASE ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

users = load_data()

# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "airdrop": False,
            "referrals": 0
        }

        # Referral check
        if context.args:
            ref_id = context.args[0]
            if ref_id in users and ref_id != user_id:
                users[ref_id]["balance"] += 20
                users[ref_id]["referrals"] += 1

    save_data(users)

    await update.message.reply_text(
        "🚀 Welcome to ZoldX Coin Bot\n\n"
        "Commands:\n"
        "/balance - Check balance\n"
        "/airdrop - Free coins (1 time)\n"
        "/invite - Get referral link"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bal = users.get(user_id, {}).get("balance", 0)
    await update.message.reply_text(f"💰 Your balance: {bal} ZOLDX")

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if users[user_id]["airdrop"]:
        await update.message.reply_text("❌ Airdrop already claimed!")
        return

    users[user_id]["balance"] += 100
    users[user_id]["airdrop"] = True
    save_data(users)

    await update.message.reply_text("🎁 Airdrop claimed! +100 ZOLDX")

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    link = f"https://t.me/ZoldX_bot?start={user_id}"
    await update.message.reply_text(
        f"👥 Invite friends & earn 20 ZOLDX each!\n\n{link}"
    )

# ---------- BOT SETUP ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("airdrop", airdrop))
app.add_handler(CommandHandler("invite", invite))

app.run_polling()
