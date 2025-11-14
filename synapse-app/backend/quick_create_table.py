"""
Quick script to create chat_records table in Supabase
"""

from app.services.supabase_client import get_supabase_client

def create_table():
    """Create the chat_records table"""

    sql = """
    CREATE TABLE IF NOT EXISTS chat_records (
        id UUID PRIMARY KEY,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        source_app TEXT DEFAULT 'Unknown',
        content_type TEXT DEFAULT 'chat',
        tags TEXT[] DEFAULT '{}',
        word_count INTEGER DEFAULT 0,
        text_preview TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_chat_records_created_at ON chat_records(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_chat_records_source_app ON chat_records(source_app);
    CREATE INDEX IF NOT EXISTS idx_chat_records_tags ON chat_records USING GIN(tags);
    """

    print("Creating chat_records table in Supabase...")

    try:
        supabase = get_supabase_client()

        # Try to query the table first to see if it exists
        try:
            result = supabase.table("chat_records").select("id").limit(1).execute()
            print("[OK] Table 'chat_records' already exists!")
            return True
        except Exception as e:
            if "could not find" in str(e).lower() or "does not exist" in str(e).lower():
                print("[INFO] Table does not exist, needs to be created manually")
                print("\nPlease run this SQL in Supabase SQL Editor:")
                print("=" * 70)
                print(sql)
                print("=" * 70)
                print("\nSteps:")
                print("1. Go to https://supabase.com/dashboard")
                print("2. Select your project")
                print("3. Click 'SQL Editor'")
                print("4. Paste the SQL above")
                print("5. Click 'Run'")
                return False
            else:
                raise

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        return False

if __name__ == "__main__":
    create_table()
