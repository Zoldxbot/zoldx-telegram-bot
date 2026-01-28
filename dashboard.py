from flask import Flask, request, render_template_string, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_123_change_kar_den"   # ← yeh change kar dena production mein

DATA_FILE = "users.json"
ADMIN_PASSWORD = "admin1234"   # ← yeh bhi change kar dena (ya environment variable bana dena)

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ----------------- HTML Templates (simple inline) -----------------

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Admin Login</title></head>
<body>
    <h2>Admin Login</h2>
    <form method="post">
        Password: <input type="password" name="password">
        <input type="submit" value="Login">
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ZoldX Admin Dashboard</title>
    <style>table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid black; padding: 8px; }</style>
</head>
<body>
    <h1>ZoldX Admin Dashboard</h1>
    <p><a href="{{ url_for('logout') }}">Logout</a></p>
    
    <h2>All Users</h2>
    <table>
        <tr>
            <th>User ID</th>
            <th>Balance</th>
            <th>Referrals</th>
            <th>Wallet</th>
            <th>Action</th>
        </tr>
        {% for uid, data in users.items() %}
        <tr>
            <td>{{ uid }}</td>
            <td>{{ data.balance }}</td>
            <td>{{ data.referrals }}</td>
            <td>{{ data.wallet }}</td>
            <td>
                <form action="{{ url_for('update_balance') }}" method="post" style="display:inline;">
                    <input type="hidden" name="uid" value="{{ uid }}">
                    New Balance: <input type="number" name="balance" value="{{ data.balance }}" style="width:80px;">
                    <input type="submit" value="Update">
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_PAGE, error="Wrong password!")
    return render_template_string(LOGIN_PAGE)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    users = load_users()
    return render_template_string(DASHBOARD_PAGE, users=users)

@app.route('/update_balance', methods=['POST'])
def update_balance():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    uid = request.form.get('uid')
    try:
        new_balance = int(request.form.get('balance'))
        users = load_users()
        if uid in users:
            users[uid]['balance'] = new_balance
            save_users(users)
    except:
        pass  # silent fail for now
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
