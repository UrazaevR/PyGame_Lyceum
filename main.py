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
        self.atack_group = pygame.sprite.Group()
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
            x, y = random.randrange(10, self.width - 32, 15), random.randrange(10, self.height - 32, 15)
            while [x, y] in stars_coors:
                x, y = random.randrange(10, self.width - 32, 15), random.randrange(10, self.height - 32, 15)
            stars_coors.append([x, y])
            star = Star(load_image('img/Stars.png', resize=random.uniform(0.3, 0.8), colorkey=-1), 3, 1, x, y)
            self.stars.add(star)
        self.running = True
        self.playing = False
        self.player = None
        self.screens = {}
        self.btn_cont = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 20),
                                   'Continue the game!', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_play = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 100),
                                   'Play!', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_set = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 180),
                                  'Settings', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_set.connect(self.settings)
        self.btn_author = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 260),
                                     'Author', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_exit = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 340),
                                   'Exit', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_back = GameButton(self.win, (300, 60), ((self.width - 300) // 2, 340),
                                   'Back', 5, 'yellow', 'yellow', text_color='Red')
        self.btn_back.connect(self.back)
        self.music_volume = GameSlider(self.win, (self.width - 300) // 2, 100, 300, bar_color='red',
                                       value=int(read_set('music_volume')), color='yellow', cickle_color='red')
        self.sound_volume = GameSlider(self.win, (self.width - 300) // 2, 200, 300, bar_color='red',
                                       value=int(read_set('sound_volume')), color='yellow', cickle_color='red')
        self.music_volume.connect(self.change_music_volume)
        self.sound_volume.connect(self.change_sound_volume)
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
        self.screens['settings'].append(self.music_volume)
        self.screens['settings'].append(self.sound_volume)
        self.score = 0
        self.i = 0

    def play(self):
        self.score = 0
        self.player_and_enemy_group.empty()
        self.enemies.empty()
        self.atack_group.empty()
        self.player = Player(self, load_image('img/Player.png', -1, 2), 3, 1, (self.width - 128) // 2, self.height - 140)
        self.player_and_enemy_group.add(self.player)
        self.playing = True

    def settings(self):
        self.current_screen = 'settings'

    def back(self):
        self.current_screen = 'main'

    def game_continue(self):
        self.playing = True

    def change_music_volume(self, value):
        save_conf('music_volume', str(int(value)))

    def change_sound_volume(self, value):
        save_conf('sound_volume', str(int(value)))

    def get_music_volume(self) -> int:
        return int(read_set('music_volume'))

    def get_sound_volume(self) -> int:
        return int(read_set('sound_volume'))

    def pause(self):
        self.playing = False
        self.btn_cont.set_visible()

    def run(self):
        while self.running:
            self.i += 1
            if self.i == 1001:
                self.i = 0
            self.win.fill(pygame.Color('black'))
            if self.i % 12 == 0:
                self.stars.update()
            if self.playing and self.i % 33 == 0:
                met_coors = []
                for i in range(3 * (1 + self.score // 10000)):
                    x = random.randrange(15, self.width - 74, 10)
                    while x in met_coors:
                        x = random.randrange(15, self.width - 74, 10)
                    met_coors.append(x)
                    self.player_and_enemy_group.add(Meteor(self,
                                                           load_image(f'img'
                                                                      f'/Meteor{random.randint(1, 5)}.png', -1,
                                                                      random.uniform(1, 2)),
                                                           1, 1, x))
            if self.playing and self.i % 400 == 0 and self.score >= 2500:
                x = random.randint(40, self.width - 104)
                e = Enemy(self, load_image(f'img/Enemy_plane{random.randint(1, 3)}.png', -1, 2), 3, 1, x, 20)
                self.player_and_enemy_group.add(e)
                self.enemies.add(e)
            self.stars.draw(self.win)
            events = pygame.event.get()
            if not self.playing:
                for widget in self.screens[self.current_screen]:
                    widget.get_events(events)
                    widget.update()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
            if self.playing:
                if self.i % 6 == 0:
                    self.enemies.update(self.player.rect.centerx)
                if self.player.hp <= 0:
                    self.playing = False
                    self.btn_cont.set_visible(False)
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.pause()
                        if event.key == pygame.K_SPACE:
                            self.player.atack()
                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    if self.player.rect.x > 0:
                        self.player.update(-7, 0)
                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    if self.player.rect.x < self.width - self.player.rect.width:
                        self.player.update(7, 0)
                self.player_and_enemy_group.update()
                self.atack_group.update()
                self.atack_group.draw(self.win)
                self.player_and_enemy_group.draw(self.win)
                self.win.blit(self.font.render('Best Score', True, 'yellow'), (self.width - 185, 5))
                self.win.blit(self.font.render(read_set('best_score'), True, 'yellow'), (self.width - 150, 40))
                self.win.blit(self.font.render(str(self.score), True, 'yellow'), (self.width - 150, 70))
            FPS = int(clock.get_fps())
            self.win.blit(self.font.render(str(FPS), True, 'green'), (5, 5))
            if self.score > int(read_set('best_score')):
                save_conf('best_score', str(self.score))
            pygame.display.update()
            fps = 10 * (self.score / 1000 + 1)
            if fps > 60 or not self.playing:
                fps = 60
            clock.tick(int(fps))

    def kill(self):
        self.playing = False
        self.running = False
        pygame.quit()
        print('Удачного дня!')


if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except Exception as ex:
        print(ex)