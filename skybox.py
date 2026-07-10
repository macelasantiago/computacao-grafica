import OpenGL.GL as gl
import numpy as np
import ctypes
import glm
from shader_utils import Shader
from PIL import Image
import os

class Skybox:
    def __init__(self, faces_paths):
        
        vertices = np.array([
            -1.0,  1.0, -1.0,  -1.0, -1.0, -1.0,   1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,   1.0,  1.0, -1.0,  -1.0,  1.0, -1.0,
            -1.0, -1.0,  1.0,  -1.0, -1.0, -1.0,  -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,  -1.0,  1.0,  1.0,  -1.0, -1.0,  1.0,
             1.0, -1.0, -1.0,   1.0, -1.0,  1.0,   1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,   1.0,  1.0, -1.0,   1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,  -1.0,  1.0,  1.0,   1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,   1.0, -1.0,  1.0,  -1.0, -1.0,  1.0,
            -1.0,  1.0, -1.0,   1.0,  1.0, -1.0,   1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,  -1.0,  1.0,  1.0,  -1.0,  1.0, -1.0,
            -1.0, -1.0, -1.0,  -1.0, -1.0,  1.0,   1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,  -1.0, -1.0,  1.0,   1.0, -1.0,  1.0
        ], dtype=np.float32)
        
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * 4, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        gl.glBindVertexArray(0)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        v_shader_path = os.path.join(base_dir, "skybox_vertex.glsl")
        f_shader_path = os.path.join(base_dir, "skybox_fragment.glsl")

        self.shader = Shader(v_shader_path, f_shader_path)
        
        self.texture_id = self._load_cubemap(faces_paths)

    def _load_cubemap(self, faces_paths):
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, texture_id)

        for i, path in enumerate(faces_paths):
            try:
                img = Image.open(path).convert("RGB")
                
                img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                
                img_data = np.array(img, dtype=np.uint8)
                width, height = img.size
                gl.glTexImage2D(
                    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                    0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data
                )
                print(f"Face da Skybox carregada: {path}")
            except Exception as e:
                print(f"Erro crítico ao carregar face da skybox {path}: {e}")

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

        return texture_id

    def draw(self, view_matrix, proj_matrix):
        gl.glDepthFunc(gl.GL_LEQUAL)
        
        self.shader.use()
        
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.shader.program, "projection"), 1, gl.GL_FALSE, glm.value_ptr(proj_matrix))
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.shader.program, "view"), 1, gl.GL_FALSE, glm.value_ptr(view_matrix))
        
        gl.glBindVertexArray(self.vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.texture_id)
        gl.glUniform1i(gl.glGetUniformLocation(self.shader.program, "skybox"), 0)
        
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)
        
        gl.glDepthFunc(gl.GL_LESS)