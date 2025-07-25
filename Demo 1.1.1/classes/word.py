# classes/word.py
from classes.cube import cube

def create_chunk_cubos(chunk_cubos):
    cube_map = {}
    for cubo in chunk_cubos:
        cube_map[(cubo.x, cubo.y, cubo.z)] = cubo
    return cube_map

def get_cubo_en_pos(cube_map, x, y, z, chunk_pos, chunks, CHUNK_SIZE=16):
    chunk_x = chunk_pos[0] + (x // CHUNK_SIZE)
    chunk_z = chunk_pos[2] + (z // CHUNK_SIZE)
    local_x = x % CHUNK_SIZE
    if local_x < 0:
        local_x += CHUNK_SIZE
    local_z = z % CHUNK_SIZE
    if local_z < 0:
        local_z += CHUNK_SIZE

    for chunk_data, c_pos in chunks:
        if c_pos == (chunk_x, chunk_pos[1], chunk_z):
            cube_map = create_chunk_cubos(chunk_data[0])
            return cube_map.get((local_x, y, local_z))
    return None

def chunkgen(seed=0, csize=16, chunk_coords=(0, 0, 0)):
    CHUNK_SIZE = csize
    cx, cy, cz = chunk_coords
    cubos = []

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                global_y = y + cy * CHUNK_SIZE
                if global_y > 64:
                    cubos.append(cube.cube_air(xyz=(x, y, z)))
                elif 64 >= global_y > 60:
                    cubos.append(cube.cube_grass(xyz=(x, y, z)))
                elif 60 >= global_y > 4:
                    cubos.append(cube.cube_cobelstone(xyz=(x, y, z)))
                elif global_y <= 4:
                    cubos.append(cube.cube_magma(xyz=(x, y, z)))

    return [[cubos, [cx, cy, cz]]]

