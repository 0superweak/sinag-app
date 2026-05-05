import os
import hashlib
import json

DB_FILE = "wlm_users.txt"


def _hash_password(password):
    """
    Hashes the user password using SHA-256 for basic security.
    """
    return hashlib.sha256(password.encode()).hexdigest()


class Database:
    """
    Handles all local text-based database interactions for Vapor user accounts.

    Record format (pipe-delimited, 9 fields):
        username | hashed_pw | display_name | bio | saved_games
        | favorites | recents | ratings_json | games_played
    """

    @staticmethod
    def register_user(username, password, display_name="Freshman", bio="No bio set yet."):
        if Database.user_exists(username):
            return False
        try:
            hashed = _hash_password(password)
            with open(DB_FILE, "a") as f:
                # New fields default to empty
                f.write(f"{username}|{hashed}|{display_name}|{bio}|||||\n")
            return True
        except Exception as e:
            print(f"[DB ERROR] Registration failed: {e}")
            return False

    @staticmethod
    def login_user(username, password):
        if not os.path.exists(DB_FILE):
            return None
        try:
            hashed = _hash_password(password)
            with open(DB_FILE, "r") as f:
                for line in f:
                    data = line.strip().split("|", -1)
                    if len(data) >= 2 and data[0] == username and data[1] == hashed:
                        return data
            return None
        except Exception as e:
            print(f"[DB ERROR] Login failed: {e}")
            return None

    @staticmethod
    def user_exists(username):
        if not os.path.exists(DB_FILE):
            return False
        try:
            with open(DB_FILE, "r") as f:
                for line in f:
                    if line.startswith(f"{username}|"):
                        return True
            return False
        except Exception:
            return False

    @staticmethod
    def sync_data(user, password, title, bio,
                  games_list, favorites=None, recents=None,
                  ratings=None, games_played=None):
        """
        Persists all user state back to the flat-file database.

        Parameters
        ----------
        games_list    : list/set  of saved app IDs
        favorites     : list/set  of favourite app IDs
        recents       : list      of recently-viewed app IDs (ordered)
        ratings       : dict      {app_id: score}  score 1-5
        games_played  : list/set  of played app IDs
        """
        if not os.path.exists(DB_FILE):
            return
        lines = []
        try:
            with open(DB_FILE, "r") as f:
                lines = f.readlines()

            def _ids(col):
                if col is None:
                    return ""
                if isinstance(col, dict):
                    return json.dumps(col, separators=(",", ":"))
                return ",".join(str(x) for x in col)

            saved_str       = _ids(games_list)
            favorites_str   = _ids(favorites)
            recents_str     = _ids(recents)
            ratings_str     = _ids(ratings)   # stored as JSON blob
            played_str      = _ids(games_played)

            with open(DB_FILE, "w") as f:
                for line in lines:
                    data = line.strip().split("|")
                    if data[0] == user:
                        f.write(
                            f"{user}|{password}|{title}|{bio}|"
                            f"{saved_str}|{favorites_str}|{recents_str}|"
                            f"{ratings_str}|{played_str}\n"
                        )
                    else:
                        f.write(line)
        except Exception as e:
            print(f"[DB ERROR] Sync failed: {e}")
