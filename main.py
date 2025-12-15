from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
import random

# ---------------- SETTINGS ----------------
Window.size = (360, 640)

GRAVITY = -900
JUMP_FORCE = 320
PIPE_SPEED = 160
PIPE_GAP = 180
PIPE_WIDTH = 80


# ---------------- BIRD ----------------
class Bird(Image):
    velocity = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (60, 60)

    def update(self, dt):
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt
        return self.y <= 0

    def jump(self):
        self.velocity = JUMP_FORCE

    def hitbox(self):
        return (self.x + 8, self.y + 8, self.width - 16, self.height - 16)


# ---------------- PIPE ----------------
class Pipe(Image):
    def hitbox(self):
        return (self.x + 8, self.y + 8, self.width - 16, self.height - 16)


# ---------------- GAME ----------------
class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Background
        self.bg = Image(
            source="background.jpg",
            allow_stretch=True,
            keep_ratio=False
        )
        self.bg.size = Window.size
        self.add_widget(self.bg)

        # Sounds
        self.music = SoundLoader.load("music.mp3")
        self.hit_sound = SoundLoader.load("hit.wav")

        if self.music:
            self.music.loop = True
            self.music.volume = 0.5
            self.music.play()

        # Bird
        self.bird = Bird(source="bird.jpg")
        self.bird.pos = (80, Window.height / 2)
        self.add_widget(self.bird)

        # Score
        self.score = 0
        self.score_label = Label(
            text="0",
            font_size=40,
            pos=(Window.width / 2 - 10, Window.height - 80)
        )
        self.add_widget(self.score_label)

        # Game state
        self.pipes = []
        self.game_over = False

        self.label = Label(
            text="",
            font_size=32,
            center=(Window.width / 2, Window.height / 2),
            halign="center"
        )
        self.add_widget(self.label)

        Clock.schedule_interval(self.update, 1 / 60)
        Clock.schedule_interval(self.spawn_pipes, 2)

        Window.bind(on_touch_down=self.on_touch)

    # ---------------- PIPE SPAWN ----------------
    def spawn_pipes(self, dt):
        if self.game_over:
            return

        gap_center = random.randint(200, Window.height - 200)

        bottom = Pipe(source="pipe.jpg")
        bottom.size = (PIPE_WIDTH, gap_center - PIPE_GAP / 2)
        bottom.pos = (Window.width, 0)

        top = Pipe(source="pipe.jpg")
        top.size = (
            PIPE_WIDTH,
            Window.height - (gap_center + PIPE_GAP / 2)
        )
        top.pos = (Window.width, gap_center + PIPE_GAP / 2)
        top.flip_vertical = True

        self.add_widget(bottom)
        self.add_widget(top)

        self.pipes.append({
            "bottom": bottom,
            "top": top,
            "passed": False
        })

    # ---------------- COLLISION ----------------
    def collide(self, a, b):
        ax, ay, aw, ah = a.hitbox()
        bx, by, bw, bh = b.hitbox()

        return not (
            ax + aw < bx or
            ax > bx + bw or
            ay + ah < by or
            ay > by + bh
        )

    # ---------------- UPDATE ----------------
    def update(self, dt):
        if self.game_over:
            return

        if self.bird.update(dt):
            self.end_game()
            return

        for pipe in self.pipes:
            bottom = pipe["bottom"]
            top = pipe["top"]

            bottom.x -= PIPE_SPEED * dt
            top.x -= PIPE_SPEED * dt

            if self.collide(self.bird, bottom) or self.collide(self.bird, top):
                self.end_game()
                return

            if not pipe["passed"] and bottom.x + bottom.width < self.bird.x:
                pipe["passed"] = True
                self.score += 1
                self.score_label.text = str(self.score)

        self.pipes = [
            p for p in self.pipes
            if p["bottom"].x + p["bottom"].width > 0
        ]

    # ---------------- GAME OVER ----------------
    def end_game(self):
        self.game_over = True
        self.label.text = "GAME OVER\nTap to Restart"

        if self.music:
            self.music.stop()
        if self.hit_sound:
            self.hit_sound.play()

    def reset(self):
        self.clear_widgets()
        self.__init__()

    # ---------------- INPUT ----------------
    def on_touch(self, *args):
        if self.game_over:
            self.reset()
        else:
            self.bird.jump()


# ---------------- APP ----------------
class FlappyApp(App):
    def build(self):
        return Game()


if __name__ == "__main__":
    FlappyApp().run()
