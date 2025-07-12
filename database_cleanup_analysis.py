#!/usr/bin/env python3
"""
Database cleanup analysis script
Analyzes which tables are actually used in the application
"""

import mysql.connector
from config import Config
import os
import re

def analyze_database_usage():
    """Analyze database table usage in the application"""
    
    # Connect to database
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute('SHOW TABLES')
        tables = [table[0] for table in cursor.fetchall()]
        
        print("DATABASE CLEANUP ANALYSIS")
        print("=" * 50)
        print(f"Found {len(tables)} tables in database")
        print()
        
        # Analyze each table
        table_usage = {}
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            row_count = cursor.fetchone()[0]
            
            # Check if table is used in Python files
            python_files = []
            for root, dirs, files in os.walk('app'):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            # Check if table is used in HTML files
            html_files = []
            for root, dirs, files in os.walk('app/templates'):
                for file in files:
                    if file.endswith('.html'):
                        html_files.append(os.path.join(root, file))
            
            # Search for table usage
            used_in_python = False
            used_in_html = False
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if table in content:
                            used_in_python = True
                            break
                except:
                    pass
            
            for html_file in html_files:
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if table in content:
                            used_in_html = True
                            break
                except:
                    pass
            
            table_usage[table] = {
                'rows': row_count,
                'used_in_python': used_in_python,
                'used_in_html': used_in_html
            }
        
        # Print analysis
        print("TABLE USAGE ANALYSIS:")
        print("-" * 50)
        
        unused_tables = []
        empty_unused_tables = []
        
        for table, info in table_usage.items():
            status = "ACTIVE" if info['used_in_python'] else "UNUSED"
            row_info = f"{info['rows']} rows"
            
            print(f"{table:<30} {status:<8} {row_info}")
            
            if not info['used_in_python']:
                unused_tables.append(table)
                if info['rows'] == 0:
                    empty_unused_tables.append(table)
        
        print()
        print("RECOMMENDATIONS:")
        print("-" * 50)
        
        if empty_unused_tables:
            print("Tables that can be safely removed (empty + unused):")
            for table in empty_unused_tables:
                print(f"  - {table}")
        
        if unused_tables:
            print(f"\nTables with no backend implementation ({len(unused_tables)}):")
            for table in unused_tables:
                rows = table_usage[table]['rows']
                if rows > 0:
                    print(f"  - {table} ({rows} rows) - NEEDS BACKEND IMPLEMENTATION")
                else:
                    print(f"  - {table} (empty)")
        
        # Check for features that need implementation
        print("\nFEATURES NEEDING IMPLEMENTATION:")
        print("-" * 50)
        
        if 'favorit_aset' in tables and not table_usage['favorit_aset']['used_in_python']:
            print("  - Favorit Aset (Frontend exists, backend missing)")
        
        if 'notifikasi_user' in tables and not table_usage['notifikasi_user']['used_in_python']:
            print("  - Notifikasi User (Frontend exists, backend missing)")
        
        if 'histori_sewa' in tables and not table_usage['histori_sewa']['used_in_python']:
            print("  - Histori Sewa (Frontend exists, backend missing)")
        
        cursor.close()
        conn.close()
        
        return {
            'unused_tables': unused_tables,
            'empty_unused_tables': empty_unused_tables,
            'table_usage': table_usage
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    analysis = analyze_database_usage()
