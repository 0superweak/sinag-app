import flet as ft
from config import *
from supabase_client import SupabaseClient
from language import t as _t

# Added 'on_lang_change' to the arguments to match the call in main.py
def build_profile_view(page: ft.Page, app_state, on_logout, on_lang_change):
    saved_count  = len(app_state.data["owned"])
    fav_count    = len(app_state.data["favorites"])
    played_count = len(app_state.data["games_played"])
    rated_count  = len(app_state.data["ratings"])
    avg_rating   = round(sum(app_state.data["ratings"].values()) / rated_count, 1) if rated_count else 0
    # ... rest of your code remains the same

    def stat_tile(icon, label, value, color=C_TEXT):
        return ft.Container(
            bgcolor=C_BG2, border_radius=8, padding=12, expand=True,
            content=ft.Column([
                ft.Icon(icon, color=color, size=20),
                ft.Text(str(value), color=color, size=18, weight=ft.FontWeight.BOLD),
                ft.Text(label, color=C_DIM, size=10),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        )

    def open_settings_sheet(e):
        def change_color(color_hex):
            app_state.data["current_accent"] = color_hex
            page.theme = ft.Theme(color_scheme_seed=color_hex)
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Accent set to {color_hex}"), open=True))
            page.update()

        def toggle_lang(e):
            current = app_state.data.get("lang", "fil")
            app_state.data["lang"] = "en" if current == "fil" else "fil"
            app_state.sync()
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Language set to {_t(app_state, 'lang_toggle')}"), open=True))
            config_sheet.open = False
            page.update()
            on_lang_change()

        config_sheet = ft.BottomSheet(
            ft.Container(
                bgcolor=C_BG1, padding=20, border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                content=ft.Column([
                    ft.Text(_t(app_state, "settings_title"), color=app_state.data["current_accent"], size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(_t(app_state, "accent_label"), color=C_TEXT, size=12),
                    ft.Row([
                        ft.Container(width=30, height=30, bgcolor="#F4A823", border_radius=15, on_click=lambda _: change_color("#F4A823")),
                        ft.Container(width=30, height=30, bgcolor="#a3be8c", border_radius=15, on_click=lambda _: change_color("#a3be8c")),
                        ft.Container(width=30, height=30, bgcolor="#b48ead", border_radius=15, on_click=lambda _: change_color("#b48ead")),
                        ft.Container(width=30, height=30, bgcolor="#66c0f4", border_radius=15, on_click=lambda _: change_color("#66c0f4")),
                        ft.Container(width=30, height=30, bgcolor="#e86c6c", border_radius=15, on_click=lambda _: change_color("#e86c6c")),
                    ], spacing=15),
                    ft.Divider(height=10, color=C_BORDER),
                    ft.Row([
                        ft.Text(_t(app_state, "lang_label"), color=C_TEXT, size=12),
                        ft.OutlinedButton(content=ft.Text(_t(app_state, "lang_toggle")), on_click=toggle_lang, height=30, style=ft.ButtonStyle(color=app_state.data["current_accent"])),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], tight=True, spacing=15),
            )
        )
        page.overlay.append(config_sheet)
        config_sheet.open = True
        page.update()

    def open_feedback_sheet(e):
        feedback_field = ft.TextField(
            hint_text="Isulat ang iyong feedback...",
            bgcolor=C_BG2, border_color=C_BORDER,
            multiline=True, min_lines=3, max_lines=5,
            text_size=13,
        )

        def submit_feedback(e):
            msg = feedback_field.value.strip()
            if not msg:
                return
            try:
                SupabaseClient.submit_feedback(app_state.data.get("user_id"), msg)
            except Exception:
                pass
            feedback_sheet.open = False
            page.overlay.append(ft.SnackBar(content=ft.Text("Salamat sa iyong feedback! 🙏"), open=True))
            page.update()

        feedback_sheet = ft.BottomSheet(
            ft.Container(
                bgcolor=C_BG1, padding=20,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                content=ft.Column([
                    ft.Text("IBAHAGI ANG FEEDBACK", color=app_state.data["current_accent"], size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Ano ang maaari naming pagbutihin?", color=C_DIM, size=12),
                    feedback_field,
                    ft.Button(
                        content=ft.Text("IPADALA", color=C_BG0, weight=ft.FontWeight.BOLD),
                        style=ft.ButtonStyle(bgcolor=app_state.data["current_accent"]),
                        width=float("inf"),
                        on_click=submit_feedback,
                    ),
                ], tight=True, spacing=12),
            )
        )
        page.overlay.append(feedback_sheet)
        feedback_sheet.open = True
        page.update()

    recent_count = len(app_state.data.get("recents", []))

    stats_row_1 = ft.Row(spacing=8, controls=[
        stat_tile(ft.Icons.BOOKMARK, "Na-save", saved_count, app_state.data["current_accent"]),
        stat_tile(ft.Icons.FAVORITE, "Paborito", fav_count, C_RED),
        stat_tile(ft.Icons.SPORTS_ESPORTS, "Nalaro", played_count, "#a3be8c"),
    ])

    stats_row_2 = ft.Row(spacing=8, controls=[
        stat_tile(ft.Icons.STAR, "Na-rate", rated_count, C_GOLD),
        stat_tile(ft.Icons.GRADE, "Avg Rating", f"{avg_rating:.1f}" if rated_count else "—", C_GOLD),
        stat_tile(ft.Icons.HISTORY, "Binisita", recent_count, C_DIM),
    ])

    return ft.Container(
        padding=20,
        content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16, controls=[
            ft.Row([
                ft.Text("AKING PROFILE", color=app_state.data["current_accent"], size=12, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.SETTINGS, icon_color=app_state.data["current_accent"], on_click=open_settings_sheet),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Container(
                    width=60, height=60, bgcolor=app_state.data["current_accent"], border_radius=30,
                    content=ft.Text((app_state.data["user"] or "?")[0].upper(), color=C_BG0, weight=ft.FontWeight.BOLD, size=20),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(app_state.data["display_name"], color=C_TEXT, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"@{app_state.data['user']}", color=C_DIM, size=12),
                ]),
            ]),
            ft.Divider(color=C_BORDER),
            stats_row_1,
            stats_row_2,
            ft.Divider(color=C_BORDER),
            ft.Button(
                content=ft.Row([ft.Icon(ft.Icons.FEEDBACK_OUTLINED, color=app_state.data["current_accent"], size=16), ft.Text("Ibahagi ang Feedback", color=app_state.data["current_accent"], weight=ft.FontWeight.BOLD)], tight=True, spacing=8),
                width=float("inf"),
                on_click=open_feedback_sheet,
            ),
            ft.Button(
                content=ft.Text("Mag-logout", color=C_RED, weight=ft.FontWeight.BOLD),
                width=float("inf"),
                on_click=lambda _: on_logout(),  # This matches your argument 'on_logout'
            ),
        ]),
    )
