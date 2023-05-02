from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.config import Config
from kivy.core.window import Window
from random import random

from kivy.utils import rgba
import pygame
from pygame import mixer

# wave files used from PythonPiano script
Config.set('graphics', 'resizable', True)

sector_mapping = {
    "1": "C1",
    "2": "Db1",
    "3": "D1",
    "4": "Eb1",
    # fill in etc.
}

flat_and_sharp_mapping = {
    "Db": "C#",
    "Eb": "D#",
    # mappings to convert from flat to sharp 
}
class PianoKey(FloatLayout):
    def __init__(self, note, octave, white=True, **kwargs):
        super().__init__(**kwargs)
        self.white = white
        self.note = note
        with self.canvas:
            if (white):
                Color(rgba=(0, 0, 0, 1))
                self.rect = RoundedRectangle(radius=[10, 10, 10, 10],size=(1, 1), pos=(0,0))
                self.default_color = Color(1, 1, 1, 1)
                self.rect_color = Color(1, 1, 1, 1)
                self.border = RoundedRectangle(radius=[10, 10, 10, 10], size=(1, 1), pos=(0,0))
            else:
                Color(rgba=(0, 0, 0, 1))
                self.rect = RoundedRectangle(radius=[10, 10, 10, 10],size=(1, 1), pos=(0,0))
                self.default_color = Color(0, 0, 0, 1)
                self.rect_color = Color(0, 0, 0, 1)
                self.border = RoundedRectangle(radius=[10, 10, 10, 10], size=(1, 1), pos=(0, 0))

        if (white):
            self.add_widget(Label(text=note, pos_hint={"center_x": 0.5, "center_y": 0.12}, color=(0,0,0,1)))
        else:
            self.add_widget(Label(text=note, pos_hint = {"center_x": 0.5, "center_y": 0.12}, color=(1, 1, 1, 1)))
        self.bind(pos=self.update)
        self.bind(size=self.update)

        try:
            self.sound = mixer.Sound(f'assets/{note}{octave}.wav')   
        except:
            self.sound = mixer.Sound(f'assets/C1.wav')


    def update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.pos = (self.rect.pos[0]+1, self.rect.pos[1]+1)
        self.border.size = (self.rect.size[0]-4, self.rect.size[1]-3)

    def on_touch_down(self, touch):
        # can make this do other stuff later, use for testing right now
        if self.collide_point(*touch.pos):
            touch.grab(self)

            print(self.note)
            # if self.rect_color != self.default_color:
            #     self.rect_color = self.default_color
            # else:
            self.rect_color.rgb = (random(), random(), random(), 1)
            # probably messed up a little bit of the logic here             

            # can set a volume before playing (float between 0 to 1.0, using sound.set_volume())
            self.sound.set_volume(1.0)
            self.sound.play(0, 1000)
            return True
def makePiano():
    pass
class PianoBoard(RelativeLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # put these guys into an array? or manually instiate? 
        self.add_widget(PianoKey("C", 1, size_hint=(1/29, 1), pos_hint={"x":0/29}))
        self.add_widget(PianoKey("D", 1, size_hint=(1/29, 1), pos_hint={"x":1/29}))
        self.add_widget(PianoKey("E", 1, size_hint=(1/29, 1), pos_hint={"x":2/29}))
        self.add_widget(PianoKey("F", 1, size_hint=(1/29, 1), pos_hint={"x":3/29}))
        self.add_widget(PianoKey("G", 1, size_hint=(1/29, 1), pos_hint={"x":4/29}))
        self.add_widget(PianoKey("A", 1, size_hint=(1/29, 1), pos_hint={"x":5/29}))
        self.add_widget(PianoKey("B", 1, size_hint=(1/29, 1), pos_hint={"x":6/29}))

        self.add_widget(PianoKey("C", 2, size_hint=(1/29, 1), pos_hint={"x":7/29}))
        self.add_widget(PianoKey("D", 2, size_hint=(1/29, 1), pos_hint={"x":8/29}))
        self.add_widget(PianoKey("E", 2, size_hint=(1/29, 1), pos_hint={"x":9/29}))
        self.add_widget(PianoKey("F", 2, size_hint=(1/29, 1), pos_hint={"x":10/29}))
        self.add_widget(PianoKey("G", 2, size_hint=(1/29, 1), pos_hint={"x":11/29}))
        self.add_widget(PianoKey("A", 2, size_hint=(1/29, 1), pos_hint={"x":12/29}))
        self.add_widget(PianoKey("B", 2, size_hint=(1/29, 1), pos_hint={"x":13/29}))

        self.add_widget(PianoKey("C", 3, size_hint=(1/29, 1), pos_hint={"x":14/29}))
        self.add_widget(PianoKey("D", 3, size_hint=(1/29, 1), pos_hint={"x":15/29}))
        self.add_widget(PianoKey("E", 3, size_hint=(1/29, 1), pos_hint={"x":16/29}))
        self.add_widget(PianoKey("F", 3, size_hint=(1/29, 1), pos_hint={"x":17/29}))
        self.add_widget(PianoKey("G", 3, size_hint=(1/29, 1), pos_hint={"x":18/29}))
        self.add_widget(PianoKey("A", 3, size_hint=(1/29, 1), pos_hint={"x":19/29}))
        self.add_widget(PianoKey("B", 3, size_hint=(1/29, 1), pos_hint={"x":20/29}))

        self.add_widget(PianoKey("C", 4, size_hint=(1/29, 1), pos_hint={"x":21/29}))
        self.add_widget(PianoKey("D", 4, size_hint=(1/29, 1), pos_hint={"x":22/29}))
        self.add_widget(PianoKey("E", 4, size_hint=(1/29, 1), pos_hint={"x":23/29}))
        self.add_widget(PianoKey("F", 4, size_hint=(1/29, 1), pos_hint={"x":24/29}))
        self.add_widget(PianoKey("G", 4, size_hint=(1/29, 1), pos_hint={"x":25/29}))
        self.add_widget(PianoKey("A", 4, size_hint=(1/29, 1), pos_hint={"x":26/29}))
        self.add_widget(PianoKey("B", 4, size_hint=(1/29, 1), pos_hint={"x":27/29}))
        self.add_widget(PianoKey("C", 5, size_hint=(1/29, 1), pos_hint={"x":28/29}))

        self.add_widget(PianoKey("Db", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 1/58, "y": 0.37}))
        self.add_widget(PianoKey("Eb", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 3/58, "y": 0.37}))
        self.add_widget(PianoKey("Gb", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 7/58, "y": 0.37}))
        self.add_widget(PianoKey("Ab", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 9/58, "y": 0.37}))
        self.add_widget(PianoKey("Bb", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 11/58, "y": 0.37}))

        self.add_widget(PianoKey("Db", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 15/58, "y": 0.37}))
        self.add_widget(PianoKey("Eb", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 17/58, "y": 0.37}))
        self.add_widget(PianoKey("Gb", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 21/58, "y": 0.37}))
        self.add_widget(PianoKey("Ab", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 23/58, "y": 0.37}))
        self.add_widget(PianoKey("Bb", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 25/58, "y": 0.37}))

        self.add_widget(PianoKey("Db", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 29/58, "y": 0.37}))
        self.add_widget(PianoKey("Eb", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 31/58, "y": 0.37}))
        self.add_widget(PianoKey("Gb", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 35/58, "y": 0.37}))
        self.add_widget(PianoKey("Ab", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 37/58, "y": 0.37}))
        self.add_widget(PianoKey("Bb", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 39/58, "y": 0.37}))

        self.add_widget(PianoKey("Db", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 43/58, "y": 0.37}))
        self.add_widget(PianoKey("Eb", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 45/58, "y": 0.37}))
        self.add_widget(PianoKey("Gb", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 49/58, "y": 0.37}))
        self.add_widget(PianoKey("Ab", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 51/58, "y": 0.37}))
        self.add_widget(PianoKey("Bb", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 53/58, "y": 0.37}))


# could eventually make this into a thing to flip it to flats if wanted 
# smoother way to instantiate? 
class PianoApp(App):
    def build(self):
        pygame.init()
        mixer.set_num_channels(50)
        #Window.clearcolor = rgba("#570861")
        Window.size = (1000, 700)
        return PianoBoard(size_hint=(1, 0.5))

if __name__ == "__main__":
    white_sounds = []

    PianoApp().run()