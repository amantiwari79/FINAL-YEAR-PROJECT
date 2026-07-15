import sqlite3
import os

DB_FILE = 'db.sqlite3'

def get_connection():
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found in the current directory.")
        return None
    return sqlite3.connect(DB_FILE)

def get_tables():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
    conn.close()
    return tables

def list_tables():
    tables = get_tables()
    print("\n=== Tables in db.sqlite3 ===")
    if not tables:
        print("No user tables found.")
        return
    for i, table in enumerate(tables, 1):
        print(f" [{i}] {table}")
    print("============================\n")

def view_table_schema(table_name):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"\n=== Schema for table: {table_name} ===")
        print(f"{'CID':<5} | {'Column Name':<30} | {'Type':<15} | {'Not Null':<10} | {'Primary Key':<5}")
        print("-" * 75)
        for col in columns:
            # col format: (cid, name, type, notnull, dflt_value, pk)
            pk = "Yes" if col[5] else "No"
            nn = "Yes" if col[3] else "No"
            print(f"{col[0]:<5} | {col[1]:<30} | {col[2]:<15} | {nn:<10} | {pk:<5}")
    except sqlite3.Error as e:
        print(f"Error viewing schema: {e}")
    finally:
        conn.close()
    print("======================================\n")

def view_table_data(table_name, limit=10):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        # Get column names first
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols = [col[1] for col in cursor.fetchall()]
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
        rows = cursor.fetchall()
        
        print(f"\n=== Data in table: {table_name} (Showing top {limit} rows) ===")
        # Print column headers
        header = " | ".join(cols)
        print(header)
        print("-" * len(header))
        
        if not rows:
            print("(Table is empty)")
        else:
            for row in rows:
                print(" | ".join(str(val) for val in row))
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
    finally:
        conn.close()
    print("=================================================================\n")

def main():
    while True:
        print("--- db.sqlite3 Viewer Menu ---")
        print("1. List all tables")
        print("2. View Table Schema")
        print("3. View Table Data")
        print("4. Exit")
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            list_tables()
        elif choice in ('2', '3'):
            tables = get_tables()
            if not tables:
                print("No tables available.")
                continue
            list_tables()
            try:
                idx = int(input(f"Select table number (1-{len(tables)}): ").strip())
                if 1 <= idx <= len(tables):
                    table_name = tables[idx - 1]
                    if choice == '2':
                        view_table_schema(table_name)
                    else:
                        limit_str = input("Enter row limit (default 10): ").strip()
                        limit = int(limit_str) if limit_str.isdigit() else 10
                        view_table_data(table_name, limit)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == '4':
            print("Exiting viewer.")
            break
        else:
            print("Invalid choice, please select 1-4.")

if __name__ == "__main__":
    main()
