from app import mysql

def create_favorites_table():
    try:
        cur = mysql.connection.cursor()
        
        # Check if favorit_aset table exists
        cur.execute("SHOW TABLES LIKE 'favorit_aset'")
        if cur.fetchone():
            print("✅ favorit_aset table already exists")
        else:
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
                  KEY `aset_id` (`aset_id`),
                  KEY `user_id` (`user_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """)
            
            mysql.connection.commit()
            print("✅ favorit_aset table created successfully")
        
        cur.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating favorites table: {e}")
        return False

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        create_favorites_table()
