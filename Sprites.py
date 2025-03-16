import pygame
import os
import random


def load_image(name: str, colorkey=None, resize: float=1.0) -> pygame.Surface | pygame.SurfaceType:
    """Функция для загрузки изображения взятая из учебника с некоторыми доработками"""
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        quit(0)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    image = pygame.transform.scale(image, (image.get_width() * resize, image.get_height() * resize))
    return image


class Border(pygame.sprite.Sprite):
    """Класс границ, взят из учебника"""
    def __init__(self, game, x1: int, y1: int, x2: int, y2: int):
        super().__init__()
        if x1 == x2:  # вертикальная стенка
            self.add(game.vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(game.horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Star(pygame.sprite.Sprite):
    """Спрайт звезды для заднего фона игры"""
    def __init__(self, sheet: pygame.Surface | pygame.SurfaceType, columns: int, rows: int, x: int, y: int):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.rect = self.rect.move(x, y)
        self.update()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        if self.cur_frame != len(self.frames) - 1:
            self.cur_frame += 1
        else:
            self.cur_frame = 0


class Lazer(pygame.sprite.Sprite):
    """Класс реализующий выстрелы игроков и врагов"""
    def __init__(self, game, sheet: pygame.Surface | pygame.SurfaceType, columns: int, rows: int, x: int, y: int,
                 vec: str='up', host: str='player'):
        super().__init__()
        self.frames = []
        self.host = host
        self.game = game
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.vec = vec
        self.rect = self.rect.move(x, y)
        self.game.atack_group.add(self)
        self.update()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        if self.rect.y < 0:
            self.kill()
        for meteor in self.game.player_and_enemy_group:
            if isinstance(meteor, Meteor) and self.host == 'player':
                if pygame.sprite.collide_mask(self, meteor):
                    meteor.kill()
                    self.game.score += 100
                    self.kill()
            elif isinstance(meteor, Enemy) and self.host == 'player':
                if pygame.sprite.collide_mask(self, meteor):
                    meteor.hp -= 1
                    self.game.score += 75
                    self.kill()
            elif isinstance(meteor, Player) and self.host == 'enemy':
                if pygame.sprite.collide_mask(self, meteor):
                    meteor.hp -= 1
                    self.kill()
        if self.cur_frame != len(self.frames) - 1:
            self.cur_frame += 1
        else:
            self.cur_frame = 0
        if self.vec == 'down':
            self.rect.y += 15
        else:
            self.rect.y -= 15


class Flame(pygame.sprite.Sprite):
    """Спрайт пламени позади звездолетов"""
    def __init__(self, game, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.game = game
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.rect = self.rect.move(x, y)
        self.update()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self, x=None, y=None):
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        if self.cur_frame != len(self.frames) - 1:
            self.cur_frame += 1
        else:
            self.cur_frame = 0
        if x is not None and y is not None:
            self.rect.x += x
            self.rect.y += y


class Player(pygame.sprite.Sprite):
    """Спрайт для отрисовки игрока и генерации лазеров при атаке"""
    def __init__(self, game, sheet: pygame.Surface | pygame.SurfaceType, columns: int, rows: int, x: int, y: int):
        super().__init__()
        self.frames = []
        self.game = game
        self.hp = 3
        self.lazer_sound = pygame.mixer.Sound('data/sounds/Laser_Shoot.wav')
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.rect = self.rect.move(x, y)
        self.flame = Flame(self.game, load_image('img/Flames.png', -1, 0.3), 12, 1, self.rect.centerx - 11, self.rect.centery + 48)
        self.game.player_and_enemy_group.add(self.flame)
        self.update()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def atack(self):
        """Функция отвечающая за атаку:
        Она создает объекты класса Lazer в количестве и положении зависящих от уровня звездолета"""
        lvl = self.game.score // 1000
        if lvl == 0:
            lvl = 1
        if lvl > 5:
            lvl = 5
        weapon_points = {1: [[self.rect.centerx, self.rect.centery]],
                         2: [[self.rect.centerx - 10, self.rect.centery], [self.rect. centerx + 10, self.rect.centery]],
                         3: [[self.rect.centerx, self.rect.centery], [self.rect.centerx - 20, self.rect.centery],
                             [self.rect.centerx + 20, self.rect.centery]],
                         4: [[self.rect.centerx - 7, self.rect.centery],
                             [self.rect.centerx + 7, self.rect.centery],
                             [self.rect.centerx - 20, self.rect.centery],
                             [self.rect.centerx + 20, self.rect.centery]],
                         5: [[self.rect.centerx, self.rect.centery],
                             [self.rect.centerx - 30, self.rect.centery],
                             [self.rect.centerx + 30, self.rect.centery],
                             [self.rect.centerx - 15, self.rect.centery],
                             [self.rect.centerx + 15, self.rect.centery]]}
        for point in weapon_points[lvl]:
            Lazer(self.game, load_image('img/Lazer.png', -1), 1, 1, point[0] - 6, point[-1])
        self.lazer_sound.set_volume(self.game.get_sound_volume() / 100)
        self.lazer_sound.play()

    def update(self, x=None, y=None):
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        if self.hp == 3:
            self.cur_frame = 0
        elif self.hp == 2:
            self.cur_frame = 1
        else:
            self.cur_frame = 2
        if x is not None and y is not None:
            self.rect.x += x
            self.rect.y += y
            self.flame.update(x, y)


class Enemy(pygame.sprite.Sprite):
    """Спрайт для отрисовки врага и генерации лазеров при атаке"""
    def __init__(self, game, sheet: pygame.Surface | pygame.SurfaceType, columns: int, rows: int, x: int, y: int):
        super().__init__()
        self.frames = []
        self.game = game
        self.hp = 3
        self.lazer_sound = pygame.mixer.Sound('data/sounds/Laser_Shoot.wav')
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.d_pos = [-2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2,
                      +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2, +2]
        self.cur_pos = 0
        self.lvl = random.randint(1, 3)
        self.rect = self.rect.move(x, y)
        self.flame = Flame(self.game, load_image('img/Flames_for_Enemy.png', -1, 0.3), 12, 1, self.rect.centerx - 11, self.rect.centery - 65)
        self.game.player_and_enemy_group.add(self.flame)
        self.update()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def atack(self):
        """Функция отвечающая за атаку:
        Она создает объекты класса Lazer в количестве и положении зависящих от уровня звездолета"""
        if self.lvl > 3:
            self.lvl = 3
        weapon_points = {1: [[self.rect.centerx, self.rect.centery]],
                         2: [[self.rect.centerx - 10, self.rect.centery], [self.rect. centerx + 10, self.rect.centery]],
                         3: [[self.rect.centerx, self.rect.centery], [self.rect.centerx - 20, self.rect.centery], [self.rect.centerx + 20, self.rect.centery]]}
        for point in weapon_points[self.lvl]:
            Lazer(self.game, load_image('img/Lazer.png', -1), 1, 1, point[0] - 6, point[-1], 'down', 'enemy')
        self.lazer_sound.set_volume(self.game.get_sound_volume() / 100)
        self.lazer_sound.play()

    def update(self, x=None):
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        if self.hp == 3:
            self.cur_frame = 0
        elif self.hp == 2:
            self.cur_frame = 1
        else:
            self.cur_frame = 2
        if self.hp <= 0:
            self.game.score += 200
            self.flame.kill()
            self.kill()
        if x is not None:
            if x - 15 <= self.rect.centerx <= x + 15:
                self.atack()
        self.rect.x += self.d_pos[self.cur_pos]
        self.flame.rect.x += self.d_pos[self.cur_pos]
        self.cur_pos += 1
        if self.cur_pos == len(self.d_pos):
            self.cur_pos = 0


class Meteor(pygame.sprite.Sprite):
    """Спрайт метеоритов"""
    def __init__(self, game, sheet: pygame.Surface | pygame.SurfaceType, columns: int, rows: int, x: int):
        super().__init__()
        self.frames = []
        self.game = game
        self.boom_sound = pygame.mixer.Sound('data/sounds/Explosion.wav')
        d_y, d_x = (random.randint(3, 7), random.randint(-2, 2))
        while d_y == 0:
            d_y = random.randint(3, 7)
        while d_x == 0:
            d_x = random.randint(-10, 10)
        self.vect = (d_x, d_y)
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.rect = self.rect.move(x, 5)
        self.update()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        for border in self.game.horizontal_borders:
            if pygame.sprite.collide_mask(self, border):
                self.kill()
        for border in self.game.vertical_borders:
            if pygame.sprite.collide_mask(self, border):
                self.kill()
        if self.cur_frame != len(self.frames) - 1:
            self.cur_frame += 1
        else:
            self.cur_frame = 0
        if pygame.sprite.collide_mask(self, self.game.player):
            self.game.player.hp -= 1
            self.boom_sound.set_volume(self.game.get_sound_volume() / 100)
            self.boom_sound.play()
            self.kill()
        self.rect.x += self.vect[0]
        self.rect.y += self.vect[-1]