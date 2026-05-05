from backend import trace
import flet as ft
import threading
import random
import time
from config import *
from steam_api import SteamAPI
from supabase_client import SupabaseClient


def build_store_view(page: ft.Page, app_state):
    store_grid = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=12)

    # ── Search Logic ────────────────────────────────────────────────────────
    def handle_typing(e):
        app_state.data["search_active"] = False
        render_store_items(e.control.value.lower())

    def execute_global_search(term):
        if not term:
            app_state.data["search_active"] = False
            render_store_items()
            return
        store_grid.controls.clear()
        store_grid.controls.append(search_container)
        store_grid.controls.append(
            ft.Container(content=ft.ProgressRing(color=app_state.data["current_accent"]), alignment=ft.Alignment(0, 0),
                         padding=40)
        )
        page.update()
        app_state.data["search_active"] = True

        def _search_thread():
            results = []
            safe_term = term.replace(" ", "+")
            search_url = f"https://store.steampowered.com/api/storesearch/?term={safe_term}&l=english&cc=ph"
            try:
                # 1. Try Steam search
                search_res = SteamAPI.fetch(search_url)
                if search_res and search_res.get("items"):
                    matched_ids = [item["id"] for item in search_res["items"][:10]]
                    results = app_state.fetch_software_batch(matched_ids)
            except Exception:
                pass

            # 2. Try IGDB search and merge results
            try:
                igdb_results = app_state.search_igdb(term)
                if igdb_results:
                    # Filter out duplicates if any (by name)
                    existing_names = [r["name"].lower() for r in results]
                    for ir in igdb_results:
                        if ir["name"].lower() not in existing_names:
                            results.append(ir)
            except Exception:
                pass

            if not results:
                matched_apps = [app for app in app_state.data["master_list"] if
                                app.get("name") and term in app["name"].lower()]
                matched_apps.sort(key=lambda x: (x["name"].lower() != term, len(x["name"])))
                results = app_state.fetch_software_batch([app["appid"] for app in matched_apps[:5]])

            app_state.data["search_results"] = results

            # FIX: UI update goes through run_task, not directly from thread.
            async def _ui():
                try:
                    render_store_items()
                except RuntimeError:
                    pass

            page.run_task(_ui)

        threading.Thread(target=_search_thread, daemon=True).start()

    search_field = ft.TextField(
        hint_text="Hanapin ang catalog...", bgcolor=C_BG2, border_color=C_BORDER,
        on_change=handle_typing, on_submit=lambda e: execute_global_search(e.control.value.lower()),
        text_size=14, height=45,
    )
    search_container = ft.Container(padding=ft.Padding(15, 10, 15, 10), content=search_field)

    # ── Ratings & Details ───────────────────────────────────────────────────
    def _stars_str(val: float) -> str:
        full = int(val)
        half = (val - full) >= 0.5
        empty = 5 - full - (1 if half else 0)
        return "★" * full + ("½" if half else "") + "☆" * empty

    def build_star_row(app_id, size=18, on_rated=None):
        aid = str(app_id)
        current = float(app_state.data["ratings"].get(aid, 0))

        star_text = ft.Text(_stars_str(current) if current else "☆☆☆☆☆", size=size, color=C_GOLD)
        label_ref = ft.Text(f"  {current:.1f}/5" if current else "  I-rate ang laro", size=11,
                            color=C_GOLD if current else C_DIM, italic=not bool(current))

        def _rate(val):
            rounded = round(val * 2) / 2
            app_state.data["ratings"][aid] = rounded
            app_state.sync()
            star_text.value = _stars_str(rounded)
            label_ref.value = f"  {rounded:.1f}/5"
            label_ref.color = C_GOLD
            label_ref.italic = False
            if on_rated:
                on_rated()
            page.update()

        slider = ft.Slider(min=0, max=5, divisions=10, value=current, active_color=C_GOLD, thumb_color=C_GOLD,
                           on_change_end=lambda e: _rate(e.control.value), expand=True)
        return ft.Column([ft.Row([star_text, label_ref], spacing=2, tight=True), slider], spacing=0)

    def open_game_details(game_data):
        aid = str(game_data["app_id"])
        if aid in app_state.data["recents"]:
            app_state.data["recents"].remove(aid)
        app_state.data["recents"].insert(0, aid)
        if len(app_state.data["recents"]) > RECENTS_MAX:
            app_state.data["recents"] = app_state.data["recents"][:RECENTS_MAX]
        app_state.sync()

        def close_dialog(e):
            page.dialog.open = False
            page.update()

        async def open_external_store(e):
            # Do NOT close the dialog before launching — closing disrupts the
            # Flet session state and forces a re-login when the user returns.
            if game_data.get("source") == "IGDB" and game_data.get("external_url"):
                url = game_data["external_url"]
            else:
                url = f"https://store.steampowered.com/app/{aid}"
            await page.launch_url(url, web_popup_window_name="_blank")

        def toggle_fav_dlg(e):
            if aid in app_state.data["favorites"]:
                app_state.data["favorites"].discard(aid)
            else:
                app_state.data["favorites"].add(aid)
            app_state.sync()
            _refresh_action_row()
            render_store_items()
            page.update()

        def toggle_played_dlg(e):
            if aid in app_state.data["games_played"]:
                app_state.data["games_played"].discard(aid)
            else:
                app_state.data["games_played"].add(aid)
            app_state.sync()
            _refresh_action_row()
            render_store_items()
            page.update()

        fav_btn = ft.Container()
        played_btn = ft.Container()
        action_row = ft.Row([fav_btn, played_btn], spacing=8)

        def _refresh_action_row():
            is_fav = aid in app_state.data["favorites"]
            is_played = aid in app_state.data["games_played"]
            fav_btn.content = ft.Container(
                bgcolor=C_RED + "22" if is_fav else C_BG2, border=ft.Border.all(1, C_RED + "66"), border_radius=8,
                padding=ft.Padding(12, 8, 12, 8), ink=True, on_click=toggle_fav_dlg,
                content=ft.Row([ft.Text("❤" if is_fav else "♡", color=C_RED, size=14),
                                ft.Text("Paborito" if is_fav else "I-paborito", color=C_RED, size=11,
                                        weight=ft.FontWeight.BOLD)], spacing=4, tight=True)
            )
            played_btn.content = ft.Container(
                bgcolor=app_state.data["current_accent"] + "22" if is_played else C_BG2,
                border=ft.Border.all(1, app_state.data["current_accent"] + "66"), border_radius=8,
                padding=ft.Padding(12, 8, 12, 8), ink=True, on_click=toggle_played_dlg,
                content=ft.Row([ft.Text("🎮", size=14),
                                ft.Text("Nalaro na" if is_played else "Nalaro", color=app_state.data["current_accent"],
                                        size=11, weight=ft.FontWeight.BOLD)], spacing=4, tight=True)
            )

        _refresh_action_row()

        genre_row = ft.Row([
            ft.Container(content=ft.Text(g, size=9, color=app_state.data["current_accent"], weight=ft.FontWeight.BOLD),
                         bgcolor=app_state.data["current_accent"] + "18", border_radius=4,
                         padding=ft.Padding(6, 2, 6, 2))
            for g in game_data.get("genres", GAME_GENRES.get(aid, []))
        ], spacing=6, wrap=True)

        star_row = build_star_row(aid, size=22, on_rated=lambda: render_store_items())

        details_dlg = ft.AlertDialog(
            bgcolor=C_BG1, title=ft.Text(game_data["name"], color=C_TEXT, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Container(
                    content=ft.Image(src=game_data["img"], height=160, fit=ft.BoxFit.COVER, expand=True),
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                ft.Container(height=5),
                genre_row,
                ft.Text(game_data["desc"], color=C_DIM, size=12),
                ft.Container(height=4), action_row, ft.Container(height=4),
                ft.Row([ft.Text("Rating mo:", color=C_DIM, size=11)]), star_row,
            ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton(
                    content=ft.Text("VIEW ON IGDB" if game_data.get("source") == "IGDB" else "VIEW ON STEAM",
                                    color=C_TEXT),
                    on_click=open_external_store
                ),
                ft.TextButton(content=ft.Text("ISARA", color=app_state.data["current_accent"]), on_click=close_dialog),
            ],
        )
        page.dialog = details_dlg
        details_dlg.open = True
        page.update()

    # ── Store Rendering ─────────────────────────────────────────────────────
    def _build_genre_filter_row():
        chips = []
        for g in ALL_GENRES:
            is_active = app_state.data["genre_filter"] == g

            def _on_chip(e, _g=g):
                app_state.data["genre_filter"] = _g
                render_store_items(search_field.value.lower() if search_field.value else "")

            chips.append(
                ft.Container(
                    content=ft.Text(g, size=11, color=C_BG0 if is_active else C_DIM, weight=ft.FontWeight.BOLD),
                    bgcolor=app_state.data["current_accent"] if is_active else C_BG2, border_radius=20,
                    padding=ft.Padding(12, 6, 12, 6), on_click=_on_chip, ink=True,
                )
            )
        return ft.Container(padding=ft.Padding(12, 6, 12, 6),
                            content=ft.Row(chips, scroll=ft.ScrollMode.AUTO, spacing=8))

    def _build_store_card(g):
        aid = str(g["app_id"])
        is_owned = aid in app_state.data["owned"]

        def save_game(e=None, _aid=aid):
            app_state.data["owned"].add(_aid)
            app_state.sync()
            page.overlay.append(ft.SnackBar(content=ft.Text("Nai-save na!"), open=True))
            render_store_items()
            page.update()

        def show_confirm_save(e, game_name):
            e.stop_propagation = True
            def close_dlg(e_dlg):
                confirm_dlg.open = False
                page.update()

            confirm_dlg = ft.AlertDialog(
                bgcolor=C_BG1,
                title=ft.Text("I-save ang laro?", weight=ft.FontWeight.BOLD),
                content=ft.Text(f"Gusto mo bang idagdag ang {game_name} sa iyong library?", size=12, color=C_TEXT),
                actions=[
                    ft.TextButton("Huwag na", on_click=close_dlg),
                    ft.ElevatedButton(
                        "Ituloy", 
                        bgcolor=app_state.data["current_accent"],
                        color=C_BG0,
                        on_click=lambda evt: (save_game(), close_dlg(None))
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(confirm_dlg)
            confirm_dlg.open = True
            page.update()

        user_rating = app_state.data["ratings"].get(aid, 0)
        rating_display = ft.Text(f"★ {float(user_rating):.1f}/5" if user_rating else g.get("rating", ""), color=C_GOLD, size=11,
                                 weight=ft.FontWeight.BOLD)

        pinoy_badge = ft.Container(
            content=ft.Text("🇵🇭 MADE IN PH", size=9, weight=ft.FontWeight.BOLD, color=C_BG0),
            bgcolor=app_state.data["current_accent"], border_radius=4, padding=ft.Padding(6, 2, 6, 2),
            visible=aid in FILIPINO_IDS
        )

        igdb_badge = ft.Container(
            content=ft.Text("IGDB", size=9, weight=ft.FontWeight.BOLD, color=C_BG0),
            bgcolor=C_DIM, border_radius=4, padding=ft.Padding(6, 2, 6, 2),
            visible=g.get("source") == "IGDB"
        )

        genres = g.get("genres", GAME_GENRES.get(aid, []))
        genre_chips = ft.Row([ft.Container(content=ft.Text(gn, size=8, color=C_DIM), bgcolor=C_BG2, border_radius=3,
                                           padding=ft.Padding(4, 1, 4, 1)) for gn in genres[:3]],
                             spacing=4) if genres else ft.Container()

        return ft.Container(
            bgcolor=C_BG1, border_radius=12, border=ft.Border.all(1, C_BORDER), margin=ft.Margin(12, 0, 12, 0),
            ink=True,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_click=lambda e, gd=g: open_game_details(gd),
            content=ft.Column(spacing=0, controls=[
                ft.Container(
                    content=ft.Image(src=g.get("img", ""), height=160, fit=ft.BoxFit.COVER, expand=True),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                ft.Container(
                    padding=12,
                    content=ft.Column(spacing=6, controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Column(expand=True, controls=[
                                ft.Row(
                                    [ft.Text(g.get("name", ""), color=C_TEXT, size=14, weight=ft.FontWeight.BOLD, no_wrap=True),
                                     pinoy_badge, igdb_badge]),
                                ft.Row([ft.Text(g.get("price", ""), color=app_state.data["current_accent"], size=12,
                                                weight=ft.FontWeight.BOLD), rating_display]),
                                genre_chips,
                            ]),
                            ft.Button(
                                content=ft.Text("NAKASAVE" if is_owned else "I-SAVE",
                                                color=C_BG0 if not is_owned else C_DIM, weight=ft.FontWeight.BOLD),
                                style=ft.ButtonStyle(
                                    bgcolor=app_state.data["current_accent"] if not is_owned else C_BG2),
                                on_click=lambda evt, gn=g.get("name", ""): show_confirm_save(evt, gn) if not is_owned else None,
                            ),
                        ])
                    ])
                )
            ])
        )

    def render_store_items(filter_term=""):
        store_grid.controls.clear()
        store_grid.controls.append(search_container)
        store_grid.controls.append(_build_genre_filter_row())

        header_title = "GLOBAL SEARCH RESULTS" if app_state.data["search_active"] else "VAPOR STORE"
        store_grid.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(header_title, color=app_state.data["current_accent"], size=12, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        visible=not app_state.data["search_active"],
                        content=ft.Container(
                            content=ft.Text("🇵🇭 PINOY PICKS", size=9, weight=ft.FontWeight.BOLD, color=C_BG0),
                            bgcolor=app_state.data["current_accent"], border_radius=4, padding=ft.Padding(6, 3, 6, 3)),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding(15, 5, 15, 5),
            )
        )

        if app_state.data["search_active"]:
            display_list = app_state.data["search_results"]
        else:
            gf = app_state.data["genre_filter"]
            display_list = [
                g for g in app_state.data["all_games"]
                if filter_term in g["name"].lower() and (
                            gf == "All" or gf in g.get("genres", GAME_GENRES.get(str(g["app_id"]), [])))
            ]

        for g in display_list:
            store_grid.controls.append(_build_store_card(g))

        if not display_list and not app_state.data["is_loading"]:
            store_grid.controls.append(
                ft.Container(
                    padding=40, alignment=ft.Alignment(0, 0),
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, color=C_DIM, size=40),
                        ft.Text("Walang nahanap na laro.", color=C_DIM, size=12),
                        ft.Text("Subukan pindutin ang 'Enter' para sa Global Search.",
                                color=app_state.data["current_accent"], size=10),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )

        if app_state.data["is_loading"]:
            store_grid.controls.append(
                ft.Container(ft.ProgressRing(color=app_state.data["current_accent"]), alignment=ft.Alignment(0, 0),
                             padding=20))

        try:
            page.update()
        except Exception:
            pass

    # ── Data Loading ────────────────────────────────────────────────────────
    def load_initial_store():
        trace("load_initial_store triggered.", "STORE")
        app_state.data["is_loading"] = True
        render_store_items()
        trace("Initial spinner rendered.", "STORE")

        def _fetch_thread():
            trace("Fetch thread started.", "STORE_API")

            try:
                trace("Pinging Steam for master list...", "STORE_API")
                res = SteamAPI.fetch("https://api.steampowered.com/IStoreService/GetAppList/v1/?max_results=50000",
                                     use_auth=True)
                apps = res.get("response", {}).get("apps", [])
                if apps:
                    app_state.data["master_list"] = apps
                    app_state.data["master_ids"] = [app["appid"] for app in apps]
                    random.shuffle(app_state.data["master_ids"])
                    trace(f"Master list loaded: {len(apps)} games found.", "STORE_API")
                else:
                    app_state.data["master_ids"] = FALLBACK_IDS
            except Exception as e:
                trace(f"Master list fetch failed: {e}", "STORE_API")
                app_state.data["master_ids"] = FALLBACK_IDS

            try:
                trace("Fetching Filipino curated games...", "STORE_API")
                db_pinoy_ids = SupabaseClient.get_curated_pinoy_ids()
                combined_pinoy_ids = list(set(FILIPINO_IDS + db_pinoy_ids))

                trace(
                    f"Fetching {len(combined_pinoy_ids)} games (This will take {len(combined_pinoy_ids) * 1.5} seconds...)",
                    "STORE_API")
                app_state.data["all_games"] = app_state.fetch_software_batch(combined_pinoy_ids)
                trace("Curated games successfully loaded!", "STORE_API")

            except Exception as e:
                trace(f"Failed to fetch curated games: {e}", "STORE_API")
                app_state.data["all_games"] = []
            finally:
                trace("Fetch complete. Removing spinner.", "STORE")
                app_state.data["is_loading"] = False

                # FIX: UI update goes through run_task so Flet's render cycle
                # isn't driven from a background thread, which was causing
                # spurious scroll events that retriggered loading.
                async def _ui():
                    try:
                        render_store_items()
                    except RuntimeError:
                        pass

                page.run_task(_ui)

        threading.Thread(target=_fetch_thread, daemon=True).start()

    def load_more_software(e):
        if not app_state.data["search_active"] and not app_state.data[
            "is_loading"] and e.pixels >= e.max_scroll_extent - 400:
            app_state.data["is_loading"] = True
            render_store_items()

            # Capture scroll position now before handing off to thread.
            _scroll_pos = e.pixels

            def _scroll_thread():
                try:
                    start = app_state.data["batch_index"] * 15
                    new_batch = app_state.fetch_software_batch(app_state.data["master_ids"][start:start + 15])
                    if new_batch:
                        app_state.data["all_games"].extend(new_batch)
                        app_state.data["batch_index"] += 1
                finally:
                    app_state.data["is_loading"] = False

                    # FIX: Run UI work on the main thread, then pull the
                    # scroll position back above the trigger threshold so
                    # page.update() doesn't immediately re-fire on_scroll
                    # and kick off another infinite load cycle.
                    async def _ui():
                        try:
                            render_store_items()
                            if store_grid.page:
                                await store_grid.scroll_to(offset=_scroll_pos - 600, duration=0)
                        except RuntimeError:
                            pass  # Ignore if session was closed while loading

                    page.run_task(_ui)

            threading.Thread(target=_scroll_thread, daemon=True).start()

    store_grid.on_scroll = load_more_software

    # Boot sequence
    if not app_state.data["all_games"]:
        load_initial_store()
    else:
        render_store_items()

    return store_grid