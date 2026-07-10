import OpenGL.GL as gl

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = self._compile_shaders(vertex_path, fragment_path)

    def _read_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _compile_shaders(self, v_path, f_path):
        v_code = self._read_file(v_path)
        f_code = self._read_file(f_path)

        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex, v_code)
        gl.glCompileShader(vertex)

        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment, f_code)
        gl.glCompileShader(fragment)

        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex)
        gl.glAttachShader(program, fragment)
        gl.glLinkProgram(program)
        return program

    def use(self):
        gl.glUseProgram(self.program)