import flet as ft
import threading
from config import *
from supabase_client import SupabaseClient

def build_news_view(page: ft.Page, app_state, rebuild_cb):

    def open_link(url):
        # Use a confirmation dialog; close dialog first, then launch URL.
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Buksan ang link?", weight=ft.FontWeight.BOLD),
            content=ft.Text(url, color=C_DIM, size=11, selectable=True),
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def _close_dialog():
            dlg.open = False
            page.update()

        async def _confirm(e):
            _close_dialog()
            await page.launch_url(url, web_popup_window_name="_blank")

        def _cancel(e):
            _close_dialog()

        dlg.actions = [
            ft.TextButton("Huwag na", on_click=_cancel),
            ft.FilledButton("Buksan", on_click=_confirm),
        ]
        
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def _is_followed(news_id):
        return news_id in app_state.data["followed_news"]

    def _toggle_follow(news_id, news_title, e):
        # Stop the tap from bubbling up to the card's on_click (which opens the link)
        e.stop_propagation = True

        if news_id in app_state.data["followed_news"]:
            app_state.data["followed_news"].discard(news_id)
            page.overlay.append(ft.SnackBar(content=ft.Text("Hindi na sinusundan."), open=True))
        else:
            app_state.data["followed_news"].add(news_id)
            page.overlay.append(ft.SnackBar(content=ft.Text("Sinusundan na! Maabisuhan ka sa mga updates."), open=True))
            # Send a test follow-notification email to the logged-in user
            def _send_email():
                try:
                    user_id = app_state.data.get("user_id")
                    if user_id:
                        profile = SupabaseClient.get_profile(user_id)
                        email = profile.get("email") if profile else None
                        if email:
                            SupabaseClient.send_follow_notification(email, news_title)
                except Exception as ex:
                    print(f"[NEWS] Email notification failed: {ex}")
            threading.Thread(target=_send_email, daemon=True).start()

        app_state.sync()
        rebuild_cb()

    def news_card(news_id, tag, tag_color, title, body, cta_icon, cta_label, cta_color, url, img_emoji=""):
        followed = _is_followed(news_id)

        follow_btn = ft.Container(
            content=ft.Row([
                ft.Text("🔔" if followed else "🔕", size=12),
                ft.Text("Following" if followed else "Follow", size=10, color=app_state.data["current_accent"] if followed else C_DIM, weight=ft.FontWeight.BOLD),
            ], spacing=4, tight=True),
            bgcolor=app_state.data["current_accent"] + "22" if followed else C_BG2,
            border_radius=6, padding=ft.Padding(8, 5, 8, 5),
            on_click=lambda e, nid=news_id, t=title: _toggle_follow(nid, t, e), ink=True,
        )

        return ft.Container(
            bgcolor=C_BG1, border_radius=12, border=ft.Border.all(1, app_state.data["current_accent"] + "88" if followed else C_BORDER),
            ink=True, on_click=lambda _, u=url: open_link(u), padding=0,
            content=ft.Column(spacing=0, controls=[
                ft.Container(
                    bgcolor=tag_color + "22", border_radius=ft.BorderRadius.only(top_left=12, top_right=12), padding=ft.Padding(14, 10, 14, 10),
                    content=ft.Row([
                        ft.Container(content=ft.Text(tag, size=9, color=tag_color, weight=ft.FontWeight.BOLD), bgcolor=tag_color + "33", border_radius=4, padding=ft.Padding(6, 3, 6, 3)),
                        ft.Row([ft.Text(img_emoji, size=20), follow_btn], spacing=8),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ),
                ft.Container(
                    padding=14,
                    content=ft.Column(spacing=8, controls=[
                        ft.Text(title, color=C_TEXT, size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(body, color=C_DIM, size=12),
                        ft.Row([
                            ft.Text(cta_icon, size=14, color=cta_color),
                            ft.Text(cta_label, size=11, color=cta_color, weight=ft.FontWeight.BOLD),
                        ], spacing=6),
                    ]),
                ),
            ]),
        )

    followed_count = len(app_state.data["followed_news"])
    follow_status = ft.Container(
        visible=followed_count > 0, bgcolor=app_state.data["current_accent"] + "18", border_radius=8, padding=ft.Padding(12, 8, 12, 8),
        content=ft.Row([
            ft.Text("🔔", size=14),
            ft.Text(f"Sinusundan mo ang {followed_count} balita.", color=app_state.data["current_accent"], size=11, weight=ft.FontWeight.BOLD),
        ], spacing=8),
    )

    featured = ft.Container(
        bgcolor=app_state.data["current_accent"] + "18", border_radius=14, border=ft.Border.all(1, app_state.data["current_accent"] + ("88" if _is_followed("bayani-featured") else "55")),
        padding=20, ink=True, on_click=lambda _: open_link("https://store.steampowered.com/app/1281400"),
        content=ft.Column(spacing=10, controls=[
            ft.Row([
                ft.Container(content=ft.Text("⭐ FEATURED", size=9, color=app_state.data["current_accent"], weight=ft.FontWeight.BOLD), bgcolor=app_state.data["current_accent"] + "22", border_radius=4, padding=ft.Padding(8, 3, 8, 3)),
                ft.Container(
                    content=ft.Row([
                        ft.Text("🔔" if _is_followed("bayani-featured") else "🔕", size=12),
                        ft.Text("Following" if _is_followed("bayani-featured") else "Follow", size=10, color=app_state.data["current_accent"] if _is_followed("bayani-featured") else C_DIM, weight=ft.FontWeight.BOLD),
                    ], spacing=4, tight=True),
                    bgcolor=app_state.data["current_accent"] + "22" if _is_followed("bayani-featured") else C_BG2,
                    border_radius=6, padding=ft.Padding(8, 5, 8, 5),
                    on_click=lambda e: _toggle_follow("bayani-featured", "Bayani: Kung Fu & Electronica", e), ink=True,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Bayani: Kung Fu & Electronica", color=C_TEXT, size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Ang Pinoy action-RPG na halo ng Filipino mythology at neon combat. May full controller support na.", color=C_DIM, size=12),
            ft.Row([
                ft.Text("🎮", size=16),
                ft.Text("VIEW ON STEAM", color=app_state.data["current_accent"], size=11, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=10, color=app_state.data["current_accent"]),
            ], spacing=6),
        ]),
    )

    return ft.Container(
        expand=True, padding=ft.Padding(14, 10, 14, 0),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=12,
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Text("PINOY DEV FEED", color=app_state.data["current_accent"], size=12, weight=ft.FontWeight.BOLD),
                        ft.Container(content=ft.Text("LIVE", size=9, color="#a3be8c", weight=ft.FontWeight.BOLD), bgcolor="#a3be8c22", border_radius=4, padding=ft.Padding(6, 2, 6, 2)),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding(0, 0, 0, 4),
                ),
                follow_status, featured,
                ft.Text("PINAKABAGONG BALITA", color=C_DIM, size=10, weight=ft.FontWeight.BOLD),
                news_card("until-then-ost", "RELEASE", "#a3be8c", "Until Then — Full OST Now Streaming", "Polychroma Games drops the complete soundtrack. 34 original tracks by Filipino artists.", "♫", "LISTEN NOW", "#a3be8c", "https://open.spotify.com", "🎵"),
                news_card("prince-of-ibalong", "REVEAL", app_state.data["current_accent"], "The Prince of Ibalong — Official Reveal", "Action-adventure mula sa Bicolano epic mythology. Mag-wishlist na!", "🌐", "VIEW POST", "#1877F2", "https://facebook.com", "🏔"),
                news_card("lost-and-found", "TRAILER", C_RED, "Lost & Found — Announcement Trailer", "Narrative puzzle game tungkol sa pamilya at alaala.", "▶", "WATCH TRAILER", C_RED, "https://youtube.com", "🔍"),
                news_card("anito-legends-s3", "UPDATE", "#b48ead", "Anito Legends Season 3 Patch Notes", "Bagong hero Diwata, ranked overhaul, at performance fixes.", "📋", "READ PATCH NOTES", "#b48ead", "https://anito.gg", "⚔"),
                news_card("ggj-ph-2026", "COMMUNITY", "#ebcb8b", "Global Game Jam PH 2026 — Recap", "Mahigit 200 Filipino devs sa 8 lungsod. Tingnan ang mga winner!", "🏆", "SEE WINNERS", "#ebcb8b", "https://globalgamejam.org", "🎮"),
                ft.Container(height=20),
            ],
        )
    )