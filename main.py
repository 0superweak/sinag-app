import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="supabase_auth|supabase")

import os
print(os.path.abspath("wlm_users.txt"))

# main.py
import flet as ft
import os
import threading
import time
from config import *
from backend import AppState, trace
from supabase_client import SupabaseClient

# Import your split UI modules
from views.auth import build_login_view, build_onboarding_view
from splash import build_splash_screen
from views.store import build_store_view
from views.news import build_news_view
from views.friends import build_friends_view
from views.library import build_library_view
from views.profile import build_profile_view

def main(page: ft.Page):
    # ── App Configuration ───────────────────────────────────────────────────
    page.title      = "Sinag"
    page.bgcolor    = C_BG0
    page.theme_mode = ft.ThemeMode.DARK
    page.padding    = 0
    page.theme      = ft.Theme(color_scheme_seed=C_ACCENT)

    app_state = AppState(page)
    main_content = ft.Column(expand=True)

    # ── Diagnostics ─────────────────────────────────────────────────────────
    def _heartbeat():
        while True:
            trace("❤️ Python is alive", "HEARTBEAT")
            time.sleep(2)

    threading.Thread(target=_heartbeat, daemon=True, name="Heartbeat").start()

    # ── State Methods ───────────────────────────────────────────────────────
    def handle_logout():
        trace("Logging out user...", "AUTH")
        if app_state.data.get("user_id"):
            SupabaseClient.update_status(app_state.data["user_id"], "Offline")

        app_state.clear_session()

        # Reset core state
        app_state.data.update({
            "user_id": None, "user": None, "pass": None,
            "owned": set(), "favorites": set(), "recents": [],
            "ratings": {}, "games_played": set(), "followed_news": set(),
            "all_games": [], "current_tab": 0
        })
        show_login()

    def show_login():
        page.controls.clear()
        page.add(login_view)
        page.update()

    def _enter_app(user, email, password, stay_logged_in):
        trace("User authenticated, entering app shell...", "ROUTER")
        try:
            profile = SupabaseClient.get_profile(user.id)
            dname = profile.get("display_name", email.split("@")[0]) if profile else email.split("@")[0]
            uname = profile.get("username", email.split("@")[0]) if profile else email.split("@")[0]
        except Exception:
            dname = uname = email.split("@")[0]

        app_state.update({
            "user_id": user.id, "user": uname,
            "pass": password, "display_name": dname
        })

        # ── Restore flat-file state (owned, favorites, recents, ratings, played) ──
        try:
            from database import Database
            import json
            row = Database.login_user(uname, password)
            if row and len(row) >= 9:
                def _ids(s): return set(x for x in s.split(",") if x) if s else set()
                app_state.data["owned"]        = _ids(row[4])
                app_state.data["favorites"]    = _ids(row[5])
                app_state.data["recents"]      = [x for x in row[6].split(",") if x] if row[6] else []
                app_state.data["ratings"]      = json.loads(row[7]) if row[7] else {}
                app_state.data["games_played"] = _ids(row[8])
        except Exception as ex:
            trace(f"Failed to restore user data from DB: {ex}", "AUTH")

        if stay_logged_in:
            app_state.save_session(email, password)
        else:
            app_state.clear_session()

        app_state.load_followed_news()
        SupabaseClient.update_status(user.id, "Online")

        # Prep UI
        build_nav_buttons()
        page.controls.clear()
        page.add(app_shell)

        # ── THE FIX: Force the engine to paint the new app shell immediately ──
        page.update()

        trace("App shell added to screen.", "ROUTER")

        trace("Calling navigate(0)...", "ROUTER")
        navigate(0)

    # ── Navigation Router ───────────────────────────────────────────────────
    def navigate(idx):
        trace(f"Switching to tab {idx}...", "ROUTER")
        app_state.data["current_tab"] = idx
        main_content.controls.clear()

        if idx == 0:
            main_content.controls.append(build_store_view(page, app_state))
        elif idx == 1:
            main_content.controls.append(build_news_view(page, app_state, lambda: navigate(1)))
        elif idx == 2:
            main_content.controls.append(build_friends_view(page, app_state, build_nav_buttons))
        elif idx == 3:
            main_content.controls.append(build_library_view(page, app_state))
        elif idx == 4:
            main_content.controls.append(build_profile_view(page, app_state, handle_logout, on_lang_change=build_nav_buttons))

        page.update()

    # ── Navigation Bar Component ────────────────────────────────────────────
    custom_nav_bar_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND)
    custom_nav_bar = ft.Container(
        bgcolor=C_BG1,
        border=ft.Border(top=ft.BorderSide(1, C_BORDER)),
        padding=ft.Padding(0, 10, 0, 12),
        content=custom_nav_bar_row,
    )

    def init_nav_bar():
        nav_items = [
            ("Tindahan", ft.Icons.STOREFRONT),
            ("Balita",   ft.Icons.NEWSPAPER),
            ("Kaibigan", ft.Icons.PEOPLE),
            ("Library",  ft.Icons.BOOKMARK),
            ("Profile",  ft.Icons.PERSON),
        ]
        app_state.data["nav_controls"] = []
        custom_nav_bar_row.controls.clear()

        for idx, (label_text, icon_dat) in enumerate(nav_items):
            icon_control = ft.Icon(icon_dat, color=C_DIM, size=22)
            icon_container = ft.Container(content=icon_control, scale=ft.Scale(1.0), animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT))
            badge_control = ft.Container(content=ft.Text("!", color=C_BG0, size=9, weight=ft.FontWeight.BOLD), bgcolor=C_RED, width=12, height=12, border_radius=6, alignment=ft.Alignment(0, 0), right=-4, top=-4, visible=False)
            label_control = ft.Text(label_text, size=9, color=C_DIM, weight=ft.FontWeight.BOLD)
            indicator_control = ft.Container(width=18, height=3, bgcolor="transparent", border_radius=2, animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT))

            app_state.data["nav_controls"].append({
                "icon": icon_control, "icon_container": icon_container,
                "label": label_control, "indicator": indicator_control, "badge": badge_control,
            })

            custom_nav_bar_row.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Stack([icon_container, badge_control]),
                        label_control, indicator_control,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    on_click=lambda e, i=idx: _nav_with_anim(i),
                    padding=ft.Padding(12, 6, 12, 6), ink=True, border_radius=20,
                )
            )

    def build_nav_buttons():
        if not app_state.data.get("nav_controls"):
            init_nav_bar()

        for idx, ctrl in enumerate(app_state.data["nav_controls"]):
            is_active  = (idx == app_state.data["current_tab"])
            is_pulsing = (idx == app_state.data["nav_anim_idx"])
            has_notif = (idx == 2 and len(app_state.data["unread_chats"]) > 0)

            accent = app_state.data["current_accent"]
            ctrl["icon"].color = accent if is_active else C_DIM
            ctrl["icon_container"].scale = ft.Scale(1.25 if is_pulsing else 1.0)
            ctrl["label"].color = accent if is_active else C_DIM
            ctrl["indicator"].bgcolor = accent if is_active else "transparent"
            ctrl["badge"].visible = has_notif

    def _nav_with_anim(idx):
        if app_state.data["current_tab"] == idx: return
        app_state.data["nav_anim_idx"] = idx
        app_state.data["current_tab"] = idx
        build_nav_buttons()
        page.update()
        navigate(idx)

        async def _clear_pulse():
            import asyncio
            await asyncio.sleep(0.15)
            app_state.data["nav_anim_idx"] = -1
            build_nav_buttons()
            custom_nav_bar.update()

        page.run_task(_clear_pulse)

    # ── App Shell Structure ─────────────────────────────────────────────────
    app_shell = ft.Container(
        expand=True, bgcolor=C_BG0, padding=ft.Padding(0, 44, 0, 0),
        content=ft.Column(
            expand=True, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(expand=True, width=480, content=ft.Column(expand=True, spacing=0, controls=[main_content, custom_nav_bar]))
            ],
        ),
    )

    login_view = build_login_view(page, app_state, _enter_app)

    # ── Boot Sequence ───────────────────────────────────────────────────────
    ONBOARD_FLAG = os.path.join(os.path.expanduser("~"), ".vapor_onboarded")
    is_first_run = not os.path.exists(ONBOARD_FLAG)

    if is_first_run:
        # ── First-time user: splash → onboarding → login ────────────────────
        def _on_splash_done_first():
            page.controls.clear()
            page.add(build_onboarding_view(page, app_state, show_login))
            page.update()

        splash = build_splash_screen(page, _on_splash_done_first)
        page.add(splash)

    else:
        # ── Returning user: splash → auto-login attempt or login screen ──────
        saved_email, saved_pass = app_state.load_session()
        _boot = {"user": None, "done": False, "splash_done": False}

        def _try_enter():
            if _boot["done"] and _boot["splash_done"]:
                if _boot["user"]:
                    _enter_app(_boot["user"], saved_email, saved_pass, True)
                else:
                    show_login()

        def _on_splash_done_returning():
            _boot["splash_done"] = True
            _try_enter()

        splash = build_splash_screen(page, _on_splash_done_returning)
        page.add(splash)

        if saved_email:
            def _boot_restore():
                try:
                    user = SupabaseClient.log_in(saved_email, saved_pass)
                    _boot["user"] = user
                except Exception:
                    _boot["user"] = None
                _boot["done"] = True

                # Guard: only schedule back onto the event loop if the Flet
                # session connection is still alive. If it's None the app
                # closed (or hasn't fully started) and there's nothing to do.
                try:
                    conn = page.session.connection if page.session else None
                    if conn is None or conn.loop is None:
                        return
                    import asyncio
                    async def _ui():
                        _try_enter()
                    conn.loop.call_soon_threadsafe(
                        lambda: asyncio.ensure_future(_ui(), loop=conn.loop)
                    )
                except Exception as ex:
                    print(f"[BOOT] Could not schedule _try_enter: {ex}")

            threading.Thread(target=_boot_restore, daemon=True).start()
        else:
            _boot["done"] = True

    page.update()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")