import requests

class SteamAPI:
    KEY = "78049A0EC744DAC3737F62D885C5C03B"

    @staticmethod
    def fetch(url, use_auth=False):
        # Using a standard browser User-Agent prevents Steam from blocking the request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        target_url = url

        if use_auth:
            separator = "&" if "?" in url else "?"
            target_url = f"{url}{separator}key={SteamAPI.KEY}"

        # Clean up strict routing issues (Steam APIs hate trailing slashes)
        if target_url.endswith("/v2/"):
            target_url = target_url[:-1]

        # ONLY send age-gate cookies to the Storefront, never to the API backend
        cookies = {}
        if "store.steampowered.com" in url:
            cookies = {
                "birthtime": "283993201",
                "lastagecheckage": "1-0-1990",
                "wants_mature_content": "1"
            }

        try:
            response = requests.get(target_url, headers=headers, cookies=cookies, timeout=10)
            response.raise_for_status() # This will catch 404s and 403s properly
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[API WARN] Fetch failed for {target_url}: {e}")
            return {}
        except ValueError:
            print(f"[API WARN] JSON decode failed for {target_url}")
            return {}