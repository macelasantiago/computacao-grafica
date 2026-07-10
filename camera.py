import glm
import math

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.radius = 10.0
        self.yaw = -90.0
        self.pitch = 45.0
        
        self.last_x = width / 2
        self.last_y = height / 2
        self.first_mouse = True
        
        self.camera_pos = glm.vec3(0.0, 0.0, 0.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        
        self.projection = glm.perspective(glm.radians(45.0), width / height, 0.1, 100.0)
        self.update_camera_vectors()

    def update_camera_vectors(self):
        x = self.radius * math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        y = self.radius * math.sin(math.radians(self.pitch))
        z = self.radius * math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        
        self.camera_pos = glm.vec3(x, y, z)
        self.view = glm.lookAt(self.camera_pos, glm.vec3(0, 0, 0), self.up)

    def process_mouse_movement(self, xoffset, yoffset):
        sensitivity = 0.1
        self.yaw += xoffset * sensitivity
        self.pitch += yoffset * sensitivity

        if self.pitch > 89.0: self.pitch = 89.0
        if self.pitch < 10.0: self.pitch = 10.0

        self.update_camera_vectors()

    def get_matrices(self):
        return self.view, self.projection