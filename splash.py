# splash.py
import math
import asyncio
import flet as ft
from config import C_BG0, C_ACCENT, C_TEXT, C_DIM

# ── Helpers ───────────────────────────────────────────────────────────────────

def _ray(angle_deg: float, length: float, width: float, cx: float, cy: float) -> ft.Container:
    """A single tapered ray, starting from the sun edge."""
    rad    = math.radians(angle_deg)
    offset = 40                              # distance from centre to ray base
    x = cx + math.cos(rad) * offset - width / 2
    y = cy + math.sin(rad) * offset - length / 2
    return ft.Container(
        width=width,
        height=length,
        left=x,
        top=y,
        rotate=ft.Rotate(angle=math.radians(angle_deg + 90)),
        border_radius=width,
        bgcolor=C_ACCENT,
        opacity=0,
        scale=ft.Scale(0.4),
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
    )

# ── Main builder ──────────────────────────────────────────────────────────────

def build_splash_screen(page: ft.Page, on_done) -> ft.Container:
    # Internal Stack size to keep rays relative to core
    SUN_SIZE = 200
    CX, CY = SUN_SIZE / 2, SUN_SIZE / 2

    # ── Sun core ──────────────────────────────────────────────────────────────
    sun_core = ft.Container(
        width=80, height=80,
        left=CX - 40, top=CY - 40,
        border_radius=40,
        bgcolor=C_ACCENT,
        opacity=0,
        scale=ft.Scale(0.3),
        animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(700, ft.AnimationCurve.ELASTIC_OUT),
        # SHADOW REMOVED: Fixes the horizontal 'red ray' artifact in browsers
    )

    # ── Rays: 16 Restored ─────────────────────────────────────────────────────
    NUM_RAYS = 16
    rays: list[ft.Container] = []
    for i in range(NUM_RAYS):
        angle  = i * (360 / NUM_RAYS)
        length = 68 if i % 2 == 0 else 38
        width  = 5  if i % 2 == 0 else 3
        rays.append(_ray(angle, length, width, CX, CY))

    # ── Logo text ─────────────────────────────────────────────────────────────
    logo_text = ft.Container(
        content=ft.Text(
            "SINAG",
            size=52,
            weight=ft.FontWeight.BOLD,
            color=C_ACCENT,
            style=ft.TextStyle(letter_spacing=12),
        ),
        alignment=ft.Alignment(0, 0),
        opacity=0,
        offset=ft.Offset(0, 0.2),
        animate_opacity=ft.Animation(700, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(700, ft.AnimationCurve.EASE_OUT),
    )

    # ── Tagline ───────────────────────────────────────────────────────────────
    tagline = ft.Container(
        content=ft.Text(
            "Discover Filipino Games",
            size=13,
            color=C_DIM,
            style=ft.TextStyle(letter_spacing=2.5),
        ),
        alignment=ft.Alignment(0, 0),
        opacity=0,
        offset=ft.Offset(0, 0.2),
        animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        animate_offset=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
    )

    # ── Progress Bar ──────────────────────────────────────────────────────────
    progress_track = ft.Container(width=120, height=2, bgcolor=f"{C_ACCENT}22", opacity=0, animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT))
    progress_fill = ft.Container(width=0, height=2, bgcolor=C_ACCENT, opacity=0, animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT))
    progress_stack = ft.Stack([progress_track, progress_fill], width=120)

    # ── Sun Assembly ──────────────────────────────────────────────────────────
    sun_assembly = ft.Stack([*rays, sun_core], width=SUN_SIZE, height=SUN_SIZE)

    # ── Outer wrapper ─────────────────────────────────────────────────────────
    wrapper = ft.Container(
        expand=True, bgcolor=C_BG0,
        content=ft.Column(
            expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(expand=3),
                sun_assembly,
                ft.Container(height=20),
                logo_text,
                tagline,
                ft.Container(expand=4),
                ft.Container(content=progress_stack, padding=ft.Padding(0, 0, 0, 60)),
            ]
        ),
        opacity=1,
        animate_opacity=ft.Animation(550, ft.AnimationCurve.EASE_IN),
    )

    # ── Animation sequence ────────────────────────────────────────────────────
    async def _animate():
        await asyncio.sleep(0.1)
        sun_core.opacity, sun_core.scale = 1, ft.Scale(1.0)
        page.update()
        await asyncio.sleep(0.35)
        for wave in range(4): # 4 waves of 4 rays
            for i in range(wave, NUM_RAYS, 4):
                rays[i].opacity, rays[i].scale = 0.9, ft.Scale(1.0)
            page.update()
            await asyncio.sleep(0.06)
        await asyncio.sleep(0.3)
        logo_text.opacity, logo_text.offset = 1, ft.Offset(0, 0)
        page.update()
        await asyncio.sleep(0.45)
        tagline.opacity, tagline.offset = 1, ft.Offset(0, 0)
        page.update()
        await asyncio.sleep(0.3)
        progress_track.opacity, progress_fill.opacity, progress_fill.width = 1, 1, 120
        page.update()
        await asyncio.sleep(1.0)
        wrapper.opacity = 0
        page.update()
        await asyncio.sleep(0.6)
        on_done()

    page.run_task(_animate)
    return wrapper