import pygame


class GameButton:
    """Виджет кнопки, написанный для PyGame"""
    def __init__(self, screen: pygame.Surface, size: tuple[int, int]=(100, 50),
                 coors: tuple[int, int]=(0, 0), text: str='Button', border_radius: int=0,
                 color: str='white', bordercolor: str='black',
                 font: str="Roboto Condensed", font_size: int=50, text_color: str='black'):
        self.border_radius = border_radius
        self.screen = screen
        self.font_size = font_size
        self.font = font
        self.width, self.height = self.size = size
        self.x, self.y = self.coors = coors
        self.text = text
        self.text_color = pygame.Color(text_color)
        self.backgroundcolor = pygame.Color(color)
        self.bordercolor = pygame.Color(bordercolor)
        self.function = None
        self.is_visible = True
        self.font_set()
        self.update()

    def set_text(self, text: str) -> None:
        self.text = text
        self.font_set()

    def font_set(self) -> None:
        letter = pygame.font.SysFont(self.font, self.font_size).render(self.text,
                                                                       True, self.text_color, self.backgroundcolor)
        rect = letter.get_rect()
        while rect.height >= self.height - 2 or rect.width >= self.width - 2:
            self.font_size -= 1
            letter = pygame.font.SysFont(self.font, self.font_size).render(self.text,
                                                                           True, self.text_color, self.backgroundcolor)
            rect = letter.get_rect()

    def update(self) -> None:
        if self.is_visible:
            letter = pygame.font.SysFont(self.font, self.font_size).render(self.text,
                                                                           True, self.text_color, self.backgroundcolor)
            pygame.draw.rect(self.screen, self.bordercolor, (*self.coors, *self.size), border_radius=self.border_radius)
            t_x = (self.width - letter.get_width()) // 2 + self.x
            t_y = (self.height - letter.get_height()) // 2 + self.y
            self.screen.blit(letter, (t_x, t_y))

    def get_events(self, events: list[pygame.event.Event]) -> None:
        if self.is_visible:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x1, y1 = event.pos
                        if (self.x <= x1 <= self.x + self.width) and (self.y <= y1 <= self.y + self.height):
                            if self.function is not None:
                                self.function()

    def connect(self, function: callable) -> None:
        if callable(function):
            self.function = function
        else:
            raise TypeError

    def move(self, x: int, y: int) -> None:
        self.x, self.y = self.coors = [x, y]
        self.update()

    def set_visible(self, flag: bool=True) -> None:
        self.is_visible = flag


class GameSlider:
    '''Виджет слайдера, написанный для PyGame'''
    def __init__(self, screen: pygame.Surface, x: int=0, y: int=0, width: int=100, height: int=4,
                 value: int=0, max_value: int=100, min_value: int=0,
                 cickle_color='blue', color='white', bar_color='white'):
        self.screen = screen
        self.coors = self.x, self.y = x, y
        self.width = width
        self.height = height
        self.value = value
        self.max_value = max_value
        self.min_value = min_value
        self.len_del = self.width / (self.max_value - self.min_value)
        self.cickle_color = pygame.color.Color(cickle_color)
        self.color = pygame.color.Color(color)
        self.function = None
        self.drag = False
        self.is_visible = True
        self.bar_color = pygame.color.Color(bar_color)

    def update(self) -> None:
        if self.is_visible:
            pygame.draw.line(self.screen, self.bar_color, (self.x, self.y),
                             (self.x + (self.value - self.min_value) * self.len_del, self.y), self.height)
            pygame.draw.line(self.screen, self.color,
                             (self.x + (self.value - self.min_value) * self.len_del, self.y),
                             (self.x + self.width, self.y), self.height)
            pygame.draw.circle(self.screen, self.cickle_color,
                               (self.x + (self.value - self.min_value) * self.len_del,
                                self.y + (self.height // 2)), self.height + 4)

    def set_value(self, value: int) -> None:
        if self.min_value <= self.value <= self.max_value:
            self.value = value
            if self.function is not None:
                self.function(self.value)
            self.update()

    def get_events(self, events: list[pygame.event.Event]) -> None:
        if self.is_visible:
            center = self.x + (self.value - self.min_value) * self.len_del, self.y + (self.height // 2)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x1, y1 = event.pos
                    if (x1 - center[0]) ** 2 + (y1 - center[-1]) ** 2 <= (self.height + 4) ** 2:
                        self.drag = True
                if event.type == pygame.MOUSEMOTION:
                    if self.drag:
                        x = event.rel[0]
                        self.value += x / self.len_del
                        if self.value < self.min_value:
                            self.value = self.min_value
                        elif self.value > self.max_value:
                            self.value = self.max_value
                        if self.function is not None:
                            self.function(self.value)
                        self.update()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.drag = False

    def set_visible(self, flag: bool=True):
        self.is_visible = flag

    def connect(self, function: callable):
        if callable(function):
            self.function = function
        else:
            raise TypeError