import pygame
import random
import math
import sys

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
# WIDTH, HEIGHT = 720, 1280  # Для теста на ПК

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Снежный гонщик")
clock = pygame.time.Clock()

SKY = (135, 206, 235)
SNOW = (245, 250, 255)
SNOW_DARK = (220, 230, 245)
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
GOLD = (255, 215, 0)
GREEN = (50, 200, 80)
RED = (220, 50, 50)
BLUE = (50, 120, 220)
GRAY = (120, 120, 140)
DARKGRAY = (70, 70, 90)
BROWN = (140, 90, 50)
PURPLE = (150, 70, 200)

FS = max(16, WIDTH // 28)
font = pygame.font.SysFont("Arial", FS, bold=True)
small = pygame.font.SysFont("Arial", int(FS * 0.75))
big = pygame.font.SysFont("Arial", int(FS * 2.2), bold=True)

TRANSPORTS = [
    {"name": "Санки",       "price": 0,    "speed": 4,   "color": BROWN,  "width": 40, "height": 30, "desc": "Классика"},
    {"name": "Сноуборд",    "price": 200,  "speed": 5.5, "color": BLUE,   "width": 30, "height": 56, "desc": "Быстрее"},
    {"name": "Лыжи",        "price": 450,  "speed": 6.5, "color": RED,    "width": 50, "height": 52, "desc": "Ловкий"},
    {"name": "Снегоход",    "price": 900,  "speed": 8,   "color": GRAY,   "width": 58, "height": 40, "desc": "Мощь!"},
    {"name": "Сноуборд Pro","price": 1600, "speed": 9.5, "color": PURPLE, "width": 34, "height": 64, "desc": "Профи"},
]

UPGRADES = [
    {"name": "Скорость +", "price": 300, "effect": "speed",  "desc": "+1 скорость"},
    {"name": "Магнит",     "price": 400, "effect": "magnet", "desc": "Тянет монеты"},
    {"name": "Деньги +",   "price": 500, "effect": "coins",  "desc": "x2 за монету"},
]

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT * 0.75
        self.base_speed = 4
        self.speed = 4
        self.width = 40
        self.height = 30
        self.color = BROWN
        self.level = 0
        self.owned = [0]
        self.upgrades = {"speed": 0, "magnet": 0, "coins": 0}
        self.tilt = 0
        self.target = None

    def apply_transport(self, idx):
        t = TRANSPORTS[idx]
        self.level = idx
        self.base_speed = t["speed"]
        self.width = t["width"]
        self.height = t["height"]
        self.color = t["color"]
        self.speed = self.base_speed + self.upgrades["speed"]

    def magnet_radius(self):
        return 40 + self.upgrades["magnet"] * 45

    def update(self, keys, touches):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= self.speed * 0.7
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += self.speed * 0.7

        if touches:
            tx, ty = touches[0]
            dx += (tx - self.x) * 0.12
            dy += (ty - self.y) * 0.12
            self.target = (tx, ty)

        if abs(dx) > 0.2:
            self.tilt = max(-8, min(8, self.tilt + (1 if dx > 0 else -1)))
        else:
            self.tilt *= 0.85

        self.x += dx
        self.y += dy
        self.x = max(self.width // 2, min(WIDTH - self.width // 2, self.x))
        self.y = max(HEIGHT * 0.35, min(HEIGHT - self.height // 2, self.y))

    def draw(self, surf):
        px, py = int(self.x), int(self.y)
        w, h = self.width, self.height
        shadow = pygame.Surface((w + 14, h // 2 + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (100, 120, 150, 90), shadow.get_rect())
        surf.blit(shadow, (px - (w + 14) // 2, py + h // 3))

        if self.level == 0:
            pygame.draw.ellipse(surf, self.color, (px - w // 2, py - h // 2, w, h))
            pygame.draw.ellipse(surf, BLACK, (px - w // 2, py - h // 2, w, h), 2)
        elif self.level == 1:
            pygame.draw.ellipse(surf, self.color, (px - w // 2, py - h // 2, w, h))
            pygame.draw.ellipse(surf, WHITE, (px - w // 2, py - h // 2, w, h), 2)
        elif self.level == 2:
            pygame.draw.rect(surf, self.color, (px - w // 2, py - h // 2, w // 3, h))
            pygame.draw.rect(surf, self.color, (px + w // 6, py - h // 2, w // 3, h))
            pygame.draw.rect(surf, WHITE, (px - w // 2, py - h // 2, w // 3, h), 2)
            pygame.draw.rect(surf, WHITE, (px + w // 6, py - h // 2, w // 3, h), 2)
        elif self.level == 3:
            pygame.draw.rect(surf, self.color, (px - w // 2, py - h // 2, w, h), border_radius=8)
            pygame.draw.rect(surf, BLACK, (px - w // 2, py - h // 2, w, h), 2, border_radius=8)
            pygame.draw.circle(surf, BLACK, (px - w // 3, py + h // 3), 7)
            pygame.draw.circle(surf, BLACK, (px + w // 3, py + h // 3), 7)
        else:
            pygame.draw.ellipse(surf, self.color, (px - w // 2, py - h // 2, w, h))
            pygame.draw.ellipse(surf, GOLD, (px - w // 2, py - h // 2, w, h), 3)
            pygame.draw.circle(surf, GOLD, (px, py), 6)

class Coin:
    def __init__(self, x, y, value=10):
        self.x = x
        self.y = y
        self.value = value
        self.r = 11
        self.bob = random.uniform(0, math.tau)

    def update(self, scroll):
        self.y += scroll
        self.bob += 0.1

    def draw(self, surf):
        py = int(self.y + math.sin(self.bob) * 3)
        pygame.draw.circle(surf, GOLD, (int(self.x), py), self.r)
        pygame.draw.circle(surf, (200, 160, 0), (int(self.x), py), self.r, 2)
        pygame.draw.circle(surf, (255, 245, 150), (int(self.x) - 3, py - 3), 2)

    def off_screen(self):
        return self.y > HEIGHT + 20

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(24, 42)

    def update(self, scroll):
        self.y += scroll

    def draw(self, surf):
        pygame.draw.rect(surf, BROWN, (self.x - 4, self.y, 8, self.size // 2))
        for i in range(3):
            w = self.size - i * 7
            top_y = self.y - i * (self.size // 3)
            pygame.draw.polygon(surf, (30, 120, 60), [
                (self.x - w // 2, top_y),
                (self.x + w // 2, top_y),
                (self.x, top_y - self.size // 2),
            ])

    def off_screen(self):
        return self.y > HEIGHT + 60

class Snowflake:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, HEIGHT)
        self.speed = random.uniform(1, 3)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = -5
            self.x = random.randint(0, WIDTH)

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.size)
      def make_button(rect, text, color=GOLD):
    return {"rect": pygame.Rect(rect), "text": text, "color": color}

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player = Player()
        self.coins = []
        self.trees = []
        self.snowflakes = [Snowflake() for _ in range(60)]
        self.money = 0
        self.score = 0
        self.speed_scroll = 3.0
        self.menu = False
        self.menu_tab = 0
        self.menu_sel = 0
        self.spawn_coin_t = 0
        self.spawn_tree_t = 0
        self.paused = False
        self.btn_menu = make_button((WIDTH - 120, 15, 100, 50), "🛒", GOLD)
        self.btn_pause = make_button((WIDTH - 235, 15, 100, 50), "⏸", WHITE)
        self.shop_scroll = 0

    def update(self, keys, touches):
        dt = clock.get_time() / 16.0
        if self.menu or self.paused:
            for s in self.snowflakes: s.update()
            return

        game_touches = [t for t in touches
                        if not self.btn_menu["rect"].collidepoint(t)
                        and not self.btn_pause["rect"].collidepoint(t)]

        self.player.update(keys, game_touches)

        scroll = self.speed_scroll + self.player.upgrades["speed"] * 0.3
        mr = self.player.magnet_radius()

        for c in self.coins[:]:
            c.update(scroll)
            dist = math.hypot(c.x - self.player.x, c.y - self.player.y)
            if dist < mr:
                c.x -= (c.x - self.player.x) * 0.18
                c.y -= (c.y - self.player.y) * 0.18
            if dist < c.r + self.player.width // 2 + 6:
                self.money += int(c.value * (1 + self.player.upgrades["coins"]))
                self.score += c.value
                self.coins.remove(c)
            elif c.off_screen():
                self.coins.remove(c)

        for t in self.trees[:]:
            t.update(scroll)
            if math.hypot(t.x - self.player.x, t.y - self.player.y) < t.size // 2 + 12:
                self.money = max(0, self.money - 20)
                self.trees.remove(t)
            elif t.off_screen():
                self.trees.remove(t)

        for s in self.snowflakes: s.update()

        self.spawn_coin_t += dt
        if self.spawn_coin_t > 20:
            self.spawn_coin_t = 0
            self.coins.append(Coin(random.randint(40, WIDTH - 40), -20,
                                   value=random.choice([10, 10, 10, 20, 50])))

        self.spawn_tree_t += dt
        if self.spawn_tree_t > 55:
            self.spawn_tree_t = 0
            self.trees.append(Tree(random.randint(40, WIDTH - 40), -60))

        self.score += 0.1

    def draw(self, surf):
        surf.fill(SKY)
        pygame.draw.rect(surf, SNOW, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
        for i in range(0, HEIGHT - HEIGHT // 2, 40):
            pygame.draw.line(surf, SNOW_DARK, (0, HEIGHT // 2 + i), (WIDTH, HEIGHT // 2 + i), 1)

        for t in self.trees: t.draw(surf)
        for c in self.coins: c.draw(surf)
        for s in self.snowflakes: s.draw(surf)
        self.player.draw(surf)

        hud = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        hud.fill((20, 30, 50, 180))
        surf.blit(hud, (0, 0))

        surf.blit(font.render(f"💰 {self.money}", True, GOLD), (20, 25))
        surf.blit(small.render(f"Счёт: {int(self.score)}", True, WHITE), (20, 55))
        surf.blit(small.render(f"🛷 {TRANSPORTS[self.player.level]['name']}", True, GREEN),
            (WIDTH // 2 - 80, 30))

        self._draw_button(surf, self.btn_pause)
        self._draw_button(surf, self.btn_menu)

        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 130))
            surf.blit(overlay, (0, 0))
            p = big.render("ПАУЗА", True, WHITE)
            surf.blit(p, (WIDTH // 2 - p.get_width() // 2, HEIGHT // 2 - 40))
            hint = small.render("Коснись экрана — продолжить", True, WHITE)
            surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 30))

        if self.menu:
            self.draw_menu(surf)

    def _draw_button(self, surf, btn):
        pygame.draw.rect(surf, (60, 70, 110), btn["rect"], border_radius=10)
        pygame.draw.rect(surf, btn["color"], btn["rect"], 2, border_radius=10)
        t = small.render(btn["text"], True, btn["color"])
        surf.blit(t, (btn["rect"].centerx - t.get_width() // 2,
                      btn["rect"].centery - t.get_height() // 2))

    def draw_menu(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 40, 230))
        surf.blit(overlay, (0, 0))

        title = big.render("🛒 МАГАЗИН", True, WHITE)
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        surf.blit(font.render(f"💰 {self.money}", True, GOLD), (WIDTH // 2 - 50, 20 + title.get_height() + 10))

        tab_y = 20 + title.get_height() + 50
        tab_w = WIDTH // 2 - 20
        tab1 = pygame.Rect(20, tab_y, tab_w, 60)
        tab2 = pygame.Rect(WIDTH // 2, tab_y, tab_w, 60)

        c1 = GOLD if self.menu_tab == 0 else WHITE
        c2 = GOLD if self.menu_tab == 1 else WHITE
        pygame.draw.rect(surf, (40, 50, 90), tab1, border_radius=8)
        pygame.draw.rect(surf, c1, tab1, 2, border_radius=8)
        pygame.draw.rect(surf, (40, 50, 90), tab2, border_radius=8)
        pygame.draw.rect(surf, c2, tab2, 2, border_radius=8)

        t1 = font.render("Транспорт", True, c1)
        t2 = font.render("Улучшения", True, c2)
        surf.blit(t1, (tab1.centerx - t1.get_width() // 2, tab1.centery - t1.get_height() // 2))
        surf.blit(t2, (tab2.centerx - t2.get_width() // 2, tab2.centery - t2.get_height() // 2))

        self.tab1_rect = tab1
        self.tab2_rect = tab2

        y = tab_y + 80
        items = TRANSPORTS if self.menu_tab == 0 else UPGRADES
        self.item_rects = []

        for i, item in enumerate(items):
            rect = pygame.Rect(20, y, WIDTH - 40, 90)
            self.item_rects.append((rect, i))
            owned = self.menu_tab == 0 and i in self.player.owned
            equipped = self.menu_tab == 0 and i == self.player.level
            bg = (60, 80, 140) if equipped else (30, 40, 80)
            pygame.draw.rect(surf, bg, rect, border_radius=10)
            pygame.draw.rect(surf, WHITE if self.menu_tab == 1 or owned else GRAY, rect, 2, border_radius=10)

            if self.menu_tab == 0:
                name_text = item["name"] + ("  ✅" if equipped else "")
                surf.blit(font.render(name_text, True, GREEN if equipped else WHITE), (rect.x + 15, rect.y + 10))
                surf.blit(small.render(f"{item['desc']} | Скорость {item['speed']}", True, (200, 200, 220)), (rect.x + 15, rect.y + 40))
                if equipped: price_s, pc = "АКТИВНО", GREEN
                elif owned: price_s, pc = "Надеть", BLUE
                else: price_s, pc = f"💰 {item['price']}", GOLD
            else:
                lvl = self.player.upgrades[item["effect"]]
                surf.blit(font.render(f"{item['name']}  ур.{int(lvl)}", True, WHITE), (rect.x + 15, rect.y + 10))
                surf.blit(small.render(item["desc"], True, (200, 200, 220)), (rect.x + 15, rect.y + 40))
                price_s, pc = f"💰 {item['price']}", GOLD

            pt = font.render(price_s, True, pc)
            surf.blit(pt, (rect.right - pt.get_width() - 20, rect.centery - pt.get_height() // 2))
            y += 100
            if y > HEIGHT - 120: break

        self.btn_close = make_button((WIDTH // 2 - 100, HEIGHT - 90, 200, 70), "Закрыть", WHITE)
        self._draw_button(surf, self.btn_close)

    def handle_shop_tap(self, pos):
        if self.btn_close["rect"].collidepoint(pos):
            self.menu = False
            return
        if self.tab1_rect.collidepoint(pos):
            self.menu_tab = 0
            return
        if self.tab2_rect.collidepoint(pos):
            self.menu_tab = 1
            return
        for rect, i in self.item_rects:
            if rect.collidepoint(pos):
                if self.menu_tab == 0:
                    if i in self.player.owned: self.player.apply_transport(i)
                    elif self.money >= TRANSPORTS[i]["price"]:
                        self.money -= TRANSPORTS[i]["price"]
                        self.player.owned.append(i)
                        self.player.apply_transport(i)
                else:
                    item = UPGRADES[i]
                    if self.money >= item["price"]:
                        self.money -= item["price"]
                        self.player.upgrades[item["effect"]] += 1
                        if item["effect"] == "speed":
                            self.player.speed = self.player.base_speed + self.player.upgrades["speed"]
                        item["price"] = int(item["price"] * 1.4)
                return
              def main():
    game = Game()
    running = True
    touches = {}

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.FINGERDOWN:
                x, y = int(event.x * WIDTH), int(event.y * HEIGHT)
                touches[event.finger_id] = (x, y)
                _handle_tap(game, (x, y))
            elif event.type == pygame.FINGERMOTION:
                x, y = int(event.x * WIDTH), int(event.y * HEIGHT)
                touches[event.finger_id] = (x, y)
            elif event.type == pygame.FINGERUP:
                touches.pop(event.finger_id, None)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touches["mouse"] = event.pos
                _handle_tap(game, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                touches.pop("mouse", None)
            elif event.type == pygame.MOUSEMOTION:
                if "mouse" in touches: touches["mouse"] = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.menu: game.menu = False
                    else: game.menu = True
                elif event.key == pygame.K_p:
                    game.paused = not game.paused

        keys = pygame.key.get_pressed()
        touch_list = list(touches.values())

        if not game.paused:
            game.update(keys, touch_list)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

def _handle_tap(game, pos):
    if game.paused:
        game.paused = False
        return
    if game.menu:
        game.handle_shop_tap(pos)
        return
    if game.btn_menu["rect"].collidepoint(pos):
        game.menu = True
        game.menu_tab = 0
    elif game.btn_pause["rect"].collidepoint(pos):
        game.paused = True

if __name__ == "__main__":
    main()
