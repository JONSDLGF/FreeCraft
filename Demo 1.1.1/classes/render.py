# classes/render.py
import OpenGL.GL as gl
import numpy as np
import ctypes
import pygame
from PIL import Image
import base64
import io
from classes.word import create_chunk_cubos, get_cubo_en_pos
import math

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
    
    def normalize(self):
        l = self.length
        if l == 0:
            return Vector((0, 0, 0))
        return Vector((self.x / l, self.y / l, self.z / l))


class TextureManager:
    def __init__(self):
        self.textures = {}
        self.default_texture_base64 = """Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8A"""
        self.default_texture = base64.b64decode(self.default_texture_base64)
        self.default_texture_data = Image.open(io.BytesIO(self.default_texture)).convert("RGBA")

    def get_texture(self, path):
        if path in self.textures:
            return self.textures[path]
        try:
            img = Image.open(path).convert("RGBA")
        except Exception as e:
            print(f"Error loading texture '{path}': {e}")
            img = self.default_texture_data
        img_data = img.tobytes()
        width, height = img.size
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        self.textures[path] = texture_id
        return texture_id

class Camera:
    def __init__(self, player):
        self.player = player
        self.fov = 70.0
        self.aspect = 4/3
        self.near = 0.1
        self.far = 1000.0

    def aplicar_camara(self):
        gl.glLoadIdentity()
        gl.glRotatef(-self.player.camara_rotacion_y, 1, 0, 0)  # Pitch
        gl.glRotatef(-self.player.camara_rotacion_x, 0, 1, 0)  # Yaw
        pos = self.player.get_player_position_in_chunk()
        gl.glTranslatef(-pos[0], -pos[1], -pos[2])

    def position(self):
        pos = self.player.get_player_position_in_chunk()
        return Vector(pos)
    
    @property
    def angle_x(self):
        return self.player.camara_rotacion_x

    @property
    def angle_y(self):
        return self.player.camara_rotacion_y


class Renderer:
    def __init__(self):
        self.texture_manager = TextureManager()
        self.direcciones = {
            "up": (0, 1, 0), "down": (0, -1, 0), "left": (-1, 0, 0),
            "right": (1, 0, 0), "front": (0, 0, 1), "back": (0, 0, -1)
        }
        self.cara_indices = {
            "up": 0, "down": 1, "left": 2,
            "right": 3, "front": 4, "back": 5
        }
        self.vbo_cache = {}
        self.max_vbo_cache_size = 50

    def chunk_block_put(self, cube, chunk_pos, player, CHUNK_SIZE=16):
        real_chunk_pos = [chunk_pos[i] - player.chunk_xyz[i] for i in range(3)]
        return [cube.x + real_chunk_pos[0] * CHUNK_SIZE,
                cube.y + real_chunk_pos[1] * CHUNK_SIZE,
                cube.z + real_chunk_pos[2] * CHUNK_SIZE]

    def create_chunk_vbo(self, chunk_cubos, chunk_pos, chunks, player, CHUNK_SIZE=16):
        vertices, tex_coords, texture_ids = [], [], []
        cube_map = create_chunk_cubos(chunk_cubos)

        for cubo in chunk_cubos:
            if cubo.air:
                continue
            for cara, (dx, dy, dz) in self.direcciones.items():
                vecino = self.get_cubo_global(cubo.x + dx, cubo.y + dy, cubo.z + dz, chunk_pos, chunks, CHUNK_SIZE)
                if not vecino or not vecino.solid:
                    s = cubo.size / 2.0
                    x, y, z = self.chunk_block_put(cubo, chunk_pos, player, CHUNK_SIZE)
                    face_vertices = {
                        "up": [(x-s, y+s, z-s), (x+s, y+s, z-s), (x+s, y+s, z+s), (x-s, y+s, z+s)],
                        "down": [(x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y-s, z-s), (x-s, y-s, z-s)],
                        "left": [(x-s, y-s, z-s), (x-s, y-s, z+s), (x-s, y+s, z+s), (x-s, y+s, z-s)],
                        "right": [(x+s, y-s, z+s), (x+s, y-s, z-s), (x+s, y+s, z-s), (x+s, y+s, z+s)],
                        "front": [(x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y+s, z+s), (x-s, y+s, z+s)],
                        "back": [(x+s, y-s, z-s), (x-s, y-s, z-s), (x-s, y+s, z-s), (x+s, y+s, z-s)]
                    }
                    face_tex_coords = [(0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
                    vertices.extend(face_vertices[cara])
                    tex_coords.extend(face_tex_coords)
                    texture_ids.append(self.texture_manager.get_texture(cubo.texture[self.cara_indices[cara]]))

        if not vertices:
            return None, 0, [], 0

        vertices = np.array(vertices, dtype=np.float32)
        tex_coords = np.array(tex_coords, dtype=np.float32)

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes + tex_coords.nbytes, None, gl.GL_STATIC_DRAW)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, vertices.nbytes, tex_coords.nbytes, tex_coords)

        return vbo, len(vertices) // 3, texture_ids, vertices.nbytes

    def get_cubo_global(self, x, y, z, chunk_pos, chunks, CHUNK_SIZE):
        cx, cy, cz = chunk_pos
        lx, ly, lz = x, y, z
        if lx < 0: cx -= 1; lx += CHUNK_SIZE
        elif lx >= CHUNK_SIZE: cx += 1; lx -= CHUNK_SIZE
        if ly < 0: cy -= 1; ly += CHUNK_SIZE
        elif ly >= CHUNK_SIZE: cy += 1; ly -= CHUNK_SIZE
        if lz < 0: cz -= 1; lz += CHUNK_SIZE
        elif lz >= CHUNK_SIZE: cz += 1; lz -= CHUNK_SIZE
        for c, pos in chunks:
            if pos == (cx, cy, cz):
                for cubo in c:
                    if cubo.x == lx and cubo.y == ly and cubo.z == lz:
                        return cubo
        return None

    def face_culling(self, chunks, CHUNK_SIZE=16):
        culled = 0
        for chunk_data, chunk_pos in chunks:
            for cubo in chunk_data:
                if cubo.air:
                    continue
                visible = False
                for dx, dy, dz in self.direcciones.values():
                    vecino = self.get_cubo_global(cubo.x + dx, cubo.y + dy, cubo.z + dz, chunk_pos, chunks, CHUNK_SIZE)
                    if not vecino or not vecino.solid:
                        visible = True
                        break
                cubo.visible = visible
                if not visible:
                    culled += 1
        print(f"Face culling ocultó {culled} bloques.")

    def render_chunk_vbo(self, vbo, vertex_count, texture_ids, tex_coords_offset):
        if vertex_count == 0: return
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, None)
        gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, ctypes.c_void_p(tex_coords_offset))
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)

        current_texture, start_idx = None, 0
        for i, texture_id in enumerate(texture_ids):
            if texture_id != current_texture:
                if current_texture is not None:
                    gl.glBindTexture(gl.GL_TEXTURE_2D, current_texture)
                    gl.glDrawArrays(gl.GL_QUADS, start_idx * 4, (i - start_idx) * 4)
                current_texture, start_idx = texture_id, i
        if current_texture:
            gl.glBindTexture(gl.GL_TEXTURE_2D, current_texture)
            gl.glDrawArrays(gl.GL_QUADS, start_idx * 4, (len(texture_ids) - start_idx) * 4)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)

    def is_chunk_in_frustum(self, chunk_pos, camera, player, CHUNK_SIZE=16):
        rel_pos = Vector([(chunk_pos[i] - player.chunk_xyz[i]) * CHUNK_SIZE for i in range(3)])
        cam_pos = camera.position()
        dir_to_chunk = rel_pos - cam_pos

        fov_rad = math.radians(camera.fov)
        half_fov = fov_rad / 2.0
        dist = dir_to_chunk.length
        if dist == 0:
            return True  # El chunk está en la misma posición que la cámara; debe renderizarse

        cam_dir_x = math.cos(math.radians(camera.angle_x)) * math.cos(math.radians(camera.angle_y))
        cam_dir_y = math.sin(math.radians(camera.angle_y))
        cam_dir_z = math.sin(math.radians(camera.angle_x)) * math.cos(math.radians(camera.angle_y))
        cam_dir = Vector((cam_dir_x, cam_dir_y, cam_dir_z)).normalize()

        dot = (dir_to_chunk.x * cam_dir.x + dir_to_chunk.y * cam_dir.y + dir_to_chunk.z * cam_dir.z) / dist
        angle_to_chunk = math.acos(dot)

        return dist <= camera.far and angle_to_chunk <= half_fov

    def render_3D_all(self, chunks, player, camera, CHUNK_SIZE=16):
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glDepthRange(0.0, 1.0)
        camera.aplicar_camara()

        rendered_chunks = 0
        for chunk_data, chunk_pos in chunks:
            chunk_key = tuple(chunk_pos)
            if chunk_key not in self.vbo_cache:
                self.vbo_cache[chunk_key] = self.create_chunk_vbo(chunk_data, chunk_pos, chunks, player, CHUNK_SIZE)
            if self.is_chunk_in_frustum(chunk_pos, camera, player):
                vbo, vertex_count, texture_ids, tex_coords_offset = self.vbo_cache[chunk_key]
                self.render_chunk_vbo(vbo, vertex_count, texture_ids, tex_coords_offset)
                rendered_chunks += 1

        if len(self.vbo_cache) > self.max_vbo_cache_size:
            self.vbo_cache = {k: v for k, v in self.vbo_cache.items() if k in [c[1] for c in chunks]}

        print(f"Rendered {rendered_chunks} chunks, Cache size: {len(self.vbo_cache)}")

    def cleanup_vbos(self):
        for chunk_key, vbo_data in self.vbo_cache.items():
            gl.glDeleteBuffers(1, [vbo_data[0]])
        self.vbo_cache.clear()

    def render_3D_objects(self, player, camera):
        pass

    def set_fullscreen():
        screen_info = pygame.display.Info()
        screen = pygame.display.set_mode(
            (screen_info.current_w, screen_info.current_h),
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN
        )
        return screen_info.current_w, screen_info.current_h

    def set_windowed(width=800, height=600):
        screen = pygame.display.set_mode(
            (width, height),
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        return width, height