import flet as ft
import threading
import time
from config import *
from supabase_client import SupabaseClient

def build_friends_view(page: ft.Page, app_state, update_nav_callback=None):
    friends_list   = ft.Column(spacing=10)
    requests_list  = ft.Column(spacing=8)
    search_results = ft.Column(spacing=8)
    status_text    = ft.Text("", color=C_DIM, size=12, italic=True)

    friend_search_field = ft.TextField(
        hint_text="Hanapin gamit ang Username...", bgcolor=C_BG2,
        border_color=C_BORDER, text_size=13, height=42, expand=True
    )

    def _avatar(name, size=38, color=None):
        return ft.Container(
            width=size, height=size, bgcolor=color or app_state.data["current_accent"],
            border_radius=size // 2, alignment=ft.Alignment(0, 0),
            content=ft.Text(name[0].upper() if name else "?", color=C_BG0, weight=ft.FontWeight.BOLD, size=size // 2),
        )

    def open_chat(friend_id, friend_name):
        chat_messages = ft.ListView(expand=True, spacing=4, auto_scroll=True)
        msg_input = ft.TextField(hint_text="Mag-type ng mensahe...", expand=True, bgcolor=C_BG2, border_color=C_BORDER)

        # Clear unread notification
        if friend_id in app_state.data["unread_chats"]:
            app_state.data["unread_chats"].discard(friend_id)
            if update_nav_callback:
                update_nav_callback()
            page.update()

        chat_state = {"is_open": True}

        def load_msgs():
            msgs = SupabaseClient.get_messages(app_state.data["user_id"], friend_id)
            if msgs:
                app_state.data["chat_last_viewed"][friend_id] = msgs[-1]["created_at"]

            if len(msgs) != len(chat_messages.controls):
                chat_messages.controls.clear()
                if not msgs:
                    chat_messages.controls.append(ft.Text("Wala pa. Say hi!", color=C_DIM, italic=True))
                for m in msgs:
                    is_me = m["sender_id"] == app_state.data["user_id"]
                    chat_messages.controls.append(
                        ft.Container(
                            content=ft.Text(m["content"], color=C_BG0 if is_me else C_TEXT),
                            bgcolor=app_state.data["current_accent"] if is_me else C_BG2,
                            padding=10, border_radius=8,
                            alignment=ft.Alignment(1, 0) if is_me else ft.Alignment(-1, 0),
                            margin=ft.Margin(left=40 if is_me else 0, right=0 if is_me else 40, top=2, bottom=2)
                        )
                    )
                async def _ui():
                    try:
                        page.update()
                    except RuntimeError:
                        pass
                page.run_task(_ui)

        def _poll_messages():
            while chat_state["is_open"]:
                load_msgs()
                time.sleep(3)

        def send_click(e):
            if msg_input.value.strip():
                SupabaseClient.send_message(app_state.data["user_id"], friend_id, msg_input.value.strip())
                msg_input.value = ""
                page.update()
                load_msgs()

        chat_dlg = ft.BottomSheet(
            on_dismiss=lambda e: chat_state.update({"is_open": False}),
            content=ft.Container(
                bgcolor=C_BG1, padding=20, height=500,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Makipagusap kay {friend_name}", size=16, weight=ft.FontWeight.BOLD, color=app_state.data["current_accent"]),
                        ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: (setattr(chat_dlg, "open", False) or chat_state.update({"is_open": False}) or page.update()))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=C_BORDER),
                    ft.Container(content=chat_messages, expand=True),
                    ft.Row([msg_input, ft.IconButton(ft.Icons.SEND, icon_color=app_state.data["current_accent"], on_click=send_click)])
                ])
            )
        )
        page.overlay.append(chat_dlg)
        chat_dlg.open = True
        page.update()
        threading.Thread(target=_poll_messages, daemon=True).start()

    def _friend_row(username, display_name, friend_id):
        has_unread = friend_id in app_state.data["unread_chats"]
        return ft.Container(
            bgcolor=C_BG1, border_radius=10, border=ft.Border.all(1, C_BORDER), padding=ft.Padding(12, 10, 12, 10),
            content=ft.Row([
                _avatar(display_name),
                ft.Column([
                    ft.Text(display_name, color=C_TEXT, weight=ft.FontWeight.BOLD, size=13),
                    ft.Text(f"@{username}", color=C_DIM, size=11),
                ], expand=True, spacing=2),
                ft.IconButton(
                    ft.Icons.CHAT_BUBBLE_OUTLINE if not has_unread else ft.Icons.CHAT_BUBBLE,
                    icon_color=app_state.data["current_accent"] if not has_unread else C_RED,
                    on_click=lambda e: open_chat(friend_id, display_name)
                ),
            ], spacing=12),
        )

    def _request_row(username, display_name, req_id):
        def accept(e):
            SupabaseClient.accept_friend(req_id)
            load_all()
        def decline(e):
            SupabaseClient.decline_friend(req_id)
            load_all()

        return ft.Container(
            bgcolor=C_BG1, border_radius=10, border=ft.Border.all(1, C_BORDER), padding=ft.Padding(12, 10, 12, 10),
            content=ft.Row([
                _avatar(display_name, color="#b48ead"),
                ft.Column([
                    ft.Text(display_name, color=C_TEXT, weight=ft.FontWeight.BOLD, size=13),
                    ft.Text(f"@{username} ay gustong makipagkaibigan", color=C_DIM, size=11)
                ], expand=True, spacing=2),
                ft.Row([
                    ft.Container(content=ft.Text("✔", color="#a3be8c", size=16), on_click=accept, ink=True, bgcolor=C_BG2, border_radius=6, padding=ft.Padding(8, 4, 8, 4)),
                    ft.Container(content=ft.Text("✖", color=C_RED, size=16), on_click=decline, ink=True, bgcolor=C_BG2, border_radius=6, padding=ft.Padding(8, 4, 8, 4)),
                ], spacing=6),
            ], spacing=12),
        )

    def do_search(e):
        term = friend_search_field.value.strip()
        if not term: return
        search_results.controls.clear()
        search_results.controls.append(ft.ProgressRing(color=app_state.data["current_accent"], width=20, height=20))
        page.update()

        def _t():
            results = SupabaseClient.search_users(term)
            search_results.controls.clear()
            if not results:
                search_results.controls.append(ft.Text("Wala pa.", color=C_DIM, italic=True, size=12))
            for u in results:
                uname, dname, target_id = u.get("username", ""), u.get("display_name", u.get("username", "")), u.get("id")
                if target_id == app_state.data["user_id"]: continue

                def send_req(e, _tid=target_id, _un=uname):
                    SupabaseClient.send_friend_request(app_state.data["user_id"], _tid)
                    page.overlay.append(ft.SnackBar(content=ft.Text(f"Nag-send ng request kay @{_un}"), open=True))
                    page.update()
                    load_all()

                search_results.controls.append(
                    ft.Container(
                        bgcolor=C_BG1, border_radius=10, padding=12, border=ft.Border.all(1, C_BORDER),
                        content=ft.Row([
                            _avatar(dname, color="#ebcb8b"),
                            ft.Column([ft.Text(dname, weight=ft.FontWeight.BOLD), ft.Text(f"@{uname}", size=11, color=C_DIM)], expand=True),
                            ft.Container(content=ft.Text("+ ADD", size=10, weight=ft.FontWeight.BOLD), bgcolor=C_BG2, padding=8, border_radius=6, on_click=send_req)
                        ])
                    )
                )
            async def _ui():
                try:
                    page.update()
                except RuntimeError:
                    pass
            page.run_task(_ui)
        threading.Thread(target=_t, daemon=True).start()

    def load_all():
        friends_list.controls.clear()
        requests_list.controls.clear()
        status_text.value = "Sandali lang..."
        page.update()

        def _t():
            try:
                accepted = SupabaseClient.get_friends(app_state.data["user_id"])
                pending  = SupabaseClient.get_pending_requests(app_state.data["user_id"])
                requests_list.controls.clear()
                if pending:
                    requests_list.controls.append(ft.Text("MGA FRIEND REQUESTS", color=C_DIM, size=10, weight=ft.FontWeight.BOLD))
                    for r in pending:
                        profile = r.get("profiles", {})
                        requests_list.controls.append(_request_row(profile.get("username", r["from_user"]), profile.get("display_name", "Unknown"), r["id"]))

                friends_list.controls.clear()
                if not accepted:
                    friends_list.controls.append(ft.Text("I-search sa itaas para magdagdag ng kaibigan!", color=C_DIM, italic=True, size=12))
                for f in accepted:
                    friends_list.controls.append(_friend_row(f["username"], f["display_name"], f["id"]))
                status_text.value = f"{len(accepted)} kaibigan"
            except Exception as ex:
                print(f"Error: {ex}")

            async def _ui():
                try:
                    page.update()
                except RuntimeError:
                    pass
            page.run_task(_ui)

        threading.Thread(target=_t, daemon=True).start()

    load_all()

    return ft.Column(expand=True, spacing=0, controls=[
        ft.Container(
            padding=ft.Padding(15, 14, 15, 8),
            content=ft.Row([ft.Text("MGA KAIBIGAN", color=app_state.data["current_accent"], size=12, weight=ft.FontWeight.BOLD), status_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ),
        ft.Container(
            padding=ft.Padding(12, 0, 12, 10),
            content=ft.Row([
                friend_search_field,
                ft.Container(content=ft.Text("HANAPIN", color=C_BG0, size=10, weight=ft.FontWeight.BOLD), bgcolor=app_state.data["current_accent"], border_radius=6, padding=ft.Padding(12, 10, 12, 10), on_click=do_search, ink=True),
            ], spacing=8),
        ),
        ft.Container(
            expand=True, padding=ft.Padding(12, 0, 12, 0),
            content=ft.Column(
                expand=True, scroll=ft.ScrollMode.AUTO, spacing=10,
                controls=[
                    search_results, requests_list,
                    ft.Text("IYONG MGA KAIBIGAN", color=C_DIM, size=10, weight=ft.FontWeight.BOLD),
                    friends_list, ft.Container(height=20)
                ]
            ),
        ),
    ])
