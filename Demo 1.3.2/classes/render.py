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
        self.textures_path = {}    # mapa path -> (offset, size)
        self.texture_ids = {}      # mapa path -> OpenGL texture id

        self.morethan = 512
        self.MIBmax = 20
        self.cache = bytearray((2**20) * self.MIBmax)

        # Textura por defecto codificada en base64 (un pixel transparente o algo similar)
        self.default_texture_base64 = (
            "Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA"
            "/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA"
            "/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wA"
            "A/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA"
            "/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAA/wAA/wAA/wAA/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAA/wAA/wAA"
            "/wAA/wAA/wAA/wAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD"
            "/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8A"
            "AP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AA"
            "AD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/"
            "AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP"
            "8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8A"
            "AP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD"
            "/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD"
            "/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP"
            "8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/A"
            "AD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/A"
            "AD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8A"
            "AP8AAP8AAP8AAP8AAP8AAP8AAAD/AAD/AAD/AAD/AAD/AAD/AAD/AAD/AP8AAP8AAP8AAP8AAP8AAP8AAP8A"
            "AP8AA=="
        )
        default_texture_bytes = base64.b64decode(self.default_texture_base64)
        self.default_texture_data = Image.open(io.BytesIO(default_texture_bytes)).convert("RGBA")

        # Carga textura por defecto para asegurar que texture_ids no esté vacía
        self.new("assets/textures/cube/block_FC;ERR_SIDE.png")

    def get_texture(self, path):
        if len(self.textures_path) > self.morethan:
            self.reload()
        # Retorna id de textura ya cargada si existe
        if path in self.texture_ids:
            return self.texture_ids[path]

        # Intentar cargar la imagen
        try:
            img = Image.open(path).convert("RGBA")  # PNG con transparencia
        except Exception as e:
            print(f"[TextureManager] Error cargando {path}: {e}. Usando textura por defecto.")
            img = self.default_texture_data

        width, height = img.size
        tex_data = img.tobytes()

        # Crear textura OpenGL
        tex_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)

        # Subir datos con canal alpha
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height,
                        0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, tex_data)

        # Filtrado NEAREST para evitar suavizado/antialiasing
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        # Habilitar wrap para evitar bordes raros si se repite
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        self.texture_ids[path] = tex_id
        return tex_id

    def new(self, path):
        # Esta función parece manejar un cache interno, la dejo intacta pero puedes mejorarla si quieres
        if self.textures_path:
            last_offset, last_size = next(reversed(self.textures_path.values()))
            new_offset = last_offset + (last_size ** 2) * 4
        else:
            new_offset = 0

        try:
            with Image.open(path) as img:
                img = img.convert("RGBA")
                width, height = img.size
        except Exception as e:
            print(f"[TextureManager] Error al cargar imagen {path}: {e}")
            img = self.default_texture_data
            width, height = img.size

        if width != height:
            raise ValueError(f"[TextureManager] Textura no cuadrada: {path} ({width}x{height})")

        size = width
        img_bytes = img.tobytes()
        end = new_offset + len(img_bytes)
        if end > len(self.cache):
            raise MemoryError("[TextureManager] Cache llena")

        self.cache[new_offset:end] = img_bytes

        # Guardar en path map (offset y tamaño)
        self.textures_path[path] = (new_offset, size)
        return [new_offset, size]

    def get_texture_bin(self, offset, size):
        return self.cache[offset:offset + (size ** 2) * 4], size

    def reload(self):
        print("[TextureManager] Limpiando cache de texturas")
        self.textures_path.clear()
        self.cache = bytearray(2 ** 20 * self.MIBmax)

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

class Render_cube:
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

    def render_3D_all(self, chunk_cube_map, face_masks, player):
        for chunk_key, chunk_data in chunk_cube_map.items():  # chunk_data es un dict {(x,y,z): cubo}
            cx, cy, cz = map(int, chunk_key.split("~"))
            dx = cx - player.chunk_xyz[0]
            dy = cy - player.chunk_xyz[1]
            dz = cz - player.chunk_xyz[2]

            for pos, cubo in chunk_data.items():  # ahora pos = (x, y, z)
                if not cubo.see:
                    continue

                gx = cubo.x + dx * 16
                gy = cubo.y + dy * 16
                gz = cubo.z + dz * 16
                face_mask = face_masks.get((chunk_key, pos), 0b111111)
                self.render_3D_cube(cubo, (gx, gy, gz), face_mask)

    def face_culling(self, chunks, chunk_cube_map, CHUNK_SIZE=17):
        """:| hemm tambien funciona pero el render_3D_all sera el problema?"""
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
                # ok que mierda a pasado cuando lo e puesto en not, ya se ve bien, es un misterio
                if not cubo.see:
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
                    if not vecino.see:
                        face_mask |= (1 << i)
                face_masks[(chunk_key, pos)] = face_mask
        return face_masks

    def get_cubo_global(self, x, y, z, chunk_pos, chunk_cube_map, CHUNK_SIZE):
        """esta funcion esta bien asi que no la toques"""
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

    def set_fullscreen(self):
        screen_info = pygame.display.Info()
        screen = pygame.display.set_mode(
            (screen_info.current_w, screen_info.current_h),
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN
        )
        return screen_info.current_w, screen_info.current_h

    def set_windowed(self, width=800, height=600):
        screen = pygame.display.set_mode(
            (width, height),
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        return width, height


class Render_entity:
    def __init__(self):
        self.texture_manager = TextureManager()