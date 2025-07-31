# assets/classes/cubo.py

class cube:
    def __init__(self, func=None, xyz=(0, 0, 0), see=True, solid=True, NAME="ERR", textures=0):
        """
        esta clase es para los bloques y se ira actualizando por cada nueva mecanicas asi que
        sera compatible
        """

        self.size = 1
        self.name = NAME
        self.intern_func = func if func is not None else self.default_behavior
        self.x, self.y, self.z = xyz
        self.see = see    #### MUY INPORTANTE QUE SI see ES TURE SE VERA SI NO ES PUES NO DE VERA
        # error de el rende4rizado if cube.see:... severia ser if not cube.see:...
        self.solid = solid

        base_path = "assets/textures/cube"

        # Texturas por cara, según el esquema nuevo
        if textures == None and see == False:
            self.texture=[None]*6
        elif textures == 0:
            self.texture = [
                f"{base_path}/block_FC;{NAME}_SIDE.png",
                f"{base_path}/block_FC;{NAME}_SIDE.png",
                f"{base_path}/block_FC;{NAME}_SIDE.png",
                f"{base_path}/block_FC;{NAME}_SIDE.png",
                f"{base_path}/block_FC;{NAME}_SIDE.png",
                f"{base_path}/block_FC;{NAME}_SIDE.png",
            ]
        elif textures == 1:
            # TOP/BOTTOM personalizados, resto iguales
            self.texture = [
                f"{base_path}/block_FC;{NAME}_TOP.png",
                f"{base_path}/block_FC;{NAME}_BOTTOM.png",
                f"{base_path}/block_FC;{NAME}_SIDE.png",  # LEFT
                f"{base_path}/block_FC;{NAME}_SIDE.png",  # RIGHT
                f"{base_path}/block_FC;{NAME}_SIDE.png",  # FRONT
                f"{base_path}/block_FC;{NAME}_SIDE.png",  # BACK
            ]
        elif textures == 2:
            # Todos los lados por separado
            self.texture = [
                f"{base_path}/block_FC;{NAME}_TOP.png",
                f"{base_path}/block_FC;{NAME}_BOTTOM.png",
                f"{base_path}/block_FC;{NAME}_LEFT.png",
                f"{base_path}/block_FC;{NAME}_RIGHT.png",
                f"{base_path}/block_FC;{NAME}_FRONT.png",
                f"{base_path}/block_FC;{NAME}_BACK.png",
            ]
        else:
            # Textura igual para todo
            default_texture = f"{base_path}/block_{NAME}_ALL.png"
            self.texture = [default_texture] * 6

        # Fallback: si una ruta es None o vacía, se reemplaza por la default
        fallback = f"{base_path}/block_{NAME}_ALL.png"
        self.texture = [t if t else fallback for t in self.texture]
    
    def default_behavior(self, *args): pass

    @classmethod
    def cube_air(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, see=False, solid=False, NAME="AIR", textures=None)

    @classmethod
    def cube_grass(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, NAME="GRASS", textures=1)

    @classmethod
    def cube_cobblestone(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, NAME="COBBLESTONE", textures=2)

    @classmethod
    def cube_magma(cls, xyz=(0, 0, 0)):
        return cls(xyz=xyz, NAME="MAGMA", textures=2)
