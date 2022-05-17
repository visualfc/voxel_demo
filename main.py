from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(voxel_edges=0, exposure=2)
scene.set_floor(-0.85, (1.0, 1.0, 1.0))
scene.set_directional_light((1, 1, -1), 0.2, (1, 0.8, 0.6))

@ti.func
def block(pos, size, mat, color, boder_color):
    mx, my, mz = pos.x+size.x-1, pos.y+size.y-1, pos.z+size.z-1
    for x, y, z in ti.ndrange((pos[0], pos[0] + size[0]), (pos[1], pos[1] + size[1]), (pos[2], pos[2] + size[2])):
        bx = (x == pos.x or x == pos.x+size.x-1)
        by = (y == pos.y or y == pos.y+size.y-1)
        bz = (z == pos.z or z == pos.z+size.z-1)
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

@ti.func
def draw_text(pos, data, color):
    for i in range(8):
        if ((data[0] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y+7,pos.z), 1, color)
        if ((data[1] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y+6,pos.z), 1, color)
        if ((data[2] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y+5,pos.z), 1, color)
        if ((data[3] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y+4,pos.z), 1, color)
        if ((data[4] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y+3,pos.z), 1, color)
        if ((data[5] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y+2,pos.z), 1, color)
        if ((data[6] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y+1,pos.z), 1, color)
        if ((data[7] << i)&0x00ff) >> 7 == 1:scene.set_voxel(ivec3(pos.x+i,pos.y,pos.z), 1, color)

@ti.kernel
def initialize_voxels():
    # https://www.colinfahey.com/tetris/tetris.html
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
    # draw text 3d tetris
    xoff,yoff,zoff = -60,10,-40
    draw_text(ivec3(xoff+12,yoff+8,zoff),[0x00,0x1C,0x22,0x02,0x1C,0x02,0x22,0x1C],darkgreen)
    draw_text(ivec3(xoff+20,yoff+8,zoff),[0x00,0x3C,0x22,0x22,0x22,0x22,0x22,0x3C],darkgreen)
    draw_text(ivec3(xoff,yoff,zoff),[0x00,0x3E,0x08,0x08,0x08,0x08,0x08,0x08],darkgreen)
    draw_text(ivec3(xoff+6,yoff,zoff),[0x00,0x3E,0x20,0x20,0x3E,0x20,0x20,0x3E],darkgreen)
    draw_text(ivec3(xoff+12,yoff,zoff),[0x00,0x3E,0x08,0x08,0x08,0x08,0x08,0x08],darkgreen)
    draw_text(ivec3(xoff+18,yoff,zoff),[0x00,0x38,0x24,0x24,0x38,0x30,0x28,0x24],darkgreen)
    draw_text(ivec3(xoff+24,yoff,zoff),[0x00,0x1C,0x08,0x08,0x08,0x08,0x08,0x1C],darkgreen)
    draw_text(ivec3(xoff+30,yoff,zoff),[0x00,0x1C,0x22,0x20,0x1C,0x02,0x22,0x1C],darkgreen)
    # draw 3d tetris
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
