import PIL.Image

class cube:
    def __init__(self, xyz=(0,0,0), air=True, textures=1, solid=True, ID1=0, ID2=0):
        self.size=16
        self.x=xyz[0]
        self.y=xyz[1]
        self.z=xyz[2]
        """
        si solid es true
           es un cubo sólido
        si solid es false
           si air es true
              es un cubo de aire y no se renderiza ni colisiona
           si air es false
              es un enttyblock
              entonces que es un entity
              es un cubo que puede ser renderizado pero no colisiona
              o tener viscosidad/repelecion/apciones con el jugador
        """
        self.solid=solid
        self.air=air
        self.texture_default=f"assets/textures/cube/block_{ID1}-{ID2}_0.png"
        if textures==0:
            self.texture=[
                f"assets/textures/cube/block_{ID1}-{ID2}_1.png",  # id 0 is up
                f"assets/textures/cube/block_{ID1}-{ID2}_2.png",  # id 1 is down
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",  # id 2 is left
                f"assets/textures/cube/block_{ID1}-{ID2}_4.png",  # id 3 is right
                f"assets/textures/cube/block_{ID1}-{ID2}_5.png",  # id 4 is front
                f"assets/textures/cube/block_{ID1}-{ID2}_6.png"   # id 5 is back
            ]
        if textures==1:
            self.texture=[
                f"assets/textures/cube/block_{ID1}-{ID2}_1.png",  # id 0 is up
                f"assets/textures/cube/block_{ID1}-{ID2}_2.png",  # id 1 is down
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",  # id 2 is left
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",  # id 3 is right
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png",  # id 4 is front
                f"assets/textures/cube/block_{ID1}-{ID2}_3.png"   # id 5 is back
            ]
        else:
            self.texture=[
                self.texture_default,
                self.texture_default,
                self.texture_default,
                self.texture_default,
                self.texture_default,
                self.texture_default
            ]
        for i in range(len(self.texture)):
            if not self.texture[i]:
                self.texture[i] = self.texture_default