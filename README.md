# Smart Email Assistant

A comprehensive AI-powered email management tool that integrates with Microsoft Outlook to provide intelligent email summarization, relevance filtering, and automated reply generation using local LLM (Ollama).

## 🚀 Features

- **Email Integration**: Seamless connection with Microsoft Outlook/Exchange
- **AI-Powered Summarization**: Automatic email content summarization using Ollama phi-3 mini
- **Relevance Filtering**: Intelligent spam and irrelevant email detection
- **Smart Reply Generation**: Context-aware reply drafting with conversation history
- **Live Email Monitoring**: Real-time processing of incoming emails
- **Modern UI**: Responsive React dashboard with beautiful animations
- **Reply Management**: In-app email composition and sending
- **Thread Context**: Maintains conversation context for better replies

## 🛠 Technology Stack

**Backend:**
- Flask (Python web framework)
- SQLite (Local database)
- Microsoft Graph API (Email integration)
- Ollama (Local LLM inference)

**Frontend:**
- React 18 (UI framework)
- Tailwind CSS (Styling)
- Framer Motion (Animations)
- Axios (API communication)

## 📋 Prerequisites

1. **Python 3.8+**
2. **Node.js 16+**
3. **Ollama** (for local AI inference)
4. **Microsoft Azure App Registration** (for Outlook API access)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart-email-assistant
```

### 2. Install Ollama and AI Model

```bash
# Install Ollama (visit https://ollama.ai for OS-specific instructions)
# For Linux/macOS:
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the phi-3 mini model
ollama pull phi3:mini

# Start Ollama service
ollama serve
```

### 3. Setup Microsoft Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "App registrations" → "New registration"
3. Configure:
   - **Name**: Smart Email Assistant
   - **Redirect URI**: `http://localhost:5000/auth/callback`
   - **Account types**: Accounts in any organizational directory and personal Microsoft accounts

4. Add API Permissions:
   - Microsoft Graph → Delegated permissions:
     - `Mail.Read`
     - `Mail.Send`
     - `Mail.ReadWrite`
     - `User.Read`

5. Generate Client Secret:
   - Go to "Certificates & secrets" → "New client secret"
   - Copy the secret value (you won't see it again!)

6. Note down:
   - Application (client) ID
   - Client secret value

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_SECRET_KEY=your_flask_secret_key_here

# Microsoft Azure Configuration
OUTLOOK_CLIENT_ID=your_azure_client_id_here
OUTLOOK_CLIENT_SECRET=your_azure_client_secret_here
REDIRECT_URI=http://localhost:5000/auth/callback
FRONTEND_URL=http://localhost:3000

# Optional: Ollama Configuration (defaults shown)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

### 5. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Install additional Tailwind CSS plugins
npm install -D @tailwindcss/typography @tailwindcss/forms @tailwindcss/aspect-ratio
```

## 🚀 Running the Application

### Start the Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

The backend will start on `http://localhost:5000`

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm start
```

The frontend will start on `http://localhost:3000`

### Ensure Ollama is Running (Terminal 3)

```bash
ollama serve
```

## 🎯 Usage Instructions

### First Time Setup

1. **Access the Application**: Open `http://localhost:3000`
2. **Connect Email**: Click "Sign in with Microsoft" to authenticate
3. **Verify Services**: Check that both Microsoft Auth and Ollama AI show green status
4. **Sync Emails**: Click "Sync Emails" to fetch and process recent emails
5. **Manage Emails**: View summaries, draft replies, and send responses

### Features Overview

#### Email Management
- **Dashboard View**: Grid or list view of processed emails
- **Filtering**: Filter by all emails, needs reply, or already replied
- **Search**: Search through email content, subjects, and senders
- **Real-time Updates**: Automatic processing of new incoming emails

#### AI Features
- **Relevance Detection**: Automatically filters out spam and irrelevant emails
- **Smart Summarization**: Bullet-point summaries of email content
- **Context-Aware Replies**: Generates professional replies considering conversation history
- **Reply Regeneration**: Generate new reply drafts if not satisfied

#### Email Actions
- **View Full Email**: Read complete email content with formatting
- **Edit Replies**: Modify AI-generated replies before sending
- **Send Replies**: Send responses directly from the application
- **Track Status**: Visual indicators for replied/unreplied emails

## 🔍 Troubleshooting

### Common Issues

1. **Ollama Not Running**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # If not running, start it
   ollama serve
   ```

2. **Authentication Errors**
   - Verify Azure app registration settings
   - Check redirect URI matches exactly
   - Ensure API permissions are granted and admin consented

3. **Email Sync Issues**
   - Check internet connection
   - Verify Microsoft Graph API permissions
   - Check browser console for detailed error messages

4. **AI Processing Slow**
   - Ollama performance depends on hardware
   - Consider using a smaller model for faster processing
   - Check system resources (CPU/RAM usage)

### Debug Mode

Enable debug logging by setting environment variables:

```bash
# Backend debugging
export FLASK_DEBUG=1
export FLASK_ENV=development

# Frontend debugging
export REACT_APP_DEBUG=1
```

## 📊 Performance Optimization

### Backend Optimization
- **Concurrent Processing**: Emails are processed in parallel using ThreadPoolExecutor
- **Database Indexing**: SQLite indexes on timestamp and reply status
- **Caching**: Email content caching to avoid re-processing

### Frontend Optimization
- **Lazy Loading**: Components load on demand
- **Virtual Scrolling**: Efficient handling of large email lists
- **Optimistic Updates**: UI updates immediately for better UX

## 🔒 Security Considerations

- **Local Storage**: All email data stored locally in SQLite
- **Token Security**: OAuth tokens stored in secure session storage
- **API Rate Limiting**: Respects Microsoft Graph API rate limits
- **Data Privacy**: No email data sent to external services (except Microsoft)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed description and logs


**Note**: This application processes emails locally using Ollama for maximum privacy and security. No email content is sent to external AI services.