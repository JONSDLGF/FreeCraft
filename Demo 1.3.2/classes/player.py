# assets/classes/player.py

import math
import pygame

class Vector:
    def __init__(self, xyz):
        self.x, self.y, self.z = xyz

    def __add__(self, other):
        return Vector((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def __mul__(self, scalar):
        return Vector((self.x * scalar, self.y * scalar, self.z * scalar))

    @property
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

class Player:
    def __init__(self, xyz=(0, 0, 0), grav=False):
        self.cmove = 16
        self.chunk_xyz = [0, 2, 0]
        self.xyz = list(xyz)
        self.camara_rotacion_x = 0
        self.camara_rotacion_y = 0
        self.speed = 0.1
        self.grav = grav

    def move_event(self):
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_rel()
        self.camara_rotacion_x -= mx * 0.1
        self.camara_rotacion_y -= my * 0.1
        self.camara_rotacion_x %= 360  # Normaliza a 0 - 359
        self.camara_rotacion_y = max(-90, min(90, self.camara_rotacion_y))

        yaw = math.radians(self.camara_rotacion_x)
        forward_x = math.sin(yaw)
        forward_z = math.cos(yaw)
        right_x = math.cos(yaw)
        right_z = -math.sin(yaw)

        if keys[pygame.K_w]:
            self.xyz[0] -= forward_x * self.speed
            self.xyz[2] -= forward_z * self.speed
        if keys[pygame.K_s]:
            self.xyz[0] += forward_x * self.speed
            self.xyz[2] += forward_z * self.speed
        if keys[pygame.K_a]:
            self.xyz[0] -= right_x * self.speed
            self.xyz[2] -= right_z * self.speed
        if keys[pygame.K_d]:
            self.xyz[0] += right_x * self.speed
            self.xyz[2] += right_z * self.speed
        if keys[pygame.K_SPACE]:
            self.xyz[1] += self.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.xyz[1] -= self.speed
        #if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:

        self._update_chunk_position()

    def _update_chunk_position(self):
        for i in range(3):
            moved_chunks, pos = divmod(self.xyz[i], self.cmove)
            if pos < 0:
                moved_chunks -= 1
                pos += self.cmove
            self.chunk_xyz[i] += int(moved_chunks)
            self.xyz[i] = pos

    def get_global_position(self):
        return [self.xyz[0] + self.chunk_xyz[0] * self.cmove,
                self.xyz[1] + self.chunk_xyz[1] * self.cmove,
                self.xyz[2] + self.chunk_xyz[2] * self.cmove]

    def get_player_position_in_chunk(self):
        return [self.xyz[0],
                self.xyz[1],
                self.xyz[2]]