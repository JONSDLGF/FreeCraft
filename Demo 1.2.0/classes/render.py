# classes/render.py

import OpenGL.GL as gl
import pygame
from PIL import Image
import base64
import io
import math
import classes.cube as cube

class Vector:
    def __init__(self, xyz):
        self.x, self.y, self.z = xyz

    def __truediv__(self, scalar):
        return Vector((self.x / scalar, self.y / scalar, self.z / scalar))

    def __add__(self, other):
        return Vector((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def __mul__(self, scalar):
        return Vector((self.x * scalar, self.y * scalar, self.z * scalar))

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
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
        self.textures_path = {}
        self.texture_ids = {}
        self.morethan = 20
        self.MIBmax = 10
        self.cache = bytearray(2**20*self.MIBmax)
        self.default_texture_base64 = """Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8A"""
        self.default_texture = base64.b64decode(self.default_texture_base64)
        self.default_texture_data = Image.open(io.BytesIO(self.default_texture)).convert("RGBA")
        self.new("assets/textures/cube/block_FC;ERR_SIDE.png")

    def get_texture(self, path):
        if path in self.texture_ids:
            return self.texture_ids[path]

        # Cargar imagen y subir textura si no existe aún
        try:
            img = Image.open(path).convert("RGBA")
        except:
            img = self.default_texture_data

        width, height = img.size
        tex_data = img.tobytes()

        tex_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, tex_data)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        self.texture_ids[path] = tex_id
        return tex_id

    def new(self, path):
        # Calcular nuevo offset
        if self.textures_path:
            last_offset, last_size = next(reversed(self.textures_path.values()))
            new_offset = last_offset + (last_size ** 2) * 4
        else:
            new_offset = 0  # Primera textura

        # Cargar imagen desde disco
        try:
            with Image.open(path) as img:
                img = img.convert("RGBA")
                width, height = img.size
        except Exception as e:
            print(f"[TextureManager] Error al cargar imagen {path}: {e}")
            img = self.default_texture_data
            width, height = img.size

        # Verificar que sea cuadrada
        if width != height:
            raise ValueError(f"[TextureManager] Textura no cuadrada: {path} ({width}x{height})")

        size = width  # o height

        # Guardar los bytes en el cache
        img_bytes = img.tobytes()
        end = new_offset + len(img_bytes)
        if end > len(self.cache):
            raise MemoryError("[TextureManager] Cache llena")

        self.cache[new_offset:end] = img_bytes

        return [new_offset, size]

    def get_texture_bin(self,offset,size):
        return self.cache[offset:offset+(size**2)*4], size

    def reload(self):
        if len(self.textures_path) > self.morethan:
            print("[TextureManager] Limpiando cache de texturas")
            self.textures_path.clear()
            self.cache = bytearray(2**20 * self.MIBmax)
            self.new("assets/textures/cube/block_FC;ERR_SIDE.png")  # vuelve a cargar la textura por defecto

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

    def render_3D_cube(self, cubo, xyz, faceculling):
        x, y, z = xyz
        faces = [
            ("TOP",    (0, 1, 0),    (0b000001)),
            ("BOTTOM", (0, -1, 0),   (0b000010)),
            ("LEFT",   (-1, 0, 0),   (0b000100)),
            ("RIGHT",  (1, 0, 0),    (0b001000)),
            ("FRONT",  (0, 0, 1),    (0b010000)),
            ("BACK",   (0, 0, -1),   (0b100000)),
        ]
        size = cubo.size

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)

        for i, (face_name, normal, mask_bit) in enumerate(faces):
            if not (faceculling & mask_bit):
                continue

            tex_id = self.texture_manager.get_texture(cubo.texture[i])
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glBegin(gl.GL_QUADS)
            gl.glNormal3f(*normal)
            cara = self.get_face_vertices(i, x, y, z, size)
            for v in cara:
                gl.glTexCoord2f(*v[3:])
                gl.glVertex3f(*v[:3])
            gl.glEnd()

    def get_face_vertices(self, face_index, x, y, z, size):
        s = size / 2
        vertices = [
            [(x + s, y + s, z - s, 0, 1), (x - s, y + s, z - s, 1, 1), (x - s, y + s, z + s, 1, 0), (x + s, y + s, z + s, 0, 0)],
            [(x + s, y - s, z + s, 0, 1), (x - s, y - s, z + s, 1, 1), (x - s, y - s, z - s, 1, 0), (x + s, y - s, z - s, 0, 0)],
            [(x - s, y - s, z - s, 0, 1), (x - s, y - s, z + s, 1, 1), (x - s, y + s, z + s, 1, 0), (x - s, y + s, z - s, 0, 0)],
            [(x + s, y - s, z + s, 0, 1), (x + s, y - s, z - s, 1, 1), (x + s, y + s, z - s, 1, 0), (x + s, y + s, z + s, 0, 0)],
            [(x - s, y - s, z + s, 0, 1), (x + s, y - s, z + s, 1, 1), (x + s, y + s, z + s, 1, 0), (x - s, y + s, z + s, 0, 0)],
            [(x + s, y - s, z - s, 0, 1), (x - s, y - s, z - s, 1, 1), (x - s, y + s, z - s, 1, 0), (x + s, y + s, z - s, 0, 0)]
        ]
        return vertices[face_index]

    def render_3D_all(self, chunks, face_masks, player):
        for chunk_key, chunk_data in chunks.items():
            cx, cy, cz = map(int, chunk_key.split("~"))
            dx = cx - player.chunk_xyz[0]
            dy = cy - player.chunk_xyz[1]
            dz = cz - player.chunk_xyz[2]

            for cubo in chunk_data:
                if cubo.see:
                    continue
                gx = cubo.x + dx * 16
                gy = cubo.y + dy * 16
                gz = cubo.z + dz * 16

                face_mask = face_masks.get((chunk_key, (cubo.x, cubo.y, cubo.z)), 0b111111)
                self.render_3D_cube(cubo, (gx, gy, gz), face_mask)

    def face_culling(self, chunks, chunk_cube_map, CHUNK_SIZE=16):
        direcciones = {
            0: ( 0,  1,  0),
            1: ( 0, -1,  0),
            2: (-1,  0,  0),
            3: ( 1,  0,  0),
            4: ( 0,  0,  1),
            5: ( 0,  0, -1),
        }

        face_masks = {}

        for chunk_key, chunk_pos in [(k, tuple(map(int, k.split("~")))) for k in chunks.keys()]:
            cubos = chunk_cube_map[chunk_key]
            for pos, cubo in cubos.items():
                if cubo.see:
                    continue
                face_mask = 0
                for i, (dx, dy, dz) in direcciones.items():
                    vecino = self.get_cubo_global(
                        cubo.x + dx,
                        cubo.y + dy,
                        cubo.z + dz,
                        chunk_pos,
                        chunk_cube_map,
                        CHUNK_SIZE
                    )
                    if vecino.see:
                        face_mask |= (1 << i)

                face_masks[(chunk_key, pos)] = face_mask

        return face_masks

    def get_cubo_global(self, x, y, z, chunk_pos, chunk_cube_map, CHUNK_SIZE):
        cx, cy, cz = chunk_pos
        lx, ly, lz = x, y, z
        if lx < 0: cx -= 1; lx += CHUNK_SIZE
        elif lx >= CHUNK_SIZE: cx += 1; lx -= CHUNK_SIZE
        if ly < 0: cy -= 1; ly += CHUNK_SIZE
        elif ly >= CHUNK_SIZE: cy += 1; ly -= CHUNK_SIZE
        if lz < 0: cz -= 1; lz += CHUNK_SIZE
        elif lz >= CHUNK_SIZE: cz += 1; lz -= CHUNK_SIZE

        key = f"{cx}~{cy}~{cz}"
        if key in chunk_cube_map:
            return chunk_cube_map[key].get((lx, ly, lz), cube.cube((x, y, z), see=True))
        return cube.cube((x, y, z), see=True)

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
