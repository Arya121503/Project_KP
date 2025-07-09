#!/usr/bin/env python3
"""
Script untuk inisialisasi database dengan context Flask
"""

from app import create_app
from app.database import init_mysql_db

def main():
    app = create_app()
    with app.app_context():
        init_mysql_db()
        print("Database initialization completed!")

if __name__ == "__main__":
    main()
