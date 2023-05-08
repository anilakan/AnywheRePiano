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
        new_layout = RelativeLayout(size_hint = (1, 0.5), pos_hint={"y": 0.5})
        new_layout.add_widget(Button(text="Recalibrate", size_hint = (0.2, 0.3), pos_hint = {"center_x": 0.25, "y": 0.3}))
        new_layout.add_widget(Button(text="Metronome", size_hint = (0.2, 0.3), pos_hint = {"center_x": 0.5, "y": 0.3}))
        new_layout.add_widget(Button(text="Start MIDI", size_hint = (0.2, 0.3), pos_hint = {"center_x": 0.75, "y": 0.3}))

        self.add_widget(new_layout)

        self.the_app = the_app
        self.read_event = Clock.schedule_interval(self.read_hands, 1/60)
        self.Ltext = ["thumb left", "index left", "middle left", "ring left", "pinky left"]
        self.Rtext = ["thumb right", "index right", "middle right", "ring right", "pinky right"]
        self.prev_right = [piano.FakeKey(), piano.FakeKey(),piano.FakeKey(),piano.FakeKey(),piano.FakeKey(),piano.FakeKey(), piano.FakeKey(),piano.FakeKey(),piano.FakeKey(),piano.FakeKey()]
        self.prev_left = [piano.FakeKey(), piano.FakeKey(),piano.FakeKey(),piano.FakeKey(),piano.FakeKey(),piano.FakeKey(), piano.FakeKey(),piano.FakeKey(),piano.FakeKey(),piano.FakeKey()]

    def read_hands(self, *args):
        try:
            r_sectors = self.the_app.screen1.cv_layout.Rsectors

            for i, fings in enumerate(r_sectors):
                note = self.board.sector_mapping[str(fings)]
                finger = self.the_app.right_array[i]
                finger['note'] = note
                if self.prev_right[i] != note:
                    self.prev_right[i].turn_off_color()
                self.prev_right[i] = note
                note.run_key(finger["volume"])
        except:
            pass
        
        try:
            l_sectors = self.the_app.screen1.cv_layout.Lsectors

            for i, fings in enumerate(l_sectors):
                note = self.board.sector_mapping[str(fings)]
                finger = self.the_app.finger_array[i]
                finger['note'] = note
                if self.prev_left[i] != note:
                    self.prev_left[i].turn_off_color()
                self.prev_left[i] = note
                #print(self.Ltext[i], finger)
                note.run_key(finger["volume"])
        except:
            pass
    
    

class Screen3(Screen):
    def __init__(self, the_app, **kwargs):
        super().__init__(**kwargs)
        self.ble_button = Button(text="Connect Left Hand", size_hint = (0.25, 0.25), pos_hint={"center_x": 0.25, "y": 0.5})
        self.add_widget(self.ble_button)

        self.ble_right = Button(text="Connect Right Hand", size_hint = (0.25, 0.25), pos_hint = {"center_x": 0.75, "y": 0.5})
        self.add_widget(self.ble_right)
        self.test_button = Button(text="Proceed to Calibration", size_hint = (0.5, 0.1), pos_hint = {"center_x": 0.5, "y":0.15})
        self.add_widget(self.test_button)

       # self.disconnect_button = Button(text=", size_hint = (0.25, 0.25), pos_hint = {"x": 0.25, "y": 0.25})
       # self.add_widget(self.disconnect_button)
        self.the_app = the_app
        self.ble_button.bind(on_press=self.callback_one)
        self.test_button.bind(on_press = self.print_func)
        self.ble_right.bind(on_press=self.callback_two)
        #self.disconnect_button.bind(on_press = self.disconnect_ble)

        self.mask_left_pinky = 0xf0000000
        self.mask_left_middle = 0xf00000
        self.mask_left_index = 0xf0000
        self.mask_left_thumb = 0xf000
        self.mask_left_ring = 0xf00

        self.mask_right_thumb = 0xf0000000
        self.mask_right_index = 0xf00
        self.mask_right_middle = 0xf00000
        self.mask_right_ring = 0xf0000
        self.mask_right_pinky = 0xf000



    def callback_one(self, instance):

    #        loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop((loop))
        asyncio.ensure_future(self.ble(loop))

        print('hey')

    def callback_two(self, instance):
        # loop = asyncio.get_event_loop()
        # asyncio.ensure_future(self.ble_right_func(loop))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop((loop))
        asyncio.ensure_future(self.ble_right_func(loop))

    def print_func(self, instance):
        App.get_running_app().root.current = "calibration"



    async def ble(self, loop):
        print('hi')
        devices = await BleakScanner.discover()
        # remember to disconnect from BlueSee
        found_ble = False

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
            await client.connect()
            svcs = client.services
            while(client.is_connected): # add in a self.stop here 
                for service in svcs:
                    for char in service.characteristics:
                        
                        value = await client.read_gatt_char(char.uuid)
                        value = int.from_bytes(value, byteorder='big')
                        self.the_app.left_pinky['volume'] = (value & self.mask_left_pinky) >> 28

                        # clean up middle and index here
                        self.the_app.left_index['volume'] = (value & self.mask_left_middle) >> 20
                        self.the_app.left_middle['volume'] = (value & self.mask_left_index) >> 16
                        self.the_app.left_thumb['volume'] = (value & self.mask_left_thumb) >> 12
                        self.the_app.left_ring['volume'] = (value & self.mask_left_ring) >> 8

                        # print("index: ", self.the_app.left_index['volume'])
                        # print("pinky: ", self.the_app.left_pinky['volume'])
                        # print("middle: ", self.the_app.left_middle['volume'])
                        # print("thumb: ", self.the_app.left_thumb['volume'])
                        # print("ring: ", self.the_app.left_ring['volume'])


                        #print("pinky: ", hex((value & self.mask_left_pinky)>>28))
                       # print(int.from_bytes(value,byteorder='big'))

    async def ble_right_func(self, loop):
            print('hi')
            devices = await BleakScanner.discover()
            # remember to disconnect from BlueSee
            found_ble = False
            # for d in devices: 
            #     print(d.details)
            for d in devices: 
                if d.name == "BLE_Right":
                    print(d.address)
                    print(d.details)
                    found_ble = True
                    break
            if not found_ble:
                print("oh no")
                exit()
            address = d.address

            async with BleakClient(address) as client:
                await client.connect()
                svcs = client.services
                while(client.is_connected): # add in a self.stop here 
                    for service in svcs:
                        for char in service.characteristics:
                            
                            value = await client.read_gatt_char(char.uuid)
                            value = int.from_bytes(value, byteorder='big')
                            self.the_app.right_pinky['volume'] = (value & self.mask_right_pinky) >> 12

                            # clean up middle and index here
                            self.the_app.right_index['volume'] = (value & self.mask_right_index) >> 8
                            self.the_app.right_middle['volume'] = (value & self.mask_right_middle) >> 20
                            self.the_app.right_thumb['volume'] = (value & self.mask_right_thumb) >> 28
                            self.the_app.right_ring['volume'] = (value & self.mask_right_ring) >> 16

                            #print("index: ", self.the_app.right_index['volume'])
                            # print("pinky: ", self.the_app.right_pinky['volume'])
                            # print("middle: ", self.the_app.right_middle['volume'])
                            # print("thumb: ", self.the_app.right_thumb['volume'])
                            # print("ring: ", self.the_app.right_ring['volume'])


                            #print("pinky: ", hex((value & self.mask_left_pinky)>>28))
                        # print(int.from_bytes(value,byteorder='big'))
            

class PianoApp(App):
    def build(self):
        pygame.init()
        mixer.set_num_channels(50)

        Window.size = (1000, 700)


        self.left_pinky = {"volume": 0, "note": 0}
        self.left_middle = {"volume": 0, "note": 0}
        self.left_index = {"volume": 0, "note": 0}
        self.left_thumb = {"volume": 0, "note": 0}
        self.left_ring = {"volume": 0, "note": 0}

        self.right_pinky = {"volume": 0, "note": 0}
        self.right_middle = {"volume": 0, "note": 0}
        self.right_index = {"volume": 0, "note": 0}
        self.right_thumb = {"volume": 0, "note": 0}
        self.right_ring = {"volume": 0, "note": 0}



        self.finger_array = [self.left_thumb, self.left_index, self.left_middle, self.left_ring, self.left_pinky]
        self.right_array = [self.right_thumb, self.right_index, self.right_middle, self.right_ring, self.right_pinky]

        self.screen1 = Screen1(name="calibration")
        self.screen2 = Screen2(self, name="piano")
        self.screen3 = Screen3(self, name="connection")


        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(self.screen3)

        sm.add_widget(self.screen1)
        sm.add_widget(self.screen2)


        return sm
    
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(PianoApp().async_run())
    loop.close()


