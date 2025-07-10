"""
Database Update Script for Edit Profile Feature
This script adds the necessary columns to the users table for the edit profile functionality.
"""

import mysql.connector
from config import Config

def update_database():
    """Add additional fields to users table"""
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        
        cursor = connection.cursor()
        
        # Check if columns already exist before adding them
        cursor.execute("DESCRIBE users")
        existing_columns = [column[0] for column in cursor.fetchall()]
        
        updates = []
        
        # Add phone column if not exists
        if 'phone' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT NULL")
            updates.append("phone")
        
        # Add company column if not exists  
        if 'company' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN company VARCHAR(100) DEFAULT NULL")
            updates.append("company")
        
        # Add address column if not exists
        if 'address' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT DEFAULT NULL")
            updates.append("address")
        
        # Add created_at column if not exists
        if 'created_at' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            updates.append("created_at")
        
        # Add updated_at column if not exists
        if 'updated_at' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            updates.append("updated_at")
        
        connection.commit()
        
        if updates:
            print(f"Successfully added columns: {', '.join(updates)}")
        else:
            print("All columns already exist. No updates needed.")
            
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_database()
