#!/usr/bin/env python3
"""
FINAL LAUNCHER - Telkom Property Prediction System
One-click solution untuk menjalankan aplikasi
"""
import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("="*60)
    print("🏢 TELKOM PROPERTY PREDICTION SYSTEM")
    print("🚀 FINAL LAUNCHER")
    print("="*60)
    
    print("\n📋 Status Check:")
    
    # 1. Check Python environment
    print("✅ Python environment: Active")
    
    # 2. Check database
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='db_kp',
            connection_timeout=3
        )
        connection.close()
        print("✅ Database: Connected")
    except:
        print("❌ Database: Not connected")
        print("💡 Make sure MySQL/XAMPP is running")
        input("Press Enter after starting MySQL, or Ctrl+C to exit...")
        return
    
    # 3. Check dependencies
    try:
        import flask
        import pandas
        import sklearn
        print("✅ Dependencies: Installed")
    except ImportError as e:
        print(f"❌ Dependencies: Missing {e}")
        return
    
    print("\n🎉 All systems ready!")
    print("\n🚀 Starting application...")
    print("📍 URL: http://localhost:5000")
    print("🔑 Admin Login: admin@telkom.co.id / admin123")
    print("\n" + "="*50)
    
    # Start the application
    try:
        # Open browser after a delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run Flask app
        from app import create_app
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running: python setup_database_fixed.py")

if __name__ == "__main__":
    main()
