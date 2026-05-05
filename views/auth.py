import flet as ft
import os
import threading
from config import *
from supabase_client import SupabaseClient

# ── 1. ONBOARDING CAROUSEL ───────────────────────────────────────────────────
def build_onboarding_view(page: ft.Page, app_state, on_finish):
    slide_state = {"idx": 0}
    slides = [
        {
            "emoji": "Mabuhay!", "title": "Maligayang pagdating sa Sinag",
            "body": "Ang iyong tahanan para sa larong gawa ng mga Pinoy.\n\nIbinibida ang husay ng mga lokal na developer.",
            "btn": "NEXT →", "btn2": "Huwag nang ipakita",
        },
        {
            "emoji": "🔔", "title": "Manatiling Updated",
            "body": "Alamin agad ang mga bagong Larong Pinoy, patch notes, at community events.",
            "btn": "I-ON ANG NOTIFICATIONS", "btn2": "Mamaya na",
        },
        {
            "emoji": "🚀", "title": "Handa na!",
            "body": "Tuklasin, i-save, at i-rate ang mga Larong Pinoy.\n\nMag-login na para magsimula.",
            "btn": "MAGSIMULA", "btn2": None,
        },
    ]

    emoji_ref   = ft.Text("", size=38, weight=ft.FontWeight.BOLD, color=app_state.data["current_accent"], text_align=ft.TextAlign.CENTER)
    title_ref   = ft.Text("", size=26, weight=ft.FontWeight.BOLD, color=C_TEXT, text_align=ft.TextAlign.CENTER)
    body_ref    = ft.Text("", size=14, color=C_DIM, text_align=ft.TextAlign.CENTER)
    primary_btn = ft.Container()
    skip_btn    = ft.Container()
    dot_row     = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8)

    slide_col = ft.Column(
        [emoji_ref, ft.Container(height=16), title_ref, ft.Container(height=12), body_ref],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
    )

    def _dots(active):
        dot_row.controls.clear()
        for d in range(len(slides)):
            dot_row.controls.append(
                ft.Container(
                    width=24 if d == active else 8, height=8,
                    bgcolor=app_state.data["current_accent"] if d == active else C_BG2,
                    border_radius=4, animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
                )
            )

    def _finish_onboarding(e=None):
        flag_path = os.path.join(os.path.expanduser("~"), ".vapor_onboarded")
        try:
            with open(flag_path, "w") as _f: _f.write("1")
        except Exception: pass
        on_finish()

    def _go_next(e=None):
        if slide_state["idx"] < len(slides) - 1:
            slide_state["idx"] += 1
            _render_slide()
        else:
            _finish_onboarding()

    def _render_slide():
        s = slides[slide_state["idx"]]
        idx = slide_state["idx"]
        emoji_ref.value = s["emoji"]
        title_ref.value = s["title"]
        body_ref.value  = s["body"]
        _dots(idx)
        primary_btn.content = ft.Button(
            content=ft.Text(s["btn"], color=C_BG0, weight=ft.FontWeight.BOLD, size=14),
            style=ft.ButtonStyle(bgcolor=app_state.data["current_accent"], padding=ft.Padding(32, 14, 32, 14)),
            on_click=_go_next,
        )
        if s["btn2"]:
            skip_btn.content = ft.TextButton(content=ft.Text(s["btn2"], color=C_DIM, size=13), on_click=_finish_onboarding)
            skip_btn.visible = True
        else:
            skip_btn.visible = False
        page.update()

    _render_slide()
    return ft.Container(
        expand=True, bgcolor=C_BG0, padding=ft.Padding(32, 60, 32, 40),
        content=ft.Column(
            expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.LIGHT_MODE, color=app_state.data["current_accent"], size=18),
                    ft.Text("S I N A G", size=15, color=app_state.data["current_accent"], weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([slide_col], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([dot_row, ft.Container(height=24), primary_btn, ft.Container(height=8), skip_btn], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ],
        ),
    )


# ── 2. LOGIN & REGISTRATION VIEW ─────────────────────────────────────────────
def build_login_view(page: ft.Page, app_state, on_login_success):
    email_input = ft.TextField(label="EMAIL", border_color=C_BORDER, bgcolor=C_BG2, width=300)
    user_input  = ft.TextField(label="USERNAME", border_color=C_BORDER, bgcolor=C_BG2, width=300, visible=False)
    pass_input  = ft.TextField(label="PASSWORD", password=True, can_reveal_password=True, border_color=C_BORDER, bgcolor=C_BG2, width=300)
    name_input  = ft.TextField(label="DISPLAY NAME", border_color=C_BORDER, bgcolor=C_BG2, width=300, visible=False)

    stay_logged_in = ft.Checkbox(label="Manatiling naka-login", value=False, active_color=app_state.data["current_accent"], label_style=ft.TextStyle(color=C_DIM, size=12))

    def toggle_mode(e):
        app_state.data["is_register_mode"] = not app_state.data["is_register_mode"]
        user_input.visible  = app_state.data["is_register_mode"]
        name_input.visible  = app_state.data["is_register_mode"]
        stay_logged_in.visible = not app_state.data["is_register_mode"]
        login_btn.content.value = "MAG-PAREHISTRO" if app_state.data["is_register_mode"] else "PUMASOK"
        reg_lnk.content.value  = "Bumalik sa Login" if app_state.data["is_register_mode"] else "Gumawa ng Account"
        page.update()

    def login_or_register(e):
        if not email_input.value or not pass_input.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Email at Password ay kailangan."), open=True))
            page.update()
            return

        login_btn.disabled = True
        orig_content = login_btn.content
        login_btn.content = ft.ProgressRing(width=20, height=20, color=C_BG0, stroke_width=2)
        page.update()

        # FIX: Capture input values before entering the thread so we don't
        # touch Flet controls from a background thread.
        _email = email_input.value.strip()
        _pass  = pass_input.value.strip()
        _stay  = stay_logged_in.value
        _uname = user_input.value.lower().strip() if user_input.value else "user"
        _dname = name_input.value.strip() or user_input.value.strip()

        def _auth_thread():
            login_success = False
            try:
                if not app_state.data["is_register_mode"]:
                    user = SupabaseClient.log_in(_email, _pass)
                    if user:
                        # FIX: Schedule the entire UI transition on the main
                        # event loop via page.run_task so Flet's render cycle
                        # isn't driven from a background thread.
                        async def _enter():
                            on_login_success(user, _email, _pass, _stay)
                        page.run_task(_enter)
                        login_success = True
                    else:
                        async def _fail():
                            page.overlay.append(ft.SnackBar(content=ft.Text("Nabigo ang login. Suriin ang credentials."), open=True))
                            page.update()
                        page.run_task(_fail)
                else:
                    user = SupabaseClient.sign_up(
                        email=_email, password=_pass,
                        username=_uname,
                        display_name=_dname,
                    )
                    if user:
                        async def _reg():
                            page.overlay.append(ft.SnackBar(content=ft.Text("Nalikha ang Account! Maaari ka nang mag-login."), open=True))
                            toggle_mode(None)
                        page.run_task(_reg)
            finally:
                if not login_success:
                    # FIX: Reset button state via run_task, not directly from thread.
                    async def _reset():
                        login_btn.disabled = False
                        login_btn.content  = orig_content
                        page.update()
                    page.run_task(_reset)

        threading.Thread(target=_auth_thread, daemon=True).start()

    login_btn = ft.Button(content=ft.Text("PUMASOK", color=C_BG0, weight=ft.FontWeight.BOLD), style=ft.ButtonStyle(bgcolor=app_state.data["current_accent"]), width=300, on_click=login_or_register)
    reg_lnk = ft.TextButton(content=ft.Text("Gumawa ng Account", color=app_state.data["current_accent"]), on_click=toggle_mode)

    return ft.Container(
        expand=True, bgcolor=C_BG0, alignment=ft.Alignment(0, 0), padding=ft.Padding(0, 40, 0, 20),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Row([ft.Icon(ft.Icons.LIGHT_MODE, color=app_state.data["current_accent"], size=36), ft.Text("S I N A G", size=32, weight=ft.FontWeight.BOLD, color=app_state.data["current_accent"])], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("Tahanan ng Larong Lokal", color=C_DIM, size=12),
                ft.Container(height=10),
                user_input, name_input, email_input, pass_input,
                ft.Container(content=stay_logged_in, width=300),
                login_btn, reg_lnk,
            ]
        ),
    )
