from tkinter import *
import tkinter.ttk as ttk
from pydantic import BaseModel
from enum import Enum

METER_TO_PIXELS = 100
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800
ROOM_COLOR = "#d2d2d2"

class Orientation(Enum):
        HORIZONTAL = 1
        VERTICAL = 2

class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    def __mul__(self, other):
        return Vector2D(self.x * other, self.y * other)
    def __str__(self):
        return f"({self.x}, {self.y})"

class Wall:
    def __init__(self, start: Vector2D, end: Vector2D):
        self.start = start
        self.end = end
        self.length = Utils.distance_to(start, end)

        #self.doors = [Door]

    def draw(self):
        canvas.create_line(self.start.x, self.start.y, self.end.x, self.end.y, fill="green", width=2)


class Window:
    def __init__(self, attached_wall: Wall, width: float, wall_placement: float,  orientation: Orientation = Orientation.HORIZONTAL):
        self.width = width * METER_TO_PIXELS
        self.position =  Utils.lerp(attached_wall.start, attached_wall.end, wall_placement)

        if(orientation == Orientation.HORIZONTAL):
            self.start = Vector2D(self.position.x - (width / 2), self.position.y)
            self.end = Vector2D(self.position.x + (width / 2), self.position.y)
        elif(orientation == Orientation.VERTICAL):
            self.start = Vector2D(self.position.x, self.position.y - (width / 2))
            self.end = Vector2D(self.position.x, self.position.y + (width / 2))

    def draw(self):
        canvas.create_line(self.start.x, self.start.y, self.end.x, self.end.y, fill="blue", width=3)

class Room:
    # width and height are in meters
    def __init__(self, width: float, height: float):
        self.width = width * METER_TO_PIXELS
        self.height = height * METER_TO_PIXELS

        self.center_point = Vector2D(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)

        self.top_left_point = Vector2D(self.center_point.x - (self.width / 2), self.center_point.y - (self.height / 2))
        self.top_right_point = Vector2D(self.center_point.x + (self.width / 2), self.center_point.y - (self.height / 2))
        self.bottom_left_point = Vector2D(self.center_point.x - (self.width / 2), self.center_point.y + (self.height / 2))
        self.bottom_right_point = Vector2D(self.center_point.x + (self.width / 2), self.center_point.y + (self.height / 2))

        self.walls = [
            Wall(self.top_left_point, self.top_right_point),
            Wall(self.top_right_point, self.bottom_right_point),
            Wall(self.bottom_right_point, self.bottom_left_point),
            Wall(self.bottom_left_point, self.top_left_point)
        ]

    def draw(self):

        canvas.create_rectangle(self.top_left_point.x, self.top_left_point.y, self.bottom_right_point.x, self.bottom_right_point.y, fill=ROOM_COLOR)
        for wall in self.walls:
            wall.draw()

class Utils:
    @staticmethod
    def distance_to(p1: Vector2D, p2: Vector2D):
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5

    @staticmethod
    def lerp(p1: Vector2D, p2: Vector2D, a: float):
        #Perform linear interpolation for x between (x1,y1) and (x2,y2)

        return p1 * (1 - a) + p2 * a

master_window = Tk()
canvas = Canvas(master_window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack(side="bottom", fill="both", expand=True)
#canvas.create_line(0, y, canvas_width, y)


my_room = Room(width=10, height=5)
window1 = Window(attached_wall=my_room.walls[0], width=100, wall_placement=0.2, orientation=Orientation.HORIZONTAL)
my_room.draw()
window1.draw()





mainloop()

exit()