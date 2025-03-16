from config_manager import *
from PyGameWidgets import *
from Sprites import *

pygame.init()
clock = pygame.time.Clock()
infoObject = pygame.display.Info()


class Game:
    """Основной класс игры, в нем находится главный игровой цикл (функция run) и различные побочные функции,
    которые по сути можно было определить вне класса в мэйне
    P.S. Очень люблю библиотеку PyQt, поэтому попытался привести PyGame к чему-то подобному,
    отсюда схожые методы у виджетов и впринципе обилие классов"""

    def __init__(self):
        pygame.init()
        self.all_sprites = pygame.sprite.Group()
        self.vertical_borders = pygame.sprite.Group()
        self.horizontal_borders = pygame.sprite.Group()
        self.player_and_enemy_group = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.attack_group = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        pygame.display.set_caption('Galaxy Game')
        self.font = pygame.font.SysFont("Roboto Condensed", 50)
        self.size = self.width, self.height = infoObject.current_w, infoObject.current_h
        self.win = pygame.display.set_mode(self.size)
        self.win.fill(pygame.Color('black'))
        Border(self, -100, 1, infoObject.current_w + 100, 1)
        Border(self, -100, infoObject.current_h + 100, infoObject.current_w + 100, infoObject.current_h + 100)
        Border(self, -100, 1, -100, infoObject.current_h + 100)
        Border(self, infoObject.current_w + 100, 1, infoObject.current_w + 100, infoObject.current_h + 100)
        stars_coors = []
        for i in range(170):
            x, y = (random.randrange(10, self.width - 32, 15),
                    random.randrange(10, self.height - 32, 15))
            while [x, y] in stars_coors:
                x, y = (random.randrange(10, self.width - 32, 15),
                        random.randrange(10, self.height - 32, 15))
            stars_coors.append([x, y])
            star = Star(load_image('img/Stars.png', resize=random.uniform(0.3, 0.8), colorkey=-1),
                        3, 1, x, y)
            self.stars.add(star)
        self.running = True
        self.playing = False
        self.player = None
        self.screens = {}
        self.btn_cont = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 20),
                                   'Continue the game!', 5, 'yellow', 'yellow',
                                   text_color='Red')
        self.btn_play = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 100),
                                   'Play!', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_set = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 180),
                                  'Settings', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_set.connect(self.settings)
        self.btn_author = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 260),
                                     'Author', 5, 'yellow', 'yellow',
                                     text_color='Red')
        self.btn_exit = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 340),
                                   'Exit', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_back = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 440),
                                   'Back', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_back.connect(self.back)
        self.music_label = GameLabel(self.win, (300, 50), ((self.width - 300) // 2, 100),
                                     text=f'Music volume: {self.get_music_volume()}', color='yellow')
        self.music_volume = GameSlider(self.win, (self.width - 300) // 2, 170, 300, bar_color='red',
                                       value=int(read_set('music_volume')), color='yellow', cickle_color='red')
        self.sound_label = GameLabel(self.win, (300, 50), ((self.width - 300) // 2, 240),
                                     text=f'Sound volume: {self.get_sound_volume()}', color='yellow')
        self.sound_volume = GameSlider(self.win, (self.width - 300) // 2, 310, 300, bar_color='red',
                                       value=int(read_set('sound_volume')), color='yellow', cickle_color='red')
        self.music_volume.connect(self.change_music_volume)
        self.sound_volume.connect(self.change_sound_volume)
        self.music = pygame.mixer.Sound('data/sounds/retro-fon.mp3')
        self.music.set_volume(self.get_music_volume() / 100)
        self.music.play(loops=-1)
        self.btn_cont.set_visible(False)
        self.current_screen = 'main'
        self.btn_cont.connect(self.game_continue)
        self.btn_play.connect(self.play)
        self.btn_exit.connect(self.kill)
        self.screens['main'] = []
        self.screens['main'].append(self.btn_cont)
        self.screens['main'].append(self.btn_play)
        self.screens['main'].append(self.btn_set)
        self.screens['main'].append(self.btn_author)
        self.screens['main'].append(self.btn_exit)
        self.screens['settings'] = []
        self.screens['settings'].append(self.btn_back)
        self.screens['settings'].append(self.music_label)
        self.screens['settings'].append(self.music_volume)
        self.screens['settings'].append(self.sound_label)
        self.screens['settings'].append(self.sound_volume)
        self.score = 0

    def play(self) -> None:
        """Функция начала новой игры.
        Она очищает все группы спрайтов, обнуляет счет, спавнит игрока
        и устанавливает флаг игрового цикла в положение True"""
        self.score = 0
        self.player_and_enemy_group.empty()
        self.enemies.empty()
        self.attack_group.empty()
        self.player = Player(self, load_image('img/Player.png', -1, 2),
                             3, 1, (self.width - 128) // 2,
                             self.height - 140)
        self.player_and_enemy_group.add(self.player)
        self.playing = True

    def settings(self) -> None:
        """Кнопка переключения на экран настроек"""
        self.current_screen = 'settings'

    def back(self) -> None:
        """Кнопка возврата в главное меню"""
        self.current_screen = 'main'

    def game_continue(self) -> None:
        """Функция для продолжения игрового цикла"""
        self.playing = True

    def change_music_volume(self, value: float) -> None:
        """Функция для изменения значения громкости музыки и сохранения ее нового значения"""
        save_conf('music_volume', str(int(value)))
        self.music_label.set_text(f'Music volume: {int(value)}')
        self.music.set_volume(value / 100)

    def change_sound_volume(self, value: float) -> None:
        """Функция для изменения значения громкости звука и сохранения ее нового значения"""
        save_conf('sound_volume', str(int(value)))
        self.sound_label.set_text(f'Sound volume: {int(value)}')

    def get_music_volume(self) -> int:
        """Функция, которая возвращает текущее значение громкости музыки"""
        return int(read_set('music_volume'))

    def get_sound_volume(self) -> int:
        """Функция, которая возвращает текущее значение громкости звука"""
        return int(read_set('sound_volume'))

    def pause(self) -> None:
        """Функция, которая ставит игровой цикл на паузу и делает кнопку 'Продолжить игру' видимой"""
        self.playing = False
        self.btn_cont.set_visible()

    def meteor_spawn(self) -> None:
        """Функция спавнит некоторое количество метеоритов, в зависимости от числа очков игрока"""
        met_coors = []
        for i in range(3 * (1 + self.score // 10000)):
            x = random.randrange(15, self.width - 74, 10)
            while x in met_coors:
                x = random.randrange(15, self.width - 74, 10)
            met_coors.append(x)
            self.player_and_enemy_group.add(
                Meteor(self, load_image(f'img/Meteor{random.randint(1, 5)}.png', -1,
                                        random.uniform(1, 2)), 1, 1, x))

    def enemy_spawn(self) -> None:
        """Функция спавнит врага в рандомной точке вверху экрана"""
        x = random.randint(40, self.width - 104)
        e = Enemy(self, load_image(f'img/Enemy_plane{random.randint(1, 3)}.png', -1, 2),
                  3, 1, x, 20)
        self.player_and_enemy_group.add(e)
        self.enemies.add(e)

    def run(self) -> None:
        """Основная функция класса Game
        Внутри находится основной цикл, в котором рисуется все приложение, а также главный игровой цикл"""
        METEOR_SPAWN_EVENT = pygame.USEREVENT + 1
        ENEMY_SPAWN_EVENT = pygame.USEREVENT + 2
        STARS_UPDATE_EVENT = pygame.USEREVENT + 3
        ENEMY_UPDATE_EVENT = pygame.USEREVENT + 4
        pygame.time.set_timer(METEOR_SPAWN_EVENT, max(250, int(-0.1 * self.score + 1000)))
        pygame.time.set_timer(ENEMY_SPAWN_EVENT, max(500, int(-0.8 * self.score + 10000)))
        pygame.time.set_timer(STARS_UPDATE_EVENT, 500)
        pygame.time.set_timer(ENEMY_UPDATE_EVENT, 200)
        while self.running:
            self.win.fill(pygame.Color('black'))
            self.stars.draw(self.win)
            events = pygame.event.get()
            if not self.playing:
                for widget in self.screens[self.current_screen]:
                    widget.get_events(events)
                    widget.update()
            for event in events:
                if event.type == STARS_UPDATE_EVENT:
                    self.stars.update()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
            if self.playing:
                if self.player.hp <= 0:
                    self.playing = False
                    self.btn_cont.set_visible(False)
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.pause()
                        if event.key == pygame.K_SPACE:
                            self.player.attack()
                    elif event.type == METEOR_SPAWN_EVENT:
                        self.meteor_spawn()
                    elif event.type == ENEMY_SPAWN_EVENT:
                        self.enemy_spawn()
                    elif event.type == ENEMY_UPDATE_EVENT:
                        self.enemies.update(self.player.rect.centerx)
                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    if self.player.rect.x > 0:
                        self.player.update(-7, 0)
                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    if self.player.rect.x < self.width - self.player.rect.width:
                        self.player.update(7, 0)
                self.player_and_enemy_group.update()
                self.attack_group.update()
                self.attack_group.draw(self.win)
                self.player_and_enemy_group.draw(self.win)
                self.win.blit(self.font.render('Best Score', True, 'yellow'),
                              (self.width - 185, 5))
                self.win.blit(self.font.render(read_set('best_score'), True, 'yellow'),
                              (self.width - 150, 40))
                self.win.blit(self.font.render(str(self.score), True, 'yellow'),
                              (self.width - 150, 70))
            FPS = int(clock.get_fps())
            self.win.blit(self.font.render(str(FPS), True, 'green'), (5, 5))
            if self.score > int(read_set('best_score')):
                save_conf('best_score', str(self.score))
            pygame.display.update()
            clock.tick(60)

    def kill(self) -> None:
        """Функция для выхода из игры в целом
        Останавливает все циклы и выходит из pygame"""
        self.playing = False
        self.running = False
        self.music.stop()
        pygame.quit()


if __name__ == '__main__':
    start_config()
    game = Game()
    try:
        game.run()
    except Exception as ex:
        print(ex)
