from math import sqrt

DEFAULT_CONFIG = {"fill": "purple",
                  "side": 80,
                  "outline": "black",
                  "width": 1,
                  "cols":10,
                  "rows":10,
                  "enemy_size":40}


class Point():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def getX(self): return self.x

    def getY(self): return self.y


class Square():
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


class Build(Square):
    def __init__(self, x, y, pathable=True):
        super().__init__(x, y)
        #self.can_be_path = pathable
        #self.fill_color = "green" if self.can_be_path else "red"
        self.fill_color = DEFAULT_CONFIG["fill"]
        self.path = False
        self.turret_built = False

    def draw(self, canvas):
        return canvas.create_rectangle(self.x, self.y, self.x + self.side, self.y + self.side, fill=self.fill_color,
                                       outline=self.outline_color, width=self.outline_width)

    def detect_cursor(self, point):
        return True if self.x <= point.x <= self.x + self.side and self.y <= point.y <= self.y + self.side else False


class Path(Square):
    def __init__(self, x, y, start=False, end=False):
        super().__init__(x, y)
        self.fill_color = "blue"
        self.start = start
        self.end = end
        self.path = True

    def draw(self, canvas):
        return canvas.create_rectangle(self.x, self.y, self.x + self.side, self.y + self.side, fill=self.fill_color,
                                       outline=self.outline_color, width=self.outline_width)

    def detect_cursor(self, point):
        return True if self.x <= point.x <= self.x + self.side and self.y <= point.y <= self.y + self.side else False


class Turret(Square):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x + DEFAULT_CONFIG["side"] / 2
        self.y = y + DEFAULT_CONFIG["side"] / 2
        self.fill_color = "red"
        self.damage = 50
        self.bullet_size = 5
        self.damage_amp = 2
        self.level = 1
        self.range = DEFAULT_CONFIG["side"] * 3
        self.enemies = []
        self.in_range = []

    def draw(self, canvas):
        return canvas.create_oval(self.x - self.side / 4, self.y - self.side / 4, self.x + self.side / 4,
                                  self.y + self.side / 4, fill="red", outline=self.outline_color, width=5)

    def draw_range(self, canvas):
        return canvas.create_oval(self.x - self.range, self.y - self.range, self.x + self.range, self.y + self.range, fill="", outline="black", width="5")

    def detect_cursor(self, point):
        return True if sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2)) < DEFAULT_CONFIG["side"] / 4 else False

    def attack(self):
        self.in_range = []
        for enemy in self.enemies:
            x = enemy.x
            y = enemy.y
            dxc = x - self.x
            dyc = y - self.y
            dis = sqrt(pow(dxc, 2) + pow(dyc, 2))
            if dis < self.range:
                self.in_range.append(enemy)
        if len(self.in_range) > 0:
            enemy = self.in_range[0]
            dxc = enemy.x - self.x
            dyc = enemy.y - self.y

            if dxc == 0:
                vel_x = 0
            else:
                vel_x = abs(dxc) / dxc if abs(dxc) > abs(dyc) else abs(dxc) / dyc
            if x - self.x < 0:
                vel_x *= -1

            if dyc == 0:
                vel_y = 0
            else:
                vel_y = abs(dyc) / dyc if abs(dyc) > abs(dxc) else abs(dyc) / dxc
            if y - self.y < 0:
                vel_y *= -1

            bullet = Bullet(self.x, self.y, vel_x, vel_y, self.damage, self.bullet_size)
            return bullet
        else:
            return False


class Bullet(Square):
    def __init__(self, x, y, vel_x, vel_y, damage, side):
        super.__init__(x, y)
        self.x = x
        self.y = y
        self.fill_color = "black"
        self.side = side
        self.speed = 20
        self.hits = 1
        self.damage = damage
        self.destroyed = False
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.enemies = []
        #MAYBE UDĚLEJ V GAME.PY AŤ SE NEMUSÍ FURT NĚJAK VKLÁDAT self.enemies KVŮLI HODNOTÁM x A y.. Attack taky
    def draw(self, canvas):
        return canvas.create_oval(self.x - self.side / 2, self.y - self.side / 2, self.x + self.side / 2, self.y + self.side / 2,
                                  fill=self.fill_color, outline="")

    def move(self):
        self.x += self.vel_x * self.speed
        self.y += self.vel_y * self.speed

    def is_destroyed(self):
        if self.hits < 1:
            self.destroyed = True

    def hit_enemy(self):
        for enemy in self.enemies:
            point = Point(enemy.x, enemy.y)
            dx = point.x - self.x
            dy = point.y - self.y
            dist = sqrt(pow(dx, 2) + pow(dy, 2))
            if dist < (DEFAULT_CONFIG["enemy_size"] + self.size) / 2 and self.hits > 0:
                self.hits -= 1
                self.enemies.remove(enemy)
                print("Hit appended: {}".format(enemy))
                self.is_destroyed()

class Enemy(Square):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 100
        self.speed = 5
        self.vel_x = 1
        self.vel_y = 0
        self.fill_color = "orange"
        self.side = DEFAULT_CONFIG["enemy_size"]
        self.path = []
        self.img = None
        self.img_side = self.side / (2 * sqrt(2))

    def draw(self, canvas):
        canvas.create_oval(self.x - self.side / 2, self.y - self.side / 2, self.x + self.side / 2, self.y + self.side / 2, fill=self.fill_color, outline=self.outline_color, width=self.outline_width)
        canvas.create_image(self.x , self.y , image=self.img)
        #canvas.create_image
        return True

    def move(self):
        self.x += self.vel_x * self.speed
        self.y += self.vel_y * self.speed

    def set_dir(self):
        closest_point = Point(10000, 10000)
        for s in self.path:

            point = Point(s.x + s.side / 2, s.y + s.side / 2)
            print("--Processing point:")
            print(point.x)
            print(point.y)
            print("--")
#dxc = distance - x - closest(point)
#dx = distance - x
#dist = distance po pyt. větě (dist_closest... logicky)

            dxc = closest_point.x - self.x
            dyc = closest_point.y - self.y
            dist_closest = sqrt(pow(dxc, 2) + pow(dyc, 2))
            dx = point.x - self.x
            dy = point.y - self.y
            dist = sqrt(pow(dx, 2) + pow(dy, 2))

            #Pozor na mocniny - dělají abs

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
            self.vel_x = abs(dxc) / dxc if abs(dxc) > abs(dyc) else abs(dxc) / dyc
        if closest_point.x - self.x < 0:
            self.vel_x *= -1

        if dyc == 0:
            self.vel_y = 0
        else:
            self.vel_y = abs(dyc) / dyc if abs(dyc) > abs(dxc) else abs(dyc) / dxc
        if closest_point.y - self.y < 0:
            self.vel_y *= -1

        print("Vel_x: {}, Vel_y: {}".format(self.vel_x, self.vel_y))

    def set_passed(self):
        for s in self.path:
            point = Point(s.x + s.side / 2, s.y + s.side / 2)
            dx = point.x - self.x
            dy = point.y - self.y
            dist = sqrt(pow(dx, 2) + pow(dy, 2))
            if dist < 5:
                self.path.remove(s)
                print("Passed appended: {}".format(s))
                self.set_dir()

    def reached_end(self):
        if len(self.path) == 0:
            return True
        else:
            return False

    def dead(self):
        if self.hp < 1:
            return True
        else:
            return False