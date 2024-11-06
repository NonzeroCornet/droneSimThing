import pygame
import json
import tkinter as tk
from tkinter import filedialog

pygame.init()

WIDTH = 1280
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Obstacle Course Maker")

BLUEPRINT_BLUE = (0, 61, 89)
GRID_COLOR = (41, 98, 125)
DETAIL_COLOR = (173, 216, 230)
TEXT_COLOR = (59, 94, 118)
TOOLBAR_BG = (0, 51, 79)
ICON_COLOR = (173, 216, 230)
RED_SQUARE = (255, 50, 50)
BLUE_SQUARE = (50, 50, 255)

GRID_SIZE = 20
MAJOR_GRID_SIZE = 100

TOOLBAR_WIDTH = 40
ICON_SIZE = 30
ICON_PADDING = 5
TOOLBAR_TOP_PADDING = 50
EXPORT_ICON_Y = 250

level = {
    "markers": [],
    "circles": [],
    "lines": [],
}
deleting = False

isDragging = False


def save_json_file(data):

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        initialfile="Untitled.json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Export Obstacle Course",
    )

    if file_path:
        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
            print(f"File saved as {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")


def load_json_file():

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Select JSON File",
    )

    if file_path:
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            print(f"File loaded successfully from {file_path}")
            return data
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    else:
        print("No file selected.")
        return None


icon_areas = [
    pygame.Rect(0, TOOLBAR_TOP_PADDING - 10, TOOLBAR_WIDTH, ICON_SIZE),
    pygame.Rect(
        0, TOOLBAR_TOP_PADDING + ICON_SIZE + ICON_PADDING, TOOLBAR_WIDTH, ICON_SIZE
    ),
    pygame.Rect(
        0,
        (TOOLBAR_TOP_PADDING + 2 * (ICON_SIZE + ICON_PADDING)) - 10,
        TOOLBAR_WIDTH,
        ICON_SIZE,
    ),
    pygame.Rect(
        0,
        TOOLBAR_TOP_PADDING + 3 * (ICON_SIZE + ICON_PADDING),
        TOOLBAR_WIDTH,
        ICON_SIZE,
    ),
    pygame.Rect(
        0,
        TOOLBAR_TOP_PADDING + 4 * (ICON_SIZE + ICON_PADDING),
        TOOLBAR_WIDTH,
        ICON_SIZE,
    ),
]

font = pygame.font.SysFont("arial", 14)


class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.dragging_position = False
        self.dragging_radius = False

    def draw(self, screen):
        pygame.draw.circle(screen, (81, 125, 0), (self.x, self.y), self.radius, 2)

    def update(self, pos, dragging):

        if self.dragging_position:
            self.x, self.y = pos
        elif self.dragging_radius:

            self.radius = max(
                5, int(((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5)
            )

    def check_drag(self, pos):
        global isDragging
        global level
        global deleting

        distance = ((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5
        if distance <= self.radius and not isDragging:
            if deleting:
                level["circles"].remove(self)
                deleting = False
            else:
                isDragging = True
            if distance >= self.radius - 5:
                self.dragging_radius = True
            else:
                self.dragging_position = True

    def release(self):
        global isDragging
        self.dragging_position = False
        self.dragging_radius = False
        isDragging = False


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.dragging_start = False
        self.dragging_end = False

    def draw(self, screen):
        pygame.draw.line(
            screen, (191, 255, 0), (self.x1, self.y1), (self.x2, self.y2), 2
        )

    def update(self, pos, dragging):
        if self.dragging_start:
            self.x1, self.y1 = pos
        elif self.dragging_end:
            self.x2, self.y2 = pos

    def check_drag(self, pos):
        global isDragging
        global level
        global deleting
        if abs(self.x1 - pos[0]) < 5 and abs(self.y1 - pos[1]) < 5 and not isDragging:
            if deleting:
                level["lines"].remove(self)
                deleting = False
            else:
                isDragging = True
            self.dragging_start = True
        elif abs(self.x2 - pos[0]) < 5 and abs(self.y2 - pos[1]) < 5 and not isDragging:
            if deleting:
                level["lines"].remove(self)
                deleting = False
            else:
                isDragging = True
            self.dragging_end = True

    def release(self):
        global isDragging
        self.dragging_start = False
        self.dragging_end = False
        isDragging = False


class Marker:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.dragging = False

    def draw(self, screen):
        color = BLUE_SQUARE if self.type else RED_SQUARE
        pygame.draw.rect(screen, color, (self.x, self.y, 95, 95))

    def update(self, pos):
        if self.dragging:
            self.x, self.y = (pos[0] - 48, pos[1] - 48)

    def check_drag(self, pos):
        global isDragging
        if (
            self.x <= pos[0] <= self.x + 95
            and self.y <= pos[1] <= self.y + 95
            and not isDragging
        ):
            self.dragging = True
            isDragging = True

    def release(self):
        global isDragging
        self.dragging = False
        isDragging = False


def draw_grid():
    for x in range(TOOLBAR_WIDTH, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (TOOLBAR_WIDTH, y), (WIDTH, y), 1)
    for x in range(TOOLBAR_WIDTH, WIDTH, MAJOR_GRID_SIZE):
        pygame.draw.line(screen, DETAIL_COLOR, (x, 0), (x, HEIGHT), 2)
    for y in range(0, HEIGHT, MAJOR_GRID_SIZE):
        pygame.draw.line(screen, DETAIL_COLOR, (TOOLBAR_WIDTH, y), (WIDTH, y), 2)


def draw_measurement_text():

    text_surface = font.render("98 mm", True, TEXT_COLOR)

    text_x = TOOLBAR_WIDTH + 5
    text_y = 5

    screen.blit(text_surface, (text_x, text_y))

    bar_y = text_y + text_surface.get_height() + 2
    pygame.draw.line(screen, TEXT_COLOR, (text_x, bar_y), (text_x + 90, bar_y), 1)


def draw_toolbar():
    pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, TOOLBAR_WIDTH, HEIGHT))
    screen.blit(font.render("BDU", True, TEXT_COLOR), (7, 3))
    screen.blit(font.render("v1.0", True, TEXT_COLOR), (9, 17))

    current_y = TOOLBAR_TOP_PADDING
    pygame.draw.circle(screen, ICON_COLOR, (TOOLBAR_WIDTH // 2, current_y), 10, 2)
    current_y += ICON_SIZE + ICON_PADDING
    line_y = current_y
    pygame.draw.line(
        screen,
        ICON_COLOR,
        (ICON_PADDING, line_y),
        (TOOLBAR_WIDTH - ICON_PADDING, line_y + ICON_SIZE // 2),
        2,
    )
    current_y += ICON_SIZE + ICON_PADDING

    trash_top = current_y
    trash_width = 16
    trash_height = 20
    trash_color = ICON_COLOR
    if deleting:
        trash_color = (255, 0, 0)
    pygame.draw.rect(
        screen,
        trash_color,
        (TOOLBAR_WIDTH // 2 - trash_width // 2, trash_top, trash_width, trash_height),
        2,
    )
    pygame.draw.rect(
        screen,
        trash_color,
        (TOOLBAR_WIDTH // 2 - trash_width // 2 - 4, trash_top - 4, trash_width + 8, 4),
    )
    pygame.draw.rect(
        screen,
        trash_color,
        (TOOLBAR_WIDTH // 2 - trash_width // 2 + 2, trash_top - 6, trash_width - 4, 4),
    )
    current_y += ICON_SIZE + ICON_PADDING

    pygame.draw.polygon(
        screen,
        ICON_COLOR,
        [
            (TOOLBAR_WIDTH // 2, current_y),
            (TOOLBAR_WIDTH // 2 - 8, current_y + 10),
            (TOOLBAR_WIDTH // 2 + 8, current_y + 10),
        ],
    )
    pygame.draw.rect(
        screen, ICON_COLOR, (TOOLBAR_WIDTH // 2 - 5, current_y + 10, 10, 10)
    )
    current_y += ICON_SIZE + ICON_PADDING

    pygame.draw.polygon(
        screen,
        ICON_COLOR,
        [
            (TOOLBAR_WIDTH // 2, current_y + 20),
            (TOOLBAR_WIDTH // 2 - 8, current_y + 10),
            (TOOLBAR_WIDTH // 2 + 8, current_y + 10),
        ],
    )
    pygame.draw.rect(screen, ICON_COLOR, (TOOLBAR_WIDTH // 2 - 5, current_y, 10, 15))


SelectedTool = -1


def is_mouse_over_icon(pos):
    global SelectedTool
    s = 0
    for area in icon_areas:
        if area.collidepoint(pos):
            SelectedTool = s
            return True
        s += 1
    SelectedTool = -1
    return False


def main():
    running = True
    clock = pygame.time.Clock()
    global deleting
    global level
    level = {
        "markers": [Marker(43, 304, True), Marker(1144, 303, False)],
        "circles": [],
        "lines": [],
    }

    while running:
        mouse_pos = pygame.mouse.get_pos()

        if is_mouse_over_icon(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for marker in level["markers"][::-1]:
                    marker.check_drag(mouse_pos)
                for line in level["lines"][::-1]:
                    line.check_drag(mouse_pos)
                for circle in level["circles"][::-1]:
                    circle.check_drag(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                for circle in level["circles"]:
                    circle.release()
                for line in level["lines"]:
                    line.release()
                for marker in level["markers"]:
                    marker.release()
                if SelectedTool == 0:
                    level["circles"].append(Circle(100, 100, 100))
                elif SelectedTool == 1:
                    level["lines"].append(Line(100, 100, 200, 200))
                elif SelectedTool == 2:
                    deleting = not deleting
                elif SelectedTool == 3:
                    inp = load_json_file()
                    if inp:
                        new = {"markers": [], "circles": [], "lines": []}
                        for marker in inp["markers"]:
                            new["markers"].append(
                                Marker(marker[0], marker[1], marker[2])
                            )
                        for circle in inp["circles"]:
                            new["circles"].append(
                                Circle(circle[0], circle[1], circle[2])
                            )
                        for line in inp["lines"]:
                            new["lines"].append(
                                Line(line[0], line[1], line[2], line[3])
                            )
                        level = new
                elif SelectedTool == 4:
                    out = {"markers": [], "circles": [], "lines": []}
                    for marker in level["markers"]:
                        out["markers"].append([marker.x, marker.y, marker.type])
                    for circle in level["circles"]:
                        out["circles"].append([circle.x, circle.y, circle.radius])
                    for line in level["lines"]:
                        out["lines"].append([line.x1, line.y1, line.x2, line.y2])
                    save_json_file(out)
            elif event.type == pygame.MOUSEMOTION:
                for circle in level["circles"]:
                    circle.update(mouse_pos, pygame.mouse.get_pressed()[0])
                for line in level["lines"]:
                    line.update(mouse_pos, pygame.mouse.get_pressed()[0])
                for marker in level["markers"]:
                    marker.update(mouse_pos)

        screen.fill(BLUEPRINT_BLUE)
        draw_grid()
        draw_measurement_text()
        draw_toolbar()
        for circle in level["circles"]:
            circle.draw(screen)
        for line in level["lines"]:
            line.draw(screen)
        for marker in level["markers"]:
            marker.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
