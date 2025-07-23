#!/usr/bin/env python3
"""
Startup script for Smart ATS Flask API with enhanced error checking
"""
import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("Example .env file:")
        print("GOOGLE_API_KEY=your_google_api_key_here")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'google.generativeai',
        'PyPDF2',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def test_gemini_connection():
    """Test connection to Gemini API"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Test with Gemini 2.0
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Test connection. Respond with 'OK'.")
        
        if response.text:
            print("✅ Gemini 2.0 API connection successful")
            return True
        else:
            print("❌ Gemini 2.0 API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini 2.0 API connection failed: {e}")
        print("   Check your GOOGLE_API_KEY and internet connection")
        return False

def start_server():
    """Start the Flask server"""
    try:
        print("🚀 Starting Smart ATS Flask API...")
        print("   Server will be available at: http://localhost:5000")
        print("   Health check: http://localhost:5000/")
        print("   API endpoint: http://localhost:5000/analyze")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 50)
        
        # Import and run the Flask app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main startup function"""
    print("🔧 Smart ATS API Startup Check")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Test Gemini connection
    if not test_gemini_connection():
        print("\n⚠️  Gemini API test failed, but starting server anyway...")
        print("   The server will start but AI analysis may not work")
    
    print("\n" + "=" * 40)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
