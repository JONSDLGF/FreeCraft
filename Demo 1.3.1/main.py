# main.py

import sys
import time
import pygame
import json
import os
from classes.render import Render_cube, Render_entity, Camera
from classes.player import Player
from classes.net    import net
from classes.logic  import log
from classes.word   import chunkgen, build_chunk_cube_map # esas funciones se dejara para pasar a el chunk_manager
from classes.chunk  import chunk_manager                 # pronto en la 1.4.X
import gui.render as gui                                # por lo tanto en la 1.3.X sera la gui update
# chat y menus
import OpenGL.GL as gl
import OpenGL.GLU as glu

def game(width, height, Net:bool=False, ip:str="", name:str="Pacheco"):
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(70, width / height, 0.1, 1000.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    if not name.strip():
        name = "Pacheco"

    if Net:
        server = net.conect(ip,name)
    RENDER_DISTANCE = 0
    player = Player(xyz=(8, 3, 8))
    render_cube = Render_cube()
    #render_entity = Renderer_entity()
    camara = Camera(player)
    input_handler = gui.InputHandler()

    seed = 0
    chunks = []
    last_chunk_xyz = None

    running = True
    debug = False
    frame = []
    framet = 60
    FPS = 0.0
    menu_game = False
    chat = False
    chat_:list[tuple[str,str]]=[]
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
                        width, height = render_cube.set_windowed()
                    else:
                        width, height = render_cube.set_fullscreen()
                if event.key == pygame.K_c and not menu_game and not chat:
                    chat = not chat
                    pygame.mouse.set_pos(width // 2, height // 2)
                    pygame.event.set_grab(not chat)
                    pygame.mouse.set_visible(chat)

        gl.glClearColor(0.5, 0.7, 1.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if not menu_game and not chat:
            player.move_event()
        
        if not Net:
            current_chunk_xyz = tuple(player.chunk_xyz)
            if current_chunk_xyz != last_chunk_xyz:
                chunks = chunkgen(RENDER_DISTANCE, seed, current_chunk_xyz)
                chunk_cube_map = build_chunk_cube_map(chunks)
                face_culling_masks = render_cube.face_culling(chunks, chunk_cube_map)
                last_chunk_xyz = current_chunk_xyz
        else:
            update = server.update(
                player.chunk_xyz,
                player.xyz,
                name
            )
            player.chunk_xyz = update.chunk_pos
            player.xyz = update.player_pos
            chunk_cube_map = update.chunk_map
            face_culling_masks = update.masks

        camara.aplicar_camara()

        # 1ª capa: Mundo
        render_cube.render_3D_all(chunk_cube_map, face_culling_masks, player)

        #render_entity

        gl.glDisable(gl.GL_TEXTURE_2D)
        
        # 2ª capa: GUI
        skip=False
        if not menu_game:
            gui.render_gui_cross(width, height)
            if chat:
                gui.draw_chat(chat_[::-1])
                text = input_handler.input()
                if not text:
                    skip=True
                elif text=="__exit__":
                    chat = not chat
                    pygame.mouse.set_pos(width // 2, height // 2)
                    pygame.event.set_grab(not chat)
                    pygame.mouse.set_visible(chat)
                    skip=True
                if not skip:
                    if text[0]=="/":
                        command=text[1:]
                        if Net:
                            server.command(command, name)
                        else:
                            log.command(command, name)
                    else:
                        if Net:
                            server.add_mesg((name,text))
                        chat_.append((name,text))
        else:
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
    while loop:
        if menu_=="main":
            running=True
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
                    {"label": "Nuevo Juego", "row": 1.5, "col": -0.5},
                    {"label": "Net",         "row": 1.5, "col": 0.5},
                    {"label": "Salir",       "row": 1.5, "col": 1.5},
                ]

                # En tu menú
                choice = gui.render_gui_grid(width, height, buttons, rows=2, cols=2)
                if choice == 0:
                    # Iniciar juego
                    result = game(width, height)
                    menu_ = "main"
                elif choice == 1:
                    menu_ = "net"
                    running = False
                elif choice == 2:
                    running = False
                    loop = False
                
                pygame.display.flip()
        elif menu_ == "net":
            running=True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        loop = False
                        menu_ = "exit"
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        menu_ = "main"
                        running = False

                gl.glClearColor(0.55, 0.44, 0.32, 1.0)  # Fondo marrón
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

                gl.glMatrixMode(gl.GL_PROJECTION)
                gl.glLoadIdentity()
                gl.glOrtho(0, width, height, 0, -1, 1)
                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glLoadIdentity()

                # Mostrar mensaje de trabajo en progreso
                gui.draw_label("Multijugador aún no disponible", width // 2 - 150, height // 2 - 40, size=28)

                # Botón para salir
                if gui.draw_button("Salir", width // 2, height // 2 - 100):
                    menu_ = "main"
                    running = False

                pygame.display.flip()
        elif menu_=="game":
            game(width, height, debug)
            running=True
            menu_="main"
        elif menu_=="exit":
            return 0

if __name__ == "__main__":
    sys.exit(menu(sys.argv))