from scene import Scene
import taichi as ti
from taichi.math import *

# https://www.colinfahey.com/tetris/tetris.html

scene = Scene(voxel_edges=0, exposure=2)
scene.set_floor(-0.85, (1.0, 1.0, 1.0))
scene.set_directional_light((1, 1, -1), 0.2, (1, 0.8, 0.6))


@ti.func
def block(pos, size, mat, color, boder_color):
    mx, my, mz = pos.x+size.x-1, pos.y+size.y-1, pos.z+size.z-1
    for x, y, z in ti.ndrange((pos[0], pos[0] + size[0]), (pos[1], pos[1] + size[1]), (pos[2], pos[2] + size[2])):
        bx, by, bz = (x == pos.x or x == pos.x+size.x-1), (y == pos.y or y ==
                                                           pos.y+size.y-1), (z == pos.z or z == pos.z+size.z-1)
        if (bx and by) or (bx and bz) or (by and bz):
            scene.set_voxel(ivec3(x, y, z), mat, boder_color)
        else:
            scene.set_voxel(ivec3(x, y, z), mat, color)


@ti.func
def tetris(pos, r, face, border, i):
    block(pos+ivec3(i[0:3])*r, ivec3(r, r, r), 1, face, border)
    block(pos+ivec3(i[3:6])*r, ivec3(r, r, r), 1, face, border)
    block(pos+ivec3(i[6:9])*r, ivec3(r, r, r), 1, face, border)
    block(pos+ivec3(i[9:12])*r, ivec3(r, r, r), 1, face, border)


@ti.func
def create_block(pos, size, color, color_noise):
    for I in ti.grouped(
            ti.ndrange((pos[0], pos[0] + size[0]), (pos[1], pos[1] + size[1]),
                       (pos[2], pos[2] + size[2]))):
        scene.set_voxel(I, 1, color + color_noise * ti.random())


@ti.func
def tetris_bottom(pos, size, r, color, boder_color):
    for x in range(size):
        for z in range(size):
            block(pos+ivec3(x*r, 0, z*r), ivec3(r, r, r), 1, color, boder_color)


@ti.kernel
def initialize_voxels():
    # Your code here! :-)
    red, darkred = vec3(1, 0, 0), vec3(139/255, 0, 0)
    green, darkgreen = vec3(0, 1, 0), vec3(0, 100/255, 0)
    blue, darkblue = vec3(0, 0, 1), vec3(0, 0, 139/255)
    yellow, darkyellow = vec3(1, 1, 0), vec3(139/255, 139/255, 0)
    pices_o0, pices_o1, pices_o2 = [0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1], [
        0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0], [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]
    pices_i0, pices_i1, pices_i2 = [0, 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0], [
        0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 3, 0], [0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 3]
    pices_s0, pices_s1, pices_s2 = [0, 0, 0, 1, 0, 0, 1, 0, -1, 2, 0, -1], [
        0, 0, 0, 0, 1, 0, -1, 1, 0, -1, 2, 0], [0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 2]
    pices_l0, pices_l1, pices_l2 = [0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 1], [
        0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 1]
    pices_t0, pices_t1, pices_t2 = [0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0, 1], [
        0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 1, 0], [0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 1, 1]
    pices_t3, pices_t4, pices_t5 = [0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0, -1], [
        0, 0, 0, 1, 0, 0, 2, 0, 0, 1, -1, 0], [0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 1]

    x, y, z = -30, -45, -60
    size = 6
    create_block(ivec3(x-4, y-3, z-4), ivec3(44, 3, 44),
                 vec3(0, 191/255, 1), vec3(0, 0.2, 0.1))
    tetris_bottom(ivec3(x, y, z), 6, size, vec3(105/255, 105/255, 105/255), vec3(0, 0, 0))
    tetris(ivec3(x, y+size, z), size, green, darkgreen, pices_o0)
    tetris(ivec3(x+size*2, y+size, z), size, red, darkred, pices_i0)
    tetris(ivec3(x+size, y+size, z+size*2), size, yellow, darkyellow, pices_s0)
    tetris(ivec3(x, y+size, z+size*2), size, blue, darkblue, pices_t5)
    tetris(ivec3(x, y+size, z+size*3), size, green, darkgreen, pices_l0)
    tetris(ivec3(x+size*3, y+size*2, z), size, green, darkgreen, pices_t1)
    tetris(ivec3(x+size*3, y+size*10, z), size, yellow, darkyellow, pices_t4)


initialize_voxels()

scene.finish()
