# config.py
# ── Theme Constants ──────────────────────────────────────────────────────────
C_BG0    = "#0d0f14"
C_BG1    = "#161a22"
C_BG2    = "#1e2330"
C_ACCENT = "#F4A823"   # Araw Gold
C_TEXT   = "#c7d5e0"
C_DIM    = "#7b8fa3"
C_BORDER = "#9b2d30"   # updated in batch 2
C_GOLD   = "#FFD700"
C_RED    = "#e86c6c"

# ── Genre & Game System ──────────────────────────────────────────────────────
ALL_GENRES = ["All", "Action", "RPG", "Adventure", "Indie", "Horror",
              "Casual", "Puzzle", "Strategy", "Simulation", "Visual Novel"]

GAME_GENRES = {
    "4466940": ["RPG", "Action"],
    "1574820": ["Adventure", "Indie"],
    "2819970": ["Casual"],
    "1281400": ["Action", "Adventure"],
    "2282930": ["Visual Novel", "Indie"],
    "2603750": ["Strategy"],
    "279530":  ["RPG"],
}

MANUAL_PLATFORMS = {
    "1574820": ["PlayStation", "Xbox"],
    "4466940": ["Xbox"],
    "2470780": ["Android"],
    "2819970": ["Android"],
}

RECENTS_MAX = 10
FILIPINO_IDS = ["4466940", "1574820", "2819970", "1281400", "2282930", "2603750", "279530"]
FALLBACK_IDS = ["1091500", "1245620", "570", "1938090", "1086940", "1203220"]
