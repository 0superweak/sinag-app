import os
from supabase import create_client, Client

# Hardcoded for mobile build — move to .env for production
SUPABASE_URL = "https://wujmbfkrzkwldldekxbt.supabase.co"
SUPABASE_KEY = "sb_publishable_cQjFS0K8o6SSbwcI02qTPg_N-jUogBy"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class SupabaseClient:
    # ── AUTH ───────────────────────────────────────────────────────────────

    @staticmethod
    def sign_up(email, password, username, display_name):
        """
        Returns:
          - user object on success
          - "already_registered" if the email is already in use
          - None on any other error
        """
        try:
            auth_res = supabase.auth.sign_up({"email": email, "password": password})
            if not auth_res.user:
                return None

            uid = auth_res.user.id

            # Guard against duplicate profile rows (e.g. from a retry or trigger)
            existing = supabase.table("profiles").select("id").eq("id", uid).execute()
            if not existing.data:
                supabase.table("profiles").insert({
                    "id":           uid,
                    "username":     username,
                    "display_name": display_name,
                    "status":       "Online",
                }).execute()

            return auth_res.user

        except Exception as e:
            err = str(e).lower()
            if "already registered" in err or "user already registered" in err:
                return "already_registered"
            print(f"[Supabase] Sign-up Error: {e}")
            return None

    @staticmethod
    def ensure_profile_exists(user_id, email):
        """Checks if a profile exists; if not, creates one with a default name."""
        try:
            existing = supabase.table("profiles").select("id").eq("id", user_id).execute()
            if not existing.data:
                default_name = email.split("@")[0]
                supabase.table("profiles").insert({
                    "id":           user_id,
                    "username":     default_name.lower(),
                    "display_name": default_name,
                    "status":       "Online",
                }).execute()
        except Exception as e:
            print(f"[Supabase] Ensure Profile Error: {e}")

    @staticmethod
    def log_in(email, password):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                SupabaseClient.ensure_profile_exists(res.user.id, email)
                SupabaseClient.update_status(res.user.id, "Online")
            return res.user
        except Exception as e:
            print(f"[Supabase] Login Error: {e}")
            return None

    @staticmethod
    def update_status(user_id, status_text):
        try:
            supabase.table("profiles").update({"status": status_text}).eq("id", user_id).execute()
        except Exception as e:
            print(f"[Supabase] Status Update Error: {e}")

    @staticmethod
    def get_profile(user_id):
        try:
            response = supabase.table("profiles").select("*").eq("id", user_id).execute()
            if response.data and len(response.data) > 0:
                profile = response.data[0]
                # Email lives in Auth, not the profiles table — fetch and attach it.
                try:
                    auth_res = supabase.auth.admin.get_user_by_id(user_id)
                    if auth_res and auth_res.user:
                        profile["email"] = auth_res.user.email
                except Exception:
                    pass  # Non-fatal: email just won't be available for notifications
                return profile
            return None
        except Exception as e:
            print(f"[Supabase] Get Profile Error: {e}")
            return None

    # ── FRIENDS ────────────────────────────────────────────────────────────

    @staticmethod
    def search_users(term):
        try:
            res = supabase.table("profiles").select("*").or_(
                f"username.ilike.%{term}%,display_name.ilike.%{term}%"
            ).execute()
            return res.data
        except Exception as e:
            print(f"[Supabase] Search error: {e}")
            return []

    @staticmethod
    def get_friendship_status(user_a, user_b):
        try:
            res = supabase.table("friendships").select("*").or_(
                f"and(from_user.eq.{user_a},to_user.eq.{user_b}),"
                f"and(from_user.eq.{user_b},to_user.eq.{user_a})"
            ).execute()
            if res.data:
                return res.data[0]["status"]
            return None
        except Exception:
            return None

    @staticmethod
    def send_friend_request(my_id, target_id):
        try:
            supabase.table("friendships").insert({
                "from_user": my_id,
                "to_user":   target_id,
                "status":    "pending",
            }).execute()
        except Exception as e:
            print(f"[Supabase] Request Error: {e}")

    @staticmethod
    def get_friends(user_id):
        try:
            res1 = supabase.table("friendships").select(
                "to_user, profiles!friendships_to_user_fkey(username, display_name, status)"
            ).eq("from_user", user_id).eq("status", "accepted").execute()

            res2 = supabase.table("friendships").select(
                "from_user, profiles!friendships_from_user_fkey(username, display_name, status)"
            ).eq("to_user", user_id).eq("status", "accepted").execute()

            friends = []
            for r in res1.data:
                p = r.get("profiles", {})
                friends.append({
                    "id":           r["to_user"],
                    "username":     p.get("username", ""),
                    "display_name": p.get("display_name", ""),
                    "status":       p.get("status", ""),
                })
            for r in res2.data:
                p = r.get("profiles", {})
                friends.append({
                    "id":           r["from_user"],
                    "username":     p.get("username", ""),
                    "display_name": p.get("display_name", ""),
                    "status":       p.get("status", ""),
                })
            return friends
        except Exception as e:
            print(f"[Supabase] Get Friends Error: {e}")
            return []

    @staticmethod
    def get_pending_requests(user_id):
        try:
            res = supabase.table("friendships").select(
                "id, from_user, profiles!friendships_from_user_fkey(username, display_name)"
            ).eq("to_user", user_id).eq("status", "pending").execute()
            return res.data
        except Exception as e:
            print(f"[Supabase] Pending Error: {e}")
            return []

    @staticmethod
    def accept_friend(req_id):
        try:
            supabase.table("friendships").update({"status": "accepted"}).eq("id", req_id).execute()
        except Exception as e:
            print(f"[Supabase] Accept Error: {e}")

    @staticmethod
    def decline_friend(req_id):
        try:
            supabase.table("friendships").delete().eq("id", req_id).execute()
        except Exception as e:
            print(f"[Supabase] Decline Error: {e}")

    # ── MESSAGES ───────────────────────────────────────────────────────────
    # Required Supabase table:
    #   CREATE TABLE messages (
    #     id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    #     sender_id   uuid REFERENCES profiles(id) ON DELETE CASCADE,
    #     receiver_id uuid REFERENCES profiles(id) ON DELETE CASCADE,
    #     content     text NOT NULL,
    #     created_at  timestamptz DEFAULT now()
    #   );
    # RLS: enable, then:
    #   INSERT: (auth.uid() = sender_id)
    #   SELECT: (auth.uid() = sender_id OR auth.uid() = receiver_id)

    @staticmethod
    def send_message(sender_id, receiver_id, content):
        """Inserts one message row. Returns the new row dict or None."""
        try:
            res = supabase.table("messages").insert({
                "sender_id":   sender_id,
                "receiver_id": receiver_id,
                "content":     content,
            }).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"[Supabase] Send Message Error: {e}")
            return None

    @staticmethod
    def get_messages(user_a, user_b, limit=60):
        """Returns messages between two users, oldest first."""
        try:
            res = supabase.table("messages").select(
                "id, sender_id, receiver_id, content, created_at"
            ).or_(
                f"and(sender_id.eq.{user_a},receiver_id.eq.{user_b}),"
                f"and(sender_id.eq.{user_b},receiver_id.eq.{user_a})"
            ).order("created_at", desc=False).limit(limit).execute()
            return res.data
        except Exception as e:
            print(f"[Supabase] Get Messages Error: {e}")
            return []

    @staticmethod
    def get_recent_received_messages(user_id, limit=50):
        """Fetches the latest messages sent to the user from anyone."""
        try:
            res = supabase.table("messages").select("*").eq("receiver_id", user_id).order("created_at", desc=True).limit(limit).execute()
            return res.data
        except Exception as e:
            print(f"[Supabase] Recent Messages Error: {e}")
            return []

    # ── FEEDBACK ───────────────────────────────────────────────────────────

    @staticmethod
    def submit_feedback(user_id, rating, content):
        """Inserts a feedback row into the feedback table."""
        try:
            supabase.table("feedback").insert({
                "user_id": user_id,
                "rating":  rating,
                "content": content
            }).execute()
            return True
        except Exception as e:
            print(f"[Supabase] Feedback Error: {e}")
            return False

    # ── CURATED GAMES ──────────────────────────────────────────────────────

    @staticmethod
    def get_curated_pinoy_ids():
        """Fetches the list of curated Steam App IDs from Supabase."""
        try:
            res = supabase.table("curated_pinoy_games").select("app_id").eq("is_active", True).execute()
            return [item["app_id"] for item in res.data]
        except Exception as e:
            print(f"[Supabase] Curated Games Error: {e}")
            return []

    # ── NEWS NOTIFICATIONS ─────────────────────────────────────────────────

    @staticmethod
    def send_follow_notification(email: str, news_title: str):
        try:
            supabase.table("news_notifications").insert({
                "email":      email,
                "news_title": news_title,
                "sent_at":    "now()",
            }).execute()
            print(f"[EMAIL] Follow notification queued for {email} → \"{news_title}\"")
        except Exception as e:
            print(f"[EMAIL] send_follow_notification failed: {e}")

    # ── GAME SUBMISSIONS ───────────────────────────────────────────────────

    @staticmethod
    def submit_game(user_id, name, steam_id, platform, desc, link):
        """Inserts a new game submission for review."""
        try:
            supabase.table("game_submissions").insert({
                "submitter_id": user_id,
                "game_name":    name,
                "steam_id":     steam_id,
                "platform":     platform,
                "description":  desc,
                "game_link":    link
            }).execute()
            return True
        except Exception as e:
            print(f"[Supabase] Submission Error: {e}")
            return False