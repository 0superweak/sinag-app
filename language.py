# language.py  –  single source of truth for all UI text
# Usage:  from language import t
#         t(app_state, "store_title")

APP_STRINGS = {
    "fil": {
        # ── Nav bar ───────────────────────────────────────────────────────────
        "nav_store":      "Tindahan",
        "nav_news":       "Balita",
        "nav_friends":    "Kaibigan",
        "nav_library":    "Library",
        "nav_profile":    "Profile",

        # ── General ───────────────────────────────────────────────────────────
        "loading": "Sandali lang...",

        # ── Auth view ─────────────────────────────────────────────────────────
        "auth_tagline":        "Tahanan ng Larong Lokal",
        "auth_email":          "EMAIL",
        "auth_username":       "USERNAME",
        "auth_password":       "PASSWORD",
        "auth_display_name":   "DISPLAY NAME",
        "auth_stay_logged_in": "Manatiling naka-login",
        "auth_login_btn":      "PUMASOK",
        "auth_register_btn":   "MAG-PAREHISTRO",
        "auth_create_account": "Gumawa ng Account",
        "auth_back_to_login":  "Bumalik sa Login",
        "auth_required_fields":"Email at Password ay kailangan.",
        "auth_login_failed":   "Nabigo ang login. Suriin ang credentials.",
        "auth_registered":     "Nalikha ang Account! Maaari ka nang mag-login.",

        # ── Profile view ──────────────────────────────────────────────────────
        "profile_title":  "AKING PROFILE",
        "saved":          "Na-save",
        "favorites":      "Paborito",
        "played":         "Nalaro",
        "rated":          "Na-rate",
        "avg_rating":     "Avg Rating",
        "visited":        "Binisita",
        "feedback_btn":   "Ibahagi ang Feedback",
        "logout_btn":     "Mag-logout",
        "settings_title": "MGA SETTING",
        "accent_label":   "Kulay ng Accent",
        "lang_label":     "Wika",
        "lang_toggle":    "English",
        "feedback_title": "IBAHAGI ANG FEEDBACK",
        "feedback_sub":   "Ano ang maaari naming pagbutihin?",
        "feedback_hint":  "Isulat ang iyong feedback...",
        "feedback_send":  "IPADALA",
        "feedback_thanks":"Salamat sa iyong feedback! 🙏",

        # ── Store view ────────────────────────────────────────────────────────
        "store_title":          "SINAG STORE",
        "store_search_results": "MGA RESULTA",
        "store_pinoy_picks":    "PINOY PICKS",
        "store_made_in_ph":     "GAWA SA PH",
        "store_search_hint":    "Hanapin ang laro...",
        "store_empty":          "Walang nahanap na laro.",
        "store_save_btn":       "I-SAVE",
        "store_saved_btn":      "NAKASAVE",
        "store_free":           "Libre",
        "store_save_snack":     "Nai-save na!",

        # ── Store detail / game modal ─────────────────────────────────────────
        "detail_favorite":    "I-paborito",
        "detail_unfavorite":  "Paborito na",
        "detail_played":      "Nalaro",
        "detail_played_done": "Nalaro na",
        "detail_my_rating":   "Rating mo:",
        "detail_rate_hint":   "I-rate ang laro",
        "detail_store_page":  "STORE PAGE",
        "detail_close":       "ISARA",

        # ── News view ─────────────────────────────────────────────────────────
        "news_title":           "PINOY DEV FEED",
        "news_live":            "LIVE",
        "news_featured":        "FEATURED",
        "news_latest":          "PINAKABAGONG BALITA",
        "news_following_one":   "Sinusubaybayan mo ang 1 balita.",
        "news_following_n":     "Sinusubaybayan mo ang {n} balita.",
        "news_follow":          "Subaybayan",
        "news_unfollow":        "Sinusubaybayan",
        "news_follow_snack":    "Sinusubaybayan na! Maabisuhan ka sa mga updates.",
        "news_unfollow_snack":  "Hindi na sinusubaybayan.",
        "news_empty":           "Walang balita sa ngayon.",
        "news_view_steam":      "TIGNAN SA STEAM",
        "news_listen":          "PAKINGGAN NGAYON",
        "news_view_post":       "TINGNAN ANG POST",
        "news_watch":           "PANOORIN ANG TRAILER",
        "news_read_more":       "BASAHIN PA",
        "news_tag_release":     "RELEASE",
        "news_tag_reveal":      "REVEAL",
        "news_tag_trailer":     "TRAILER",
        "news_tag_update":      "UPDATE",
        "news_tag_community":   "KOMUNIDAD",

        # ── Friends view ──────────────────────────────────────────────────────
        "friends_title":          "MGA KAIBIGAN",
        "friends_count_label":    "kaibigan",
        "friends_count_one":      "1 kaibigan",
        "friends_count_n":        "{n} kaibigan",
        "friends_search_hint":    "Hanapin gamit ang Username...",
        "friends_search_btn":     "HANAPIN",
        "friends_your_list":      "IYONG MGA KAIBIGAN",
        "friends_requests_header":"MGA FRIEND REQUESTS",
        "friends_wants_to_add":   "ay gustong makipagkaibigan",
        "friends_list_empty_hint":"I-search sa itaas para magdagdag ng kaibigan!",
        "friends_empty":          "Walang kaibigan pa.",
        "friends_online":         "Online",
        "friends_offline":        "Offline",
        "friends_message":        "Mag-mensahe",
        "friends_add":            "IDAGDAG",
        "friends_added":          "Kaibigan na",
        "friends_remove":         "Alisin",
        "friends_request_sent":   "Nag-send ng request kay",
        "friends_chat_with":      "Makipagusap kay",
        "friends_chat_empty":     "Wala pa. Say hi!",

        # ── Library view ─────────────────────────────────────────────────────
        "library_title":      "LIBRARY",
        "library_tab_saved":  "Na-save",
        "library_tab_fav":    "Paborito",
        "library_tab_recent": "Pinakabago",
        "library_tab_played": "Nalaro",
        "library_empty":      "Wala pa rito.",
        "library_no_rating":  "Walang rating",
        "library_play":       "Laruin",
        "library_remove":     "Alisin",

        # ── Link / URL dialog ─────────────────────────────────────────────────
        "dialog_open_link": "Buksan ang link?",
        "dialog_cancel":    "Huwag na",
        "dialog_confirm":   "Ituloy",
    },

    "en": {
        # ── Nav bar ───────────────────────────────────────────────────────────
        "nav_store":      "Store",
        "nav_news":       "News",
        "nav_friends":    "Friends",
        "nav_library":    "Library",
        "nav_profile":    "Profile",

        # ── General ───────────────────────────────────────────────────────────
        "loading": "Loading...",

        # ── Auth view ─────────────────────────────────────────────────────────
        "auth_tagline":        "Home of Local Games",
        "auth_email":          "EMAIL",
        "auth_username":       "USERNAME",
        "auth_password":       "PASSWORD",
        "auth_display_name":   "DISPLAY NAME",
        "auth_stay_logged_in": "Stay logged in",
        "auth_login_btn":      "LOG IN",
        "auth_register_btn":   "REGISTER",
        "auth_create_account": "Create an Account",
        "auth_back_to_login":  "Back to Login",
        "auth_required_fields":"Email and Password are required.",
        "auth_login_failed":   "Login failed. Check your credentials.",
        "auth_registered":     "Account created! You can now log in.",

        # ── Profile view ──────────────────────────────────────────────────────
        "profile_title":  "MY PROFILE",
        "saved":          "Saved",
        "favorites":      "Favorites",
        "played":         "Played",
        "rated":          "Rated",
        "avg_rating":     "Avg Rating",
        "visited":        "Visited",
        "feedback_btn":   "Share Feedback",
        "logout_btn":     "Log out",
        "settings_title": "APP SETTINGS",
        "accent_label":   "Primary Accent",
        "lang_label":     "Language",
        "lang_toggle":    "Filipino",
        "feedback_title": "SHARE FEEDBACK",
        "feedback_sub":   "What can we improve?",
        "feedback_hint":  "Write your feedback...",
        "feedback_send":  "SEND",
        "feedback_thanks":"Thank you for your feedback! 🙏",

        # ── Store view ────────────────────────────────────────────────────────
        "store_title":          "SINAG STORE",
        "store_search_results": "SEARCH RESULTS",
        "store_pinoy_picks":    "PINOY PICKS",
        "store_made_in_ph":     "MADE IN PH",
        "store_search_hint":    "Search games...",
        "store_empty":          "No games found.",
        "store_save_btn":       "SAVE",
        "store_saved_btn":      "SAVED",
        "store_free":           "Free",
        "store_save_snack":     "Saved!",

        # ── Store detail / game modal ─────────────────────────────────────────
        "detail_favorite":    "Favorite",
        "detail_unfavorite":  "Favorited",
        "detail_played":      "Played",
        "detail_played_done": "Played",
        "detail_my_rating":   "My Rating:",
        "detail_rate_hint":   "Rate this game",
        "detail_store_page":  "STORE PAGE",
        "detail_close":       "CLOSE",

        # ── News view ─────────────────────────────────────────────────────────
        "news_title":           "PINOY DEV FEED",
        "news_live":            "LIVE",
        "news_featured":        "FEATURED",
        "news_latest":          "LATEST NEWS",
        "news_following_one":   "You're following 1 story.",
        "news_following_n":     "You're following {n} stories.",
        "news_follow":          "Follow",
        "news_unfollow":        "Following",
        "news_follow_snack":    "Now following! You'll be notified of updates.",
        "news_unfollow_snack":  "Unfollowed.",
        "news_empty":           "No news right now.",
        "news_view_steam":      "VIEW ON STEAM",
        "news_listen":          "LISTEN NOW",
        "news_view_post":       "VIEW POST",
        "news_watch":           "WATCH TRAILER",
        "news_read_more":       "READ MORE",
        "news_tag_release":     "RELEASE",
        "news_tag_reveal":      "REVEAL",
        "news_tag_trailer":     "TRAILER",
        "news_tag_update":      "UPDATE",
        "news_tag_community":   "COMMUNITY",

        # ── Friends view ──────────────────────────────────────────────────────
        "friends_title":          "FRIENDS",
        "friends_count_label":    "friends",
        "friends_count_one":      "1 friend",
        "friends_count_n":        "{n} friends",
        "friends_search_hint":    "Search by username...",
        "friends_search_btn":     "SEARCH",
        "friends_your_list":      "YOUR FRIENDS",
        "friends_requests_header":"FRIEND REQUESTS",
        "friends_wants_to_add":   "wants to be your friend",
        "friends_list_empty_hint":"Search above to add friends!",
        "friends_empty":          "No friends yet.",
        "friends_online":         "Online",
        "friends_offline":        "Offline",
        "friends_message":        "Message",
        "friends_add":            "ADD",
        "friends_added":          "Friends",
        "friends_remove":         "Remove",
        "friends_request_sent":   "Friend request sent to",
        "friends_chat_with":      "Chat with",
        "friends_chat_empty":     "Nothing yet. Say hi!",

        # ── Library view ─────────────────────────────────────────────────────
        "library_title":      "LIBRARY",
        "library_tab_saved":  "Saved",
        "library_tab_fav":    "Favorites",
        "library_tab_recent": "Recent",
        "library_tab_played": "Played",
        "library_empty":      "Nothing here yet.",
        "library_no_rating":  "No rating",
        "library_play":       "Play",
        "library_remove":     "Remove",

        # ── Link / URL dialog ─────────────────────────────────────────────────
        "dialog_open_link": "Open link?",
        "dialog_cancel":    "Cancel",
        "dialog_confirm":   "Continue",
    },
}


def t(app_state, key: str, **kwargs) -> str:
    """Translate a key using the current language stored in app_state.

    Supports simple format substitution:
        t(app_state, "friends_count_n", n=5)  ->  "5 kaibigan" / "5 friends"
    """
    lang = app_state.data.get("lang", "fil")
    text = APP_STRINGS.get(lang, APP_STRINGS["fil"]).get(key, key)
    return text.format(**kwargs) if kwargs else text
