# 🎓 Quiz Master V2

## 📌 Overview

**Quiz Master V2** is a more advanced version of Quiz Master with the following features:

1. Full frontend built using **Vue CLI**
2. Robust **API communication**, caching, and performance optimization
3. **Background jobs**, including scheduled and user-triggered tasks
4. **JWT-based authentication** system
5. Clean and scalable **RESTful API** design

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/23f2002880/quiz_master_23f2002880.git
cd quiz-app/backend
```

---

### 2️⃣ Create & Activate a Virtual Environment (Skip if already using one)

#### 🪟 On Windows
```bash
python -m venv venv
Set-ExecutionPolicy Unrestricted -Scope Process   # If aliasing issue occurs
venv\Scripts\activate
```

#### 🐧 On macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies :

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Caching & Background Jobs Require Redis Server

#### 🪟 On Windows  
Use **WSL2** as Redis is Linux-native.

```bash
wsl --install
# Restart your computer if prompted
```

#### 🐧 On macOS/Linux  
Redis is natively supported.

---

### 5️⃣ Set Up Redis Server

```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo apt-get install net-tools
netstat -tl
```

> ✅ If `127.0.0.1:6379` is listening, Redis is running correctly.

---

### 6️⃣ Configure Email for SMTP Notifications

1. Visit [this link](https://support.google.com/accounts/answer/185833?hl=en)
2. Ensure **2-factor authentication** is enabled
3. Create an **App Password** (use `flask-app` as the app name)
4. Replace the generated password in `task.py`

```python
def send_email(sender,receiver, subject, message, attachment):
    #############
    smtp_password='<your_pass>'
```
5. Update all sender email addresses with your own


```python
@celApp.task
def send_monthly_summary():
        ################
              send_email("<your_email>",user.email, "📊 Your Monthly Quiz Summary Report", message,tmp_path)

```
---

### 7️⃣ Setup Scheduled Tasks (Optional / For Testing)

Modify `task.py`:

```python
@celApp.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=17, minute=11),
        send_unattempted_quiz_reminders.s()
    )
    sender.add_periodic_task(
        crontab(day_of_month=30, hour=17, minute=11),
        send_monthly_summary.s()
    )
```

> 🕒 Adjust `hour`, `minute`, and `day_of_month` as needed

---

### 8️⃣ Start the Backend (Use 3 Terminals with Activated Envs)

```bash
# Terminal 1
python app.py

# Terminal 2
celery -A task beat --loglevel=info

# Terminal 3
celery -A task worker --loglevel=info -P eventlet
```

---

### 9️⃣ Set Up the Frontend

1. Download & install Node.js from [nodejs.org](https://nodejs.org/en/download)
2. Restart your system
3. Open terminal and run:

```bash
cd quiz-app/frontend
npm install
npm install @vue/cli -g
vue serve
```

> 🔗 Open [http://localhost:8080/](http://localhost:8080/) to use the app

---

## 🔐 Credentials

### 🛡️ Admin Login
- **Username**: `admin`  
- **Password**: `1234`

### 👤 Dummy User
- **Username**: `user1`  
- **Password**: `user1`

---

## 🎉 Features

- 📬 You’ll receive emails for reminders and summaries
- 📦 You can **export CSV** after attempting at least one quiz
- ⚡ API responses are **cached** using Redis
- 🖥️ Enjoy a full **Single Page Application (SPA)** experience!

---