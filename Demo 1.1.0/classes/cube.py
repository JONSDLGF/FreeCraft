# classes/cube.py
class cube:
    def __init__(self, xyz=(0,0,0), air=False, textures=1, solid=True, ID1=0, ID2=0):
        self.size = 1
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
        self.air = air
        self.solid = solid
        self.texture_default = f"assets/textures/cube/block_{ID1}-{ID2}_3.png"
        if textures == 0:
            self.texture = None
        if textures == 0:
            self.texture = [
                f"assets/textures/cube/block_{ID1}-{ID2}_1.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_2.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png"
            ]
        elif textures == 1:
            self.texture = [
                f"assets/textures/cube/block_{ID1}-{ID2}_1.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_2.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png"
            ]
        else:
            self.texture = [self.texture_default] * 6
        for i in range(len(self.texture)):
            if not self.texture[i]:
                self.texture[i] = self.texture_default

    @classmethod
    def cube_air(cls, xyz=(0,0,0)):
        return cls(xyz=xyz, air=True, solid=False, textures=2, ID1=0, ID2=0)

    @classmethod
    def cube_grass(cls, xyz=(0,0,0)):
        return cls(xyz=xyz, air=False, solid=True, textures=1, ID1=1, ID2=0)

    @classmethod
    def cube_cobelstone(cls, xyz=(0,0,0)):
        return cls(xyz=xyz, air=False, solid=True, textures=1, ID1=2, ID2=0)

    @classmethod
    def cube_magma(cls, xyz=(0,0,0)):
        return cls(xyz=xyz, air=False, solid=True, textures=1, ID1=3, ID2=0)