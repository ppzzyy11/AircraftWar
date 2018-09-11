import pygame
from plane_sprites import *


class PlaneGame(object):

    def __init__(self):
        print("Game inits")

        self.screen=pygame.display.set_mode(SCREEN_RECT.size)#set window size

        self.clock=pygame.time.Clock()#pygame clock

        self.__create_sprites()#create sprites

        pygame.time.set_timer(CREATE_ENEMY_EVENT,1000)#one enemy every 1000ms

        pygame.time.set_timer(HERO_FIRE_EVENT,400)#fire every 400ms

    def start_game(self):
        print("Game starts")

        while True:
            self.clock.tick(FPS)#FPS time tick tack
            self.__event_handler()#hand the keydown and fire and enemy event
            self.__check_collide()#deal with collide
            self.__update_sprites()#update but don't draw

            pygame.display.update()#draw


    def __event_handler(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                PlaneGame.__game_over()
            elif event.type==CREATE_ENEMY_EVENT:#enemy appears
                print("Enemy appears")
                enemy=Enemy()
                self.enemy_group.add(enemy)
            elif event.type==HERO_FIRE_EVENT:#fire
                print("Hero fires")
                self.hero.fire(2)#two bullets every fire


        keys_pressed=pygame.key.get_pressed()
        self.hero.speedx=self.hero.speedy=0

        if keys_pressed[pygame.K_RIGHT]:
            self.hero.speedx=self.hero.speed
        elif keys_pressed[pygame.K_LEFT]:
            self.hero.speedx=-self.hero.speed
        if keys_pressed[pygame.K_UP]:
            self.hero.speedy=-self.hero.speed
        elif keys_pressed[pygame.K_DOWN]:
            self.hero.speedy=self.hero.speed

    def __check_collide(self):
        pass

    def __update_sprites(self):
        pygame.sprite.groupcollide(self.hero.bullets,self.enemy_group,True,True)
        enemies=pygame.sprite.groupcollide(self.hero_group,self.enemy_group,True,True)
        if len(enemies)>0:
            self.__game_over()

        self.back_group.update()
        self.back_group.draw(self.screen)

        self.enemy_group.update()
        self.enemy_group.draw(self.screen)

        self.hero_group.update()
        self.hero_group.draw(self.screen)

        self.hero.bullets.update()
        self.hero.bullets.draw(self.screen)

    def __create_sprites(self):
        bg1=Background(False)
        bg2=Background(True)
        self.back_group=pygame.sprite.Group(bg1,bg2)

        self.enemy_group=pygame.sprite.Group()

        self.hero=Hero()
        self.hero_group=pygame.sprite.Group(self.hero)

    @staticmethod
    def __game_over():
        print("Game over")

        pygame.quit()
        exit()
        pass




game=PlaneGame()

game.start_game()
