from math import sqrt

DEFAULT_CONFIG = {"fill": "purple",
                  "side": 80,
                  "outline": "black",
                  "width": 1,
                  "cols":10,
                  "rows":10,
                  "enemy_size":40}


    # Bod
class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


    # Základ pro čtverec
class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.side = DEFAULT_CONFIG["side"]
        self.outline_color = DEFAULT_CONFIG["outline"]
        self.outline_width = DEFAULT_CONFIG["width"]
        self.fill_color = DEFAULT_CONFIG["fill"]

    def __repr__(self):
        return "Square(x: {}, y: {}, side: {}, fill_color: {} )".format(self.x, self.y, self.side, self.fill_color)

    def draw(self, canvas):
        pass


    # Čtverce, na kterých jde postavit věž
class Build(Square):
    def __init__(self, x, y, pathable=True):
        super().__init__(x, y)
        #self.can_be_path = pathable
        #self.fill_color = "green" if self.can_be_path else "red"
        self.fill_color = DEFAULT_CONFIG["fill"]
        self.path = False
        self.turret_built = False

    def __repr__(self):
        return "Build_square(x: {}, y: {})".format(self.x, self.y)

    # Vykreslení
    def draw(self, canvas):
        return canvas.create_rectangle(self.x, self.y, self.x + self.side, self.y + self.side, fill=self.fill_color,
                                       outline=self.outline_color, width=self.outline_width)
    # Detekce kurzoru
    def detect_cursor(self, point):
        return True if self.x <= point.x <= self.x + self.side and self.y <= point.y <= self.y + self.side else False


    # Cesta
class Path(Square):
    def __init__(self, x, y, start=False, end=False):
        super().__init__(x, y)
        self.fill_color = "blue"
        self.start = start
        self.end = end
        self.path = True

    def __repr__(self):
        return "Path_square(x: {}, y: {},)".format(self.x, self.y)

    # Vykreslení
    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, self.x + self.side, self.y + self.side, fill=self.fill_color,
                                       outline=self.outline_color, width=self.outline_width)

    # Detekce kurzoru
    def detect_cursor(self, point):
        return True if self.x <= point.x <= self.x + self.side and self.y <= point.y <= self.y + self.side else False


    # Věž - základ
class Turret(Square):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x + DEFAULT_CONFIG["side"] / 2
        self.y = y + DEFAULT_CONFIG["side"] / 2
        self.fill_color = "red"
        self.def_cost = 100
        self.cost = self.def_cost
        self.total_cost = self.def_cost
        self.damage = 50
        self.bullet_size = 5
        self.bullet_max_size = DEFAULT_CONFIG["side"]
        self.bullet_hits = 1
        self.damage_amp = 1.2
        self.level = 1
        self.loaded = 1
        self.load_time = 1000
        self.min_load_time = 100
        self.load_time_diff = 100
        self.range = DEFAULT_CONFIG["side"] * 3
        self.in_range = []
        self.fill_color = "white"
        self.target_mode = "first"
        self.turret_type = None

    def __repr__(self):
        return "Turret(x: {}, y: {})".format(self.x, self.y)

        # Vykreslení
    def draw(self, canvas):
        canvas.create_oval(self.x - self.side / 4, self.y - self.side / 4, self.x + self.side / 4,
                           self.y + self.side / 4, fill=self.fill_color, outline=self.outline_color, width=5)
        canvas.create_text(self.x, self.y, fill="black", font="arial 10",
                           text="{}".format(self.level))

        # Vykreslení dosahu
    def draw_range(self, canvas):
        canvas.create_oval(self.x - self.range, self.y - self.range, self.x + self.range, self.y + self.range,
                                  fill="", outline="black", width="5")

        # Detekce kurzoru
    def detect_cursor(self, point):
        return True if sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2)) < DEFAULT_CONFIG["side"] / 4 else False

        # Nabití věže
    def reload(self):
        self.loaded = 1

        # Vylepšení věže
    def upgrade(self):
        self.cost *= 2
        self.total_cost += self.cost
        self.level += 1
        self.damage *= self.damage_amp
        if self.bullet_size > self.bullet_max_size:
            self.bullet_size = self.bullet_max_size
        else:
            self.bullet_size *= self.damage_amp
        self.bullet_hits += 1


    # Věž typu "big": menší základní poškození a menší rychlost střelby.
    # Poškození střel roste rychleji než u "fast" věže.
class TurretBig(Turret):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x + DEFAULT_CONFIG["side"] / 2
        self.y = y + DEFAULT_CONFIG["side"] / 2
        self.fill_color = "red"
        self.turret_type = "big"
        self.load_time = 2000
        self.size_amp = self.damage_amp
        self.damage_amp = 2
        self.damage = 10

    def __repr__(self):
        return "Turret_Big(x: {}, y: {}, bullet_size: {}, damage: {} )".format(self.x, self.y, self.bullet_size, self.damage)

        # Vylepšení
        # Střely zasáhnou nepřítele (každého max jednou) a pokračují v cestě.
        # po levelu 5 se sníží násobitel poškození z 2 na 1.4
        # při každém vylepšení -> +1 zásah (později je nezničitelná - "nekonečno" zásahů)
    def upgrade(self):
        self.cost *= 2
        self.total_cost += self.cost
        self.level += 1
        self.damage *= self.damage_amp
        if self.bullet_size > self.bullet_max_size:
            self.bullet_size = self.bullet_max_size
        else:
            self.bullet_size *= self.size_amp
        self.bullet_hits += 1
        if self.level > 5:
            self.damage_amp = 1.4

    # Vět typu "fast": větší základní poškození, větší rychlost střelby.
    # Rychlost střelby roste s levelem, poškození roste pomaleji
    # Větší základní poškození
class TurretFast(Turret):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x + DEFAULT_CONFIG["side"] / 2
        self.y = y + DEFAULT_CONFIG["side"] / 2
        self.fill_color = "green"
        self.turret_type = "fast"

    def __repr__(self):
        return "Turret_Big(x: {}, y: {}, load_time: {}, damage: {} )".format(self.x, self.y, self.load_time, self.damage)

    # střela zasáhne nepřítele. Jestli nepřítel přežije, zasáhne jej znovu. (někdy ale projde dál -> důraz na správné umístění věží)
    # Po levelu 5 se zvýší násobitel poškození z 1.2 na 1.5
    # Střela nikdy nebude nezničitelná
    def upgrade(self):
        self.cost *= 2
        self.total_cost += self.cost
        self.level += 1
        self.damage *= self.damage_amp
        if self.load_time < self.min_load_time:
            self.load_time = self.min_load_time
        else:
            self.load_time -= self.load_time_diff
        self.bullet_hits += 1
        if self.level > 5:
            self.damage_amp = 1.5


    # Střela
class Bullet(Square):
    def __init__(self, x, y, vel_x, vel_y, damage, side, hits, turrtype):
        super().__init__(x, y)
        self.x = x
        self.y = y
        self.fill_color = "black"
        self.turret_type = turrtype
        self.side = side
        self.speed = 20
        self.hits = hits
        self.damage = damage
        self.destroyed = False
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.enemies_hit = []
        self.immortal = False

    def __repr__(self):
        return "Bullet(x: {}, y: {}, bullet_size: {}, damage: {}, hits: {})".format(self.x, self.y, self.side, self.damage, self.hits)

        # Vykreslení
    def draw(self, canvas):
        canvas.create_oval(self.x - self.side / 2, self.y - self.side / 2, self.x + self.side / 2, self.y + self.side / 2,
                                  fill=self.fill_color, outline="")

        # Pohyb
    def move(self):
        self.x += self.vel_x * self.speed
        self.y += self.vel_y * self.speed

        # Jestli je střela za okrajem, bude v loopu zničena
    def is_destroyed(self):
        if self.x < 0 or self.y < DEFAULT_CONFIG["side"] or self.x > DEFAULT_CONFIG["side"] * DEFAULT_CONFIG["cols"] or self.y > DEFAULT_CONFIG["side"] * (DEFAULT_CONFIG["rows"] + 1) or self.hits < 1:
            self.destroyed = True


    # Nepřítel
class Enemy(Square):
    def __init__(self, x, y, hp=100, speed=1):
        super().__init__(x, y)
        self.hp_max = hp
        self.percentual_hp = 100
        self.hp = hp
        self.speed = speed
        self.vel_x = 1
        self.vel_y = 0
        self.fill_color = "orange"
        self.side = DEFAULT_CONFIG["enemy_size"]
        self.path = []
        # Peníze podle rychlosti a hp (= vlny)
        self.reward = int((self.hp * self.speed) / 20)

    def __repr__(self):
        return "Enemy(x: {}, y: {}, hp: {}, speed: {} )".format(self.x, self.y, self.hp, self.speed)

        # Vykreslení
    def draw(self, canvas):
        if self.hp < 0:
            self.hp = 0
        self.percentual_hp = (self.hp / self.hp_max) * self.side
        canvas.create_oval(self.x - self.side / 2, self.y - self.side / 2, self.x + self.side / 2, self.y + self.side / 2, fill=self.fill_color, outline=self.outline_color, width=self.outline_width)
        canvas.create_rectangle(self.x - self.side / 2, self.y + self.side / 2 + 5, self.x + self.side / 2,
                                self.y + self.side / 2 + 10, fill="red", outline="black", width="2")
        canvas.create_rectangle(self.x - self.side / 2, self.y + self.side / 2 + 5, self.x - self.side / 2 + self.percentual_hp,
                                self.y + self.side / 2 + 10, fill="green", outline="")

        # pohyb
    def move(self):
        self.x += self.vel_x * self.speed
        self.y += self.vel_y * self.speed

        # Nastavení směru na nejbližší čtverec cesty
    def set_dir(self):
        closest_point = Point(10000, 10000)
        for s in self.path:

            point = Point(s.x + s.side / 2, s.y + s.side / 2)

            dxc = closest_point.x - self.x
            dyc = closest_point.y - self.y
            dist_closest = sqrt(pow(dxc, 2) + pow(dyc, 2))
            dx = point.x - self.x
            dy = point.y - self.y
            dist = sqrt(pow(dx, 2) + pow(dy, 2))

            if dist < dist_closest:
                print("self.x: {}, self.y: {}".format(self.x,self.y))
                print("closest point updated: {}, {}".format(closest_point.x, closest_point.y))
                print("self.path: {}".format(self.path))
                closest_point = point

        dxc = abs(closest_point.x - self.x)
        dyc = abs(closest_point.y - self.y)

        if dxc == 0:
            self.vel_x = 0
        else:
            self.vel_x = dxc / dxc if dxc > dyc else dxc / dyc
        if closest_point.x - self.x < 0:
            self.vel_x *= -1

        if dyc == 0:
            self.vel_y = 0
        else:
            self.vel_y = dyc / dyc if dyc > dxc else dyc / dxc
        if closest_point.y - self.y < 0:
            self.vel_y *= -1

        print("Vel_x: {}, Vel_y: {}".format(self.vel_x, self.vel_y))

        # Nastaví, které čtverce cesty už přešel, aby na ně nešel znovu
    def set_passed(self):
        for s in self.path:
            point = Point(s.x + s.side / 2, s.y + s.side / 2)
            dx = point.x - self.x
            dy = point.y - self.y
            dist = sqrt(pow(dx, 2) + pow(dy, 2))
            if dist < 10:
                self.path.remove(s)
                print("Passed appended: {}".format(s))
                self.set_dir()

        # když celou cestu prošel - umře a ubere život
    def reached_end(self):
        if len(self.path) == 0:
            return True
        else:
            return False

        # žiješ?
    def dead(self):
        if self.hp < 1:
            return True
        else:
            return False
