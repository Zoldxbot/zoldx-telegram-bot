import json
import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from web3 import Web3

# 🔐 BOT TOKEN
BOT_TOKEN = "8065897916:AAFaXXs2fQaYHz9XuYxnSbRtSJEb6zPR1z8"
ADMIN_ID = "8065897916"

DATA_FILE = "users.json"
DAY = 86400  # 24 hours

# 🌐 BSC TESTNET
w3 = Web3(Web3.HTTPProvider(
    "https://data-seed-prebsc-1-s1.binance.org:8545"
))

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

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "balance": 0,
            "airdrop_time": 0,
            "referrals": 0,
            "withdraw": 0,
            "wallet": ""
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
        "/balance - Check balance\n"
        "/airdrop - Daily free coins\n"
        "/invite - Referral link\n"
        "/setwallet <address>\n"
        "/verify - Faucet verification\n"
        "/leaderboard - Top users\n"
        "/withdraw amount"
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

    await update.message.reply_text("🎁 Daily airdrop received: +50 ZOLDX")

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    link = f"https://t.me/ZoldX_bot?start={uid}"
    await update.message.reply_text(
        f"👥 Invite friends & earn 20 ZOLDX:\n{link}"
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)[:10]
    msg = "🏆 TOP 10 HOLDERS\n\n"
    for i, (_, d) in enumerate(top, 1):
        msg += f"{i}. {d['balance']} ZOLDX\n"
    await update.message.reply_text(msg)

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if not context.args:
        await update.message.reply_text("❌ Use: /withdraw amount")
        return

    amount = int(context.args[0])
    u = get_user(uid)

    if amount > u["balance"]:
        await update.message.reply_text("❌ Insufficient balance")
        return

    u["balance"] -= amount
    u["withdraw"] += amount
    save_data(users)

    await update.message.reply_text(
        f"✅ Withdraw request sent: {amount} ZOLDX\nAdmin will review"
    )

# ---------- WALLET SYSTEM ----------

async def setwallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if not context.args:
        await update.message.reply_text(
            "❌ Use:\n/setwallet 0xABC..."
        )
        return

    wallet = context.args[0]
    users[uid]["wallet"] = wallet
    save_data(users)

    await update.message.reply_text("✅ Wallet saved")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    u = get_user(uid)

    if not u["wallet"]:
        await update.message.reply_text(
            "❌ First set wallet:\n/setwallet 0xABC..."
        )
        return

    balance = w3.eth.get_balance(u["wallet"])

    if balance > 0:
        u["balance"] += 200
        save_data(users)
        await update.message.reply_text(
            "✅ Faucet verified!\n+200 ZOLDX"
        )
    else:
        await update.message.reply_text(
            "❌ No testnet funds found"
        )

# ---------- ADMIN COMMANDS ----------

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    uid, amt = context.args
    get_user(uid)["balance"] += int(amt)
    save_data(users)
    await update.message.reply_text("✅ Coins added")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    uid, amt = context.args
    get_user(uid)["balance"] -= int(amt)
    save_data(users)
    await update.message.reply_text("❌ Coins removed")

# ---------- BOT START ----------

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("airdrop", airdrop))
app.add_handler(CommandHandler("invite", invite))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("setwallet", setwallet))
app.add_handler(CommandHandler("verify", verify))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("remove", remove))

app.run_polling()
