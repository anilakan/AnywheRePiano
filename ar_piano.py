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

from kivy.clock import Clock 
from kivy.utils import rgba
import pygame
from pygame import mixer

import cv
import piano

class PianoKey(Widget):
    def __init__(self, note, **kwargs):
        super().__init__(**kwargs)

class Screen1(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cv_layout = cv.CVLayout()
        self.add_widget(self.cv_layout)


class Screen2(Screen):
    def __init__(self, the_app, **kwargs):
        super().__init__(**kwargs)
        #self.add_widget(Label(text="here is the piano"))
        self.board = piano.PianoBoard(size_hint=(1, 0.5))
        self.add_widget(self.board)
        self.the_app = the_app
        self.read_event = Clock.schedule_interval(self.read_hands, 1/30)
        
    def read_hands(self, *args):
        try:
            r_sectors = self.the_app.screen1.cv_layout.Rsectors
            l_sectors = self.the_app.screen1.cv_layout.Lsectors
            for fings in r_sectors:
                self.board.sector_mapping[str(fings)].sound.play(0, 1000)
            for fings in l_sectors:
                self.board.sector_mapping[str(fings)].sound.play(0, 1000)
            
        except:
            pass


class PianoApp(App):
    def build(self):
        pygame.init()
        mixer.set_num_channels(50)

        Window.size = (1000, 700)

        self.screen1 = Screen1(name="calibration")
        self.screen2 = Screen2(self, name="piano")

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(self.screen1)
        sm.add_widget(self.screen2)

        return sm
    
if __name__ == "__main__":
    PianoApp().run()

