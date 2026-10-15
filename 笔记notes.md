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




##AI自动驾驶 (plane_ai.py)
敌机只会匀速竖直下落, 子弹匀速向上, 所以未来几秒的局面是可以精确预测的. AI每一帧:

1. 预测空中已有的子弹会击毁哪些敌机, 这些敌机不再视为威胁
2. 模拟 9x9 种两段式移动方案(先按方向1移动8帧, 再按方向2移动到第45帧)
3. 按安全(不相撞, 保持距离)、进攻(最后停在目标敌机正下方)、位置(靠近屏幕底部)给方案打分
4. 执行最优方案的第一步, 下一帧重新规划

运行:

    python3 plane_main.py --ai     # AI开局接管
    python3 plane_main.py          # 手动游戏, 任意时刻按 A 键切换AI开/关

无界面批量测试(按帧计时, 不限帧率, 固定随机种子):

    python3 ai_benchmark.py [局数] [每局最长秒数]
