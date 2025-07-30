# assets/classes/cubo.py

class cube:
    def __init__(self, xyz=(0, 0, 0), see=True, solid=True, ID="ERR", textures=1):
        self.size = 1
        self.x, self.y, self.z = xyz
        self.see = see
        self.solid = solid

        base_path = "assets/textures/cube"

        # Texturas por cara, según el esquema nuevo
        if textures == None:
            self.texture=[None]*6
        elif textures == 0:
            # TOP/BOTTOM personalizados, resto iguales
            self.texture = [
                f"{base_path}/block_FC;{ID}_TOP.png",
                f"{base_path}/block_FC;{ID}_BOTTOM.png",
                f"{base_path}/block_FC;{ID}_SIDE.png",  # LEFT
                f"{base_path}/block_FC;{ID}_SIDE.png",  # RIGHT
                f"{base_path}/block_FC;{ID}_SIDE.png",  # FRONT
                f"{base_path}/block_FC;{ID}_SIDE.png",  # BACK
            ]
        elif textures == 1:
            # Todos los lados por separado
            self.texture = [
                f"{base_path}/block_FC;{ID}_TOP.png",
                f"{base_path}/block_FC;{ID}_BOTTOM.png",
                f"{base_path}/block_FC;{ID}_LEFT.png",
                f"{base_path}/block_FC;{ID}_RIGHT.png",
                f"{base_path}/block_FC;{ID}_FRONT.png",
                f"{base_path}/block_FC;{ID}_BACK.png",
            ]
        else:
            # Textura igual para todo
            default_texture = f"{base_path}/block_{ID}_ALL.png"
            self.texture = [default_texture] * 6

        # Fallback: si una ruta es None o vacía, se reemplaza por la default
        fallback = f"{base_path}/block_{ID}_ALL.png"
        self.texture = [t if t else fallback for t in self.texture]

    @classmethod
    def cube_air(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, see=False, solid=False, ID="AIR", textures=None)

    @classmethod
    def cube_grass(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, ID="GRASS", textures=0)

    @classmethod
    def cube_cobblestone(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, ID="COBBLESTONE", textures=2)

    @classmethod
    def cube_magma(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, ID="MAGMA", textures=2)
