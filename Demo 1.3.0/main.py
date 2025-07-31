# main.py

import sys
import time
import pygame
import json
import os
from classes.render import Renderer, Camera
from classes.player import Player
from classes.word import chunkgen, build_chunk_cube_map # esas funciones se dejara para pasar a el chunk_manager
from classes.chunk import chunk_manager                 # pronto en la 1.4.X
import gui.render as gui                                # por lo tanto en la 1.3.X sera la gui update
# chat y menus
import OpenGL.GL as gl
import OpenGL.GLU as glu

def game(width, height, debug):
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(70, width / height, 0.1, 1000.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    RENDER_DISTANCE = 0
    player = Player(xyz=(8, 3, 8))
    render = Renderer()
    camara = Camera(player)

    seed = 0
    chunks = []
    last_chunk_xyz = None

    running = True
    frame = []
    framet = 60
    FPS = 0.0
    menu_game=False
    pygame.mouse.set_pos(width // 2, height // 2)
    pygame.event.set_grab(not menu_game)
    pygame.mouse.set_visible(menu_game)

    while running:
        init_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_game = not menu_game # despues se cambiara para agregar el menu del juego
                    pygame.mouse.set_pos(width // 2, height // 2)
                    pygame.event.set_grab(not menu_game)
                    pygame.mouse.set_visible(menu_game)
                if event.key == pygame.K_F3:
                    debug = not debug
                if event.key == pygame.K_F11:
                    if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                        width, height = Renderer.set_windowed()
                    else:
                        width, height = Renderer.set_fullscreen()

        gl.glClearColor(0.5, 0.7, 1.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if not menu_game:
            player.move_event()

        current_chunk_xyz = tuple(player.chunk_xyz)
        if current_chunk_xyz != last_chunk_xyz:
            chunks = chunkgen(RENDER_DISTANCE, seed, current_chunk_xyz)
            chunk_cube_map = build_chunk_cube_map(chunks)
            face_culling_masks = render.face_culling(chunks, chunk_cube_map)
            last_chunk_xyz = current_chunk_xyz

        camara.aplicar_camara()

        # 1ª capa: Mundo
        render.render_3D_all(chunk_cube_map, face_culling_masks, player)
        
        gl.glDisable(gl.GL_TEXTURE_2D)
        
        # 2ª capa: GUI
        if not menu_game:
            gui.render_gui_cross(width, height)
        else:
            # Menú en juego: botones "Restablecer" y "Salir"
            buttons_in_game = [
                {"label": "Bolver"},
                {"label": "Salir"}
            ]
            choice = gui.render_gui_menu(width, height, buttons=buttons_in_game, spacing=80)
            if choice == 0:
                menu_game = False
                pygame.mouse.set_pos(width // 2, height // 2)
                pygame.event.set_grab(not menu_game)
                pygame.mouse.set_visible(menu_game)
            elif choice == 1:
                return 0  # Salir del juego

        # 3ª capa: Objetos 3D
        #renderer.render_3D_objects(player)
        
        # 4ª capa: Debug
        if debug:
            gui.render_debug(player, FPS)
        
        gl.glEnable(gl.GL_TEXTURE_2D)

        pygame.display.flip()

        end_time = time.time()
        frame.append(end_time - init_time)
        if len(frame) >= framet:
            total = sum(frame) / framet
            FPS=1.0/total
            frame = []
    return 0

def menu(argv:list[str]):
    pygame.init()
    icon_surface = pygame.image.load("assets/icon/logo.png")  # Ruta a tu icono
    pygame.display.set_icon(icon_surface)
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(70, width / height, 0.1, 1000.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    ver = "1.3.0"
    debug = True

    with open(os.path.join(os.path.dirname(__file__), "assets", "conf.json"), "r") as f:
        config = json.load(f)
    width       = config.get("width", width)
    height      = config.get("height", height)
    debug       = config.get("debug", debug)
    ver         = config.get("ver", ver)

    pygame.display.set_caption(f'FreeCraft {ver}')

    menu_="main"
    loop=True
    running=True
    while loop:
        if menu_=="main":
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        loop = False
                        menu_="exit"
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False
                        loop = False
                
                gl.glClearColor(0.55, 0.44, 0.32, 1.0)  # Marrón tierra claro
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

                # Configurar proyección 2D para el menú
                gl.glMatrixMode(gl.GL_PROJECTION)
                gl.glLoadIdentity()
                gl.glOrtho(0, width, height, 0, -1, 1)
                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glLoadIdentity()

                # Menú principal: botones "Nuevo Juego" y "Salir"
                buttons = [
                    {"label": "Nuevo Juego", "row": 1, "col": 0},
                    {"label": "Salir",        "row": 1, "col": 1},
                ]

                # En tu menú
                choice = gui.render_gui_grid(width, height, buttons, rows=2, cols=2)
                if choice == 0:
                    # Iniciar juego
                    result = game(width, height, debug)
                    menu_ = "main"
                elif choice == 1:
                    running = False
                    loop = False
                
                pygame.display.flip()
        elif menu_=="game":
            game(width, height, debug)
            running=True
            menu_="main"
        elif menu_=="exit":
            return 0

if __name__ == "__main__":
    sys.exit(menu(sys.argv))