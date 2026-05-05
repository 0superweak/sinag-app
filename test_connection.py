from supabase import create_client

SUPABASE_URL = "https://wujmbfkrzkwldldekxbt.supabase.co"
SUPABASE_KEY = "sb_publishable_cQjFS0K8o6SSbwcI02qTPg_N-jUogBy"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Client created.")
    # Try a simple select that should work with anon key
    res = supabase.table("profiles").select("id").limit(1).execute()
    print("Success! Connection works.")
    print(res.data)
except Exception as e:
    print(f"Error: {e}")
