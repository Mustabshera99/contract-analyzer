"""
Create shareable links using ngrok tunneling
"""
from pyngrok import ngrok
import requests
import time

def create_shareable_links():
    print("🌐 Creating shareable links...")
    
    # Create tunnels
    try:
        # Frontend tunnel
        frontend_tunnel = ngrok.connect(8501, "http")
        frontend_url = frontend_tunnel.public_url
        
        # Backend tunnel  
        backend_tunnel = ngrok.connect(8000, "http")
        backend_url = backend_tunnel.public_url
        
        print("✅ Shareable links created!")
        print("=" * 50)
        print(f"🎨 Frontend (Main App): {frontend_url}")
        print(f"⚙️  Backend API: {backend_url}")
        print(f"📚 API Docs: {backend_url}/docs")
        print("=" * 50)
        print("📤 Share these links with anyone on the internet!")
        print("⏰ Links will remain active while this script runs.")
        print("🛑 Press Ctrl+C to stop sharing")
        
        # Keep running
        try:
            while True:
                time.sleep(60)
                print("🔄 Tunnels still active...")
        except KeyboardInterrupt:
            print("\n🛑 Stopping tunnels...")
            ngrok.disconnect(frontend_tunnel.public_url)
            ngrok.disconnect(backend_tunnel.public_url)
            print("✅ Tunnels stopped.")
            
    except Exception as e:
        print(f"❌ Error creating tunnels: {e}")
        print("💡 Make sure ngrok is installed and both services are running")

if __name__ == "__main__":
    create_shareable_links()