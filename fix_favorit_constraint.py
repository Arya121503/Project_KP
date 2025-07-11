from app import create_app
app = create_app()
from app import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    try:
        # Check if the table exists first
        cur.execute("SHOW TABLES LIKE 'favorit_aset'")
        table_exists = cur.fetchone()
        
        if table_exists:
            print("✅ favorit_aset table exists, checking constraints...")
            
            # Get the foreign key constraints
            cur.execute("""
                SELECT 
                    TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE
                    REFERENCED_TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'favorit_aset'
            """)
            
            constraints = cur.fetchall()
            print("Current foreign key constraints:")
            for constraint in constraints:
                print(f"- {constraint[2]} references {constraint[3]}.{constraint[4]} from {constraint[0]}.{constraint[1]}")
            
            # If there's a constraint to aset_sewa, drop it
            for constraint in constraints:
                if constraint[3] == 'aset_sewa':
                    print(f"\nDropping constraint {constraint[2]}...")
                    cur.execute(f"ALTER TABLE favorit_aset DROP FOREIGN KEY {constraint[2]}")
                    mysql.connection.commit()
                    print(f"✅ Constraint {constraint[2]} dropped successfully")
            
            print("\nUpdating favorit_aset table structure...")
            # Drop the unique constraint if it exists (it probably has the FK constraint)
            try:
                cur.execute("ALTER TABLE favorit_aset DROP INDEX user_aset_idx")
                mysql.connection.commit()
                print("✅ Dropped unique constraint user_aset_idx")
            except:
                print("No unique constraint to drop or already dropped")
            
            print("Table structure updated successfully")
            
        else:
            print("❌ favorit_aset table does not exist, creating...")
            # Create favorit_aset table
            cur.execute("""
                CREATE TABLE `favorit_aset` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `user_id` int NOT NULL,
                  `aset_id` int NOT NULL,
                  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `catatan` text,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `user_aset_idx` (`user_id`, `aset_id`),
                  KEY `user_id` (`user_id`),
                  CONSTRAINT `favorit_aset_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """)
            mysql.connection.commit()
            print("✅ favorit_aset table created successfully without FK constraint to aset_sewa")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        cur.close()
