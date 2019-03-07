#飞机大战
^星期二, 11. 九月 2018 03:46下午 ^
** 基于pygame.sprite的小游戏 **
图片素材来源与网络

依赖库安装与运行:

    pip3 install pygame
    pygame plane_main.py


##使用sprite与sprite group创建类
创建了GameSprite类,
随后在GameSprite基础上创建了BackGround,Enemy,Hero,Bullet类,各个类之间独立,


##碰撞机制
采用sprite.groupcollide判定


