# backend.py
import threading
from datetime import datetime

def trace(action, component="APP"):
    """Prints a timestamped, thread-aware debug log."""
    t_name = threading.current_thread().name
    if t_name == "MainThread":
        t_name = "MAIN"
    t_stamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{t_stamp}] [{t_name}] [{component}] {action}")

import os
import time
import base64
import threading
from steam_api import SteamAPI
from igdb_api import IGDBAPI
from database import Database
from supabase_client import SupabaseClient
from config import *

class AppState:
    def __init__(self, page):
        self.page = page
        self.data = {
            "user_id":        None,
            "user":           None,
            "pass":           None,
            "display_name":   "",
            "bio":            "",
            "owned":          set(),
            "favorites":      set(),
            "recents":        [],
            "ratings":        {},
            "games_played":   set(),
            "followed_news":  set(),
            "all_games":      [],
            "master_list":    [],
            "master_ids":     [],
            "batch_index":    0,
            "current_tab":    0,
            "is_loading":     False,
            "search_active":  False,
            "search_results": [],
            "is_register_mode": False,
            "current_accent": C_ACCENT,
            "hw_accel":       True,
            "app_version":    "v1.3.1-STABLE",
            "build_date":     "April 2026",
            "lib_tab":        0,
            "nav_anim_idx":   -1,
            "genre_filter":   "All",
            "unread_chats":   set(),
            "chat_last_viewed": {},
            "nav_controls":   [],
        }

    def update(self, new_data):
        self.data.update(new_data)

    def sync(self):
        """Persists current state to the flat-file DB."""
        Database.sync_data(
            self.data["user"], self.data["pass"],
            self.data["display_name"], self.data["bio"],
            list(self.data["owned"]), list(self.data["favorites"]),
            list(self.data["recents"]), self.data["ratings"],
            list(self.data["games_played"])
        )
        try:
            news_path = os.path.join(os.path.expanduser("~"), ".vapor_followed_news")
            with open(news_path, "w") as f:
                f.write(",".join(self.data["followed_news"]))
        except Exception:
            pass

    def load_followed_news(self):
        try:
            news_path = os.path.join(os.path.expanduser("~"), ".vapor_followed_news")
            if os.path.exists(news_path):
                with open(news_path, "r") as f:
                    raw = f.read().strip()
                if raw:
                    self.data["followed_news"] = set(raw.split(","))
        except Exception:
            pass

    def save_session(self, email, password):
        try:
            payload = f"{email}:{password}"
            encoded = base64.b64encode(payload.encode()).decode()
            session_path = os.path.join(os.path.expanduser("~"), ".vapor_session")
            with open(session_path, "w") as f:
                f.write(encoded)
        except Exception as e:
            print(f"[SESSION] Save failed: {e}")

    def load_session(self):
        try:
            session_path = os.path.join(os.path.expanduser("~"), ".vapor_session")
            if not os.path.exists(session_path):
                return None, None
            with open(session_path, "r") as f:
                encoded = f.read().strip()
            if not encoded:
                return None, None
            decoded = base64.b64decode(encoded).decode()
            return decoded.split(":", 1)
        except Exception:
            return None, None

    def clear_session(self):
        try:
            session_path = os.path.join(os.path.expanduser("~"), ".vapor_session")
            if os.path.exists(session_path):
                os.remove(session_path)
        except Exception:
            pass

    def fetch_software_batch(self, ids):
        from concurrent.futures import ThreadPoolExecutor
        if not ids: return []
        results = {}
        lock = threading.Lock()

        def _fetch_one(gid):
            try:
                res = SteamAPI.fetch(f"https://store.steampowered.com/api/appdetails?appids={gid}&cc=ph")
                gid_str = str(gid)
                if res and gid_str in res and res[gid_str].get("success"):
                    data = res[gid_str]["data"]
                    if data.get("type") in ["game", "dlc"]:
                        meta = data.get("metacritic", {}).get("score")
                        rating_str = f"⭐ {meta}/100" if meta else "⭐ Very Positive"
                        platforms = [p for p, val in data.get("platforms", {}).items() if val and p in ["windows", "mac", "linux"]]
                        api_genres = [g["description"] for g in data.get("genres", []) if g.get("description") in ALL_GENRES]
                        combined_genres = list(dict.fromkeys(GAME_GENRES.get(gid_str, []) + api_genres))
                        with lock:
                            results[gid_str] = {
                                "app_id": gid_str, "name": data["name"],
                                "img": data["header_image"],
                                "price": data.get("price_overview", {}).get("final_formatted", "Free"),
                                "rating": rating_str,
                                "desc": data.get("short_description", "No description available."),
                                "platforms": [p.capitalize() for p in platforms],
                                "genres": combined_genres,
                            }
            except Exception as e:
                print(f"API Error for {gid}: {e}")

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(_fetch_one, ids)

        # Preserve original order
        return [results[str(gid)] for gid in ids if str(gid) in results]

    def search_igdb(self, term):
        """Searches IGDB for games and returns formatted results."""
        trace(f"Searching IGDB for: {term}", "IGDB")
        try:
            return IGDBAPI.search_games(term)
        except Exception as e:
            trace(f"IGDB Search failed: {e}", "IGDB")
            return []
