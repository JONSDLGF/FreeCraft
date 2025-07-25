# main.py
import sys
import time
import pygame
import json
from classes.render import Renderer, Camera
from classes.player import Player
from classes.word import chunkgen
from gui.render import render_gui, render_debug
import OpenGL.GL as gl
import OpenGL.GLU as glu

def main():
    pygame.init()
    icon_surface = pygame.image.load("assets/icon/logo.png")  # Ruta a tu icono
    pygame.display.set_icon(icon_surface)
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption('FreeCraft')

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    CHUNK_SIZE = 16
    RENDER_DISTANCE = 0
    player = Player(xyz=(0, 0, 0), cmove=CHUNK_SIZE)
    renderer = Renderer()
    camara = Camera(player)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(70, width / height, 0.1, 1000.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    seed = 0
    chunks = []
    last_chunk_xyz = None
    debug = True

    running = True
    frame = []
    framet = 60
    FPS = 0.0

    full_screen = False

    with open("assets/conf.json", "r") as f:
        config = json.load(f)
    full_screen = config.get("fullscreen", full_screen)
    width       = config.get("width", width)
    height      = config.get("height", height)
    debug       = config.get("debug", debug)
    while running:
        init_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_F3:
                    debug_mode = not debug_mode
                if event.key == pygame.K_F11:
                    if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                        width, height = Renderer.set_windowed()
                    else:
                        width, height = Renderer.set_fullscreen()
        
        player.move_event()
        current_chunk_xyz = tuple(player.chunk_xyz)
        if current_chunk_xyz != last_chunk_xyz:
            for chunk_data, _ in chunks:
                if hasattr(chunk_data, 'vbo_data'):
                    gl.glDeleteBuffers(1, [chunk_data.vbo_data[0]])
            chunks = []
            cx, cy, cz = current_chunk_xyz
            for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE+2):
                for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE+2):
                    for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE+2):
                        chunk_coords = (cx + dx, cy + dy, cz + dz)
                        chunk = chunkgen(seed, csize=CHUNK_SIZE, chunk_coords=chunk_coords)
                        chunks.extend(chunk)
            last_chunk_xyz = current_chunk_xyz

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # 1ª capa: Mundo
        renderer.render_3D_all(chunks, player, camara, CHUNK_SIZE=CHUNK_SIZE)
        
        # 2ª capa: GUI
        render_gui(width, height)
        
        # 3ª capa: Objetos 3D
        renderer.render_3D_objects(player, camara)
        
        # 4ª capa: Debug
        if debug:
            render_debug(player, FPS)
            pass

        pygame.display.flip()

        end_time = time.time()
        frame.append(end_time - init_time)
        if len(frame) >= framet:
            total = sum(frame) / framet
            FPS=1.0/total
            frame = []

    for chunk_data, _ in chunks:
        if hasattr(chunk_data, 'vbo_data'):
            gl.glDeleteBuffers(1, [chunk_data.vbo_data[0]])
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()