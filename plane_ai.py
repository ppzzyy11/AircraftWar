"""Autopilot for AircraftWar.

Enemies fly straight down at a constant speed and bullets fly straight up,
so the next few seconds of the game are fully predictable.  Every frame the
pilot:

1. predicts which enemies the bullets already in the air will destroy,
2. simulates 81 two-leg move plans (9 directions x 9 directions) over a
   short horizon against the remaining enemies,
3. scores each plan on safety (no collision, keep a margin), offence (end
   lined up under a target enemy) and position (stay near the bottom),
4. executes the first move of the best plan and replans next frame.
"""
import math

from plane_sprites import SCREEN_RECT

ACTIONS = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]

HORIZON = 45  # frames simulated ahead
FIRST_LEG = 8  # frames the first move of a plan is held
MARGIN = 12  # px of clearance the pilot tries to keep around enemies
FIRE_INTERVAL = 24  # frames between volleys (400ms at 60 FPS)
BULLET_SPEED = 4  # px per frame, Hero.fire default


class EnemyState(object):
    """Snapshot of an enemy plus the step at which it stops being dangerous."""

    def __init__(self, sprite):
        self.sprite = sprite
        self.x = sprite.rect.x
        self.y = sprite.rect.y
        self.w = sprite.rect.width
        self.h = sprite.rect.height
        self.v = sprite.speed
        # leaves the screen once y >= height, which happens after this many moves
        self.death = max(0, math.ceil((SCREEN_RECT.height - self.y) / self.v))

    def y_at(self, k):
        return self.y + self.v * k


class AIPilot(object):

    def __init__(self):
        self.target = None
        self.last_action = (0, 0)

    def control(self, hero, enemy_group, bullets):
        dx, dy = self.decide(hero, enemy_group, bullets)
        hero.speedx = dx * hero.speed
        hero.speedy = dy * hero.speed

    def decide(self, hero, enemy_group, bullets):
        enemies = [EnemyState(e) for e in enemy_group]
        self.__predict_kills(enemies, bullets)
        alive = [e for e in enemies if e.death > 0]

        hx, hy = hero.rect.x, hero.rect.y
        hw, hh = hero.rect.width, hero.rect.height
        reach = hero.speed * HORIZON
        threats = [e for e in alive
                   if e.x < hx + hw + reach + MARGIN and e.x + e.w > hx - reach - MARGIN
                   and e.y < hy + hh + reach + MARGIN
                   and e.y_at(HORIZON) + e.h > hy - reach - MARGIN]

        target_x = self.__pick_target(hero, alive)
        pref_y = SCREEN_RECT.height - hh - 40

        best_score, best_action = None, (0, 0)
        for a1 in ACTIONS:
            x1, y1, hit1, risk1 = self.__simulate(hero, hx, hy, 0, FIRST_LEG, a1, threats)
            if hit1 is not None:
                score = self.__score(hit1, risk1, x1, y1, hw, target_x, pref_y, a1)
            else:
                score = None
                for a2 in ACTIONS:
                    x2, y2, hit2, risk2 = self.__simulate(hero, x1, y1, FIRST_LEG, HORIZON, a2, threats)
                    s = self.__score(hit2, risk1 + risk2, x2, y2, hw, target_x, pref_y, a1)
                    if score is None or s > score:
                        score = s
            if best_score is None or score > best_score:
                best_score, best_action = score, a1

        self.last_action = best_action
        return best_action

    def __score(self, hit, risk, x, y, w, target_x, pref_y, first_action):
        score = 0.0
        if hit is not None:
            # dying is terrible, dying sooner is worse
            score -= 1e6 * (HORIZON + 1 - hit)
        score -= risk * 30
        score -= abs(x + w / 2 - target_x) * 1.0
        score -= abs(y - pref_y) * 0.3
        if first_action == self.last_action:
            score += 3  # damp jitter between near-equal plans
        return score

    @staticmethod
    def __simulate(hero, x, y, start, end, action, threats):
        """Hold `action` from step start+1 to end. Returns end position,
        first colliding step (or None) and accumulated near-miss risk."""
        w, h = hero.rect.width, hero.rect.height
        max_x = SCREEN_RECT.width - w
        max_y = SCREEN_RECT.height - h
        vx, vy = action[0] * hero.speed, action[1] * hero.speed
        risk = 0.0
        for k in range(start + 1, end + 1):
            x += vx
            y += vy
            if x < 0:
                x = 0
            elif x > max_x:
                x = max_x
            if y < 0:
                y = 0
            elif y > max_y:
                y = max_y
            for e in threats:
                if k >= e.death:
                    continue
                ey = e.y + e.v * k
                if x - MARGIN < e.x + e.w and x + w + MARGIN > e.x \
                        and y - MARGIN < ey + e.h and y + h + MARGIN > ey:
                    if x < e.x + e.w and x + w > e.x and y < ey + e.h and y + h > ey:
                        return x, y, k, risk
                    # near misses close in time matter more than distant ones
                    risk += 1.0 - k / (HORIZON + 1.0)
        return x, y, None, risk

    @staticmethod
    def __predict_kills(enemies, bullets):
        """Mark enemies that bullets already in flight are going to destroy."""
        events = []
        for b in bullets:
            bs = -b.speed
            for e in enemies:
                if b.rect.right <= e.x or b.rect.x >= e.x + e.w:
                    continue
                rel = bs + e.v
                # vertical overlap while lo < k < hi
                lo = (b.rect.y - e.y - e.h) / rel
                hi = (b.rect.bottom - e.y) / rel
                k = max(0, math.floor(lo) + 1)
                if k >= hi or b.rect.bottom - bs * k < 0 or k >= e.death:
                    continue
                events.append((k, id(b), b, e))
        events.sort(key=lambda ev: (ev[0], ev[1]))
        used = set()
        for k, bid, b, e in events:
            # each bullet and each enemy dies on its first hit
            if bid in used or k >= e.death:
                continue
            used.add(bid)
            e.death = k

    def __pick_target(self, hero, alive):
        """Choose an enemy to line up under; returns the x to aim for."""
        cx = hero.rect.centerx
        best, best_cost = None, None
        for e in alive:
            gap = hero.rect.top - (e.y + e.h)
            if gap <= 0:
                continue
            t_arrive = gap / e.v
            t_align = abs(e.x + e.w / 2 - cx) / hero.speed
            # time to line up, wait for a volley and let the bullet fly
            t_kill = t_align + FIRE_INTERVAL + gap / (BULLET_SPEED + e.v)
            if t_kill > t_arrive:
                continue
            cost = t_align + 0.3 * t_arrive
            if e.sprite is self.target:
                cost *= 0.7  # hysteresis: stick with the current target
            if best_cost is None or cost < best_cost:
                best, best_cost = e, cost
        if best is None:
            self.target = None
            # nothing to shoot: drift towards the middle to keep escape routes open
            return SCREEN_RECT.centerx
        self.target = best.sprite
        return best.x + best.w / 2
