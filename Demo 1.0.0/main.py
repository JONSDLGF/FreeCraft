import sys
import time
import pygame
# Importar las clases necesarias
from classes.render import  render_3D_all, aplicar_camara
from classes.player import Player
from classes.cube import cube
from gui.render import render_gui
# implementar opengl
import OpenGL.GL as gl
import OpenGL.GLU as glu

def main():
    
    pygame.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption('Simple Pygame Window')

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    player = Player(xyz=(0, 17, 0))

    # Crear un chunk de cubos primitibos
    chunck = []
    for y in range(1):
        for z in range(10):
            for x in range(10):
                chunck.append(cube(xyz=(x,y,z)))

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(70, width / height, 0.1, 1000.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    # Main loop
    running = True
    frame = []
    framet = 60
    while running:
        init_time = time.time()
        # usar el esc para salir
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        player.move_event()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        aplicar_camara(player)

        # Renderizar el chunk de cubos
        render_3D_all(chunck)
        
        # Renderizar la GUI
        render_gui()

        pygame.display.flip()

        end_time = time.time()
        frame.append(end_time - init_time)
        if len(frame) >= framet:
            total=sum(frame)/framet
            print(f"FPS: {1/total:.2f}")
            frame = []

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()