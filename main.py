import json
import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = "8293542167"  # 👈 اپنی Telegram ID

DATA_FILE = "users.json"
DAY = 86400

# ---------- DATABASE ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

users = load_data()

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "balance": 0,
            "airdrop_time": 0,
            "referrals": 0,
            "withdraw": 0
        }
    return users[uid]

# ---------- USER COMMANDS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    get_user(uid)

    if context.args:
        ref = context.args[0]
        if ref in users and ref != uid:
            users[ref]["balance"] += 20
            users[ref]["referrals"] += 1

    save_data(users)

    await update.message.reply_text(
        "🚀 ZoldX Coin Bot\n\n"
        "/balance\n"
        "/airdrop\n"
        "/invite\n"
        "/leaderboard\n"
        "/withdraw <amount>"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(str(update.effective_user.id))
    await update.message.reply_text(f"💰 Balance: {u['balance']} ZOLDX")

async def airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    u = get_user(uid)
    now = time.time()

    if now - u["airdrop_time"] < DAY:
        left = int((DAY - (now - u["airdrop_time"])) / 3600)
        await update.message.reply_text(f"⏳ Next airdrop in {left} hours")
        return

    u["balance"] += 50
    u["airdrop_time"] = now
    save_data(users)

    await update.message.reply_text("🎁 +50 ZOLDX added")

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    link = f"https://t.me/YOUR_BOT_USERNAME?start={uid}"
    await update.message.reply_text(f"👥 Invite link:\n{link}")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)[:10]
    msg = "🏆 TOP 10 USERS\n\n"
    for i, (_, d) in enumerate(top, 1):
        msg += f"{i}. {d['balance']} ZOLDX\n"
    await update.message.reply_text(msg)

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ /withdraw amount")
        return

    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("❌ Amount must be number")
        return

    uid = str(update.effective_user.id)
    u = get_user(uid)

    if amount > u["balance"]:
        await update.message.reply_text("❌ Not enough balance")
        return

    u["balance"] -= amount
    u["withdraw"] += amount
    save_data(users)

    await update.message.reply_text("✅ Withdraw request sent")

# ---------- ADMIN ----------

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    if len(context.args) != 2:
        await update.message.reply_text("/add user_id amount")
        return

    uid, amt = context.args
    get_user(uid)["balance"] += int(amt)
    save_data(users)
    await update.message.reply_text("✅ Added")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    if len(context.args) != 2:
        await update.message.reply_text("/remove user_id amount")
        return

    uid, amt = context.args
    get_user(uid)["balance"] -= int(amt)
    save_data(users)
    await update.message.reply_text("❌ Removed")

# ---------- START BOT ----------

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("airdrop", airdrop))
app.add_handler(CommandHandler("invite", invite))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("remove", remove))

print("Bot Started Successfully")
app.run_polling()
