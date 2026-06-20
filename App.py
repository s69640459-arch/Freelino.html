from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

# ================= DB =================
def db():
    return sqlite3.connect("data.db")


def init_db():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        phone TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        plan INTEGER,
        messages INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        owner TEXT,
        category TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        text TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ================= USER =================
def get_user():
    try:
        return open("user.txt").read().split("|")[0]
    except:
        return "guest"


def set_user(phone):
    with open("user.txt", "w") as f:
        f.write(phone)


def get_role(phone):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE phone=?", (phone,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else "guest"


def get_plan(phone):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT plan FROM users WHERE phone=?", (phone,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def get_limit(plan):
    limits = {
        0: 20,
        1: 35,
        2: 45,
        3: 60,
        4: 80,
        5: 120,
        6: 999
    }
    return limits.get(plan, 20)


# ================= TEMPLATE =================
page = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>Freelino Ultimate</title>

<style>
body{background:#0b1220;color:white;font-family:tahoma;margin:0}
header{background:#111827;padding:15px;text-align:center;font-size:18px}
a{color:#38bdf8;margin:10px;text-decoration:none}
.card{background:#1f2937;margin:15px;padding:15px;border-radius:12px}
input,select,button{width:90%;padding:10px;margin:5px;border-radius:8px;border:none}
button{background:#22c55e;cursor:pointer}
.badge{background:#334155;padding:5px 10px;border-radius:8px;display:inline-block}
</style>

</head>

<body>

<header>
🚀 Freelino Ultimate | {{user}} | {{role}} | پلن: {{plan}} | محدودیت: {{limit}}
</header>

<div class="card">
<a href="/">خانه</a>
<a href="/panel">پنل</a>
<a href="/register">ثبت نام</a>
<a href="/login">ورود</a>
<a href="/projects">پروژه‌ها</a>
<a href="/chat">چت</a>
</div>

<div class="card">
{{content|safe}}
</div>

</body>
</html>
"""

# ================= HOME =================
@app.route("/")
def home():
    user = get_user()
    role = get_role(user)
    plan = get_plan(user)

    return render_template_string(
        page,
        user=user,
        role=role,
        plan=plan,
        limit=get_limit(plan),
        content="🔥 سیستم فریلنسری فعال است"
    )

# ================= PANEL =================
@app.route("/panel")
def panel():

    user = get_user()
    role = get_role(user)
    plan = get_plan(user)

    if role == "freelancer":
        content = """
        <h2>👨‍💻 پنل فریلنسر</h2>
        <div class="badge">پروژه‌های پیشنهادی</div>
        <p>اینجا بعداً پروژه‌های مرتبط با مهارت‌ها نمایش داده می‌شود</p>
        """

    elif role == "client":
        content = """
        <h2>🧑‍💼 پنل کارفرما</h2>
        <div class="badge">ساخت پروژه</div>
        <p>اینجا پروژه ثبت می‌کنی و فریلنسرها پیشنهاد می‌دهند</p>
        """

    else:
        content = "<h2>اول وارد شو</h2>"

    return render_template_string(page,
        user=user,
        role=role,
        plan=plan,
        limit=get_limit(plan),
        content=content
    )

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]
        role = request.form["role"]

        conn = db()
        c = conn.cursor()

        c.execute("""
        INSERT OR REPLACE INTO users VALUES(?,?,?,?,?)
        """, (phone, password, role, 0, 20))

        conn.commit()
        conn.close()

        return redirect("/login")


    form = """
    <h2>ثبت نام</h2>
    <form method="POST">
    <input name="phone" placeholder="شماره"><br>
    <input name="password" type="password"><br>

    <select name="role">
        <option value="freelancer">فریلنسر</option>
        <option value="client">کارفرما</option>
    </select>

    <button>ثبت</button>
    </form>
    """

    return render_template_string(page,
        user=get_user(),
        role="guest",
        plan=0,
        limit=20,
        content=form
    )

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]

        conn = db()
        c = conn.cursor()

        c.execute("""
        SELECT * FROM users WHERE phone=? AND password=?
        """, (phone, password))

        user = c.fetchone()
        conn.close()

        if user:
            set_user(phone)
            return redirect("/panel")

    form = """
    <h2>ورود</h2>
    <form method="POST">
    <input name="phone"><br>
    <input name="password" type="password"><br>
    <button>ورود</button>
    </form>
    """

    return render_template_string(page,
        user=get_user(),
        role="guest",
        plan=0,
        limit=20,
        content=form
    )

# ================= PROJECTS =================
@app.route("/projects", methods=["GET","POST"])
def projects():

    user = get_user()

    conn = db()
    c = conn.cursor()

    if request.method == "POST":
        c.execute("""
        INSERT INTO projects(title, owner, category)
        VALUES(?,?,?)
        """, (request.form["title"], user, "general"))
        conn.commit()

    c.execute("SELECT * FROM projects")
    data = c.fetchall()
    conn.close()

    html = """
    <h2>📌 پروژه‌ها</h2>

    <form method="POST">
    <input name="title" placeholder="عنوان پروژه"><br>
    <button>ثبت</button>
    </form>
    <hr>
    """

    for p in data:
        html += f"<div>📌 {p[1]} | 👤 {p[2]} | 🏷 {p[3]}</div><hr>"

    return render_template_string(page,
        user=user,
        role=get_role(user),
        plan=get_plan(user),
        limit=get_limit(get_plan(user)),
        content=html
    )

# ================= CHAT =================
@app.route("/chat", methods=["GET","POST"])
def chat():

    sender = get_user()
    plan = get_plan(sender)

    conn = db()
    c = conn.cursor()

    if request.method == "POST":

        c.execute("""
        INSERT INTO messages(sender,receiver,text)
        VALUES(?,?,?)
        """, (sender, request.form["receiver"], request.form["text"]))

        conn.commit()

    c.execute("SELECT * FROM messages")
    msgs = c.fetchall()
    conn.close()

    html = """
    <h2>💬 چت سیستم</h2>

    <form method="POST">
    <input name="receiver" placeholder="گیرنده"><br>
    <input name="text" placeholder="پیام"><br>
    <button>ارسال</button>
    </form>
    <hr>
    """

    for m in msgs:
        html += f"<div>💬 {m[1]} ➜ {m[2]} : {m[3]}</div><hr>"

    return render_template_string(page,
        user=sender,
        role=get_role(sender),
        plan=plan,
        limit=get_limit(plan),
        content=html
    )

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

# ================= DB =================
def db():
    return sqlite3.connect("data.db")


def init_db():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        phone TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        plan INTEGER,
        messages INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        owner TEXT,
        category TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        text TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ================= USER =================
def get_user():
    try:
        return open("user.txt").read().split("|")[0]
    except:
        return "guest"


def set_user(phone):
    with open("user.txt", "w") as f:
        f.write(phone)


def get_role(phone):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE phone=?", (phone,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else "guest"


def get_plan(phone):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT plan FROM users WHERE phone=?", (phone,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def get_limit(plan):
    limits = {
        0: 20,
        1: 35,
        2: 45,
        3: 60,
        4: 80,
        5: 120,
        6: 999
    }
    return limits.get(plan, 20)


# ================= TEMPLATE =================
page = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>Freelino Ultimate</title>

<style>
body{background:#0b1220;color:white;font-family:tahoma;margin:0}
header{background:#111827;padding:15px;text-align:center;font-size:18px}
a{color:#38bdf8;margin:10px;text-decoration:none}
.card{background:#1f2937;margin:15px;padding:15px;border-radius:12px}
input,select,button{width:90%;padding:10px;margin:5px;border-radius:8px;border:none}
button{background:#22c55e;cursor:pointer}
.badge{background:#334155;padding:5px 10px;border-radius:8px;display:inline-block}
</style>

</head>

<body>

<header>
🚀 Freelino Ultimate | {{user}} | {{role}} | پلن: {{plan}} | محدودیت: {{limit}}
</header>

<div class="card">
<a href="/">خانه</a>
<a href="/panel">پنل</a>
<a href="/register">ثبت نام</a>
<a href="/login">ورود</a>
<a href="/projects">پروژه‌ها</a>
<a href="/chat">چت</a>
</div>

<div class="card">
{{content|safe}}
</div>

</body>
</html>
"""

# ================= HOME =================
@app.route("/")
def home():
    user = get_user()
    role = get_role(user)
    plan = get_plan(user)

    return render_template_string(
        page,
        user=user,
        role=role,
        plan=plan,
        limit=get_limit(plan),
        content="🔥 سیستم فریلنسری فعال است"
    )

# ================= PANEL =================
@app.route("/panel")
def panel():

    user = get_user()
    role = get_role(user)
    plan = get_plan(user)

    if role == "freelancer":
        content = """
        <h2>👨‍💻 پنل فریلنسر</h2>
        <div class="badge">پروژه‌های پیشنهادی</div>
        <p>اینجا بعداً پروژه‌های مرتبط با مهارت‌ها نمایش داده می‌شود</p>
        """

    elif role == "client":
        content = """
        <h2>🧑‍💼 پنل کارفرما</h2>
        <div class="badge">ساخت پروژه</div>
        <p>اینجا پروژه ثبت می‌کنی و فریلنسرها پیشنهاد می‌دهند</p>
        """

    else:
        content = "<h2>اول وارد شو</h2>"

    return render_template_string(page,
        user=user,
        role=role,
        plan=plan,
        limit=get_limit(plan),
        content=content
    )

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]
        role = request.form["role"]

        conn = db()
        c = conn.cursor()

        c.execute("""
        INSERT OR REPLACE INTO users VALUES(?,?,?,?,?)
        """, (phone, password, role, 0, 20))

        conn.commit()
        conn.close()

        return redirect("/login")


    form = """
    <h2>ثبت نام</h2>
    <form method="POST">
    <input name="phone" placeholder="شماره"><br>
    <input name="password" type="password"><br>

    <select name="role">
        <option value="freelancer">فریلنسر</option>
        <option value="client">کارفرما</option>
    </select>

    <button>ثبت</button>
    </form>
    """

    return render_template_string(page,
        user=get_user(),
        role="guest",
        plan=0,
        limit=20,
        content=form
    )

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]

        conn = db()
        c = conn.cursor()

        c.execute("""
        SELECT * FROM users WHERE phone=? AND password=?
        """, (phone, password))

        user = c.fetchone()
        conn.close()

        if user:
            set_user(phone)
            return redirect("/panel")

    form = """
    <h2>ورود</h2>
    <form method="POST">
    <input name="phone"><br>
    <input name="password" type="password"><br>
    <button>ورود</button>
    </form>
    """

    return render_template_string(page,
        user=get_user(),
        role="guest",
        plan=0,
        limit=20,
        content=form
    )

# ================= PROJECTS =================
@app.route("/projects", methods=["GET","POST"])
def projects():

    user = get_user()

    conn = db()
    c = conn.cursor()

    if request.method == "POST":
        c.execute("""
        INSERT INTO projects(title, owner, category)
        VALUES(?,?,?)
        """, (request.form["title"], user, "general"))
        conn.commit()

    c.execute("SELECT * FROM projects")
    data = c.fetchall()
    conn.close()

    html = """
    <h2>📌 پروژه‌ها</h2>

    <form method="POST">
    <input name="title" placeholder="عنوان پروژه"><br>
    <button>ثبت</button>
    </form>
    <hr>
    """

    for p in data:
        html += f"<div>📌 {p[1]} | 👤 {p[2]} | 🏷 {p[3]}</div><hr>"

    return render_template_string(page,
        user=user,
        role=get_role(user),
        plan=get_plan(user),
        limit=get_limit(get_plan(user)),
        content=html
    )

# ================= CHAT =================
@app.route("/chat", methods=["GET","POST"])
def chat():

    sender = get_user()
    plan = get_plan(sender)

    conn = db()
    c = conn.cursor()

    if request.method == "POST":

        c.execute("""
        INSERT INTO messages(sender,receiver,text)
        VALUES(?,?,?)
        """, (sender, request.form["receiver"], request.form["text"]))

        conn.commit()

    c.execute("SELECT * FROM messages")
    msgs = c.fetchall()
    conn.close()

    html = """
    <h2>💬 چت سیستم</h2>

    <form method="POST">
    <input name="receiver" placeholder="گیرنده"><br>
    <input name="text" placeholder="پیام"><br>
    <button>ارسال</button>
    </form>
    <hr>
    """

    for m in msgs:
        html += f"<div>💬 {m[1]} ➜ {m[2]} : {m[3]}</div><hr>"

    return render_template_string(page,
        user=sender,
        role=get_role(sender),
        plan=plan,
        limit=get_limit(plan),
        content=html
    )

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
