# main.py
import sys
import time
import pygame
import json
import os
from classes.render import Renderer, Camera
from classes.player import Player
from classes.word import chunkgen, build_chunk_cube_map
from gui.render import render_gui, render_debug
import OpenGL.GL as gl
import OpenGL.GLU as glu

def main(argv:list[str]):

    pygame.init()
    icon_surface = pygame.image.load("assets/icon/logo.png")  # Ruta a tu icono
    pygame.display.set_icon(icon_surface)
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(70, width / height, 0.1, 1000.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    RENDER_DISTANCE = 1
    player = Player(xyz=(0, 0, 0))
    render = Renderer()
    camara = Camera(player)

    seed = 0
    chunks = []
    last_chunk_xyz = None
    debug = True

    running = True
    frame = []
    framet = 60
    FPS = 0.0

    full_screen = False
    ver = "1.2.0"

    with open(os.path.join(os.path.dirname(__file__), "assets", "conf.json"), "r") as f:
        config = json.load(f)
    full_screen = config.get("fullscreen", full_screen)
    width       = config.get("width", width)
    height      = config.get("height", height)
    debug       = config.get("debug", debug)
    ver         = config.get("ver", ver)

    pygame.display.set_caption(f'FreeCraft {ver}')

    while running:
        init_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_F3:
                    debug = not debug
                if event.key == pygame.K_F11:
                    if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                        width, height = Renderer.set_windowed()
                    else:
                        width, height = Renderer.set_fullscreen()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.5, 0.7, 1.0, 1)

        player.move_event()

        current_chunk_xyz = tuple(player.chunk_xyz)
        if current_chunk_xyz != last_chunk_xyz:
            chunks = chunkgen(RENDER_DISTANCE, seed, current_chunk_xyz)
            chunk_cube_map = build_chunk_cube_map(chunks)
            face_culling_masks = render.face_culling(chunks, chunk_cube_map)
            last_chunk_xyz = current_chunk_xyz


        camara.aplicar_camara()

        # 1ª capa: Mundo
        render.render_3D_all(chunks, face_culling_masks, player)

        # 2ª capa: GUI
        render_gui(width, height)
        
        # 3ª capa: Objetos 3D
        #renderer.render_3D_objects(player)
        
        # 4ª capa: Debug
        if debug:
            render_debug(player, FPS)

        pygame.display.flip()

        end_time = time.time()
        frame.append(end_time - init_time)
        if len(frame) >= framet:
            total = sum(frame) / framet
            FPS=1.0/total
            frame = []

    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))