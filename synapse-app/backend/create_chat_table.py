"""
Create chat_records table in Supabase
Run this script to set up the database table for MCP chat storage
"""

from app.services.supabase_client import get_supabase_client

def create_chat_records_table():
    """Create the chat_records table using Supabase client"""

    supabase = get_supabase_client()

    # Read the SQL migration
    with open('migrations/create_chat_records_table.sql', 'r') as f:
        sql = f.read()

    print("Creating chat_records table in Supabase...")
    print("SQL:", sql[:200] + "...")

    try:
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'query': sql}).execute()
        print("[OK] Table created successfully!")
        print("You can now use the MCP server to store chat conversations.")

    except Exception as e:
        print(f"[ERROR] Failed to create table: {e}")
        print("\nPlease run the SQL manually in Supabase SQL Editor:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to 'SQL Editor'")
        print("4. Copy the SQL from migrations/create_chat_records_table.sql")
        print("5. Run it")

if __name__ == "__main__":
    create_chat_records_table()
