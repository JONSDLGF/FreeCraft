# asstes/classes/word.py
import random
from classes.cube import cube

def capa(Y, Ymax, Ymin):
    return Ymin <= Y <= Ymax

def chunkgen(RENDER_DISTANCE, seed=0, chunk_coords=(0, 0, 0)):
    cx, cy, cz = chunk_coords
    chunks = {}

    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE):
        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE):
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE):
                chunk_x = cx + dx
                chunk_y = cy + dy
                chunk_z = cz + dz

                blocks = []
                for x in range(16):
                    for z in range(16):
                        for y in range(16):
                            global_y = y + chunk_y * 16
                            pos = (x, y, z)

                            if not capa(global_y, 256, 64):
                                blocks.append(cube.cube_air(xyz=pos))
                            elif capa(global_y, 63, 60):
                                blocks.append(cube.cube_grass(xyz=pos))
                            elif capa(global_y, 59, 0):
                                blocks.append(cube.cube_cobblestone(xyz=pos))
                            else:
                                blocks.append(cube.cube_magma(xyz=pos))

                chunk_key = f"{chunk_x}~{chunk_y}~{chunk_z}"
                chunks[chunk_key] = blocks

    return chunks

def build_chunk_cube_map(chunks):
    chunk_cube_map = {}
    for chunk_key, cubos in chunks.items():
        chunk_cube_map[chunk_key] = {(cubo.x, cubo.y, cubo.z): cubo for cubo in cubos}
    return chunk_cube_map