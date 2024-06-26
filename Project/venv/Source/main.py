from tkinter import *
import tkinter.ttk as ttk
from pydantic import BaseModel
from enum import Enum
from typing import List
import math

METER_TO_PIXELS = 100
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800
ROOM_COLOR = "#d2d2d2"
SOFA_COLOR = "#f4a460"
TABLE_COLOR = "#8b4513"
COFFEE_TABLE_COLOR = "#8b4513"
CHAIR_COLOR = "#8b4513"
TV_COLOR = "#8b4513"
LAMP_COLOR = "#8b4513"
AREA_COLOR = "#3333aa"

class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    def __mul__(self, other):
        return Vector2D(self.x * other, self.y * other)
    def __div__(self, other):
        return Vector2D(self.x / other, self.y / other)
    def __eq__(self, __value: object) -> bool:
        return self.x == __value.x and self.y == __value.y
    def __str__(self):
        return f"({self.x}, {self.y})"
    def scale(self, scalar: float):
        return Vector2D(self.x * scalar, self.y * scalar)

class Wall:
    def __init__(self, position: Vector2D, length: float, rotation: float = 0):
        self.position = position
        self.length = length
        self.rotation = rotation

        self.update_points()

    def update_points(self):
        half_length = self.length / 2

        # Points before rotation
        start_point = Vector2D(-half_length, 0)
        end_point = Vector2D(half_length, 0)

        # Rotation matrix components
        cos_theta = math.cos(self.rotation)
        sin_theta = math.sin(self.rotation)

        # Apply rotation
        self.start = Vector2D(cos_theta * start_point.x - sin_theta * start_point.y + self.position.x,
                              sin_theta * start_point.x + cos_theta * start_point.y + self.position.y)

        self.end = Vector2D(cos_theta * end_point.x - sin_theta * end_point.y + self.position.x,
                            sin_theta * end_point.x + cos_theta * end_point.y + self.position.y)

    def draw(self):
        canvas.create_line(self.start.x, self.start.y, self.end.x, self.end.y, fill="green", width=2)

class Window(Wall):
    def __init__(self, attached_wall: Wall, wall_placement: float,  length: float, rotation: float = 0):
        self.position =  Utils.lerp(attached_wall.start, attached_wall.end, wall_placement)
        super().__init__(self.position, length, rotation)

    def draw(self):
        canvas.create_line(self.start.x, self.start.y, self.end.x, self.end.y, fill="blue", width=3)

class Door(Wall):
    def __init__(self, attached_wall: Wall, wall_placement: float, length: float, rotation: float = 0):
        self.position =  Utils.lerp(attached_wall.start, attached_wall.end, wall_placement)
        super().__init__(self.position, length, rotation)

    def draw(self):
        canvas.create_line(self.start.x, self.start.y, self.end.x, self.end.y, fill="brown", width=3)

class BoundingBox:
    def __init__(self, width: float, height: float, position: Vector2D = Vector2D(0, 0), rotation: float = 0):
        self.height = height                            # Height in meters
        self.width = width                              # Width in meters
        self.position = position                        # Position of the center of the bounding box
        self.rotation = rotation                        # Rotation in radians
        self.height_px = height * METER_TO_PIXELS       # Height in pixels
        self.width_px = width * METER_TO_PIXELS         # Width in pixels

        self.update_corners()

    def update_corners(self):
        hw = self.width_px / 2
        hh = self.height_px / 2

        # Points before rotation
        points = [
            Vector2D(-hw, -hh),
            Vector2D(hw, -hh),
            Vector2D(hw, hh),
            Vector2D(-hw, hh)
        ]

        # Rotate points
        cos_theta = math.cos(self.rotation)
        sin_theta = math.sin(self.rotation)

        self.corners = []
        for point in points:
            x_rot = cos_theta * point.x - sin_theta * point.y + self.position.x
            y_rot = sin_theta * point.x + cos_theta * point.y + self.position.y
            self.corners.append(Vector2D(x_rot, y_rot))

        self.top_left, self.top_right, self.bottom_right, self.bottom_left = self.corners

    def place(self, new_position: Vector2D, rotation: float = 0):
        self.position = new_position
        self.rotation = rotation
        self.update_corners()


    def draw(self, line_color: str = "red", fill_color: str = "white", show_direction: bool = False):
        #canvas.create_line(self.top_left.x, self.top_left.y, self.top_right.x, self.top_right.y, fill="red")
        #canvas.create_line(self.top_right.x, self.top_right.y, self.bottom_right.x, self.bottom_right.y, fill="red")
        #canvas.create_line(self.bottom_right.x, self.bottom_right.y, self.bottom_left.x, self.bottom_left.y, fill="red")
        #canvas.create_line(self.bottom_left.x, self.bottom_left.y, self.top_left.x, self.top_left.y, fill="red")

        canvas.create_polygon(self.top_left.x, self.top_left.y, self.top_right.x, self.top_right.y, self.bottom_right.x, self.bottom_right.y, self.bottom_left.x, self.bottom_left.y, outline=line_color, fill=fill_color)

        if show_direction:
            direction_identifier_position = Utils.midpoint(self.top_left, self.top_right)
            did_right = Utils.midpoint(self.top_right, self.bottom_right)
            did_right = Utils.midpoint(did_right, direction_identifier_position)
            did_left = Utils.midpoint(self.top_left, self.bottom_left)
            did_left = Utils.midpoint(did_left, direction_identifier_position)
            canvas.create_line(direction_identifier_position.x, direction_identifier_position.y, did_right.x, did_right.y, fill="black")
            canvas.create_line(direction_identifier_position.x, direction_identifier_position.y, did_left.x, did_left.y, fill="black")

        #canvas.create_polygon(self.top_left.x, self.top_left.y, self.bottom_right.x, self.bottom_right.y, outline="red")


class Furniture:
    def __init__(self, bounding_box: BoundingBox):
        self.bounding_box = bounding_box

    def draw(self):
        self.bounding_box.draw()

# Furniture classes
class Sofa(Furniture):
    def __init__(self, width: float, height:float, position: Vector2D = Vector2D(0, 0), rotation = 0):
        super().__init__(BoundingBox(width=width, height=height, position=position, rotation=rotation))

    def draw(self):
        self.bounding_box.draw(fill_color=SOFA_COLOR, show_direction=True)
        canvas.create_text(self.bounding_box.position.x, self.bounding_box.position.y, text="Sofa", fill="black")

class Table(Furniture):
    def __init__(self, width: float, height:float, position: Vector2D = Vector2D(0, 0), rotation = 0):
        super().__init__(BoundingBox(width=width, height=height, position=position, rotation=rotation))

    def draw(self):
        self.bounding_box.draw(fill_color=TABLE_COLOR)
        canvas.create_text(self.bounding_box.position.x, self.bounding_box.position.y, text="Table", fill="black")

class CoffeeTable(Table):
    def __init__(self, width: float, height:float, position: Vector2D = Vector2D(0, 0), rotation = 0):
        super().__init__(width=width, height=height, position=position, rotation=rotation)

    def draw(self):
        self.bounding_box.draw(fill_color=COFFEE_TABLE_COLOR)
        canvas.create_text(self.bounding_box.position.x, self.bounding_box.position.y, text="Coffee Table", fill="black")

class Chair(Furniture):
    def __init__(self, width: float, height:float, position: Vector2D = Vector2D(0, 0), rotation = 0):
        super().__init__(BoundingBox(width=width, height=height, position=position, rotation=rotation))

    def draw(self):
        self.bounding_box.draw(fill_color=CHAIR_COLOR, show_direction=True)
        canvas.create_text(self.bounding_box.position.x, self.bounding_box.position.y, text="Chair", fill="black")

class TV(Furniture):
    def __init__(self, width: float, height:float, position: Vector2D = Vector2D(0, 0), rotation = 0):
        super().__init__(BoundingBox(width=width, height=height, position=position, rotation=rotation))

    def draw(self):
        self.bounding_box.draw(fill_color=TV_COLOR, show_direction=True)
        canvas.create_text(self.bounding_box.position.x, self.bounding_box.position.y, text="TV", fill="black")

class Lamp(Furniture):
    def __init__(self, width: float, height:float, position: Vector2D = Vector2D(0, 0), rotation = 0):
        super().__init__(BoundingBox(width=width, height=height, position=position, rotation=rotation))

    def draw(self):
        self.bounding_box.draw(fill_color=LAMP_COLOR)
        canvas.create_text(self.bounding_box.position.x, self.bounding_box.position.y, text="Lamp", fill="black")


class Area:
    def __init__(self, priority: int, name: str, children: List[Furniture] = [], fill_color: str = "white"):
        self.priority = priority
        self.name = name
        self.children = children
        self.fill_color = fill_color
        self.calculate_bounding_box()

    def add_child(self, furniture: Furniture):
        self.children.append(furniture)
    def calculate_bounding_box(self):
        if len(self.children) == 0:
            self.bounding_box = BoundingBox(width=0, height=0)
            return

        max_x, min_x, max_y, min_y = 0, CANVAS_WIDTH, 0, CANVAS_HEIGHT
        for child in self.children:
            child_bb = child.bounding_box
            max_x = max(max_x, child_bb.top_right.x, child_bb.bottom_right.x, child_bb.top_left.x, child_bb.bottom_left.x)
            min_x = min(min_x, child_bb.top_right.x, child_bb.bottom_right.x, child_bb.top_left.x, child_bb.bottom_left.x)
            max_y = max(max_y, child_bb.top_right.y, child_bb.bottom_right.y, child_bb.top_left.y, child_bb.bottom_left.y)
            min_y = min(min_y, child_bb.top_right.y, child_bb.bottom_right.y, child_bb.top_left.y, child_bb.bottom_left.y)

        width_px = max_x - min_x
        height_px = max_y - min_y
        width = width_px / METER_TO_PIXELS
        height = height_px / METER_TO_PIXELS
        position = Vector2D(min_x + width_px / 2, min_y + height_px / 2)

        self.bounding_box = BoundingBox(width=width, height=height, position=position)

    def draw(self):
        self.bounding_box.draw(fill_color=self.fill_color)
        for child in self.children:
            child.draw()


class Room:
    # width and height are in meters
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.center_point = Vector2D(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)
        self.bounding_box = BoundingBox(width=self.width, height=self.height, position=self.center_point)

        self.walls: List[Wall] = [
            Wall(position=Utils.lerp(self.bounding_box.top_left, self.bounding_box.top_right, 0.5),
                 length=Utils.distance_to(self.bounding_box.top_left, self.bounding_box.top_right),
                 rotation=0),
            Wall(position=Utils.lerp(self.bounding_box.top_right, self.bounding_box.bottom_right, 0.5),
                 length=Utils.distance_to(self.bounding_box.top_right, self.bounding_box.bottom_right),
                 rotation=math.pi/2),
            Wall(position=Utils.lerp(self.bounding_box.bottom_right, self.bounding_box.bottom_left, 0.5),
                 length=Utils.distance_to(self.bounding_box.bottom_right, self.bounding_box.bottom_left),
                 rotation=0),
            Wall(position=Utils.lerp(self.bounding_box.bottom_left, self.bounding_box.top_left, 0.5),
                 length=Utils.distance_to(self.bounding_box.bottom_left, self.bounding_box.top_left),
                 rotation=math.pi/2)
        ]

        self.doors: List[Door] = []
        self.windows: List[Window] = []
        self.furnitures = []
        self.areas = []


    def draw_room(self):
        canvas.create_rectangle(self.bounding_box.top_left.x, self.bounding_box.top_left.y, self.bounding_box.bottom_right.x, self.bounding_box.bottom_right.y, fill=ROOM_COLOR)
        for wall in self.walls:
            wall.draw()

        for door in self.doors:
            door.draw()

        for window in self.windows:
            window.draw()

        for area in self.areas:
            area.draw()

        for furniture in self.furnitures:
            furniture.draw()

    def add_door(self, door: Door):
        self.doors.append(door)

    def add_window(self, window: Window):
        self.windows.append(window)

    def add_furniture(self, furniture: Furniture):
        self.furnitures.append(furniture)

    def add_area(self, area: Area):
        self.areas.append(area)


class Utils:
    @staticmethod
    def distance_to(p1: Vector2D, p2: Vector2D):
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5

    @staticmethod
    def lerp(p1: Vector2D, p2: Vector2D, a: float):
        #Perform linear interpolation for x between (x1,y1) and (x2,y2)
        return p1 * (1 - a) + p2 * a
    @staticmethod
    def midpoint(p1: Vector2D, p2: Vector2D):
        return Vector2D((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

master_window = Tk()
canvas = Canvas(master_window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack(side="bottom", fill="both", expand=True)
#canvas.create_line(0, y, canvas_width, y)

# Create a room
my_room = Room(width=10, height=5)
window1 = Window(attached_wall=my_room.walls[0], length=200, wall_placement=0.2, rotation=0)
window2 = Window(attached_wall=my_room.walls[1], length=100, wall_placement=0.5, rotation=math.pi/2)
window3 = Window(attached_wall=my_room.walls[1], length=100, wall_placement=0.8, rotation=math.pi/2)
door1 = Door(attached_wall=my_room.walls[2], length=100, wall_placement=0.5, rotation=0)

room_box = my_room.bounding_box

# Add some furniture
sofa1_position = room_box.top_left + Vector2D(250, 250)
sofa1 = Sofa(width=2, height=1, position=sofa1_position, rotation=math.pi*3/2)
sofa2_position = sofa1_position + Vector2D(-120, -150)
sofa2 = Sofa(width=1, height=1, position=sofa2_position, rotation=math.pi)
sofa3_position = sofa1_position + Vector2D(-120, 150)
sofa3 = Sofa(width=1, height=1, position=sofa3_position, rotation=0)

coffee_table_position = room_box.top_left + Vector2D(130, 250)
coffee_table1 = CoffeeTable(width=1.6, height=0.8, position=coffee_table_position, rotation=math.pi/2)
tv_position = room_box.top_left + Vector2D(25, 250)
tv1 = TV(width=2, height=0.5, position=tv_position, rotation=math.pi/2)


table_position = room_box.position + Vector2D(250, 100)
table1 = Table(width=2, height=1, position=table_position, rotation=0)
chair1_position = table_position + Vector2D(50, 100)
chair1 = Chair(width=0.5, height=0.5, position=chair1_position, rotation=0)
chair3_position = table_position + Vector2D(50, -100)
chair3 = Chair(width=0.5, height=0.5, position=chair3_position, rotation=math.pi)
chai2_position = table_position + Vector2D(-50, -100)
chair2 = Chair(width=0.5, height=0.5, position=chai2_position, rotation=math.pi)
chair4_position = table_position + Vector2D(-50, 100)
chair4 = Chair(width=0.5, height=0.5, position=chair4_position, rotation=0)


# Create areas
living_area = Area(priority=1, name="Living Area", children=[sofa1, sofa2, sofa3, coffee_table1, tv1], fill_color=AREA_COLOR)
dining_area = Area(priority=2, name="Dining Area", children=[table1, chair1, chair2, chair3, chair4], fill_color="#aa3333")
# Add Furnitures to room
my_room.add_window(window1)
my_room.add_window(window2)
my_room.add_window(window3)
my_room.add_door(door1)
my_room.add_area(living_area)
my_room.add_area(dining_area)

my_room.draw_room()

mainloop()

exit()