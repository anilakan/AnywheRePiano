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


def callback1(instance):
    print("hey there homie")
    App.get_running_app().root.current = "second"

def callback2(instance):
    print("bye there bomie")
    #print(instance.parent.parent.parent)
    #print(App.get_running_app().root)
    App.get_running_app().root.current = "first"

class PianoKey(Widget):
    def __init__(self, note, **kwargs):
        super().__init__(**kwargs)

class Screen1(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout()
        bm = Button(text = "Hello this is Nish", size_hint=(0.5, 0.5), pos_hint={"x": 0.5, "y": 0.5})
        bm.bind(on_press=callback1)
        self.add_widget(layout)
        layout.add_widget(bm)

class Screen2(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout2 = BoxLayout()
        bm2 = Button(text = "bye bitch", size_hint=(0.5, 0.5), pos_hint={"x": 0.5, "y": 0.5})
        self.add_widget(layout2)
        layout2.add_widget(bm2)
        bm2.bind(on_press=callback2)
       

class PianoApp(App):
    def build(self):
        Window.size = (1000, 700)

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(Screen2(name="second"))
        sm.add_widget(Screen1(name="first"))

        return sm
    
if __name__ == "__main__":
    PianoApp().run()

