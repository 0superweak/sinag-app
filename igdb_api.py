import requests
import time
import os
from dotenv import load_dotenv
from logger import trace

load_dotenv()

class IGDBAPI:
    CLIENT_ID     = os.getenv("TWITCH_CLIENT_ID", "j8ctbocuz35pi42eo74kszxfdqpqtc")
    CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "3odjtvz7vj38vf1fl6ntm2bzcrezk5")
    BASE_URL      = "https://api.igdb.com/v4"

    _access_token   = None
    _token_expiry   = 0   # unix timestamp

    # ── Token Management ────────────────────────────────────────────────────

    @classmethod
    def _refresh_token(cls):
        """Fetches a fresh OAuth token from Twitch and caches it."""
        trace("Refreshing IGDB access token...", "IGDB")
        try:
            res = requests.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id":     cls.CLIENT_ID,
                    "client_secret": cls.CLIENT_SECRET,
                    "grant_type":    "client_credentials",
                },
                timeout=10,
            )
            res.raise_for_status()
            data = res.json()
            cls._access_token = data["access_token"]
            # expire 60 s early to avoid races
            cls._token_expiry = time.time() + data.get("expires_in", 3600) - 60
            trace(f"New token acquired, expires in {data.get('expires_in', 3600)}s", "IGDB")
        except Exception as e:
            trace(f"Token refresh failed: {e}", "IGDB")
            cls._access_token = None

    @classmethod
    def _get_headers(cls):
        """Returns valid auth headers, refreshing the token if expired."""
        if not cls._access_token or time.time() >= cls._token_expiry:
            cls._refresh_token()
        return {
            "Client-ID":     cls.CLIENT_ID,
            "Authorization": f"Bearer {cls._access_token}",
            "Accept":        "application/json",
        }

    # ── Core Query ──────────────────────────────────────────────────────────

    @classmethod
    def query(cls, endpoint, body):
        url = f"{cls.BASE_URL}/{endpoint}"
        try:
            response = requests.post(
                url, headers=cls._get_headers(), data=body, timeout=10
            )

            # Handle Token Expiration
            if response.status_code == 401:
                trace("401 received, forcing token refresh and retrying...", "IGDB")
                cls._access_token = None
                response = requests.post(
                    url, headers=cls._get_headers(), data=body, timeout=10
                )

            # Handle Rate Limiting
            elif response.status_code == 429:
                trace("429 Too Many Requests - sleeping for 1 second...", "IGDB")
                time.sleep(1)
                response = requests.post(
                    url, headers=cls._get_headers(), data=body, timeout=10
                )

            if response.status_code == 200:
                return response.json()

            # Log the exact reason it failed
            trace(f"IGDB API Error: {response.status_code} - {response.text}", "IGDB")
            return []

        except requests.exceptions.RequestException as e:
            trace(f"IGDB Network/Request Exception: {e}", "IGDB")
            return []
    # ── Search ──────────────────────────────────────────────────────────────

    @classmethod
    def search_games(cls, query_term, limit=10):
        trace(f"Querying IGDB for '{query_term}'", "IGDB")

        # Strip out double quotes to prevent breaking the Apicalypse syntax
        safe_term = query_term.replace('"', '')

        FIELDS = "fields name, rating, summary, cover.url, platforms.name, genres.name, url;"

        # 1. Primary: IGDB full-text search
        results = cls.query(
            "games",
            f'{FIELDS} search "{safe_term}"; limit {limit};',
        )

        # 2. Fallback: fuzzy name filter sorted by rating
        if not results:
            trace("Direct search empty, trying fuzzy name filter...", "IGDB")
            results = cls.query(
                "games",
                f'{FIELDS} where name ~ *"{safe_term}"*; sort rating desc; limit {limit};',
            )

        if not results:
            trace("No results found for query.", "IGDB")
            return []

        formatted = []
        for game in results:
            if "cover" in game and "url" in game["cover"]:
                img_url = "https:" + game["cover"]["url"].replace("t_thumb", "t_cover_big")
            else:
                img_url = "https://images.igdb.com/igdb/image/upload/t_cover_big/nocover.png"

            rating = f"⭐ {game['rating']:.1f}/100" if "rating" in game else "No Rating"
            platforms = [p["name"] for p in game.get("platforms", [])]
            genres    = [g["name"] for g in game.get("genres", [])]

            formatted.append({
                "app_id":       f"igdb-{game['id']}",
                "name":         game.get("name", "Unknown Game"),
                "img":          img_url,
                "price":        "N/A",
                "rating":       rating,
                "desc":         game.get("summary", "No description available."),
                "platforms":    platforms,
                "genres":       genres,
                "source":       "IGDB",
                "external_url": game.get("url", ""),
            })

        trace(f"Returning {len(formatted)} formatted results.", "IGDB")
        return formatted
    # Place this at the absolute bottom of igdb_api.py
if __name__ == "__main__":
    import json
    print("--- TESTING IGDB API CONNECTION ---")
    print("Attempting to search for 'Zelda'...")

    results = IGDBAPI.search_games("Zelda", limit=3)

    if results:
        print(f"\n✅ SUCCESS! Found {len(results)} games:")
        print(json.dumps(results, indent=2))
    else:
        print("\n❌ FAILED. No results returned.")
        print("Check your console trace above to see if it was a 401 (Bad Keys), 429 (Rate Limit), or something else.")