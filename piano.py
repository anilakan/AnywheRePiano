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

flat_and_sharp_mapping = {
    "Db": "C#",
    "Eb": "D#",
    # mappings to convert from flat to sharp 
}
class FakeSound():
    def __init__(self):
        pass

    def play(self, arg1, arg2):
        pass

    def set_volume(self, arg1):
        pass

class FakeKey(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note = None
        self.sound = FakeSound()

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
            # lol cop out except
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
            self.rect_color.rgb = (random(), random(), random(), random())
            # probably messed up a little bit of the logic here             

            # can set a volume before playing (float between 0 to 1.0, using sound.set_volume())
            self.sound.set_volume(1.0)
            self.sound.play(0, 1000)
            return True

class PianoBoard(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # put these guys into an array? or manually instiate? 
        silent_key = FakeKey()

        key_c1 = (PianoKey("C", 1, size_hint=(1/29, 1), pos_hint={"x":0/29}))
        key_d1 = (PianoKey("D", 1, size_hint=(1/29, 1), pos_hint={"x":1/29}))
        key_e1 = (PianoKey("E", 1, size_hint=(1/29, 1), pos_hint={"x":2/29}))
        key_f1 = (PianoKey("F", 1, size_hint=(1/29, 1), pos_hint={"x":3/29}))
        key_g1 = (PianoKey("G", 1, size_hint=(1/29, 1), pos_hint={"x":4/29}))
        key_a1 = (PianoKey("A", 1, size_hint=(1/29, 1), pos_hint={"x":5/29}))
        key_b1 = (PianoKey("B", 1, size_hint=(1/29, 1), pos_hint={"x":6/29}))

        key_c2 = (PianoKey("C", 2, size_hint=(1/29, 1), pos_hint={"x":7/29}))
        key_d2 = (PianoKey("D", 2, size_hint=(1/29, 1), pos_hint={"x":8/29}))
        key_e2 = (PianoKey("E", 2, size_hint=(1/29, 1), pos_hint={"x":9/29}))
        key_f2 = (PianoKey("F", 2, size_hint=(1/29, 1), pos_hint={"x":10/29}))
        key_g2 = (PianoKey("G", 2, size_hint=(1/29, 1), pos_hint={"x":11/29}))
        key_a2 = (PianoKey("A", 2, size_hint=(1/29, 1), pos_hint={"x":12/29}))
        key_b2 = (PianoKey("B", 2, size_hint=(1/29, 1), pos_hint={"x":13/29}))

        key_c3 = (PianoKey("C", 3, size_hint=(1/29, 1), pos_hint={"x":14/29}))
        key_d3 = (PianoKey("D", 3, size_hint=(1/29, 1), pos_hint={"x":15/29}))
        key_e3 = (PianoKey("E", 3, size_hint=(1/29, 1), pos_hint={"x":16/29}))
        key_f3 = (PianoKey("F", 3, size_hint=(1/29, 1), pos_hint={"x":17/29}))
        key_g3 = (PianoKey("G", 3, size_hint=(1/29, 1), pos_hint={"x":18/29}))
        key_a3 = (PianoKey("A", 3, size_hint=(1/29, 1), pos_hint={"x":19/29}))
        key_b3 = (PianoKey("B", 3, size_hint=(1/29, 1), pos_hint={"x":20/29}))

        key_c4 = (PianoKey("C", 4, size_hint=(1/29, 1), pos_hint={"x":21/29}))
        key_d4 = (PianoKey("D", 4, size_hint=(1/29, 1), pos_hint={"x":22/29}))
        key_e4 = (PianoKey("E", 4, size_hint=(1/29, 1), pos_hint={"x":23/29}))
        key_f4 = (PianoKey("F", 4, size_hint=(1/29, 1), pos_hint={"x":24/29}))
        key_g4 = (PianoKey("G", 4, size_hint=(1/29, 1), pos_hint={"x":25/29}))
        key_a4 = (PianoKey("A", 4, size_hint=(1/29, 1), pos_hint={"x":26/29}))
        key_b4 = (PianoKey("B", 4, size_hint=(1/29, 1), pos_hint={"x":27/29}))
        key_c5 = (PianoKey("C", 5, size_hint=(1/29, 1), pos_hint={"x":28/29}))

        key_db1 = (PianoKey("Db", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 1/58, "y": 0.37}))
        key_eb1 = (PianoKey("Eb", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 3/58, "y": 0.37}))
        key_gb1 = (PianoKey("Gb", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 7/58, "y": 0.37}))
        key_ab1 = (PianoKey("Ab", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 9/58, "y": 0.37}))
        key_bb1 = (PianoKey("Bb", 1, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 11/58, "y": 0.37}))

        key_db2 = (PianoKey("Db", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 15/58, "y": 0.37}))
        key_eb2 = (PianoKey("Eb", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 17/58, "y": 0.37}))
        key_gb2 = (PianoKey("Gb", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 21/58, "y": 0.37}))
        key_ab2 = (PianoKey("Ab", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 23/58, "y": 0.37}))
        key_bb2 = (PianoKey("Bb", 2, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 25/58, "y": 0.37}))

        key_db3 = (PianoKey("Db", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 29/58, "y": 0.37}))
        key_eb3 = (PianoKey("Eb", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 31/58, "y": 0.37}))
        key_gb3 = (PianoKey("Gb", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 35/58, "y": 0.37}))
        key_ab3 = (PianoKey("Ab", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 37/58, "y": 0.37}))
        key_bb3 = (PianoKey("Bb", 3, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 39/58, "y": 0.37}))

        key_db4 = (PianoKey("Db", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 43/58, "y": 0.37}))
        key_eb4 = (PianoKey("Eb", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 45/58, "y": 0.37}))
        key_gb4 = (PianoKey("Gb", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 49/58, "y": 0.37}))
        key_ab4 = (PianoKey("Ab", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 51/58, "y": 0.37}))
        key_bb4 = (PianoKey("Bb", 4, white=False, size_hint=(1/35, 0.63), pos_hint={"x": 53/58, "y": 0.37}))


        self.add_widget(key_c1)
        self.add_widget(key_d1)
        self.add_widget(key_e1)
        self.add_widget(key_f1)
        self.add_widget(key_g1)
        self.add_widget(key_a1)
        self.add_widget(key_b1)
        
        self.add_widget(key_c2)
        self.add_widget(key_d2)
        self.add_widget(key_e2)
        self.add_widget(key_f2)
        self.add_widget(key_g2)
        self.add_widget(key_a2)
        self.add_widget(key_b2)

        self.add_widget(key_c3)
        self.add_widget(key_d3)
        self.add_widget(key_e3)
        self.add_widget(key_f3)
        self.add_widget(key_g3)
        self.add_widget(key_a3)
        self.add_widget(key_b3)

        self.add_widget(key_c4)
        self.add_widget(key_d4)
        self.add_widget(key_e4)
        self.add_widget(key_f4)
        self.add_widget(key_g4)
        self.add_widget(key_a4)
        self.add_widget(key_b4)
        self.add_widget(key_c5)

        self.add_widget(key_db1)
        self.add_widget(key_eb1)
        self.add_widget(key_gb1)
        self.add_widget(key_ab1)
        self.add_widget(key_bb1)

        self.add_widget(key_db2)
        self.add_widget(key_eb2)
        self.add_widget(key_gb2)
        self.add_widget(key_ab2)
        self.add_widget(key_bb2)

        self.add_widget(key_db3)
        self.add_widget(key_eb3)
        self.add_widget(key_gb3)
        self.add_widget(key_ab3)
        self.add_widget(key_bb3)

        self.add_widget(key_db4)
        self.add_widget(key_eb4)
        self.add_widget(key_gb4)
        self.add_widget(key_ab4)
        self.add_widget(key_bb4)
    
        self.sector_mapping = {
        "0": silent_key,
        "1": key_c1,
        "2": key_db1, 
        "3": key_d1,
        "4": key_eb1,
        "5": key_e1,
        "6": key_f1,
        "7": key_gb1,
        "8": key_g2, 
        "9": key_ab1,
        "10": key_a1,
        "11": key_bb1,
        "12": key_b1,

        "13": key_c2,
        "14": key_db2,
        "15": key_d2,
        "16": key_eb2,
        "17": key_e2,
        "18": key_f2,
        "19": key_gb2,
        "20": key_g2, 
        "21": key_ab2,
        "22": key_a2,
        "23": key_bb2,
        "24": key_b2,

        "25": key_c3,
        "26": key_db3, 
        "27": key_d3, 
        "28": key_eb3,
        "29": key_e3,
        "30": key_f3, 
        "31": key_gb3, 
        "32": key_g3, 
        "33": key_ab3, 
        "34": key_a3, 
        "35": key_bb3, 
        "36": key_b3, 

        "37": key_c4, 
        "38": key_db4, 
        "39": key_d4, 
        "40": key_eb4, 
        "41": key_e4, 
        "42": key_f4, 
        "43": key_gb4, 
        "44": key_g4, 
        "45": key_ab4, 
        "46": key_a4, 
        "47": key_bb4, 
        "48": key_b4, 
        "49": key_c5,
        # fill in etc.
    }

class Board(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(PianoBoard(size_hint = (1, 0.5)))
        new_layout = RelativeLayout(size_hint = (1, 0.5), pos_hint={"y": 0.5})
        new_layout.add_widget(Button(text="Recalibrate", size_hint = (0.2, 0.3), pos_hint = {"center_x": 0.25, "y": 0.3}))
        new_layout.add_widget(Button(text="Metronome", size_hint = (0.2, 0.3), pos_hint = {"center_x": 0.5, "y": 0.3}))
        new_layout.add_widget(Button(text="Start MIDI", size_hint = (0.2, 0.3), pos_hint = {"center_x": 0.75, "y": 0.3}))

        self.add_widget(new_layout)

# could eventually make this into a thing to flip it to flats if wanted 
# smoother way to instantiate? 
class PianoApp(App):
    def build(self):
        pygame.init()
        mixer.set_num_channels(50)

        #Window.clearcolor = rgba("#570861")
        Window.size = (1000, 700)
        return Board(size_hint = (1, 1))

if __name__ == "__main__":
    white_sounds = []

    PianoApp().run()