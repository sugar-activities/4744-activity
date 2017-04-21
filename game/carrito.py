# -*- coding: utf-8 -*-
import spyral
import spyral.debug
import pygame
import math
import random
pygame.mixer.init()

class Interruptor(spyral.Sprite):
    def __init__(self, scene, player):
        spyral.Sprite.__init__(self, scene)
        self.image = spyral.Image("images/interruptor.png")
        self.orig_image = self.image.copy()
        self.pos = self.lejos_de_otros()
        self.anchor = "center"
        self.switch(player)

        self.layer = "objetos"

        spyral.event.register("carrito.choca", self.choca)

    def choca(self, sprite, player):
        if sprite==self:
            self.switch(player)

    def lejos_de_otros(self, x=None, y=None):
        if not y or not x:
            x, y = random.randint(50, self.scene.width-100), random.randint(50, self.scene.height-100)
        for i in self.scene.interruptores:
            if spyral.Vec2D(x,y).distance(i.pos) < self.size.get_length():
                return self.lejos_de_otros()
        return x,y

    def switch(self, player):
        self.player = player
        if player==1:
            self.flip_x = False
            color=(255,0,0,127) # Rojo
            self.image.draw_circle (color=color, position=self.size/2, radius=self.width/2, width=0)
            self.image.draw_image(self.orig_image)
        elif player==2:
            self.flip_x = True
            color=(0,255,0,127) # Verde
            self.image.draw_circle (color=color, position=self.size/2, radius=self.width/2, width=0)
            self.image.draw_image(self.orig_image)

class Carrito(spyral.Sprite):
    def __init__(self, scene, player):
        spyral.Sprite.__init__(self, scene)
        self.vel = 20
        self.anchor = "center"

        self.layer = "carros"

        self.girando = False
        self.moviendo = False
        self.frenando = False

        self.bonus = pygame.mixer.Sound('sounds/BonusCube_0.ogg')

        self.puntos = 4
        self.player = player
        if player==1:
            self.x, self.y = spyral.Vec2D(scene.size)/8.0
            spyral.event.register("input.keyboard.down.s", self.frena)
            spyral.event.register("input.keyboard.down.w", self.avanza)
            spyral.event.register("input.keyboard.down.a", self.izquierda)
            spyral.event.register("input.keyboard.down.d", self.derecha)            
            # game keys
            spyral.event.register("input.keyboard.down.keypad_2", self.frena)
            spyral.event.register("input.keyboard.down.keypad_8", self.avanza)
            spyral.event.register("input.keyboard.down.keypad_4", self.izquierda)
            spyral.event.register("input.keyboard.down.keypad_6", self.derecha)
            self.image = spyral.Image("images/etoys-car.png")
            self.angle = 0
        elif player==2:
            self.x, self.y = spyral.Vec2D(scene.size)*0.875
            spyral.event.register("input.keyboard.down.down", self.frena)
            spyral.event.register("input.keyboard.down.up", self.avanza)
            spyral.event.register("input.keyboard.down.left", self.izquierda)
            spyral.event.register("input.keyboard.down.right", self.derecha)
            # game keys
            spyral.event.register("input.keyboard.down.keypad_3", self.frena)
            spyral.event.register("input.keyboard.down.keypad_9", self.avanza)
            spyral.event.register("input.keyboard.down.keypad_7", self.izquierda)
            spyral.event.register("input.keyboard.down.keypad_1", self.derecha)
            self.image = spyral.Image("images/etoys-car-green.png")
            self.angle = math.pi

        size = spyral.Vec2D(self.image.size)
        self.mask = spyral.Rect(size/8 , size*0.875)

        spyral.event.register("director.update", self.corrige_dir)
        spyral.event.register("director.pre_render", self.chequea_choque)

        spyral.event.register("Carrito.angle.animation.end", self.fin_anim)
        spyral.event.register("Carrito.pos.animation.end", self.fin_mov)
        spyral.event.register("Carrito.vel.animation.end", self.fin_fren)
        spyral.event.register("Carrito.image.animation.end", self.fin_explosion)

    def izquierda(self, event):
        if self.moviendo and not self.girando:
            start = self.angle
            end = self.angle + math.pi/8 * (-1 if self.vel<0 else 1)
            anim = spyral.Animation("angle", spyral.easing.Linear(start, end), duration=0.2)
            self.animate(anim)
            self.girando = True

    def derecha(self, event):
        if self.moviendo and not self.girando:
            start = self.angle
            end = self.angle - math.pi/8 * (-1 if self.vel<0 else 1)
            anim = spyral.Animation("angle", spyral.easing.Linear(start, end), duration=0.2)
            self.animate(anim)
            self.girando = True

    def corrige_dir(self):
        if self.moviendo and self.girando:
            self.stop_animation(self.mov_anim)
            self.avanza(None)
        elif not self.girando and not self.moviendo and self.vel:
            self.avanza(None)

    def avanza(self, event):
        # Tengo un angulo y una velocidad
        # Tarea, obtener vector de movimiento
        if event:
            self.vel += 10
            if self.frenando:
                self.stop_animation(self.fren_anim)
                self.frenando = False
        if not self.moviendo:
            movimiento = spyral.Vec2D.from_polar(self.vel, -1 * self.angle)
            pos = self.pos
            self.mov_anim = spyral.Animation("pos", spyral.easing.LinearTuple(pos, pos+movimiento), duration=0.2)
            self.animate(self.mov_anim)
            self.moviendo = True

    def frena(self, event):
        if self.vel > 0:
            if not self.frenando:
                self.fren_anim = spyral.Animation('vel', spyral.easing.CubicIn(self.vel, 0), duration=self.vel**(1/10))
                self.animate(self.fren_anim)
                self.frenando = True
        else:
            self.vel -= 5

    def fin_anim(self, sprite):
        if sprite==self:
            self.girando = False

    def fin_mov(self, sprite):
        if sprite==self:
            self.moviendo = False

    def fin_fren(self, sprite):
        if sprite==self:
            self.frenando = False

    def fin_explosion(self, sprite):
        if sprite==self:
            self.kill()
            self.scene.fin(0)


    def chequea_choque(self, event):
        if self.x > self.scene.width:
            self.x = 0
        if self.y > self.scene.height:
            self.y = 0
        if self.x < 0:
            self.x = self.scene.width
        if self.y < 0:
            self.y = self.scene.height
        for i in self.scene.interruptores:
            if self.collide_sprite(i):
                if not i.player==self.player:
                    spyral.event.queue("carrito.choca", spyral.Event(sprite=i, player=self.player))
                    self.bonus.play()


class Juego(spyral.Scene):
    def __init__(self, activity=None, SIZE=None, *args, **kwargs):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=self.size).fill((255,255,255))

        self.layers = ["fondo", "objetos", "carros"]

        self.explotando = False

        self.rojo = Carrito(self, 1)
        self.verde = Carrito(self, 2)

        self.boom = pygame.mixer.Sound('sounds/punch.wav')

        self.interruptores = []
        for i in range(0,4):
            self.interruptores.append(Interruptor(self, 1))
        for i in range(0,4):
            self.interruptores.append(Interruptor(self, 2))

        spyral.event.register("director.update", self.chequea_choque)
        spyral.event.register("system.quit", spyral.director.pop)
        spyral.event.register("carrito.choca", self.puntaje)
        spyral.event.register("carrito.gana", self.fin)

        secuencia = []
        for i in range(0, 7):
            secuencia.append( spyral.Image("images/boom-%i.png" % i ) )

        self.explosion = spyral.Animation('image', spyral.easing.Iterate( secuencia ), 
                                        duration = 1)

        if activity:
            activity.game_button.set_active(True)
            activity.box.next_page()
            activity._pygamecanvas.grab_focus()
            activity.window.set_cursor(None)
            self.activity = activity

    def chequea_choque(self):
        if self.verde.collide_sprite(self.rojo):
            self.boom.play()
            if not self.explotando:
                self.verde.frena(None)
                self.rojo.frena(None)
                self.verde.animate(self.explosion)
                self.rojo.animate(self.explosion)
                self.explotando = True

    def puntaje(self, sprite, player):
        puntaje1, puntaje2 = 0, 0
        for i in self.interruptores:
            if i.player==1:
                puntaje1+=1
            elif i.player==2:
                puntaje2+=1
        self.rojo.puntos = puntaje1
        self.verde.puntos = puntaje2
        if not puntaje1:
            spyral.event.queue("carrito.gana", spyral.Event(player=2))
        elif not puntaje2:
            spyral.event.queue("carrito.gana", spyral.Event(player=1))

    def fin(self, player):
        final = Final(SIZE=self.size, player=player)
        spyral.director.replace(final)

class Inicio(spyral.Scene):
    def __init__(self, SIZE=None, activity=None, *args, **kwargs):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=self.size).fill((255,255,255))

        self.title = spyral.Sprite(self)
        self.title.image = spyral.Font("fonts/SFDigitalReadout-Medium.ttf", 105).render("Consenso en 8-bits")
        self.title.anchor = "midbottom"
        self.title.pos = spyral.Vec2D(self.size)/2

        #anim = spyral.Animation("visible", spyral.easing.Iterate([True,False]), duration=0.5, loop=True)
        #self.title.animate(anim) 

        self.subtitle = spyral.Sprite(self)
        self.subtitle.image = spyral.Font("fonts/SFDigitalReadout-Medium.ttf", 75).render("presiona espacio")
        self.subtitle.anchor = "midtop"
        self.subtitle.pos = spyral.Vec2D(self.size)/2

        self.player = Carrito(self, 1)
        self.player.pos = 150, 150
        self.player.vel = 30
        self.player.scale = 3

        self.player = Carrito(self, 2)
        self.player.pos = self.width-150, self.height-150
        self.player.vel = 30
        self.player.scale = 3
        self.angle = math.pi
        self.interruptores = []

        spyral.event.register("input.keyboard.down.space", self.continuar)
        spyral.event.register("input.keyboard.down.*", self.mostrar)
        spyral.event.register("system.quit", spyral.director.pop)

        if activity:
            activity.box.next_page()
            activity._pygamecanvas.grab_focus()
            activity.window.set_cursor(None)
            self.activity = activity

    def mostrar(self, event):
        print event.key
        print event

    def continuar(self):
        juego = Juego(activity=None, SIZE=self.size)
        spyral.director.replace(juego)

class Final(spyral.Scene):
    def __init__(self, SIZE, player):
        spyral.Scene.__init__(self, SIZE)
        self.background = spyral.Image(size=self.size).fill((255,255,255))

        if player:
            self.player = Carrito(self, player)
            self.player.pos = spyral.Vec2D(self.width/2, self.height/3)
            self.player.vel = 0
            self.player.scale = 3
            self.interruptores = []

            if player==1:
                texto = "gana rojo"
            elif player==2:
                texto = "gana verde"
            self.nota = spyral.Sprite(self)
            self.nota.image = spyral.Font("fonts/SFDigitalReadout-Medium.ttf", 105).render(texto)
            self.nota.anchor = "center"
            self.nota.pos = spyral.Vec2D(self.width/2, 2*self.height/3)
            
        else:
            self.player = spyral.Sprite(self)
            self.player.image = spyral.Font("fonts/SFDigitalReadout-Medium.ttf", 55).render("no hay consenso")
            self.player.anchor = "center"
            self.player.pos = spyral.Vec2D(self.size)/2

        self.aplauso = pygame.mixer.Sound('sounds/applause.wav')
        self.aplauso.play()

        anim = spyral.Animation("scale", spyral.easing.Sine(1), shift=2)
        self.player.animate(anim + anim + anim + anim + anim)

        spyral.event.register("Sprite.scale.animation.end", self.continuar)
        spyral.event.register("Carrito.scale.animation.end", self.continuar)
        spyral.event.register("system.quit", spyral.director.pop)

    def continuar(self):
        juego = Juego(activity=None, SIZE=self.size)
        spyral.director.replace(juego)
