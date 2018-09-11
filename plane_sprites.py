import random
import pygame

SCREEN_RECT=pygame.Rect(0,0,480,700)
FPS=60
CREATE_ENEMY_EVENT=pygame.USEREVENT
HERO_FIRE_EVENT=pygame.USEREVENT+1
#sprite aircraft
class GameSprite(pygame.sprite.Sprite):

    def __init__(self,image_name,speed=1):
        super().__init__()


        self.image=pygame.image.load(image_name)
        self.rect=self.image.get_rect()
        self.speed=speed


    def update(self):

        self.rect.y+=self.speed


class Background(GameSprite):

    def __init__(self,is_alt=False):
        super().__init__("./Resources/bg_01.png")
        if is_alt==True:
            self.rect.y=-self.rect.height

    def update(self):

        super().update()

        if self.rect.y>=SCREEN_RECT.height:
            self.rect.y=-self.rect.height


class Enemy(GameSprite):

    def __init__(self):
        super().__init__("./Resources/enemy-1.png")

        self.speed=random.randint(1,4)
        self.rect.bottom=0
        self.rect.x=random.randint(0,SCREEN_RECT.width-self.rect.width)


    def update(self):
        super().update()
        if self.rect.y>=SCREEN_RECT.height:
            self.kill()

    def __del__(self):
        print("Enemy reach bottom of the screen:",self.rect)


class Hero(GameSprite):

    def __init__(self):

        super().__init__("./Resources/hero.png",0)
        self.rect.centerx=SCREEN_RECT.centerx
        self.rect.centery=SCREEN_RECT.centery
        self.speedx=0
        self.speedy=0
        self.speed=3

        self.bullets=pygame.sprite.Group()


    def update(self):
        # super().update()
        self.rect.x+=self.speedx
        self.rect.y+=self.speedy

        if self.rect.x<0 :
            self.rect.x=0
        if self.rect.y<0 :
            self.rect.y=0

        if self.rect.right>SCREEN_RECT.right:
            self.rect.right=SCREEN_RECT.right
        if self.rect.bottom>SCREEN_RECT.bottom:
            self.rect.bottom=SCREEN_RECT.bottom

    def fire(self,n=1,speed=-4):

        for i in range(0,n):
            bullet=Bullet(speed)

            bullet.rect.y=self.rect.y
            bullet.rect.centerx=self.rect.centerx + (-n+1+i*2) *10

            self.bullets.add(bullet)


class Bullet(GameSprite):
    def __init__(self,speed):
        super().__init__("./Resources/bullet-1.png",speed)


    def update(self):
        super().update()

        if self.rect.bottom <0:
            self.kill()

    def __del__(self):
        print("Bullet disappears")
