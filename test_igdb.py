# test_igdb.py
from igdb_api import IGDBAPI


def test_search():
    print("--- Testing IGDB API Search ---")
    term = "Zelda"
    print(f"Searching for: {term}...")

    results = IGDBAPI.search_games(term, limit=3)

    if not results:
        print("FAIL: No results returned. Check your CLIENT_ID and ACCESS_TOKEN in igdb_api.py")
        return

    print(f"SUCCESS: Found {len(results)} games!")
    for game in results:
        print(f"\n[Game Found]")
        print(f"Name: {game['name']}")
        print(f"Source: {game['source']}")
        print(f"ID: {game['app_id']}")
        print(f"URL: {game['external_url']}")
        print(f"Img: {game['img']}")


if __name__ == "__main__":
    # We need a dummy trace function since igdb_api.py uses it
    import builtins


    def mock_trace(msg, comp): print(f"[{comp}] {msg}")


    builtins.trace = mock_trace

    test_search()
