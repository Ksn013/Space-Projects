import pygame
import math
import random
from datetime import datetime
import pytz
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Planetarium")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
GRID_COLOR = (50, 50, 80)
CONSTELLATION_COLOR = (100, 100, 255)


def equatorial_to_screen(ra, dec, time_offset=0):
    """Конвертирует экваториальные координаты в экранные"""
    current_time = datetime.now(pytz.utc)
    lst = (current_time.hour + current_time.minute / 60 + current_time.second / 3600 + time_offset) % 24
    ra_rad = math.radians((lst - ra) * 15)
    dec_rad = math.radians(dec)

    x = math.cos(dec_rad) * math.sin(ra_rad)
    y = -math.sin(dec_rad)

    scale = min(WIDTH, HEIGHT) / 2.5
    return (WIDTH / 2 + x * scale, HEIGHT / 2 + y * scale)


def load_stars():
    """Возвращает список звезд (name, ra, dec, mag, color)"""
    stars = [
        ("Sun", 0, 0, -26.74, YELLOW),
        ("Sirius", 6.75, -16.72, -1.46, WHITE),
        ("Vega", 18.62, 38.78, 0.03, WHITE),
        ("Arcturus", 14.26, 19.18, -0.05, (255, 165, 0)),
        ("Betelgeuse", 5.92, 7.41, 0.42, RED)
    ]

    for i in range(200):
        stars.append((f"Star_{i}", random.uniform(0, 24),
                      random.uniform(-90, 90), random.uniform(1.5, 6.0),
                      random.choice([WHITE, (255, 200, 150), BLUE])))
    return stars


def load_planets():
    """Возвращает список планет (name, ra, dec, mag, color, size, orbit_r, orbit_p)"""
    return [
        ("Mercury", 0, 0, -0.4, (200, 200, 200), 3, 0.4, 88),
        ("Venus", 0, 0, -4.6, (255, 255, 200), 5, 0.7, 225),
        ("Earth", 0, 0, -3.9, BLUE, 6, 1.0, 365),
        ("Mars", 0, 0, -2.0, RED, 4, 1.5, 687),
        ("Jupiter", 0, 0, -2.7, (255, 215, 150), 8, 5.2, 4333),
        ("Saturn", 0, 0, -0.2, (210, 180, 140), 7, 9.5, 10759)
    ]


def load_constellations():
    """Возвращает словарь созвездий {name: [(ra, dec), ...]}"""
    return {
        "Ursa Major": [
            (11.03, 61.75), (11.90, 53.69), (12.26, 57.03),
            (12.90, 55.96), (13.79, 49.31), (14.18, 51.68)
        ],
        "Orion": [
            (5.24, -8.20), (5.92, 7.41), (5.68, -1.94),
            (5.53, -5.91), (6.13, 9.65)
        ]
    }


class Camera:
    def __init__(self):
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def world_to_screen(self, x, y):
        return (
            WIDTH / 2 + (x - self.offset_x) * self.zoom,
            HEIGHT / 2 + (y - self.offset_y) * self.zoom
        )

    def zoom_to(self, x, y, zoom_level):
        self.offset_x = x
        self.offset_y = y
        self.zoom = zoom_level


def draw_earth(x, y, size):
    """Рисует модель Земли"""
    earth = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(earth, BLUE, (size, size), size)
    pygame.draw.ellipse(earth, GREEN, (size * 0.3, size * 0.4, size * 0.6, size * 0.3))
    pygame.draw.ellipse(earth, GREEN, (size * 0.6, size * 0.7, size * 0.3, size * 0.4))
    screen.blit(earth, (x - size, y - size))


def draw_grid():
    """Рисует координатную сетку"""
    for i in range(0, WIDTH, 50):
        pygame.draw.line(screen, GRID_COLOR, (i, 0), (i, HEIGHT), 1)
    for i in range(0, HEIGHT, 50):
        pygame.draw.line(screen, GRID_COLOR, (0, i), (WIDTH, i), 1)


#
def main():
    stars = load_stars()
    planets = load_planets()
    constellations = load_constellations()
    camera = Camera()
    
    time_offset = 0
    show_constellations = True
    show_planets = True
    show_grid = True
    earth_pos = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    time_offset -= 1
                elif event.key == K_RIGHT:
                    time_offset += 1
                elif event.key == K_c:
                    show_constellations = not show_constellations
                elif event.key == K_p:
                    show_planets = not show_planets
                elif event.key == K_g:
                    show_grid = not show_grid
                elif event.key == K_e and earth_pos:
                    camera.zoom_to(earth_pos[0], earth_pos[1], 20)
                elif event.key == K_r:
                    camera.zoom = 1.0
                    camera.offset_x = 0
                    camera.offset_y = 0
                elif event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEWHEEL:
                if event.y > 0:
                    camera.zoom *= 1.1
                else:
                    camera.zoom /= 1.1

        screen.fill(BLACK)

        if show_grid:
            draw_grid()

        for star in stars:
            name, ra, dec, mag, color = star
            x, y = equatorial_to_screen(ra, dec, time_offset)
            x, y = camera.world_to_screen(x - WIDTH / 2, y - HEIGHT / 2)
            size = max(1, int(10 / (mag + 5) * camera.zoom))

            if -100 < x < WIDTH + 100 and -100 < y < HEIGHT + 100:
                pygame.draw.circle(screen, color, (int(x), int(y)), size)

                if mag < 1 or camera.zoom > 2:
                    font = pygame.font.SysFont('Arial', max(12, int(14 * camera.zoom / 3)))
                    text = font.render(name, True, WHITE)
                    screen.blit(text, (x + size + 2, y - 10))

        if show_constellations:
            for name, points in constellations.items():
                screen_points = []
                for ra, dec in points:
                    x, y = equatorial_to_screen(ra, dec, time_offset)
                    x, y = camera.world_to_screen(x - WIDTH / 2, y - HEIGHT / 2)
                    screen_points.append((x, y))

                if len(screen_points) > 1:
                    pygame.draw.lines(screen, CONSTELLATION_COLOR, False, screen_points, 1)

                    if camera.zoom > 0.5 and screen_points:
                        font = pygame.font.SysFont('Arial', max(14, int(16 * camera.zoom / 2)))
                        text = font.render(name, True, CONSTELLATION_COLOR)
                        screen.blit(text, (screen_points[0][0] + 10, screen_points[0][1] - 15))

        if show_planets:
            for planet in planets:
                name, ra, dec, mag, color, size, orbit_r, orbit_p = planet

                days = (datetime.now().timetuple().tm_yday + time_offset * 24) % orbit_p
                angle = 2 * math.pi * days / orbit_p
                dynamic_ra = ra + orbit_r * math.cos(angle) * 5
                dynamic_dec = dec + orbit_r * math.sin(angle) * 3

                x, y = equatorial_to_screen(dynamic_ra, dynamic_dec, time_offset)
                x, y = camera.world_to_screen(x - WIDTH / 2, y - HEIGHT / 2)
                size_scaled = max(2, int(size * camera.zoom))

                if name == "Earth":
                    earth_pos = (x - WIDTH / 2, y - HEIGHT / 2)
                    if camera.zoom > 5:
                        draw_earth(x, y, size_scaled * 2)
                    else:
                        pygame.draw.circle(screen, color, (int(x), int(y)), size_scaled)
                else:
                    pygame.draw.circle(screen, color, (int(x), int(y)), size_scaled)

                if camera.zoom > 0.3:
                    font = pygame.font.SysFont('Arial', max(12, int(14 * camera.zoom / 2)))
                    text = font.render(name, True, WHITE)
                    screen.blit(text, (x + size_scaled + 5, y - 10))

        font = pygame.font.SysFont('Arial', 20)
        controls = [
            f"Time offset: {time_offset} hours (LEFT/RIGHT)",
            "C: Toggle constellations",
            "P: Toggle planets",
            "G: Toggle grid",
            "E: Find Earth",
            "R: Reset view",
            "ESC: Quit"
        ]

        for i, text in enumerate(controls):
            screen.blit(font.render(text, True, WHITE), (10, 10 + i * 25))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()

