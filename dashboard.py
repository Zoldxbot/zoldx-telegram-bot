from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

@app.route("/")
def home():
    users = load_users()

    total_users = len(users)
    total_balance = sum(u.get("balance", 0) for u in users.values())
    total_withdraw = sum(u.get("withdraw", 0) for u in users.values())

    return {
        "status": "ZoldX Dashboard Running",
        "total_users": total_users,
        "total_balance": total_balance,
        "total_withdraw_requested": total_withdraw
    }

@app.route("/users")
def all_users():
    return jsonify(load_users())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
