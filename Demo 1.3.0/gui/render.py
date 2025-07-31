# assets/gui/render.py

import OpenGL.GL as gl
import pygame

def render_gui_cross(width, height):
    gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
    gl.glPushMatrix()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, width, height, 0, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    cx, cy = width // 2, height // 2
    cross_size = 10

    gl.glBegin(gl.GL_LINES)
    gl.glColor3f(1.0, 1.0, 1.0)
    gl.glVertex2f(cx, cy - cross_size)
    gl.glVertex2f(cx, cy + cross_size)
    gl.glVertex2f(cx - cross_size, cy)
    gl.glVertex2f(cx + cross_size, cy)
    gl.glEnd()

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()
    gl.glPopAttrib()

def draw_button(label, x, y, font_size=32, padding=10, options=None):
    surface = pygame.display.get_surface()
    surface_height = surface.get_height()

    # Valores por defecto
    text_color = (0, 0, 0)
    bg_color_normal = (220, 220, 220)
    bg_color_hover = (180, 180, 180)
    font_name = None  # Fuente por defecto

    # Sobrescribir con options si existen
    if options:
        text_color = options.get("text_color", text_color)
        bg_color_normal = options.get("bg_color_normal", bg_color_normal)
        bg_color_hover = options.get("bg_color_hover", bg_color_hover)
        font_name = options.get("font_name", font_name)
        font_size = options.get("font_size", font_size)
        padding = options.get("padding", padding)

    font = pygame.font.Font(font_name, font_size)
    text_surface = font.render(label, True, text_color)
    text_w, text_h = text_surface.get_size()

    button_w = text_w + padding * 2
    button_h = text_h + padding * 2

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    btn_x = x - button_w / 2
    btn_y = y - button_h / 2

    is_hovered = (btn_x <= mouse_x <= btn_x + button_w and btn_y <= mouse_y <= btn_y + button_h)

    bg_color = bg_color_hover if is_hovered else bg_color_normal
    bg_surface = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
    bg_surface.fill(bg_color)
    bg_surface.blit(text_surface, (padding, padding))

    bg_data = pygame.image.tostring(bg_surface, "RGBA", True)

    gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
    try:
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glWindowPos2i(int(btn_x), int(surface_height - btn_y - button_h))
        gl.glDrawPixels(button_w, button_h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, bg_data)
    finally:
        gl.glPopAttrib()

    return is_hovered and mouse_buttons[0]

def render_gui_menu(width, height, buttons=None, base_x=None, base_y=None, spacing=60):
    """
    Muestra un menú con botones configurables.

    :param width: ancho de la ventana
    :param height: alto de la ventana
    :param buttons: lista de diccionarios con botones, cada uno con:
        - 'label': texto del botón
        - 'options' (opcional): dict con opciones para draw_button
    :param base_x: posición horizontal central (por defecto centro pantalla)
    :param base_y: posición vertical central (por defecto centro pantalla)
    :param spacing: separación vertical entre botones (por defecto 60)
    :return: el índice del botón pulsado, o None si no se pulsa ninguno
    """
    if buttons is None:
        buttons = [
            {"label": "Return"},
            {"label": "Settings"},
            {"label": "Exit"},
        ]

    if base_x is None:
        base_x = width // 2
    if base_y is None:
        base_y = height // 2

    gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, width, height, 0, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    result = None
    for i, btn in enumerate(buttons):
        y = base_y + (i - len(buttons)//2) * spacing
        opts = btn.get("options", None)
        if draw_button(btn["label"], base_x, y, options=opts):
            result = i
            break

    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glPopAttrib()

    return result


def render_gui_grid(width, height, buttons, rows=1, cols=1, spacing_x=20, spacing_y=20, cell_width=200, cell_height=80):
    gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, width, height, 0, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    result = None
    for idx, btn in enumerate(buttons):
        row = btn.get("row", 0)
        col = btn.get("col", 0)

        # Centro de cada celda
        x = (width - (cols * cell_width + (cols - 1) * spacing_x)) // 2 + col * (cell_width + spacing_x) + cell_width // 2
        y = (height - (rows * cell_height + (rows - 1) * spacing_y)) // 2 + row * (cell_height + spacing_y) + cell_height // 2

        opts = btn.get("options", None)
        label = btn.get("label", f"Button {idx}")

        if draw_button(label, x, y, options=opts):
            result = idx
            break

    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glPopAttrib()

    return result

def render_debug(player, FPS):
    gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
    gl.glPushMatrix()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, 800, 600, 0, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    font = pygame.font.Font(None, 24)
    chunk_pos = player.get_player_position_in_chunk()
    global_pos = player.get_global_position()
    text = [
        f"FPS: {FPS:.2f}",
        f"Chunk XYZ: {chunk_pos[0]:.2f} | {chunk_pos[1]:.2f} | {chunk_pos[2]:.2f}",
        f"Global XYZ: {global_pos[0]:.2f} | {global_pos[1]:.2f} | {global_pos[2]:.2f}",
        f"Chunk: {player.chunk_xyz[0]} | {player.chunk_xyz[1]} | {player.chunk_xyz[2]}",
        f"angle X: {player.camara_rotacion_x:.1f}",
        f"angle Y: {player.camara_rotacion_y:.1f}"
    ]
    for i, line in enumerate(text):
        text_surface = font.render(line, True, (0,0,0), (255, 255, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width, height = text_surface.get_size()
        gl.glRasterPos2f(10, 30 + i * 20)
        gl.glDrawPixels(width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text_data)

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()
    gl.glPopAttrib()