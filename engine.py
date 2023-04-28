import pygame
import os
import random


def _not_looping(key: int):
    print(f"This function should not be called! Key: {key}")


class App:
    """Subclass this to make a game! Override function `ready` if you want something to run before the loop starts. Also, be sure to set the `loop_func` later."""
    def __init__(
        self, *, 
        title: str = "game",
        logo_filename: str = None,
        size: tuple = (960, 720),
        framerate: int = 60,
        show_fps: bool = True,
        run_dir: str = None, 
        asset_subdir: str = "assets", 
        image_subdir: str = "images",
        sound_subdir: str = "sounds",
        font_subdir: str = "fonts",
    ):
        self.title = title
        self.logo_filename = logo_filename
        self.width, self.height = self.size = size
        self.framerate = framerate
        self.show_fps = show_fps

        if run_dir:
            if os.path.isdir(run_dir):
                self.run_dir = run_dir
            else:
                raise FileNotFoundError("Provided `run_dir` does not exist")
        else:
            self.run_dir = os.path.dirname(__file__)

        self.asset_dir = os.path.join(self.run_dir, asset_subdir)

        self.image_subdir = image_subdir
        self.sound_subdir = sound_subdir
        self.font_subdir = font_subdir

        self.texts = []
        self.blits = []

        # used for string-referencing scenes and sounds that have not been initialized yet
        self.scenes = {}
        self.sounds = {}

        self.first_scene = None # YOU NEED TO SET THIS!

        self.current_bgm = None

        self.SCENE_QUIT = SceneQuit(self)
        self.scenes["QUIT"] = self.SCENE_QUIT

        self.loop_func = _not_looping

    def get_asset(self, *relative_path):
        return os.path.join(self.asset_dir, *relative_path)
    
    def load_image(self, filename: str) -> pygame.Surface:
        return pygame.image.load(os.path.join(self.asset_dir, self.image_subdir, filename))

    def load_font(self, filename: str, size: int = 50) -> pygame.font.Font:
        return pygame.font.Font(os.path.join(self.asset_dir, self.font_subdir, filename), size)
    
    def load_sound(self, filename: str, name: str = None, *, vol: float = None) -> pygame.mixer.Sound:
        sound = pygame.mixer.Sound(os.path.join(self.asset_dir, self.sound_subdir, filename))
        if name: self.sounds[name] = sound
        if vol: sound.set_volume(vol)
        return sound

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key:
                    return event.key

    def text(self, content: str, color: tuple = None, background: tuple = None, font: pygame.font.Font = None, persist: bool = True):
        for text in self.texts:
            if text.content == content and ((not color) or text.color == color) and ((not background) or text.background == background) and ((not font) or text.font == font):
                return text
            
        new_text = Text(self, content, color=color, background=background, font=font)
        if persist:
            self.texts.append(new_text)
        return new_text

    def get_sound(self, sound):
        if isinstance(sound, pygame.mixer.Sound):
            return sound

        elif isinstance(sound, str):
            if sound in self.sounds:
                return self.sounds[sound]
            else:
                raise Exception(f"Sound '{sound}' not found in `sounds`")

        else:
            raise TypeError(f"Argument for `get_sound` must be of type `str` or `pygame.mixer.Sound`, not '{type(sound)}' (you said '{sound}')")

    def play_music(self, sound):
        sound = self.get_sound(sound)
        if isinstance(self.current_bgm, pygame.mixer.Sound):
            self.current_bgm.stop()
        self.current_bgm = sound
        sound.play(-1)

    def play_scene(self, scene, ready: bool = True):
        if isinstance(scene, str):
            if scene in self.scenes:
                scene = self.scenes[scene]
            else:
                raise Exception(f"Scene '{scene}' not found in `scenes`")
        
        if isinstance(scene, Scene):
            if ready:
                scene.ready()

            self.loop_func = scene.loop

        else:
            raise TypeError(f"Argument for `play_scene` must be of type `str` or `Scene`, not '{type(scene)}' (you said '{scene}')")

    def ready(self):
        """Override this function with your game's init stuff"""
        pass

    def opt_quit(self, key):
        self.running = False

    def run(self):
        """This starts the game, DO NOT override this function!"""
        pygame.init()
        pygame.mixer.init()

        # init default assets
        self.font_main = self.font_default = pygame.font.Font(None, 42)

        if self.logo_filename:
            self.logo = self.load_image(self.logo_filename)
            pygame.display.set_icon(self.logo)
            pygame.display.set_caption(self.title)
     
        # oh lol!
        self.ready()

        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

        self.running = True

        self.play_scene(self.first_scene)

        # GAME LOOP
        while self.running:
            key = self.check_events()

            self.loop_func(key)

            if self.show_fps:
                fps = int(self.clock.get_fps())
                color = tuple([random.randint(0, 255) for _ in range(3)])
                fps_text = self.font_main.render(str(fps), True, color, (0, 0, 0))
                self.screen.blit(fps_text, (5, 5))

            self.clock.tick(self.framerate)
            pygame.display.flip()


class Scene:
    """Subclass this to make a scene. Override `ready` and `loop`."""
    def __init__(self, app: App, name: str = None):
        self.app = app

        # this stores the object inside the App's scene list, allowing it to be accessed as a string, meaning no errors unless you code it wrong!
        if name: self.app.scenes[name] = self

        self.initialized = False

    def ready(self):
        """Override this function with your Scene's init process"""
        pass

    def loop(self, key: int):
        """Override this function with your Scene's loop, including argument `key` of type `int`"""
        pass


class Menu(Scene):
    def __init__(
        self, app: App, name: str, names: tuple[str], scenes: tuple[str|Scene], *, 
        sound_change: pygame.mixer.Sound = None, sound_select: pygame.mixer.Sound = None, sound_exit: pygame.mixer.Sound = None, 
        key_forward: int|tuple[int] = pygame.K_DOWN, key_backward: int|tuple[int] = pygame.K_UP, key_select: int|tuple[int] = pygame.K_RETURN, 
        key_exit: int|tuple[int] = None, parent: str|Scene = None
    ):
        super().__init__(app, name)

        self.names = names
        self.scenes = scenes
        self.sound_change = sound_change
        self.sound_select = sound_select
        self.sound_exit = sound_exit
        self.key_forward = key_forward
        self.key_backward = key_backward
        self.key_select = key_select
        self.key_exit = key_exit
        self.parent = parent

        if len(self.names) != len(self.scenes):
            raise Exception("`names` and `scenes` must be tuples of the same length")

    def ready(self):
        """Don't override this unless you know what you're doing!"""
        self.selected = 0

    def loop(self, key: int):
        """Don't override this unless you know what you're doing!"""
        if key == self.key_forward: 
            if self.sound_change:
                self.app.get_sound(self.sound_change).play()
            
            self.selected += 1

        elif key == self.key_backward:
            if self.sound_change:
                self.app.get_sound(self.sound_change).play()
            
            self.selected -= 1

        elif key == self.key_select:
            if self.sound_select:
                self.app.get_sound(self.sound_select).play()
            
            self.app.play_scene(self.scenes[self.selected])
            self.selected = 0

        elif key == self.key_exit and self.parent:
            if self.sound_exit:
                self.app.get_sound(self.sound_exit).play()
            
            self.app.play_scene(self.parent)
            self.selected = 0

        if self.selected > len(self.names) - 1:
            self.selected = 0
        elif self.selected < 0:
            self.selected = len(self.names) - 1

        self.render()

    def render(self):
        """Override this to render the menu, or leave as default"""
        self.app.screen.fill((250, 250, 250))

        for i in range(len(self.names)):
            if i == self.selected:
                color = (0, 150, 40)
            else:
                color = (0, 0, 0)

            text = self.app.text(self.names[i], color=color)
            text.blit((20, 20))


class SceneQuit(Scene):
    def __init__(self, app: App):
        self.app = app

    def loop(self):
        self.app.running = False


class Positional:
    """Class used for items that have their own x and y positions"""
    def __init__(self, app: App, *, pos: tuple = (1, 1)):
        # if isinstance(app, Scene):
        #     app = app.app
        # ^^^ this might be too nice, keep it commented for now
        
        self.app = app
        self.x, self.y = pos

    def blit(self, pos: tuple = None):
        """Blits the Positional object to the screen where it is"""
        if not pos:
            pos = self.x, self.y
        self.app.screen.blit(self.object, pos)


class Text(Positional):
    """Text object that can be reused"""
    def __init__(self, app: App, content: str, *, pos: tuple = (1, 1), color: tuple = None, background: tuple = None, font: pygame.font.Font = None, antialias: bool = True):
        super().__init__(app, pos=pos)

        if not color:
            color = (30, 10, 100)

        self.content = content
        self.color = color
        self.background = background

        if font:
            self.font = font
        else:
            self.font = self.app.font_main

        self.object = self.font.render(self.content, antialias, self.color, self.background)


class Sprite(Positional):
    """Sprites have their own x and y positions and have a function to limit them to the screen edges"""
    def  __init__(self, app: App, *, image: str, pos: tuple = (1, 1)):
        super().__init__(app, pos=pos)

        self.object = self.image = self.app.load_image(image)

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.size = self.width, self.height

        self.max_x = self.app.width - self.width
        self.max_y = self.app.height - self.height

    def restrict(self):
        """If the Sprite has gone beyond the screen edges, teleport it back to the edge"""
        if self.x < 0:
            self.x = 0
        elif self.x > self.max_x:
            self.x = self.max_x

        if self.y < 0:
            self.y = 0
        elif self.y > self.max_y:
            self.y = self.max_y


class Projectile(Sprite):
    """Projectiles are Sprites that move on their own, with the `velocity` parameter"""
    def __init__(self, app: App, *, image: str, pos: tuple = (1, 1), velocity: tuple = (0, 0), bounce: bool = False):
        super().__init__(app, image=image, pos=pos)

        self.vel_x, self.vel_y = velocity
        self.vel_x_start, self.vel_y_start = self.vel_x, self.vel_y
        self.bounce = bounce

    def step(self):
        """Moves the Projectile in a step using its `velocity`"""
        self.x += self.vel_x
        self.y += self.vel_y

        if self.bounce:
            self.restrict()

            if self.x == 0:
                self.vel_x = abs(self.vel_x)
            elif self.x == self.max_x:
                self.vel_x = -abs(self.vel_x)

            if self.y == 0:
                self.vel_y = abs(self.vel_y)
            elif self.y == self.max_y:
                self.vel_y = -abs(self.vel_y)

        else:
            if self.x > self.max_x+5 or self.x < -self.width-5 or self.y > self.max_y+5 or self.y < -self.height-5:
                del self