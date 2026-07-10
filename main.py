import glfw
from OpenGL.GL import *
import glm
import math
import random
import time
import numpy as np
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from shader_utils import Shader
from camera import Camera
from models import Cube, Cylinder, CanetaBIC, Esfera, Coroa, ModelOBJ
from texture_loader import load_texture
from skybox import Skybox

def mouse_callback(window, xpos, ypos):
    game = glfw.get_window_user_pointer(window)
    if game:
        if game.camera.first_mouse:
            game.camera.last_x, game.camera.last_y = xpos, ypos
            game.camera.first_mouse = False
        xoffset, yoffset = xpos - game.camera.last_x, game.camera.last_y - ypos
        game.camera.last_x, game.camera.last_y = xpos, ypos
        game.camera.process_mouse_movement(xoffset, yoffset)

class Game:
    def __init__(self):
        glfw.init()
        self.window = glfw.create_window(1280, 720, "A disputa dos alunos de CG", None, None)
        glfw.make_context_current(self.window)
        glEnable(GL_DEPTH_TEST)

        self.fundo_tex = load_texture("assets/lousa.png")

        self.shader = Shader("vertex_shader.glsl", "fragment_shader.glsl")
        self.camera = Camera(1280, 720)
        
        self.cube_model = Cube()
        self.cylinder_model = Cylinder()
        self.esfera_model = Esfera()
        self.coroa_model = Coroa()
        self.caneta_obj = CanetaBIC(self.cylinder_model, self.cube_model)
        
        self.pino_obj = ModelOBJ("assets/pino.obj")
        
        self.mesa_tex = load_texture("assets/madeira.jpg")
        self.livro_tex = load_texture("assets/capa_livro.png")
        self.caneta_tex = load_texture("assets/caneta.png")
        
        self.tex_poderes = {
            "C": load_texture("assets/poder_C.jpg") or self.caneta_tex,
            "L": load_texture("assets/poder_L.jpg") or self.livro_tex,
            "E": load_texture("assets/cerebro.png") or self.mesa_tex,
            "P": load_texture("assets/x.png") or self.mesa_tex
        }

        
        arquivos_skybox = [
            "assets/ceu1.jpg",
            "assets/ceu2.jpg",
            "assets/ceu3.jpg",
            "assets/ceu4.jpg",
            "assets/ceu5.jpg",
            "assets/ceu6.jpg"
        ]
        self.skybox = Skybox(arquivos_skybox)

        self.hp = [100.0, 100.0]
        self.xp = [0.0, 0.0] 
        self.multiplicador_dano = 1.0 
        self.turno = 0 
        self.estado = "ESCOLHA" 
        self.selecionado = 0 
        self.vencedor = -1
        self.sorteio_rot = 0.0
        
        self.tempo_ultimo_dano = [0.0, 0.0] 
        self.muralhas = [0, 0] 
        
        self.resultado_roleta = ["C", "L", "E", "C"]
        self.pos_herois = [
            [glm.vec3(3.5, -0.4, 1), glm.vec3(3.5, -0.4, -1)], 
            [glm.vec3(-3.5, -0.4, 1), glm.vec3(-3.5, -0.4, -1)] 
        ]
        self.pos_caneta = glm.vec3(0)

        glfw.set_window_user_pointer(self.window, self)
        glfw.set_cursor_pos_callback(self.window, mouse_callback)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def desenhar(self, modelo, textura, pos, escala, rx=0, ry=0, rz=0, brilho=glm.vec3(1.0)):
        model = glm.mat4(1.0)
        model = glm.translate(model, pos)
        model = glm.rotate(model, glm.radians(rx), glm.vec3(1, 0, 0)) 
        model = glm.rotate(model, glm.radians(ry), glm.vec3(0, 1, 0)) 
        model = glm.rotate(model, glm.radians(rz), glm.vec3(0, 0, 1)) 
        model = glm.scale(model, escala)
        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniform3f(glGetUniformLocation(self.shader.program, "lightColor"), *brilho)
        
        glActiveTexture(GL_TEXTURE0)
        
        tex_id = textura if textura is not None else self.mesa_tex
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glUniform1i(glGetUniformLocation(self.shader.program, "ourTexture"), 0)
        modelo.draw()

    def run(self):
        while not glfw.window_should_close(self.window):
            t = glfw.get_time()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            if self.estado == "GAMEOVER":
                glClearColor(0.02, 0.02, 0.05, 1.0)
            else:
                glClearColor(0.01, 0.01, 0.02, 1.0)

            self.shader.use()
            if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS: break

            if self.estado == "ESCOLHA":
                if glfw.get_key(self.window, glfw.KEY_1) == glfw.PRESS: self.selecionado = 0
                if glfw.get_key(self.window, glfw.KEY_2) == glfw.PRESS: self.selecionado = 1
                if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS: self.estado = "SORTEIO"

            elif self.estado == "SORTEIO":
                self.sorteio_rot += 50.0
                if glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS:
                    self.resultado_roleta = [random.choice(["C", "L", "E", "P"]) for _ in range(4)]
                    counts = {p: self.resultado_roleta.count(p) for p in ["C", "L", "E", "P"]}
                    
                    ult_ativo = False
                    if self.xp[self.turno] >= 100.0:
                        ult_ativo = True
                        self.xp[self.turno] = 0.0  
                        self.multiplicador_dano = 2.0  
                    else:
                        self.multiplicador_dano = 1.0

                    pontos_conhecimento = counts["C"] 
                    self.xp[self.turno] = min(self.xp[self.turno] + (pontos_conhecimento * 15.0), 100.0)

                    venceu = max(counts, key=counts.get)
                    
                    if venceu == "C":
                        self.estado = "ATAQUE"
                        self.pos_caneta = glm.vec3(self.pos_herois[self.turno][self.selecionado])
                        self.pos_caneta.y += 0.8
                    elif venceu == "L":
                        ganho_muralha = 4 if ult_ativo else 2
                        self.muralhas[self.turno] = min(self.muralhas[self.turno] + ganho_muralha, 6)
                        self.turno = 1 - self.turno
                        self.estado = "ESCOLHA"
                    elif venceu == "E":
                        ganho_xp_cerebro = 60.0 if ult_ativo else 35.0
                        self.xp[self.turno] = min(self.xp[self.turno] + ganho_xp_cerebro, 100.0)
                        self.turno = 1 - self.turno
                        self.estado = "ESCOLHA"
                    elif venceu == "P":
                        self.turno = 1 - self.turno
                        self.estado = "ESCOLHA"

            elif self.estado == "ATAQUE":
                direcao = -0.08 if self.turno == 0 else 0.08
                self.pos_caneta.x += direcao
                oponente = 1 - self.turno
                
                x_muralha_oponente = -2.0 if self.turno == 0 else 2.0
                colidiu_muralha = (self.turno == 0 and self.pos_caneta.x <= x_muralha_oponente) or \
                                  (self.turno == 1 and self.pos_caneta.x >= x_muralha_oponente)
                
                if colidiu_muralha and self.muralhas[oponente] > 0:
                    self.muralhas[oponente] -= 2 
                    self.estado = "ESCOLHA"
                    self.turno = 1 - self.turno
                
                alvo_x = -3.5 if self.turno == 0 else 3.5
                if (self.turno == 0 and self.pos_caneta.x <= alvo_x) or (self.turno == 1 and self.pos_caneta.x >= alvo_x):
                    self.hp[oponente] -= (25.0 * self.multiplicador_dano)
                    self.tempo_ultimo_dano[oponente] = t
                    
                    if self.hp[oponente] <= 0:
                        self.hp[oponente] = 0
                        self.vencedor = self.turno
                        self.estado = "GAMEOVER"
                    else:
                        self.estado = "ESCOLHA"
                        self.turno = 1 - self.turno
                
                if abs(self.pos_caneta.x) > 10: self.estado = "ESCOLHA"; self.turno = 1 - self.turno

            view, proj = self.camera.get_matrices()
            glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "view"), 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "projection"), 1, GL_FALSE, glm.value_ptr(proj))
            glUniform3f(glGetUniformLocation(self.shader.program, "lightPos"), 0.0, 5.0, 2.0)

            glUniform3f(glGetUniformLocation(self.shader.program, "spotPos"), 0.0, 5.0, 0.0)
            glUniform3f(glGetUniformLocation(self.shader.program, "spotDir"), 0.0, -1.0, 0.0)
            glUniform3f(glGetUniformLocation(self.shader.program, "spotColor"), 1.0, 0.85, 0.55)
            glUniform1f(glGetUniformLocation(self.shader.program, "spotCutOff"), math.cos(math.radians(30.0)))

            self.skybox.draw(view, proj)
            self.shader.use() 

            if self.estado != "GAMEOVER":
                if self.fundo_tex:
                    self.desenhar(self.cube_model, self.fundo_tex, glm.vec3(0.0, 3.5, -9.0), glm.vec3(18.0, 10.0, 0.1), brilho=glm.vec3(0.9))

                self.desenhar(self.cube_model, self.mesa_tex, glm.vec3(0, -1.2, 0), glm.vec3(15, 0.1, 8), brilho=glm.vec3(0.6))
                self.desenhar(self.cube_model, self.mesa_tex, glm.vec3(2.0, -0.6, 0), glm.vec3(1.2, 0.6, 1.5))
                self.desenhar(self.cube_model, self.mesa_tex, glm.vec3(-2.0, -0.6, 0), glm.vec3(1.2, 0.6, 1.5))
                
                for p in range(2):
                    x_mur = 2.0 if p == 0 else -2.0
                    for i in range(self.muralhas[p]):
                        self.desenhar(self.cube_model, self.livro_tex, glm.vec3(x_mur, -0.1 + (i*0.2), 0), glm.vec3(1.0, 0.15, 0.8), ry=i*12)

                for p in range(2):
                    cor_hp = glm.vec3(1.0 - (self.hp[p]/100.0), self.hp[p]/100.0, 0.0)
                    cor_hud_viva = cor_hp * 3.5
                    cor_xp = glm.vec3(0.0, 0.8, 1.0) 
                    
                    if self.xp[p] >= 100.0:
                        velocidade_piscado = abs(math.sin(t * 15)) 
                        cor_xp_viva = glm.mix(cor_xp * 3.5, glm.vec3(1.0, 1.0, 1.0) * 5.0, velocidade_piscado)
                    else:
                        cor_xp_viva = cor_xp * 3.5
                    
                    cor_time = glm.vec3(0.2, 0.5, 1.0) if p == 0 else glm.vec3(1.0, 0.2, 0.2)
                    
                    for i, pos in enumerate(self.pos_herois[p]):
                        jump = abs(math.sin(t*8))*0.2 if (self.turno == p and self.selecionado == i) else 0
                        
                        cor_render_pino = cor_time
                        if (t - self.tempo_ultimo_dano[p]) < 0.5:

                            if int(t * 12) % 2 == 0:
                                cor_render_pino = glm.vec3(4.0, 4.0, 4.0)

                        self.desenhar(self.pino_obj, None, pos + glm.vec3(0, jump, 0), glm.vec3(0.5, 0.5, 0.5), brilho=cor_render_pino)
                        
                        if self.xp[p] >= 100.0:
                            efeito_flutuar = math.sin(t * 5) * 0.05
                            pos_icone = pos + glm.vec3(0, 1.6 + jump + efeito_flutuar, 0)
                            self.desenhar(self.cube_model, None, pos_icone, glm.vec3(0.12, 0.12, 0.12), ry=t*120, brilho=glm.vec3(5.0, 4.5, 0.0))

                        fator_escala_vida = self.hp[p] / 100.0
                        offset_x = (1.0 - fator_escala_vida) * 0.5 if p == 0 else -(1.0 - fator_escala_vida) * 0.5
                        self.desenhar(self.cube_model, None, pos + glm.vec3(0, 1.9 + jump, -0.01), glm.vec3(1.05, 0.14, 0.04), brilho=glm.vec3(0.0))
                        self.desenhar(self.cube_model, None, pos + glm.vec3(offset_x, 1.9 + jump, 0), glm.vec3(fator_escala_vida, 0.1, 0.05), brilho=cor_hud_viva)

                        fator_escala_xp = self.xp[p] / 100.0
                        offset_x_xp = (1.0 - fator_escala_xp) * 0.5 if p == 0 else -(1.0 - fator_escala_xp) * 0.5
                        self.desenhar(self.cube_model, None, pos + glm.vec3(0, 1.75 + jump, -0.01), glm.vec3(1.05, 0.08, 0.04), brilho=glm.vec3(0.0))
                        if fator_escala_xp > 0:
                            self.desenhar(self.cube_model, None, pos + glm.vec3(offset_x_xp, 1.75 + jump, 0), glm.vec3(fator_escala_xp, 0.05, 0.05), brilho=cor_xp_viva)

                for i in range(4):
                    x_pos = -3.0 + (i * 2.0)
                    y_pos = 3.5  
                    z_pos = -8.8 
                    rot = self.sorteio_rot if self.estado == "SORTEIO" else 0
                    tex_letra = self.mesa_tex if self.estado == "SORTEIO" else self.tex_poderes[self.resultado_roleta[i]]
                    self.desenhar(self.cube_model, tex_letra, glm.vec3(x_pos, y_pos, z_pos), glm.vec3(1.6, 1.6, 0.15), rx=rot)

                if self.estado == "ATAQUE":
                    self.caneta_obj.draw(self.desenhar, self.pos_caneta, self.caneta_tex, rot_z=90 if self.turno==0 else -90)
            
            else:

                cor_azul = glm.vec3(0.2, 0.5, 2.5)
                cor_vermelha = glm.vec3(2.5, 0.2, 0.2)
                
                if self.vencedor == 0:
                    cor_ganhou = cor_azul
                    cor_perdeu = cor_vermelha
                else:
                    cor_ganhou = cor_vermelha
                    cor_perdeu = cor_azul

                self.desenhar(self.cube_model, None, glm.vec3(-3.2, 1.5, -7.0), glm.vec3(6.4, 8.0, 0.1), brilho=cor_perdeu * 0.1)
                self.desenhar(self.cube_model, None, glm.vec3(3.2, 1.5, -7.0), glm.vec3(6.4, 8.0, 0.1), brilho=cor_ganhou * 0.1)
                self.desenhar(self.cube_model, None, glm.vec3(0.0, 1.5, -6.8), glm.vec3(0.12, 8.0, 0.2), brilho=glm.vec3(0.0))

                self.desenhar(self.cube_model, None, glm.vec3(-3.2, 1.5, -5.0), glm.vec3(1.6, 1.6, 1.6), ry=t*50, brilho=cor_perdeu)

                pos_bola = glm.vec3(3.2, 1.2, -5.0)
                self.desenhar(self.esfera_model, None, pos_bola, glm.vec3(1.4, 1.4, 1.4), ry=t*40, brilho=cor_ganhou)
                
                pos_coroa = pos_bola + glm.vec3(0.0, 0.75, 0.0)
                cor_ouro_neon = glm.vec3(3.0, 2.4, 0.0) 
                self.desenhar(self.coroa_model, None, pos_coroa, glm.vec3(1.3, 1.3, 1.3), ry=t*40, brilho=cor_ouro_neon)

            glfw.swap_buffers(self.window)
            glfw.poll_events()
        glfw.terminate()

if __name__ == "__main__":
    Game().run()