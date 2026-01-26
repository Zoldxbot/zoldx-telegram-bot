from flask import Flask, render_template
import json

app = Flask(__name__)

def load_data():
    with open("users.json", "r") as f:
        return json.load(f)

@app.route("/")
def dashboard():
    users = load_data()
    total_users = len(users)
    top = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)[:10]
    return render_template(
        "index.html",
        total_users=total_users,
        top=top
    )

app.run(host="0.0.0.0", port=8080)
