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

def render_gui_grid(width, height, buttons, rows=1, cols=1, spacing_x=20, spacing_y=20, cell_width=200, cell_height=80):
    """
    Dibuja una cuadrícula de botones centrados en pantalla.
    Devuelve el índice (int) del botón presionado o None.
    """
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

        # Calcular posición centrada del botón en la celda
        grid_width  = cols * cell_width + (cols - 1) * spacing_x
        grid_height = rows * cell_height + (rows - 1) * spacing_y

        x = (width  - grid_width)  // 2 + col * (cell_width + spacing_x) + cell_width  // 2
        y = (height - grid_height) // 2 + row * (cell_height + spacing_y) + cell_height // 2

        label = btn.get("label", f"Button {idx}")
        opts  = btn.get("options", None)

        if draw_button(label, x, y, options=opts):
            result = idx  # Usar índice, no el texto
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

def draw_chat(chat_):
    font = pygame.font.Font(None, 20)
    x, y = 10, 50  # posición de inicio para el chat, por ejemplo

    for i, (user, msg) in enumerate(chat_[-10:]):  # mostrar solo los últimos 10 mensajes
        line = f"{user}: {msg}"
        text_surface = font.render(line, True, (255, 255, 255), (0, 0, 0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width, height = text_surface.get_size()
        gl.glWindowPos2d(x, y + i * (height + 2))
        gl.glDrawPixels(width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text_data)

class InputHandler:
    def __init__(self):
        self.input_buffer = ""

    def input(self):
        font = pygame.font.Font(None, 20)
        x, y = 10, 10
        text_to_return = None

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.input_buffer = ""
                    return "__exit__"
                elif event.key == pygame.K_BACKSPACE:
                    self.input_buffer = self.input_buffer[:-1]
                elif event.key == pygame.K_RETURN:
                    text_to_return = self.input_buffer
                    self.input_buffer = ""
                else:
                    char = event.unicode
                    if char.isprintable():
                        self.input_buffer += char

        # Dibujar texto en pantalla
        text_surface = font.render("> " + self.input_buffer, True, (255, 255, 255), (0, 0, 0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width, height = text_surface.get_size()
        gl.glWindowPos2d(x, y)
        gl.glDrawPixels(width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text_data)

        return text_to_return

def draw_label(text, x, y, size=24):
    font = pygame.font.Font(None, size)
    surface = font.render(text, True, (255, 255, 255), (0, 0, 0))

    # Calcular posición centrada
    text_width, text_height = surface.get_size()
    x_centered = x - text_width // 2
    y_centered = y - text_height // 2

    # Convertir a datos y dibujar con OpenGL
    data = pygame.image.tostring(surface, "RGBA", True)
    gl.glWindowPos2d(x_centered, y_centered)
    gl.glDrawPixels(text_width, text_height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)

def draw_inputbox(text, x, y, active=False):
    box_color = (0, 255, 0) if active else (200, 200, 200)
    pygame.draw.rect(pygame.display.get_surface(), box_color, (x - 100, y, 200, 30), 2)
    draw_label(text, x - 90, y + 5, size=20)