import pygame
import engine
import random

# tutorial used: https://dr0id.bitbucket.io/legacy/pygame_tutorials.html
# this game is (c) 2023 by weirdcease

class MyBulletGame(engine.App):
    def __init__(self):
        super().__init__(
            title = "Das Cash Money Adventure",
            logo_filename = "catsmirk.png",
        )

    def ready(self):
        self.load_sound("bonk.mp3", "bonk", vol=0.1)
        self.load_sound("gong.mp3", "gong", vol=0.8)
        self.load_sound("menu.mp3", "menu")
        self.load_sound("cats.mp3", "cats")

        alagard = self.load_font("alagard.ttf")
        self.font_main = alagard


class MainMenu(engine.Menu):
    def __init__(self):
        super().__init__(
            game, "menu_main", ["New Game", "Options", "Music Room", "Cat Room", "Quit"], ["stage1", None, None, "cats", "QUIT"], 
            sound_change="bonk", sound_select="gong",
        )

    def ready(self):
        self.app.play_music("menu")

    def render(self):
        self.app.screen.fill((64, 0, 0))
        self.app.screen.fill((128, 0, 0), rect=(50, self.app.height-120, 200, 70))

        for i in range(len(self.names)):
            if i == self.selected:
                color = (30, 10, 150)
                background = (160, 0, 0)
            else:
                color = (250, 40, 5)
                background = None

            text = self.app.text(self.names[i], color=color, background=background)
            text.blit((70, 70 + 30 * i))


class Cats(engine.Scene):
    def __init__(self):
        super().__init__(game, "cats")

    def ready(self):
        for _ in range(200):
            x = random.randint(100, self.app.width-100)
            y = random.randint(100, self.app.height-100)
            vel_x = random.randint(-10, 10)
            vel_y = random.randint(-10, 10)

            projectile = engine.Projectile(self.app, image="catsmirk.png", pos=(x, y), velocity=(vel_x, vel_y), bounce=True)
            self.app.blits.append(projectile)

        self.app.play_music("cats")

    def loop(self, key: int):
        if key == pygame.K_ESCAPE:
            self.app.play_scene(main_menu)
            return

        self.app.screen.fill((64, 0, 0))

        for sprite in self.app.blits:
            if isinstance(sprite, engine.Projectile):
                sprite.step()

            sprite.blit()


class Stage1(engine.Scene):
    def __init__(self):
        super().__init__(game, "stage1")

    def ready(self):
        self.player = engine.Sprite(self.app, image="catsmirk.png", pos=(self.app.width//2, self.app.height//3))
        self.app.blits.append(self.player)
        self.app.play_music("gong")

    def loop(self, key: int):
        step = 10
        self.app.screen.fill((0, 15, 64))
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.player.y -= step
        if keys[pygame.K_DOWN]:
            self.player.y += step
        if keys[pygame.K_LEFT]:
            self.player.x -= step
        if keys[pygame.K_RIGHT]:
            self.player.x += step
        if keys[pygame.K_z]:
            bullet = engine.Bullet(self.app, self.player, image="catsmirk.png", velocity=(0, -10), damage=-1)
            self.app.blits.append(bullet)
            self.player.emit(bullet)
        if keys[pygame.K_ESCAPE]:
            self.app.play_scene(main_menu)
            return

        self.player.restrict()

        for item in self.app.blits:
            if isinstance(item, engine.Bullet):
                item.step()
                item.check()

            if hasattr(item, "blit"):
                item.blit()


game = MyBulletGame()
main_menu = MainMenu()
cats = Cats()
stage1 = Stage1()

game.first_scene = main_menu

if __name__=="__main__":
    game.run()