import time
import copy
import math
import random
from dataclasses import dataclass

import pyxel


@dataclass
class Point:
    x: float
    y: float

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point={self.x, self.y}"

    def distance(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class Segment:
    start: Point
    end: Point


def get_intersection(first_segment: Segment, second_segment: Segment) -> Point:
    intersect = Point(0, 0)
    denom = (second_segment.end.x - second_segment.start.x) * (first_segment.start.y - first_segment.end.y) - (
                first_segment.start.x - first_segment.end.x) * (second_segment.end.y - second_segment.start.y)
    if denom == 0:
        return Point(0, 0)
    ta_num = (second_segment.start.y - second_segment.end.y) * (first_segment.start.x - second_segment.start.x) + (
                second_segment.end.x - second_segment.start.x) * (first_segment.start.y - second_segment.start.y)
    ta = ta_num / denom
    tb_num = (first_segment.start.y - first_segment.end.y) * (first_segment.start.x - second_segment.start.x) + (
                first_segment.end.x - first_segment.start.x) * (first_segment.start.y - second_segment.start.y)
    tb = tb_num / denom
    if 0 <= ta <= 1 and 0 <= tb <= 1:
        x = first_segment.start.x + ta * (first_segment.end.x - first_segment.start.x)
        y = first_segment.start.y + ta * (first_segment.end.y - first_segment.start.y)
        return Point(x, y)
    else:
        return Point(0, 0)
    return intersect


class Brick:
    def __init__(self, top_left=Point(0, 0), width=20, height=10, active=False):
        self.top_left = copy.copy(top_left)
        self.width = width
        self.height = height
        self.center = Point(top_left.x + width / 2, top_left.y + height / 2)
        self.active = active

    def __repr__(self):
        return f"Brick(x={self.top_left.x}, y={self.top_left.y}, center={self.center.x, self.center.y})"

    def draw(self):
        if self.active:
            pyxel.rect(int(self.top_left.x), int(self.top_left.y), self.width, self.height, pyxel.COLOR_LIGHTGRAY)
        else:
            pyxel.rectb(int(self.top_left.x), int(self.top_left.y), self.width, self.height, pyxel.COLOR_LIGHTGRAY)

    def get_bottom_segment(self) -> Segment:
        start_point = Point(self.top_left.x,
                            self.top_left.y + self.height)
        end_point = Point(self.top_left.x + self.width,
                          self.top_left.y + self.height)
        return Segment(start_point, end_point)

    def get_left_segment(self) -> Segment:
        start_point = Point(self.top_left.x,
                            self.top_left.y)
        end_point = Point(self.top_left.x,
                          self.top_left.y + self.height)
        return Segment(start_point, end_point)

    def get_right_segment(self) -> Segment:
        start_point = Point(self.top_left.x + self.width,
                            self.top_left.y)
        end_point = Point(self.top_left.x + self.width,
                          self.top_left.y + self.height)
        return Segment(start_point, end_point)

    def get_top_segment(self) -> Segment:
        start_point = Point(self.top_left.x,
                            self.top_left.y)
        end_point = Point(self.top_left.x + self.width,
                          self.top_left.y)
        return Segment(start_point, end_point)


class Ball:
    def __init__(self, center=Point(0, 0), radius=1, x_velocity=0, y_velocity=0):
        self.center = copy.copy(center)
        self.previous = Point(0, 0)
        self.radius = radius
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity

    def __repr__(self):
        return f"Ball(center={self.center}, prev={self.previous}, radius={self.radius})"

    def draw(self):
        if self.radius > 1:
            pyxel.circ(int(self.center.x), int(self.center.y), self.radius, pyxel.COLOR_LIME)
        else:
            pyxel.pix(int(self.center.x), int(self.center.y), pyxel.COLOR_LIME)

    def update(self):
        self.previous = copy.copy(self.center)
        self.center.x += self.x_velocity
        self.center.y += self.y_velocity
        if self.x_velocity < -3:
            self.x_velocity = -3
        if self.x_velocity > 3:
            self.x_velocity = 3
        if self.y_velocity < -3:
            self.y_velocity = -3
        if self.y_velocity > 3:
            self.y_velocity = 3


    def out_of_bounds(self):
        if (self.center.y + self.radius) >= pyxel.height:
            return True
        return False

    def intersect_wall(self):
        # wall bounces
        if self.center.x <= 1:
            self.x_velocity *= -1
            self.center.x = 1

        if self.center.x >= (pyxel.width - 1):
            self.x_velocity *= -1
            self.center.x = (pyxel.width - 1)

        if self.center.y <= 1:
            self.y_velocity *= -1
            self.center.y = 1

    def intersect_brick(self, brick: Brick):
        movement_segment = Segment(start=self.previous, end=self.center)

        if self.previous.x < brick.center.x:
            # can only hit left side or top or bottom
            left_intersection_point = get_intersection(movement_segment, brick.get_left_segment())
            point_array = []
            if left_intersection_point != Point(0, 0):
                point_array.append((left_intersection_point,
                                    self.center.distance(left_intersection_point),
                                    -1 * self.x_velocity,
                                    self.y_velocity))
            if self.y_velocity > 0:
                # can only hit left or top
                top_intersection_point = get_intersection(movement_segment, brick.get_top_segment())
                if top_intersection_point != Point(0, 0):
                    point_array.append((top_intersection_point,
                                        self.center.distance(top_intersection_point),
                                        self.x_velocity,
                                        -1 * self.y_velocity))

            elif self.y_velocity <= 0:
                # can only hit left or bottom
                bottom_intersection_point = get_intersection(movement_segment, brick.get_bottom_segment())
                if bottom_intersection_point != Point(0, 0):
                    point_array.append((bottom_intersection_point,
                                        self.center.distance(bottom_intersection_point),
                                        self.x_velocity,
                                        -1 * self.y_velocity))
            try:
                intersection_info = min(point_array, key=lambda k: k[1])
            except ValueError:
                print(f"{movement_segment=} {brick.get_left_segment()} {brick.get_top_segment()} {brick.get_bottom_segment()}")
                pyxel.quit()
            self.center = copy.copy(intersection_info[0])
            self.x_velocity = intersection_info[2]
            self.y_velocity = intersection_info[3]
        else:
            # can only hit right side or top or bottom
            right_intersection_point = get_intersection(movement_segment, brick.get_right_segment())
            point_array = []
            if right_intersection_point != Point(0, 0):
                point_array.append((right_intersection_point,
                                    self.center.distance(right_intersection_point),
                                    -1 * self.x_velocity,
                                    self.y_velocity))
            if self.y_velocity > 0:
                # can only hit right or top
                top_intersection_point = get_intersection(movement_segment, brick.get_top_segment())
                if top_intersection_point != Point(0, 0):
                    point_array.append((top_intersection_point,
                                        self.center.distance(top_intersection_point),
                                        self.x_velocity,
                                        -1 * self.y_velocity))

            elif self.y_velocity <= 0:
                # can only hit left or bottom
                bottom_intersection_point = get_intersection(movement_segment, brick.get_bottom_segment())
                if bottom_intersection_point != Point(0, 0):
                    point_array.append((bottom_intersection_point,
                                        self.center.distance(bottom_intersection_point),
                                        self.x_velocity,
                                        -1 * self.y_velocity))
            try:
                intersection_info = min(point_array, key=lambda k: k[1])
            except ValueError:
                print(f"{movement_segment=} {brick.get_right_segment()} {brick.get_top_segment()} {brick.get_bottom_segment()}")
                pyxel.quit()
            self.center = copy.copy(intersection_info[0])
            self.x_velocity = intersection_info[2]
            self.y_velocity = intersection_info[3]


class Bar:
    def __init__(self, location=Point(0, 0), width=20, height=3):
        self.location = copy.copy(location)
        self.width = width
        self.height = height
        self.center = Point(self.location.x + width / 2, self.location.y + height / 2)
        self.velocity = 0

    def draw(self):
        pyxel.rect(int(self.location.x), int(self.location.y), self.width, self.height, pyxel.COLOR_GREEN)

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD_1_LEFT):
            self.location.x = max(self.location.x - 2, 1)
            self.center.x = self.location.x + self.width / 2
            self.velocity = -1

        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD_1_RIGHT):
            self.location.x = min(self.location.x + 2, pyxel.width - (1 + self.width))
            self.center.x = self.location.x + self.width / 2
            self.velocity = 1


def intersect_bar(ball: Ball, bar: Bar) -> bool:
    if abs(ball.center.x - bar.center.x) < (bar.width + ball.radius) and \
            abs(ball.center.y - bar.center.y) < (bar.height + ball.radius):
        return True
    return False


def intersect_brick(ball: Ball, brick: Brick) -> bool:
    # top edge of ball less than top of brick or bottom of ball above bottom of brick
    radius = ball.radius - 1
    if abs(ball.center.x - brick.center.x) < (brick.width / 2 + radius) and \
            abs(ball.center.y - brick.center.y) < (brick.height / 2 + radius):
        print(f"{brick=} {ball=}")
        return True
    return False


class App:

    def __init__(self):
        pyxel.init(160, 120, caption="Fix it, Break it")
        # pyxel.image(0).load(0, 0, "assets/pyxel_logo_38x16.png")
        self.bar = Bar(location=Point(1, y=pyxel.height - (3 + 1)))

        self.ball = Ball(center=Point(5, y=pyxel.height - (3 + 1) - 1 - self.bar.height),
                         x_velocity=random.randint(1, 2),
                         y_velocity=-1)

        self.bricks = []

        self.level = 1
        self.mesg_time = 2
        self.playing = False
        self.paused = False
        self.lose = False
        self.win = False
        self.debug = False

        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.change_level(self.level)
        self.mesg_time = 2
        self.playing = False
        self.paused = False
        self.lose = False
        self.win = False
        self.debug = False

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_P) and self.playing:
            self.paused = not self.paused

        if pyxel.btnp(pyxel.KEY_D):
            self.debug = not self.debug

        if pyxel.btnp(pyxel.KEY_1):
            self.level = 1

        if pyxel.btnp(pyxel.KEY_1):
            self.level = 2

        if pyxel.btnp(pyxel.KEY_S):
            self.change_level(self.level)
            self.playing = True

        if self.paused or not self.playing:
            return

        if pyxel.btnp(pyxel.KEY_R):
            self.lose = True

        self.bar.update()
        self.ball.update()
        self.calculate_intersections()

        if self.lose or self.win:
            time.sleep(self.mesg_time)
            self.reset()

        if self.ball.out_of_bounds():
            self.lose = True

        all_bricks_active = True
        for brick in self.bricks:
            all_bricks_active &= brick.active
        if all_bricks_active:
            self.win = True

    def calculate_intersections(self):
        # bounce off bar
        self.ball.intersect_wall()

        if intersect_bar(self.ball, self.bar):
            self.ball.y_velocity *= -1
            self.ball.x_velocity += self.bar.velocity

        for brick in self.bricks:
            if intersect_brick(self.ball, brick):
                brick.active = not brick.active
                # adjust ball position if needed
                print(f"ball_velocity = {self.ball.x_velocity}, {self.ball.y_velocity}")
                self.ball.intersect_brick(brick)
                print(f"ball_velocity = {self.ball.x_velocity}, {self.ball.y_velocity}")

    def draw_debug(self):
        pyxel.text(5, 5, f"ball x: {self.ball.center.x}, ball y: {self.ball.center.y}", pyxel.COLOR_NAVY)
        pyxel.text(5, 10, f"ball vx: {self.ball.x_velocity}, ball vy: {self.ball.y_velocity}", pyxel.COLOR_NAVY)
        pyxel.text(5, 15, f"bar x: {self.bar.location.x}, bar y: {self.bar.location.y}", pyxel.COLOR_NAVY)

    def draw(self):
        pyxel.cls(0)
        if self.debug:
            self.draw_debug()

        if self.paused:
            pyxel.text(60, 60, f"PAUSED", pyxel.COLOR_NAVY)

        if not self.playing:
            pyxel.text(55, 5, f"Fixit Breakit", pyxel.COLOR_STEELBLUE)
            pyxel.text(5, 50, f"Use left/right arrow keys to move ", pyxel.COLOR_PEACH)
            pyxel.text(5, 60, f"Press P to pause", pyxel.COLOR_STEELBLUE)
            pyxel.text(5, 70, f"Press S to start a game", pyxel.COLOR_STEELBLUE)
            pyxel.text(5, 80, f"Press Q to quit", pyxel.COLOR_STEELBLUE)
            return

        pyxel.rectb(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_DARKGRAY)
        if self.debug:
            self.draw_debug()
        self.bar.draw()
        self.ball.draw()
        for brick in self.bricks:
            brick.draw()

        if self.lose:
            pyxel.text(40, 40, 'Game Over', pyxel.COLOR_RED)

        if self.win:
            pyxel.text(40, 40, 'You won!', pyxel.COLOR_RED)

    def change_level(self, level=1):
        self.bar.location = Point(1, y=pyxel.height - (3 + 1))

        self.ball.center = Point(5, y=pyxel.height - (3 + 1) - 1 - self.bar.height)
        self.ball.x_velocity=random.randint(1, 2)
        self.ball.y_velocity=-1

        if level == 1:
            self.bricks = [Brick(Point(25, 30)),
                           Brick(Point(45, 30)),
                           Brick(Point(65, 30)),
                           Brick(Point(90, 30)),
                           Brick(Point(20, 50)),
                           Brick(Point(40, 50)),
                           Brick(Point(60, 50)),
                           Brick(Point(100, 50)),
                           Brick(Point(120, 50))]
        elif level == 2:
            self.bricks = [Brick(Point(60, 50)),
                           Brick(Point(100, 50)),
                           Brick(Point(120, 50))]



App()
