import sys
import pygame
from plane_sprites import *
from plane_ai import AIPilot


class PlaneGame(object):

    def __init__(self,ai_enabled=False,headless=False):
        print("Game inits")

        self.screen=pygame.display.set_mode(SCREEN_RECT.size)#set window size

        self.clock=pygame.time.Clock()#pygame clock

        self.__create_sprites()#create sprites

        self.pilot=AIPilot()#autopilot, toggle with the A key
        self.ai_enabled=ai_enabled
        self.headless=headless#no FPS cap and frame-counted timers, for benchmarking
        self.frame=0
        self.score=0
        self.alive=True

        if not headless:
            pygame.time.set_timer(CREATE_ENEMY_EVENT,1000)#one enemy every 1000ms

            pygame.time.set_timer(HERO_FIRE_EVENT,400)#fire every 400ms

            pygame.font.init()
            self.font=pygame.font.SysFont(None,28)

    def start_game(self,max_frames=None):
        print("Game starts")

        while self.alive and (max_frames is None or self.frame<max_frames):
            if not self.headless:
                self.clock.tick(FPS)#FPS time tick tack
            self.__event_handler()#hand the keydown and fire and enemy event
            self.__check_collide()#deal with collide
            self.__update_sprites()#update but don't draw
            self.frame+=1

            if not self.headless:
                self.__draw_hud()
                pygame.display.update()#draw

        return self.frame,self.score


    def __event_handler(self):
        if self.headless:#same rate as the timers at 60 FPS, but driven by frames
            if (self.frame+1)%FPS==0:
                pygame.event.post(pygame.event.Event(CREATE_ENEMY_EVENT))
            if (self.frame+1)%(FPS*400//1000)==0:
                pygame.event.post(pygame.event.Event(HERO_FIRE_EVENT))

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                PlaneGame.__game_over()
            elif event.type==pygame.KEYDOWN and event.key==pygame.K_a:
                self.ai_enabled=not self.ai_enabled
            elif event.type==CREATE_ENEMY_EVENT:#enemy appears
                print("Enemy appears")
                enemy=Enemy()
                self.enemy_group.add(enemy)
            elif event.type==HERO_FIRE_EVENT:#fire
                print("Hero fires")
                self.hero.fire(2)#two bullets every fire

        if self.ai_enabled:
            self.pilot.control(self.hero,self.enemy_group,self.hero.bullets)
            return

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
        hits=pygame.sprite.groupcollide(self.hero.bullets,self.enemy_group,True,True)
        self.score+=len({enemy for enemies in hits.values() for enemy in enemies})
        enemies=pygame.sprite.groupcollide(self.hero_group,self.enemy_group,True,True)
        if len(enemies)>0:
            self.alive=False

        for group in (self.back_group,self.enemy_group,self.hero_group,self.hero.bullets):
            group.update()
            if not self.headless:
                group.draw(self.screen)

    def __draw_hud(self):
        text="Score: %d   AI: %s (A)"%(self.score,"ON" if self.ai_enabled else "OFF")
        self.screen.blit(self.font.render(text,True,(255,255,255)),(10,10))

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


if __name__=="__main__":
    game=PlaneGame(ai_enabled="--ai" in sys.argv)

    frames,score=game.start_game()
    print("Game over, survived %.1fs, score %d"%(frames/FPS,score))
    pygame.quit()
