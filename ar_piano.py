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

from bleak import BleakScanner, BleakClient
import asyncio

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
        self.board = piano.PianoBoard(size_hint=(1, 0.5))
        self.add_widget(self.board)
        self.the_app = the_app
        self.read_event = Clock.schedule_interval(self.read_hands, 1/60)
        self.Ltext = ["thumb left", "index left", "middle left", "ring left", "pinky left"]

    def read_hands(self, *args):
        try:
            r_sectors = self.the_app.screen1.cv_layout.Rsectors
            l_sectors = self.the_app.screen1.cv_layout.Lsectors
            for fings in r_sectors:
                self.board.sector_mapping[str(fings)].sound.play(0, 1000)
                # try:
                self.board.sector_mapping[str(fings)].run_finger()

                # except:
                #     print(self.board.sector_mappings(str(fings)))
            for i, fings in enumerate(l_sectors):
                self.board.sector_mapping[str(fings)].sound.play(0, 1000)
                # try:
                self.board.sector_mapping[str(fings)].run_finger()
                # except:
                #     print(self.board.sector_mappings(str(fings)))            
        except:
            pass

class Screen3(Screen):
    def __init__(self, the_app, **kwargs):
        super().__init__(**kwargs)
        self.ble_button = Button(text="connect your bluetooth here", size_hint = (0.25, 0.25))
        self.add_widget(self.ble_button)
        self.test_button = Button(text="go to piano", size_hint = (0.25, 0.25), pos_hint = {"x": 0.5, "y":0.5})
        self.add_widget(self.test_button)

        self.disconnect_button = Button(text="disconnetn", size_hint = (0.25, 0.25), pos_hint = {"x": 0.25, "y": 0.25})
        self.add_widget(self.disconnect_button)
        self.the_app = the_app
        self.ble_button.bind(on_press=self.callback_one)
        self.test_button.bind(on_press = self.print_func)
        self.disconnect_button.bind(on_press = self.disconnect_ble)

        self.mask_left_pinky = 0xf0000000
        self.mask_left_middle = 0xf00000
        self.mask_left_index = 0xf0000
        self.mask_left_thumb = 0xf000
        self.mask_left_ring = 0xf00


    def disconnect_ble(self, instance):
        self.dis_func()

    async def dis_func(self):
        await self.client.disconnect()
        print('stopped')


    def callback_one(self, instance):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.ble(loop))

        print('hey')

    def print_func(self, instance):
        App.get_running_app().root.current = "calibration"

        print("sup bitches")


    async def ble(self, loop):
        print('hi')
        devices = await BleakScanner.discover()
        # remember to disconnect from BlueSee
        found_ble = False
        # for d in devices: 
        #     print(d.details)
        for d in devices: 
            if d.name == "NishBLE!":
                print(d.address)
                print(d.details)
                found_ble = True
                break
        if not found_ble:
            print("oh no")
            exit()
        address = d.address

        async with BleakClient(address) as client:
            self.client = client
            await client.connect()
            svcs = client.services
            while(self.client.is_connected): # add in a self.stop here 
                for service in svcs:
                    for char in service.characteristics:
                        
                        value = await client.read_gatt_char(char.uuid)
                        value = int.from_bytes(value, byteorder='big')
                        self.the_app.left_pinky['volume'] = (value & self.mask_left_pinky) >> 28
                        self.the_app.left_middle['volume'] = (value & self.mask_left_middle) >> 20
                        self.the_app.left_index['volume'] = (value & self.mask_left_index) >> 16
                        self.the_app.left_thumb['volume'] = (value & self.mask_left_thumb) >> 12
                        self.the_app.left_ring['volume'] = (value & self.mask_left_ring) >> 8

                        print("Pinky: ", self.the_app.left_pinky['volume'])
                        #print("pinky: ", hex((value & self.mask_left_pinky)>>28))
                       # print(int.from_bytes(value,byteorder='big'))
        

class PianoApp(App):
    def build(self):
        pygame.init()
        mixer.set_num_channels(50)

        Window.size = (1000, 700)

        self.screen1 = Screen1(name="calibration")
        self.screen2 = Screen2(self, name="piano")
        self.screen3 = Screen3(self, name="connection")

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(self.screen3)

        sm.add_widget(self.screen1)
        sm.add_widget(self.screen2)

        self.left_pinky = {"volume": 0, "note": 0}
        self.left_middle = {"volume": 0, "note": 0}
        self.left_index = {"volume": 0, "note": 0}
        self.left_thumb = {"volume": 0, "note": 0}
        self.left_ring = {"volume": 0, "note": 0}


        return sm
    
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(PianoApp().async_run())
    loop.close()


