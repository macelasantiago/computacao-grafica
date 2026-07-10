import math
import numpy as np
from OpenGL.GL import *
import ctypes
import glm
import os

class Cube:
    def __init__(self):

        self.vertices = np.array([
            -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 0.0,
             0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0,
             0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 1.0,
            -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 1.0,

            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,
             0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
             0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
            -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,

            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,
            -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 1.1,
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.1,
            -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0, 0.0,

             0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
             0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.1,
             0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.1,
              0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0,

            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
             0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
             0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
            -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0,

            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
             0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0,
             0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
            -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 2, 2, 3, 0,
            4, 5, 6, 6, 7, 4,
            8, 9, 10, 10, 11, 8,
            12, 13, 14, 14, 15, 12,
            16, 17, 18, 18, 19, 16,
            20, 21, 22, 22, 23, 20
        ], dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        self.vbo, self.ebo = glGenBuffers(2)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)


class Cylinder:
    def __init__(self, segments=32):
        vertices = []
        
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            next_angle = 2.0 * np.pi * (i + 1) / segments
            
            x1, z1 = 0.5 * np.cos(angle), 0.5 * np.sin(angle)
            x2, z2 = 0.5 * np.cos(next_angle), 0.5 * np.sin(next_angle)
            
            u1 = i / segments
            u2 = (i + 1) / segments
            
            vertices.extend([x1, 0.5, z1,  x1, 0.0, z1,  u1, 1.0])
            vertices.extend([x1, -0.5, z1, x1, 0.0, z1,  u1, 0.0])
            vertices.extend([x2, 0.5, z2,  x2, 0.0, z2,  u2, 1.0])
            
            vertices.extend([x2, 0.5, z2,  x2, 0.0, z2,  u2, 1.0])
            vertices.extend([x1, -0.5, z1, x1, 0.0, z1,  u1, 0.0])
            vertices.extend([x2, -0.5, z2, x2, 0.0, z2,  u2, 0.0])
            
        self.vertices = np.array(vertices, dtype=np.float32)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 8)


class CanetaBIC:
    def __init__(self, cylinder, cube):
        self.cylinder, self.cube = cylinder, cube

    def draw(self, draw_func, pos, tex, rot_z=90):
        draw_func(self.cylinder, tex, pos, glm.vec3(0.06, 1.5, 0.06), ry=0, rz=rot_z)
        offset = -0.8 if rot_z == 90 else 0.8
        draw_func(self.cube, tex, pos + glm.vec3(offset, 0, 0), glm.vec3(0.12, 0.08, 0.08), ry=0, rz=rot_z)


class Esfera:
    def __init__(self, radius=0.5, sectors=30, stacks=30):
        vertices = []
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + float(i+1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)
            
            for j in range(sectors):
                lng0 = 2 * math.pi * float(j) / sectors
                x0 = math.cos(lng0)
                y0 = math.sin(lng0)
                
                lng1 = 2 * math.pi * float(j+1) / sectors
                x1 = math.cos(lng1)
                y1 = math.sin(lng1)
                
                p1 = [x0*zr0, y0*zr0, z0]
                p2 = [x1*zr0, y1*zr0, z0]
                p3 = [x0*zr1, y0*zr1, z1]
                p4 = [x1*zr1, y1*zr1, z1]
                
                v1 = p1 + [p1[0]/radius, p1[1]/radius, p1[2]/radius] + [float(j)/sectors, float(i)/stacks]
                v2 = p2 + [p2[0]/radius, p2[1]/radius, p2[2]/radius] + [float(j+1)/sectors, float(i)/stacks]
                v3 = p3 + [p3[0]/radius, p3[1]/radius, p3[2]/radius] + [float(j)/sectors, float(i+1)/stacks]
                v4 = p4 + [p4[1]/radius, p4[2]/radius, p4[2]/radius] + [float(j+1)/sectors, float(i+1)/stacks]
                
                vertices.extend(v1 + v2 + v3)
                vertices.extend(v2 + v4 + v3)
                
        self.vertices = np.array(vertices, dtype=np.float32)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)
        glBindVertexArray(0)
        
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 8)
        glBindVertexArray(0)

class Coroa:
    def __init__(self, segments=16):
        vertices_list = []
        r_base = 0.4
        r_topo = 0.6
        h = 0.4

        for i in range(segments):
            t1 = (i / segments) * 2 * math.pi
            t2 = ((i + 1) / segments) * 2 * math.pi

            xb1, zb1 = r_base * math.cos(t1), r_base * math.sin(t1)
            xb2, zb2 = r_base * math.cos(t2), r_base * math.sin(t2)
            xt1, zt1 = r_topo * math.cos(t1), r_topo * math.sin(t1)
            xt2, zt2 = r_topo * math.cos(t2), r_topo * math.sin(t2)

            n = [0.0, 1.0, 0.0]

            if i % 2 == 0:
                xt_mid, zt_mid = r_topo * math.cos((t1 + t2)/2), r_topo * math.sin((t1 + t2)/2)
                vertices_list.extend([xb1, 0.0, zb1,  n[0], n[1], n[2],  0.0, 0.0])
                vertices_list.extend([xb2, 0.0, zb2,  n[0], n[1], n[2],  1.0, 0.0])
                vertices_list.extend([xt_mid, h, zt_mid, n[0], n[1], n[2], 0.5, 1.0])
            else:
                vertices_list.extend([xb1, 0.0, zb1,  n[0], n[1], n[2],  0.0, 0.0])
                vertices_list.extend([xb2, 0.0, zb2,  n[0], n[1], n[2],  1.0, 0.0])
                vertices_list.extend([xt1, h * 0.4, zt1, n[0], n[1], n[2], 0.0, 0.5])

                vertices_list.extend([xb2, 0.0, zb2,  n[0], n[1], n[2],  1.0, 0.0])
                vertices_list.extend([xt2, h * 0.4, zt2, n[0], n[1], n[2], 1.0, 0.5])
                vertices_list.extend([xt1, h * 0.4, zt1, n[0], n[1], n[2], 0.0, 0.5])

        self.vertices = np.array(vertices_list, dtype=np.float32)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 8)
        glBindVertexArray(0)


class ModelOBJ:
    def __init__(self, filepath):
        vertices = []
        normals = []
        texcoords = []
        faces = []

        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    vertices.append([float(x) for x in line.strip().split()[1:]])
                elif line.startswith('vt '):
                    texcoords.append([float(x) for x in line.strip().split()[1:]])
                elif line.startswith('vn '):
                    normals.append([float(x) for x in line.strip().split()[1:]])
                elif line.startswith('f '):
                    face_vertices = line.strip().split()[1:]
                    for i in range(1, len(face_vertices) - 1):
                        faces.append([face_vertices[0], face_vertices[i], face_vertices[i+1]])

        vertex_data = []
        for face in faces:
            for vertex in face:
                parts = vertex.split('/')
                v_idx = int(parts[0]) - 1
                t_idx = int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1
                n_idx = int(parts[2]) - 1 if len(parts) > 2 and parts[2] else -1

                vertex_data.extend(vertices[v_idx])
                
                if n_idx != -1 and n_idx < len(normals):
                    vertex_data.extend(normals[n_idx])
                else:
                    vertex_data.extend([0.0, 1.0, 0.0]) # Fallback
                
                if t_idx != -1 and t_idx < len(texcoords):
                    vertex_data.extend(texcoords[t_idx])
                else:
                    vertex_data.extend([0.0, 0.0]) # Fallback

        self.vertices = np.array(vertex_data, dtype=np.float32)
        
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)
        
        glBindVertexArray(0)

    def draw(self):
        if len(self.vertices) == 0: return
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 8)
        glBindVertexArray(0)