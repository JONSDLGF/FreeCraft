import OpenGL.GL as gl
from PIL import Image

class TextureManager:
    def __init__(self):
        self.textures = {}  # path: texture_id

    def get_texture(self, path):
        if path in self.textures:
            return self.textures[path]
        # Cargar la textura y guardarla
        img = Image.open(path).convert("RGBA")
        img_data = img.tobytes()
        width, height = img.size
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        self.textures[path] = texture_id
        return texture_id

texture_manager = TextureManager()

# Suponiendo que cada cubo tiene cubo.x, cubo.y, cubo.z
direcciones = {
    "up":    (0, 1, 0),
    "down":  (0, -1, 0),
    "left":  (-1, 0, 0),
    "right": (1, 0, 0),
    "front": (0, 0, 1),
    "back":  (0, 0, -1)
}

def get_cubo_en_pos(chunk, x, y, z):
    for c in chunk:
        if c.x == x and c.y == y and c.z == z:
            return c
    return None

def render_3D_all(chunk):
    for cubo in chunk:
        for cara, (dx, dy, dz) in direcciones.items():
            vecino = get_cubo_en_pos(chunk, cubo.x + dx, cubo.y + dy, cubo.z + dz)
            if not vecino or not vecino.solid:
                renderizar_cara(cubo, cara)

def renderizar_cara(cubo, cara):
    # Mapear nombre de cara a índice de textura
    cara_indices = {
        "up": 0,
        "down": 1,
        "left": 2,
        "right": 3,
        "front": 4,
        "back": 5
    }
    idx = cara_indices[cara]
    textura_path = cubo.texture[idx]
    texture_id = texture_manager.get_texture(textura_path)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    # Coordenadas del cubo
    x, y, z = cubo.x*cubo.size, cubo.y*cubo.size, cubo.z*cubo.size
    s = cubo.size / 2

    # Vértices para cada cara
    vertices = {
        "up":    [(x-s, y+s, z-s), (x+s, y+s, z-s), (x+s, y+s, z+s), (x-s, y+s, z+s)],
        "down":  [(x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y-s, z-s), (x-s, y-s, z-s)],
        "left":  [(x-s, y-s, z-s), (x-s, y-s, z+s), (x-s, y+s, z+s), (x-s, y+s, z-s)],
        "right": [(x+s, y-s, z+s), (x+s, y-s, z-s), (x+s, y+s, z-s), (x+s, y+s, z+s)],
        "front": [(x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y+s, z+s), (x-s, y+s, z+s)],
        "back":  [(x+s, y-s, z-s), (x-s, y-s, z-s), (x-s, y+s, z-s), (x+s, y+s, z-s)]
    }

    # Dibujar la cara
    gl.glBegin(gl.GL_QUADS)
    gl.glTexCoord2f(0, 1); gl.glVertex3fv(vertices[cara][0])
    gl.glTexCoord2f(1, 1); gl.glVertex3fv(vertices[cara][1])
    gl.glTexCoord2f(1, 0); gl.glVertex3fv(vertices[cara][2])
    gl.glTexCoord2f(0, 0); gl.glVertex3fv(vertices[cara][3])
    gl.glEnd()

def aplicar_camara(player):
    gl.glLoadIdentity()
    gl.glRotatef(-player.camera_angle_y, 1, 0, 0)
    gl.glRotatef(-player.camera_angle_x, 0, 1, 0)
    gl.glTranslatef(-player.x, -player.y, -player.z)
