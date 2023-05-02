from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.graphics.texture import Texture
from kivy.config import Config
from kivy.core.window import Window
from random import random

import cv2 as cv
from kivy.clock import Clock
from kivy.uix.image import Image
#from openCV import warping

import asyncio
import numpy as np
import math
import newCV
import mediapipe as mp
import time


#Config.set('graphics', 'resizable', True)


class CVLayout(FloatLayout):
    def __init__(self):
        super().__init__()
        self.image = Image(size_hint = (1, 1), pos=(0, 0))
        self.add_widget(self.image)
        self.image.source = 'nish_img.jpg'
        self.button = Button(text="Capture", size_hint = (0.5, 0.05), pos_hint = {'center_x': 0.5, 'y':0.05})
        self.button.bind(on_press=self.callback_test)
        self.add_widget(self.button)
        self.start_image()
        self.choosing = True
        self.src = [[]]
        self.counter = 0
        self.actual_image = cv.imread("nish_img.jpg")

        mp_Hands = mp.solutions.hands
        self.hands = mp_Hands.Hands()
        self.num_fing = 5
        self.prev = time.time()

        self.Ltext = ["thumb left", "index left", "middle left", "ring left", "pinky left"]
        self.Rtext = ["thumb right", "index right", "middle right", "ring right", "pinky right"]

        
    def callback_test(self, event):
        cv.imwrite("clicked_image.jpg", self.image_frame)

    def start_image(self, *args):
        self.capture = cv.VideoCapture(0)
        self.load_event = Clock.schedule_interval(self.load_video, 1/30)
  
    def hands_func(self):
        self.LhandList = []
        self.RhandList = []
        RGB_image = cv.cvtColor(self.image_frame, cv.COLOR_BGR2RGB)
        self.circles = []
            # print(src)
        rect = cv.minAreaRect(self.src)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        image = cv.drawContours(self.image_frame,[box],0,(0,0,255),2)

        old_pts = np.float32([[[23, 340]]])
        new_pts = cv.perspectiveTransform(old_pts, self.H)
        cx, cy = round(new_pts[0][0][0]), round(new_pts[0][0][1])
        #print(cx,cy)
        cv.circle(self.output_img, (cx, cy), 5, (100, 255, 0), cv.FILLED)

        results = self.hands.process(RGB_image)

        multiLandMarks = results.multi_hand_landmarks
        if multiLandMarks:
            for handLms in multiLandMarks:
                handIndex = results.multi_hand_landmarks.index(handLms)
                handLabel = results.multi_handedness[handIndex].classification[0].label
                for idx, lm in enumerate(handLms.landmark):
                    if idx % 4 == 0 and idx != 0: #finger = 5
                        h, w, c = image.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv.circle(image, (cx, cy), 5, (255, 255, 0), cv.FILLED)


                        old_pts = np.float32([[[cx, cy]]])
                        new_pts = cv.perspectiveTransform(old_pts, self.H)
                        cx, cy = round(new_pts[0][0][0]), round(new_pts[0][0][1])
                        cv.circle(self.output_img, (cx, cy), 5, (255, 255, 0), cv.FILLED)
                        if handLabel == "Left":
                            self.RhandList.append((cx, cy))
                        elif handLabel == "Right":
                            self.LhandList.append((cx, cy))
                            #print(cx, cy)

       # self.print_hands()

    def print_hands(self):  
        if len(self.LhandList) > 0:
            for i in range(self.num_fing):
                px = self.LhandList[i][0]
                py = self.LhandList[i][1]
                #print("GRAB FROM LIST: ", px,py)
                if px >= self.output.shape[1] or py >= self.output.shape[0] or px < 0 or py < 0:
                    print("error out of bounds")
                else:
                    value = self.output[py,px]
                    d = self.sector.index(value)
                    print("%s: (%d,%d), value: %d, sector: %d" % (self.Ltext[i], px, py, value, d))
            print("-------------------------")

        if len(self.RhandList) > 0:
            for i in range(self.num_fing):
                px = self.RhandList[i][0]
                py = self.RhandList[i][1]
                #print(px,py)
                if px >= self.output.shape[1] or py >= self.output.shape[0] or px < 0 or py < 0:
                    print("error out of bounds")
                else:
                    value = self.output[py,px]
                    d = self.sector.index(value)
                    print("%s: (%d,%d), value: %d, sector: %d" % (self.Rtext[i], px, py, value, d))
            print("-------------------------")
        if len(self.LhandList) > 0 or len(self.RhandList) > 0:
            print(" ")
            print("**************************")
            print(" ")




    def on_touch_down(self, touch):
        #if self.image.collide_point(*touch.pos):
        if self.button.collide_point(*touch.pos):
            self.button.on_touch_down(touch)
            return True
        if self.choosing: 
            self.src += [[touch.x-40, 1400-touch.y-165]]
            d = 10
            self.canvas.add(Color(rgba=(0, 0, 1, 1)))
            self.canvas.add(Ellipse(pos = (touch.x-d/2, touch.y-d/2), size = (d, d)))
            self.counter += 1
            if self.counter == 4: 


            # start the warp now that there are 4 points to work with 
                warp, H, src, valid_contours = newCV.warping(self.actual_image, False, self.src)
                print(warp, H, src, valid_contours)
                self.warp = warp
                self.H = H
                self.src  = src
                cv.imwrite("warped2.jpg", self.warp)
                crop = 20
                self.warp= self.warp[crop:-crop, crop:-crop]
                # cv.imshow('crop', warp)

                #border the image
                bor = 50
                col = 150
                self.warp = cv.copyMakeBorder(self.warp,bor,bor,bor,bor,cv.BORDER_CONSTANT,value=[col,col,col])

                cv.imwrite("warpafter2.jpg", self.warp)
                self.thresh, self.gray = newCV.filter(self.warp)

                cv.imwrite("thresh2.jpg", self.thresh)
                cv.imwrite("grey2.jpg", self.gray)

                self.output, self.totalSections, self.sector = newCV.segment(self.thresh, self.gray, self.warp)
                print(self.output, self.totalSections, self.sector)
                cv.imwrite("output.jpg", self.output)
                self.choosing = False
                self.image.size_hint = (0.5, 0.5)

                output_img = cv.imread("output.jpg")
                self.output_img = output_img
                self.new_image = Image(size_hint = (0.5, 1), pos_hint = {"x": 0.25, "y": 0.25})
                self.add_widget(self.new_image)


                #might need to put two loocks on here


        if not self.choosing: 
            pass# run hands and render

        print(touch.x-40, 1400-touch.y-165)


        # eventually clear this off the canvas
    
        
        # if this is is on choose points 

        #print(touch.x, touch.y)
        # potentially thi is 5 off, subtract 160 instead?

    

    def load_video(self, *args):
    
        ret, frame = self.capture.read()
        self.image_frame = frame

        if not self.choosing:
            
            self.hands_func()
            buffer = cv.flip(frame, 0).tostring() # chnage to tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture

            buffer2 = cv.flip(self.output_img, 0).tostring()
            texture2 = Texture.create(size=(self.output_img.shape[1], self.output_img.shape[0]))
            texture2.blit_buffer(buffer2,  bufferfmt='ubyte')
            self.new_image.texture = texture2
     


class CVApp(App):

    def build(self):
        #layout = BoxLayout()
        #self.image = Image()
        # layout.add_widget(self.image)
        # layout.add_widget(Button(text="capture"))
        # self.capture = cv2.VideoCapture(0)
        # Clock.schedule_interval(self.load_video, 1/30)
        Window.size = (1000, 700)
        return CVLayout()
    
    def load_video(self, *args):
        try:
            ret, frame = self.capture.read()
            self.image_frame = frame
            buffer = cv.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture 
        except:
            pass


CVApp().run()
