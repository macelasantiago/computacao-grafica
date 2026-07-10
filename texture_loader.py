import glfw
from OpenGL.GL import *
from PIL import Image

def load_texture(path):
    try:
        image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        
        image = image.convert("RGBA")
        img_data = image.tobytes("raw", "RGBA", 0, -1)
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        glGenerateMipmap(GL_TEXTURE_2D)
        
        glBindTexture(GL_TEXTURE_2D, 0)
        print(f"Textura carregada com sucesso: {path} ({image.width}x{image.height})")
        return texture

    except Exception as e:
        print(f"Erro crítico ao carregar textura em {path}: {e}")
        return None