import flet as ft
from config import *

def build_library_view(page: ft.Page, app_state):
    sub_tabs  = ["Na-save", "Paborito", "Pinakabago", "Nalaro"]
    tab_icons = [ft.Icons.BOOKMARK, ft.Icons.FAVORITE, ft.Icons.HISTORY, ft.Icons.SPORTS_ESPORTS]
    lib_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def _game_by_id(app_id):
        aid = str(app_id)
        return next((g for g in app_state.data["all_games"] if str(g["app_id"]) == aid), None)

    def _get_games_for_tab(idx):
        if idx == 0: return [g for g in app_state.data["all_games"] if str(g["app_id"]) in app_state.data["owned"]]
        elif idx == 1: return [g for g in app_state.data["all_games"] if str(g["app_id"]) in app_state.data["favorites"]]
        elif idx == 2: return [g for g in [_game_by_id(aid) for aid in app_state.data["recents"]] if g]
        elif idx == 3: return [g for g in app_state.data["all_games"] if str(g["app_id"]) in app_state.data["games_played"]]
        return []

    def refresh_lib_list(idx=None):
        if idx is not None:
            app_state.data["lib_tab"] = idx

        games = _get_games_for_tab(app_state.data["lib_tab"])
        lib_list.controls.clear()

        if not games:
            lib_list.controls.append(ft.Container(content=ft.Text("Wala pa rito.", color=C_DIM, italic=True, size=13), padding=20))
        else:
            for g in games:
                aid = str(g["app_id"])
                user_stars = app_state.data["ratings"].get(aid, 0)
                star_label = f"★ {float(user_stars):.1f}/5" if user_stars else "Walang rating"

                lib_list.controls.append(
                    ft.Container(
                        bgcolor=C_BG1, padding=10, border_radius=8, border=ft.Border.all(1, C_BORDER),
                        content=ft.Row([
                            ft.Image(src=g["img"], width=100, height=56, fit=ft.BoxFit.COVER, border_radius=4),
                            ft.Column([
                                ft.Text(g["name"], color=C_TEXT, weight=ft.FontWeight.BOLD, no_wrap=True, width=110),
                                ft.Text(star_label, color=C_GOLD, size=11),
                            ], width=115, spacing=2),
                        ])
                    )
                )
        page.update()

    tab_bar_controls = []
    for i, (label, icon) in enumerate(zip(sub_tabs, tab_icons)):
        tab_bar_controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(icon, color=app_state.data["current_accent"] if i == app_state.data["lib_tab"] else C_DIM, size=18),
                    ft.Text(label, size=9, color=app_state.data["current_accent"] if i == app_state.data["lib_tab"] else C_DIM, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                on_click=lambda e, _i=i: refresh_lib_list(_i),
                padding=ft.Padding(12, 6, 12, 6), ink=True,
            )
        )

    tab_row = ft.Container(bgcolor=C_BG2, border=ft.Border(bottom=ft.BorderSide(1, C_BORDER)), content=ft.Row(tab_bar_controls, alignment=ft.MainAxisAlignment.SPACE_AROUND))
    refresh_lib_list()

    return ft.Column(expand=True, spacing=0, controls=[
        ft.Container(ft.Text("LIBRARY", color=app_state.data["current_accent"], size=12, weight=ft.FontWeight.BOLD), padding=ft.Padding(15, 14, 15, 6)),
        tab_row,
        ft.Container(content=lib_list, expand=True, padding=10),
    ])
