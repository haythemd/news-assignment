import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import httpx
        import pydantic
        import cachetools
        from dotenv import load_dotenv
        print("All requirements are installed")
        return True
    except ImportError as e:
        print(f"Missing requirement: {e}")
        print("Please run: python3 pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path(".env")
    if not env_file.exists():
        print(" No .env file found")
        print("Please create .env file with your GNEWS_API_KEY")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("GNEWS_API_KEY"):
        print("GNEWS_API_KEY not found in .env file")
        print("Please add your GNews API key to .env file")
        return False
    
    print("Environment is properly configured")
    return True

def main():
    """Main function"""
    print("Starting News API Service...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    env_ok = check_env_file()
    if not env_ok:
        print("\n Service will start but Need valid API key to fetch News")
    
    print("\nAPI Documentation is available at:")
    port = os.getenv("PORT", "8000")
    print(f"   • Swagger UI: http://localhost:{port}/docs")
    print(f"   • ReDoc: http://localhost:{port}/redoc")
    print(f"   • Health Check: http://localhost:{port}/health")
        
    # Import and run the app
    import uvicorn
    from main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(port),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )

if __name__ == "__main__":
    main()