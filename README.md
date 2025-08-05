# 📧 Smart Email Assistant

**Smart Email Assistant** is a fully local AI-powered tool that helps you manage your Outlook inbox more efficiently. It summarizes emails, filters out irrelevant ones, scores urgency, and even drafts replies for you — all **locally** on your machine using [Ollama](https://ollama.ai/). **No internet or external API calls are used for AI tasks** — your data stays 100% private.

---

## 🎥 Demo

You can check the demo video of this project here:

[Watch the demo video on Google Drive](https://drive.google.com/drive/folders/1YWAP6Ytd4UMt-jveZq9M1BHgpgqEo0iY?usp=sharing)

---

## 🔑 Why Local?

Unlike other email tools, **Smart Email Assistant runs entirely on your device**:
- Uses [Ollama](https://ollama.ai/) to run LLMs locally
- No email content ever leaves your machine
- Perfect for privacy-conscious individuals and enterprises

---

## 🚀 Key Features

- ✅ **Microsoft Outlook Integration**  
- 🧠 **AI Summarization** with `phi-3-mini` (or any Ollama-supported model)  
- 🗂️ **Inbox Relevance Scoring**: Filters out spam and low-priority emails  
- ✍️ **Smart Reply Drafts**: Context-aware replies using thread history  
- 🔁 **Live Monitoring**: Processes emails as they arrive  
- 📊 **Modern UI**: Clean, responsive React dashboard with Tailwind CSS  
- 📤 **In-App Reply & Send**  
- 🧵 **Conversation Context Handling**

---

## ⚙️ Tech Stack

**Backend**
- Flask (Python)
- SQLite
- Microsoft Graph API
- Ollama (LLM Inference)

**Frontend**
- React 18
- Tailwind CSS
- Framer Motion (Animations)
- Axios

---

## 📦 Requirements

- Python 3.8+
- Node.js 16+
- Ollama
- Microsoft Azure App Registration

---

## 🧪 Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourname/smart-email-assistant.git
cd smart-email-assistant
```

### 2. Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull phi3:mini
ollama serve
```

### 3. Setup Azure App Registration

- Go to [Azure Portal](https://portal.azure.com)
- Register a new app and note down:
  - Client ID
  - Client Secret
  - Redirect URI: `http://localhost:5000/auth/callback`
- Add Graph API permissions:
  - `Mail.Read`, `Mail.Send`, `Mail.ReadWrite`, `User.Read`

### 4. Configure Environment

Create `.env` in project root:

```env
# Flask
FLASK_SECRET_KEY=your_secret

# Microsoft Graph
OUTLOOK_CLIENT_ID=xxxxx
OUTLOOK_CLIENT_SECRET=xxxxx
REDIRECT_URI=http://localhost:5000/auth/callback

# Frontend
FRONTEND_URL=http://localhost:3000

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

---

## ⚙️ Running Locally

### Backend (Terminal 1)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

### Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run start
```

### Ollama (Terminal 3)

```bash
ollama serve
```

---

## 🧭 How to Use

1. Open `http://localhost:3000`
2. Sign in with Microsoft
3. Allow Graph API permissions
4. Start syncing emails
5. Use the dashboard to manage, summarize, and reply

---

## 🔍 Troubleshooting

- **Ollama not responding** → Run `ollama serve`
- **Microsoft auth fails** → Check redirect URI and API permissions
- **Slow AI generation** → Try smaller model or close unused apps

---

## 💡 Tips

- Set `OLLAMA_MODEL=llama3:8b` or another supported model for more advanced replies (if your hardware allows).
- Customize filters or scoring logic in `backend/email_processing.py`.

---

## 🔐 Privacy First

Your emails are:
- Stored locally in SQLite
- Processed entirely offline by Ollama
- Never sent to any third-party servers

> ✅ **Data privacy is a first-class citizen in this app.**

---

## 🧩 Contributing

PRs are welcome! Here’s how:

```bash
git checkout -b feature/my-new-feature
git commit -am "Add some feature"
git push origin feature/my-new-feature
```

Then open a Pull Request.

---

## 📄 License

[MIT License](LICENSE)
