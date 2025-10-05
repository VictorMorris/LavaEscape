import math
import random
import sys
import pygame

# ---------------------------------------
# Config
# ---------------------------------------
WIDTH, HEIGHT = 800, 900
FPS = 60

PLAYER_W, PLAYER_H = 38, 50
PLAYER_SPEED = 5
JUMP_VEL = -14
GRAVITY = 0.7
COYOTE_TIME = 0.12
JUMP_BUFFER = 0.12

PLATFORM_H = 20
LAVA_COLOR = (240, 80, 50)

FONT_NAME = "arial"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (140, 140, 140)
GREEN = (60, 210, 120)
BLUE = (80, 160, 240)
YELLOW = (255, 200, 0)
RED = (210, 50, 50)
PURPLE = (160, 100, 220)

STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_DEAD = "dead"
STATE_WIN = "win"

# ---------------------------------------
# Helper
# ---------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def circle_rect_collision(cx, cy, r, rect):
    nx = clamp(cx, rect.left, rect.right)
    ny = clamp(cy, rect.top, rect.bottom)
    dx = cx - nx
    dy = cy - ny
    return (dx * dx + dy * dy) <= r * r

# ---------------------------------------
# Entities
# ---------------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_W, PLAYER_H)
        self.velx = 0
        self.vely = 0
        self.on_ground = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.facing = 1
        self.invuln_timer = 0.0

    def update(self, dt, keys):
        # horizontal move
        self.velx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velx = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velx = PLAYER_SPEED
            self.facing = 1

        # timers
        self.coyote_timer = max(0.0, self.coyote_timer - dt)
        self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)
        self.invuln_timer = max(0.0, self.invuln_timer - dt)

        # jump buffer input
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jump_buffer_timer = JUMP_BUFFER

        # gravity
        self.vely += GRAVITY
        self.vely = clamp(self.vely, -50, 30)

    def try_jump(self):
        if self.coyote_timer > 0.0 or self.on_ground or self.jump_buffer_timer > 0.0:
            self.vely = JUMP_VEL
            self.on_ground = False
            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0

    def draw(self, surf, cam_y):
        color = YELLOW if self.invuln_timer > 0 else BLUE
        pygame.draw.rect(
            surf,
            color,
            pygame.Rect(self.rect.x, self.rect.y - cam_y, self.rect.w, self.rect.h),
        )
        # simple face
        eye_y = self.rect.y - cam_y + 15
        ex = self.rect.centerx + (10 * self.facing)
        pygame.draw.circle(surf, BLACK, (ex, eye_y), 4)

class Platform:
    def __init__(self, x, y, w):
        self.rect = pygame.Rect(x, y, w, PLATFORM_H)

    def draw(self, surf, cam_y):
        pygame.draw.rect(
            surf,
            GRAY,
            pygame.Rect(self.rect.x, self.rect.y - cam_y, self.rect.w, self.rect.h),
        )

class Saw:
    # stationary spinning saw
    def __init__(self, x, y, r=20):
        self.x = x
        self.y = y
        self.r = r
        self.angle = 0.0

    def update(self, dt):
        self.angle += 6.0 * dt

    def collides(self, rect):
        return circle_rect_collision(self.x, self.y, self.r - 2, rect)

    def draw(self, surf, cam_y):
        cy = self.y - cam_y
        pygame.draw.circle(surf, WHITE, (int(self.x), int(cy)), self.r)
        spoke_len = self.r
        for k in range(4):
            a = self.angle + k * math.pi / 2
            x2 = self.x + math.cos(a) * spoke_len
            y2 = cy + math.sin(a) * spoke_len
            pygame.draw.line(surf, BLACK, (self.x, cy), (x2, y2), 3)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(cy)), 4)

class MovingSaw(Saw):
    def __init__(self, x1, y1, x2, y2, r=22, speed=120.0):
        super().__init__(x1, y1, r)
        self.ax, self.ay = x1, y1
        self.bx, self.by = x2, y2
        self.t = 0.0
        self.dir = 1
        self.speed = speed
        self.dist = math.hypot(self.bx - self.ax, self.by - self.ay)
        self.duration = max(0.1, self.dist / self.speed)

    def update(self, dt):
        super().update(dt)
        self.t += self.dir * dt
        if self.t > self.duration:
            self.t = self.duration
            self.dir = -1
        if self.t < 0.0:
            self.t = 0.0
            self.dir = 1
        u = 0 if self.duration == 0 else self.t / self.duration
        self.x = self.ax + (self.bx - self.ax) * u
        self.y = self.ay + (self.by - self.ay) * u

class Cannon:
    # fires projectiles horizontally inward
    def __init__(self, x, y, direction=1, cooldown=1.4, speed=260, radius=10):
        self.x = x
        self.y = y
        self.dir = 1 if direction >= 0 else -1
        self.cooldown = cooldown
        self.timer = random.uniform(0, cooldown)
        self.speed = speed
        self.radius = radius

    def update(self, dt, projectiles):
        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown
            vx = self.speed * self.dir
            projectiles.append(Projectile(self.x, self.y, vx, 0, self.radius))

    def draw(self, surf, cam_y):
        cy = self.y - cam_y
        body = pygame.Rect(self.x - 16, cy - 12, 32, 24)
        pygame.draw.rect(surf, PURPLE, body)
        barrel = pygame.Rect(self.x + (14 * self.dir), cy - 6, 18 * self.dir, 12)
        pygame.draw.rect(surf, BLACK, barrel)

class Projectile:
    def __init__(self, x, y, vx, vy, r=10):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < -100 or self.x > WIDTH + 100 or self.y < -20000 or self.y > 20000:
            self.alive = False

    def collides(self, rect):
        return circle_rect_collision(self.x, self.y, self.r - 1, rect)

    def draw(self, surf, cam_y):
        pygame.draw.circle(surf, RED, (int(self.x), int(self.y - cam_y)), self.r)

class Door:
    def __init__(self, x, y, w=50, h=80):
        # y is door floor line
        self.rect = pygame.Rect(x, y - h, w, h)

    def draw(self, surf, cam_y):
        r = pygame.Rect(self.rect.x, self.rect.y - cam_y, self.rect.w, self.rect.h)
        pygame.draw.rect(surf, GREEN, r, border_radius=6)
        pygame.draw.rect(surf, BLACK, r, 3, border_radius=6)
        knob = (r.right - 12, r.centery)
        pygame.draw.circle(surf, BLACK, knob, 5)

# ---------------------------------------
# Level
# ---------------------------------------
class Level:
    def __init__(self, idx):
        self.idx = idx
        self.platforms = []
        self.saws = []
        self.moving_saws = []
        self.cannons = []
        self.projectiles = []
        self.door = None
        self.spawn = (WIDTH // 2, 0)
        self.height = 4000
        self.lava_y = 2000
        self.lava_speed = 35 + 10 * idx
        self.lava_accel = 1.001
        self.build()

    def add_platform_row(self, y, count, gap=120, jitter=30, w=180):
        margin = 60
        total_width = count * w + (count - 1) * gap
        start_x = (WIDTH - total_width) // 2
        for i in range(count):
            xi = start_x + i * (w + gap) + random.randint(-jitter, jitter)
            self.platforms.append(Platform(xi, y, w))

    def build(self):
        rng = random.Random(100 + self.idx * 7)

        # ground base
        self.platforms.append(Platform(0, 2000, WIDTH))

        # stacked rows
        y = 1800
        rows = 18 + self.idx * 4
        for i in range(rows):
            count = 3 if i % 2 == 0 else 2
            gap = 140 if self.idx == 0 else 120
            jitter = 40 if self.idx >= 1 else 25
            w = 200 if self.idx == 0 else 160
            self.add_platform_row(y, count, gap, jitter, w)

            # hazards
            if i % 3 == 2:
                for p in self.platforms[-count:]:
                    if rng.random() < 0.5:
                        sx = p.rect.centerx
                        sy = p.rect.y - 30
                        self.saws.append(Saw(sx, sy, 20 + 2 * self.idx))
            if i % 4 == 1:
                row = self.platforms[-count:]
                if len(row) >= 2:
                    a = row[0].rect
                    b = row[-1].rect
                    ymid = min(a.y, b.y) - 80
                    self.moving_saws.append(
                        MovingSaw(
                            a.centerx,
                            ymid,
                            b.centerx,
                            ymid,
                            r=22 + 2 * self.idx,
                            speed=140 + 10 * self.idx,
                        )
                    )
            if i % 5 == 0 and i > 0:
                # side cannons that fire inward
                side = rng.choice(["left", "right"])
                if side == "left":
                    cx, dir_in = 20, 1
                else:
                    cx, dir_in = WIDTH - 20, -1
                self.cannons.append(
                    Cannon(
                        cx,
                        y - 40,
                        direction=dir_in,
                        cooldown=1.6 - min(0.6, 0.1 * self.idx),
                        speed=240 + 20 * self.idx,
                    )
                )

            y -= 180 - 10 * self.idx

        # door just above the highest platform
        top_platform_y = min(p.rect.top for p in self.platforms)
        door_x = WIDTH // 2 - 25
        door_y = top_platform_y - 4
        self.door = Door(door_x, door_y)

        # world settings
        self.height = 2100 + (rows * 180)
        self.spawn = (WIDTH // 2 - PLAYER_W // 2, 2000 - PLAYER_H - 2)
        self.lava_y = 2050
        self.lava_speed = 40 + 12 * self.idx

    def update(self, dt):
        for s in self.saws:
            s.update(dt)
        for ms in self.moving_saws:
            ms.update(dt)
        for c in self.cannons:
            c.update(dt, self.projectiles)
        for pr in self.projectiles:
            pr.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # lava rises
        self.lava_speed *= self.lava_accel
        self.lava_y -= self.lava_speed * dt

    def draw(self, surf, cam_y):
        # background
        surf.fill((22, 26, 40))

        # platforms
        for p in self.platforms:
            p.draw(surf, cam_y)

        # door
        self.door.draw(surf, cam_y)
        # exit label
        exit_lbl = pygame.font.SysFont(FONT_NAME, 22, bold=True).render("EXIT", True, WHITE)
        surf.blit(
            exit_lbl,
            (self.door.rect.centerx - exit_lbl.get_width() // 2, self.door.rect.top - cam_y - 28),
        )

        # hazards
        for s in self.saws:
            s.draw(surf, cam_y)
        for ms in self.moving_saws:
            ms.draw(surf, cam_y)
        for c in self.cannons:
            c.draw(surf, cam_y)
        for pr in self.projectiles:
            pr.draw(surf, cam_y)

        # lava
        lava_h = max(0, int(HEIGHT - (self.lava_y - cam_y)))
        if lava_h > 0:
            pygame.draw.rect(surf, LAVA_COLOR, pygame.Rect(0, HEIGHT - lava_h, WIDTH, lava_h))
            for i in range(0, WIDTH, 40):
                pygame.draw.circle(surf, (255, 180, 120), (i + 20, HEIGHT - lava_h), 12)

# ---------------------------------------
# Game
# ---------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Escape the Lava!")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(FONT_NAME, 64, bold=True)
        self.font = pygame.font.SysFont(FONT_NAME, 28)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)

        self.state = STATE_MENU
        self.level_idx = 0
        self.level = None
        self.player = None
        self.lives = 3
        self.cam_y = 0.0

    def start_level(self, idx):
        self.level_idx = idx
        self.level = Level(idx)
        self.player = Player(*self.level.spawn)
        self.cam_y = self.player.rect.y - HEIGHT * 0.6
        if idx == 0:
            self.lives = 5
        elif idx == 1:
            self.lives = 4
        else:
            self.lives = 3
        self.state = STATE_PLAY

    def handle_collisions(self, dt):
        p = self.player
        lvl = self.level

        # move X with collision
        p.rect.x += int(p.velx)
        for plat in lvl.platforms:
            if p.rect.colliderect(plat.rect):
                if p.velx > 0:
                    p.rect.right = plat.rect.left
                elif p.velx < 0:
                    p.rect.left = plat.rect.right

        # move Y with collision
        p.on_ground = False
        p.rect.y += int(p.vely)
        for plat in lvl.platforms:
            if p.rect.colliderect(plat.rect):
                if p.vely > 0:
                    p.rect.bottom = plat.rect.top
                    p.vely = 0
                    p.on_ground = True
                    p.coyote_timer = COYOTE_TIME
                elif p.vely < 0:
                    p.rect.top = plat.rect.bottom
                    p.vely = 0

        # door touch
        if p.rect.colliderect(lvl.door.rect):
            self.level_idx += 1
            if self.level_idx >= 3:
                self.state = STATE_WIN
            else:
                self.start_level(self.level_idx)
            return

        # hazards
        hit = False
        for s in lvl.saws:
            if s.collides(p.rect):
                hit = True
                break
        if not hit:
            for ms in lvl.moving_saws:
                if ms.collides(p.rect):
                    hit = True
                    break
        if not hit:
            for pr in lvl.projectiles:
                if pr.collides(p.rect):
                    hit = True
                    break

        # lava
        if p.rect.bottom > lvl.lava_y:
            hit = True

        # on hit
        if hit and p.invuln_timer <= 0:
            self.lives -= 1
            if self.lives <= 0:
                self.state = STATE_DEAD
            else:
                # respawn above lava on the highest safe platform
                safe_y = None
                for plat in sorted(lvl.platforms, key=lambda a: -a.rect.y):
                    if plat.rect.top < lvl.lava_y - 60:
                        safe_y = plat.rect.top - PLAYER_H
                        break
                if safe_y is None:
                    safe_y = lvl.spawn[1]
                p.rect.x = clamp(p.rect.x, 20, WIDTH - 20 - PLAYER_W)
                p.rect.y = safe_y
                p.vely = 0
                p.invuln_timer = 1.2

        # world bounds
        p.rect.x = clamp(p.rect.x, -200, WIDTH + 200)

    def update_camera(self, dt):
        target_y = self.player.rect.y - HEIGHT * 0.6
        self.cam_y += (target_y - self.cam_y) * min(1.0, 10.0 * dt)

        # dynamic lower bound so the camera can travel to the real top
        tops = [pl.rect.top for pl in self.level.platforms]
        tops.append(self.level.door.rect.top)
        lower_bound = min(tops) - 200
        self.cam_y = clamp(self.cam_y, lower_bound, self.level.height)

    def draw_hud(self):
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level_idx + 1}/3", True, WHITE)
        self.screen.blit(lives_text, (16, 12))
        self.screen.blit(level_text, (WIDTH - level_text.get_width() - 16, 12))

        tip = self.font_small.render(
            "Move A or Left and D or Right. Jump Space or W or Up",
            True,
            WHITE,
        )
        self.screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, 12 + 30))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.state == STATE_MENU:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_1, pygame.K_RETURN, pygame.K_SPACE):
                            self.start_level(0)
                        elif event.key == pygame.K_2:
                            self.start_level(1)
                        elif event.key == pygame.K_3:
                            self.start_level(2)
                elif self.state == STATE_PLAY:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                            self.player.try_jump()
                        if event.key == pygame.K_ESCAPE:
                            self.state = STATE_MENU
                elif self.state in (STATE_DEAD, STATE_WIN):
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.state = STATE_MENU

            if self.state == STATE_MENU:
                self.draw_menu()
            elif self.state == STATE_PLAY:
                self.update_play(dt)
            elif self.state == STATE_DEAD:
                self.draw_dead()
            elif self.state == STATE_WIN:
                self.draw_win()

            pygame.display.flip()

    def update_play(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.level.update(dt)
        self.handle_collisions(dt)
        self.update_camera(dt)

        # draw world
        self.level.draw(self.screen, self.cam_y)
        self.player.draw(self.screen, self.cam_y)
        self.draw_hud()

    def draw_menu(self):
        self.screen.fill((16, 18, 28))
        title = self.font_big.render("Escape the Lava!", True, WHITE)
        sub = self.font.render("Upward jumping with lava, saws, and cannons", True, WHITE)
        play1 = self.font.render("Press 1 Enter or Space for Level 1", True, GREEN)
        play2 = self.font.render("Press 2 for Level 2", True, GREEN)
        play3 = self.font.render("Press 3 for Level 3", True, GREEN)
        info = self.font_small.render(
            "Reach the green door at the top. Avoid saws, cannons, and lava.",
            True,
            WHITE,
        )

        y = HEIGHT // 2 - 200
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y))
        y += 80
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, y))
        y += 80
        self.screen.blit(play1, (WIDTH // 2 - play1.get_width() // 2, y))
        y += 40
        self.screen.blit(play2, (WIDTH // 2 - play2.get_width() // 2, y))
        y += 40
        self.screen.blit(play3, (WIDTH // 2 - play3.get_width() // 2, y))
        y += 80
        self.screen.blit(info, (WIDTH // 2 - info.get_width() // 2, y))

    def draw_dead(self):
        self.screen.fill((10, 0, 0))
        txt = self.font_big.render("You Died", True, RED)
        hint = self.font.render("Press Enter to return to Menu", True, WHITE)
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 60))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

    def draw_win(self):
        self.screen.fill((0, 18, 0))
        txt = self.font_big.render("You Won", True, GREEN)
        hint = self.font.render("Press Enter to return to Menu", True, WHITE)
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 60))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

# ---------------------------------------
# Main
# ---------------------------------------
if __name__ == "__main__":
    Game().run()
