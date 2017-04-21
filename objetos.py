import spyral
import spyral.debug
import pygame
from random import randint, random


def reset():
    scene = spyral.director.get_scene()
    for sprite in scene._sprites.copy():
        sprite.kill()
    scene.background.fill((255,255,255))

def fps():
    scene = spyral.director.get_scene()
    scene.fps = spyral.debug.FPSSprite(scene, (255,0,0))


class Carrito(spyral.Sprite):
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)
        self.image = spyral.Image("images/etoys-car.png")
        self.vel = 100 
        self.scale = 1 
        self.x, self.y = 100, 100
        self.anchor = "midbottom"

        self.estado = "quieto"
        self.movimiento = spyral.Vec2D(0, 0)

        spyral.event.register("director.render", self.seguir_raton, scene=scene)
        spyral.event.register("director.pre_render", self.determinar_estado, scene=scene)

    def determinar_estado(self):
        if abs(self.movimiento.x) < 5 and abs(self.movimiento.y) < 5:
            self.estado = "quieto"
        else:
            self.estado = "corre_"
            if self.movimiento.y > 0:
                self.estado += "s"
            else:
                self.estado += "n"

            if self.movimiento.x > 0:
                self.estado += "e"
            else:
                self.estado += "o"

    def seguir_raton(self):
        self.stop_all_animations()
        pos = self.scene.activity._pygamecanvas.get_pointer()
        self.movimiento = pos - self.pos
        anim = spyral.Animation("pos", spyral.easing.LinearTuple(self.pos, pos), duration = 0.5)
        self.animate(anim)

class Perro(spyral.Sprite):
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)
        self.image = spyral.Image(filename="images/perro.png")

class Mono(spyral.Sprite):
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)
        #self.scene = scene
        self.image = spyral.Image(filename="images/monkey_normal.png")
        self.grito = pygame.mixer.Sound("sounds/smile.wav")
        self.x = 100
        self.y = 300

    def sonreir(self):
        self.image = spyral.Image(filename="images/monkey_smile.png")
        self.scene.redraw()
        self.grito.play()
        #self.image = spyral.Image(filename="images/monkey_normal.png")
        

class Juego(spyral.Scene):
    def __init__(self, activity=None, SIZE=None, *args, **kwargs):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=SIZE).fill((255,255,255))
        
        spyral.event.register("system.quit", spyral.director.pop)

        if activity:
            activity.box.next_page()
            activity._pygamecanvas.grab_focus()
            activity.window.set_cursor(None)
            self.activity = activity
