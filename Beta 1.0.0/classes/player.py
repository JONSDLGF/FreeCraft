import math
import pygame

class Player:
    def __init__(self, xyz=(0, 0, 0)):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
        self.camera_angle_x = 0
        self.camera_angle_y = 0
        self.speed = 0.2

    def move_event(self):
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_rel()
        self.camera_angle_x -= mx * 0.1
        self.camera_angle_y -= my * 0.1  # ← invertido para comportamiento normal
        self.camera_angle_y = max(-90, min(90, self.camera_angle_y))

        yaw = math.radians(self.camera_angle_x)

        # Direcciones ajustadas
        forward_x = math.sin(yaw)
        forward_z = math.cos(yaw)  # ← quitamos el signo negativo
        right_x = math.cos(yaw)
        right_z = -math.sin(yaw)   # ← signo invertido

        if keys[pygame.K_w]:
            self.x -= forward_x * self.speed
            self.z -= forward_z * self.speed
        if keys[pygame.K_s]:
            self.x += forward_x * self.speed
            self.z += forward_z * self.speed
        if keys[pygame.K_a]:
            self.x -= right_x * self.speed
            self.z -= right_z * self.speed
        if keys[pygame.K_d]:
            self.x += right_x * self.speed
            self.z += right_z * self.speed
        if keys[pygame.K_SPACE]:
            self.y += self.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.y -= self.speed