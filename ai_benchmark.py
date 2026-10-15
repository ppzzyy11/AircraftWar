"""Run the autopilot headless over several seeded games and report results.

    python3 ai_benchmark.py [games] [max_seconds]
"""
import contextlib
import gc
import os
import random
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER","dummy")

from plane_main import PlaneGame
from plane_sprites import FPS


def main():
    games=int(sys.argv[1]) if len(sys.argv)>1 else 10
    max_seconds=int(sys.argv[2]) if len(sys.argv)>2 else 300

    results=[]
    for seed in range(games):
        random.seed(seed)
        start=time.time()
        with open(os.devnull,"w") as devnull,contextlib.redirect_stdout(devnull):#the game prints a lot
            game=PlaneGame(ai_enabled=True,headless=True)
            frames,score=game.start_game(max_frames=max_seconds*FPS)
            survived=game.alive
            del game
            gc.collect()
        results.append((frames,score,survived))
        print("seed %2d: %s after %6.1fs game time, score %4d  (%.1fs wall)"
              %(seed,"alive" if survived else "died ",frames/FPS,score,time.time()-start))

    alive=sum(1 for r in results if r[2])
    print("survived %d/%d, mean time %.1fs, mean score %.1f"
          %(alive,games,sum(r[0] for r in results)/games/FPS,sum(r[1] for r in results)/games))


if __name__=="__main__":
    main()
