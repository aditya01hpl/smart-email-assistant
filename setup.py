"""
Smart Email Assistant Setup Script
Automated setup and validation for the email assistant application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_node_version():
    """Check if Node.js is installed and version is 16+"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().replace('v', '')
            major_version = int(version.split('.')[0])
            if major_version >= 16:
                print(f"✅ Node.js {version} - OK")
                return True
            else:
                print(f"❌ Node.js 16+ required, found {version}")
                return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            phi3_found = any('phi3' in model['name'] for model in models)
            if phi3_found:
                print("✅ Ollama running with phi3 model - OK")
                return True
            else:
                print("⚠️ Ollama running but phi3 model not found")
                print("Run: ollama pull phi3:mini")
                return False
        else:
            print("❌ Ollama not responding")
            return False
    except Exception as e:
        print("❌ Ollama not running or not installed")
        print("Please install Ollama and run: ollama serve")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'FLASK_SECRET_KEY',
        'OUTLOOK_CLIENT_ID', 
        'OUTLOOK_CLIENT_SECRET',
        'REDIRECT_URI',
        'FRONTEND_URL'
    ]
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=" in content and not content.split(f"{var}=")[1].split('\n')[0].strip():
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file configured - OK")
    return True

def setup_backend():
    """Setup Python virtual environment and install dependencies"""
    print("\n🐍 Setting up Python backend...")
    
    backend_dir = Path('backend')
    if not backend_dir.exists():
        backend_dir.mkdir()
        print("📁 Created backend directory")
    
    # Create virtual environment
    venv_dir = backend_dir / 'venv'
    if not venv_dir.exists():
        print("🔨 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)])
    
    # Determine activation script based on OS
    if platform.system() == 'Windows':
        pip_path = venv_dir / 'Scripts' / 'pip'
        python_path = venv_dir / 'Scripts' / 'python'
    else:
        pip_path = venv_dir / 'bin' / 'pip'
        python_path = venv_dir / 'bin' / 'python'
    
    # Install dependencies
    dependencies = [
        'Flask==3.0.0',
        'Flask-CORS==4.0.0', 
        'requests==2.31.0',
        'python-dotenv==1.0.0'
    ]
    
    print("📦 Installing Python dependencies...")
    for dep in dependencies:
        result = subprocess.run([str(pip_path), 'install', dep], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to install {dep}")
            print(result.stderr)
            return False
    
    print("✅ Backend setup complete")
    return True

def setup_frontend():
    """Setup React frontend if it doesn't exist"""
    print("\n⚛️ Checking React frontend...")
    
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("🔨 Creating React app...")
        result = subprocess.run(['npx', 'create-react-app', 'frontend'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to create React app")
            print(result.stderr)
            return False
    
    # Install additional dependencies
    os.chdir('frontend')
    
    additional_deps = [
        'axios',
        'react-router-dom', 
        'react-icons',
        'framer-motion',
        'react-toastify',
        'react-loading-skeleton',
        'date-fns'
    ]
    
    dev_deps = [
        'tailwindcss',
        'autoprefixer', 
        'postcss',
        '@tailwindcss/typography',
        '@tailwindcss/forms',
        '@tailwindcss/aspect-ratio'
    ]
    
    print("📦 Installing React dependencies...")
    
    # Install regular dependencies
    result = subprocess.run(['npm', 'install'] + additional_deps,
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Failed to install React dependencies")
        print(result.stderr)
        os.chdir('..')
        return False
    
    # Install dev dependencies
    result = subprocess.run(['npm', 'install', '-D'] + dev_deps,
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Failed to install dev dependencies")
        print(result.stderr)
        os.chdir('..')
        return False
    
    # Initialize Tailwind
    result = subprocess.run(['npx', 'tailwindcss', 'init', '-p'],
                          capture_output=True, text=True)
    
    # Create necessary directories
    Path('src/components').mkdir(exist_ok=True)
    Path('src/services').mkdir(exist_ok=True)
    Path('src/styles').mkdir(exist_ok=True)
    
    os.chdir('..')
    print("✅ Frontend setup complete")
    return True

def validate_file_structure():
    """Validate that all necessary files are in place"""
    print("\n📁 Validating file structure...")
    
    required_files = {
        'backend/app.py': 'Main Flask application',
        'backend/email_service.py': 'Email service integration',
        'backend/ai_service.py': 'AI service integration',
        'backend/models.py': 'Database models',
        'backend/utils.py': 'Utility functions',
        'frontend/src/App.js': 'Main React component',
        'frontend/src/components/Dashboard.js': 'Dashboard component',
        'frontend/src/components/EmailCard.js': 'Email card component',
        'frontend/src/components/EmailModal.js': 'Email modal component',
        'frontend/src/components/Sidebar.js': 'Sidebar component',
        'frontend/src/services/api.js': 'API service',
        'frontend/src/styles/globals.css': 'Global styles',
        'frontend/tailwind.config.js': 'Tailwind configuration'
    }
    
    missing_files = []
    for file_path, description in required_files.items():
        if not Path(file_path).exists():
            missing_files.append(f"{file_path} ({description})")
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease copy the provided files to their correct locations.")
        return False
    
    print("✅ All required files present")
    return True

def main():
    """Main setup function"""
    print("🚀 Smart Email Assistant Setup")
    print("=" * 40)
    
    # System checks
    print("\n🔍 System Requirements Check:")
    checks = [
        check_python_version(),
        check_node_version(),
        check_env_file()
    ]
    
    if not all(checks):
        print("\n❌ Please fix the above issues before continuing")
        return False
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed")
        return False
    
    # Setup frontend  
    if not setup_frontend():
        print("\n❌ Frontend setup failed")
        return False
    
    # Validate file structure
    if not validate_file_structure():
        print("\n❌ File structure validation failed")
        return False
    
    # Final checks
    print("\n🔍 Service Status Check:")
    ollama_ok = check_ollama()
    
    print("\n" + "=" * 40)
    print("🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Ensure Ollama is running: ollama serve")
    if not ollama_ok:
        print("2. Pull AI model: ollama pull phi3:mini")
    print(f"3. Start backend: cd backend && {'venv\\Scripts\\activate' if platform.system() == 'Windows' else 'source venv/bin/activate'} && python app.py")
    print("4. Start frontend: cd frontend && npm start")
    print("5. Open http://localhost:3000 in your browser")
    
    print("\n💡 Tips:")
    print("- Check the README.md for detailed instructions")
    print("- Use two separate terminals for backend and frontend")
    print("- Ensure your Microsoft Azure app has correct redirect URI")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        print("Please check the error and try again")