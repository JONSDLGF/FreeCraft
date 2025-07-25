# gui/render.py
import OpenGL.GL as gl
import pygame

def render_gui(width, height):
    # Guardar el estado actual de OpenGL
    gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
    gl.glPushMatrix()

    # Desactivar depth test y culling para el GUI
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    # Configurar proyección ortográfica
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, width, height, 0, -1, 1)  # Proyección dinámica
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    # Calcular centro de pantalla
    cx, cy = width // 2, height // 2
    cross_size = 10  # Tamaño de la cruz

    # Renderizar cruz (mirilla)
    gl.glBegin(gl.GL_LINES)
    gl.glColor3f(1.0, 1.0, 1.0)  # Blanco
    # Línea vertical
    gl.glVertex2f(cx, cy - cross_size)
    gl.glVertex2f(cx, cy + cross_size)
    # Línea horizontal
    gl.glVertex2f(cx - cross_size, cy)
    gl.glVertex2f(cx + cross_size, cy)
    gl.glEnd()

    # Restaurar el estado de OpenGL
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()
    gl.glPopAttrib()

def render_debug(player, FPS):
    # Guardar el estado de OpenGL
    gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
    gl.glPushMatrix()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    # Configurar proyección ortográfica
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, 800, 600, 0, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    # Renderizar texto de depuración
    font = pygame.font.Font(None, 24)
    chunk_pos = player.get_player_position_in_chunk()
    global_pos = player.get_global_position()
    text = [
        f"FPS: {FPS:.2f}",
        f"Chunk XYZ: {chunk_pos[0]:.2f} / {chunk_pos[1]:.2f} / {chunk_pos[2]:.2f}",
        f"Global XYZ: {global_pos[0]:.2f} / {global_pos[1]:.2f} / {global_pos[2]:.2f}",
        f"Chunk: {player.chunk_xyz[0]} / {player.chunk_xyz[1]} / {player.chunk_xyz[2]}",
        f"angle X: {player.camara_rotacion_x:.2f}",
        f"angle Y: {player.camara_rotacion_y:.2f}"
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