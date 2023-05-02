# import cv

# #video capture object
# cap=cv.VideoCapture(1) #iphone camera

# # capture the frames..
# while True:
#     ret, frame = cap.read()

#     cv.imshow('Frame', frame)  # Display the resulting frame
#     key = cv.waitKey(1)
#     if key == 27:  # click esc key to exit
#         break

# cap.release()
# cv.destroyAllWindows()

import cv2 as cv
import numpy as np
import math
import mediapipe as mp
import time
import sys
import os



#All openCV functions are cited from the openCV API: https://opencv.org/

def filter(img):


    scale = 1
    delta = 0
    ddepth = cv.CV_16S

    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

    blur = cv.GaussianBlur(gray, (5, 5), 0)



    grad_x = cv.Sobel(blur, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    grad_y = cv.Sobel(blur, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    
    abs_grad_x = cv.convertScaleAbs(grad_x)
    abs_grad_y = cv.convertScaleAbs(grad_y)
    
    
    grad = cv.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
 

    thresh = cv.threshold(grad, 15, 255, cv.THRESH_BINARY_INV)[1]
    


    return thresh, gray

def segment(thresh, gray, img):
    # Apply the Component analysis function
    analysis = cv.connectedComponentsWithStats(thresh,
                                                4,
                                                cv.CV_32S)
    (totalLabels, label_ids, values, centroid) = analysis
    
    # Initialize a new image to store 
    # all the output components
    output = np.zeros(gray.shape, dtype="uint8")
   
    correct = []
    # Loop through each component 
    for i in range(1,totalLabels):
        # Area of the component
        area = values[i, cv.CC_STAT_AREA] 
        # print(area)
        # print(totalLabels)
        if (area > 1000 and area < 50000):
        # if (True):
            correct+=[i]
    
    totalSections = len(correct)
    sector = [0]*(totalSections+1)
    for j in range(totalSections):
        i = correct[j]
        # Create a new image for bounding boxes
        new_img=img.copy()
        
        # Now extract the coordinate points
        x1 = values[i, cv.CC_STAT_LEFT]
        y1 = values[i, cv.CC_STAT_TOP]
        w = values[i, cv.CC_STAT_WIDTH]
        h = values[i, cv.CC_STAT_HEIGHT]
        
        # Coordinate of the bounding box
        pt1 = (x1, y1)
        pt2 = (x1+ w, y1+ h)
        (X, Y) = centroid[i]
        
        # Bounding boxes for each component
        cv.rectangle(new_img,pt1,pt2,
                    (0, 255, 0), 3)
        cv.circle(new_img, (int(X),
                            int(Y)), 
                4, (0, 0, 255), -1)

        # Create a new array to show individual component
        component = np.zeros(gray.shape, dtype="uint8")
        value = 255 * (j+1) // totalSections
        sector[j+1] = value
        componentMask = (label_ids == i).astype("uint8") * value
       

        # Apply the mask using the bitwise operator
        component = cv.bitwise_or(component,componentMask)
        output = cv.bitwise_or(output, componentMask)


    return output, totalSections, sector


class choose_points:
    def __init__(self, img):
        self.counter = 0
        self.src = [[]]
        self.img = img
    
        #if esc pressed, finish.
        cv.destroyAllWindows()

    # make this on touch cdoen 
    def get_mouse_pts(self,event,x,y,flags,param):
        if event == cv.EVENT_LBUTTONDOWN: #checks mouse left button down condition
            print("Coordinates of pixel: X: ",x,"Y: ",y)
            self.img = cv.circle(self.img, (x,y), radius=5, color=(255, 0, 0), thickness=-1)
            self.src += [[x,y]]
            self.counter += 1

        return 0

def get_src_pts(corners, h, w):

    # get dist from each edge to each of the 4 points so you know how to order them
    src = []
    # print(h,w)
    test = np.zeros((4,1))
    for i in range(np.size(corners, 0)):
        test[i] = math.dist([0,0], corners[i])
    src += [corners[np.argmin(test)]]
    test = np.zeros((4,1))
    for i in range(np.size(corners, 0)):
        test[i] = [math.dist([w-1,0], corners[i])]
    src += [corners[np.argmin(test)]]
    test = np.zeros((4,1))
    for i in range(np.size(corners, 0)):
        test[i] = math.dist([0,h-1], corners[i])
    src += [corners[np.argmin(test)]]
    test = np.zeros((4,1))
    for i in range(np.size(corners, 0)):
        test[i] = math.dist([w-1,h-1], corners[i])
    src += [corners[np.argmin(test)]]
    return np.float32(src)
    
def get_dst_pts(w, h):
    return np.float32([(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]), h, w

def warping(img, valid_contours, src):
    boundaries = [
        ([60, 60, 140], [120, 120, 205]), #red
        # ([0, 0, 45], [60, 60, 230]), #red
        ]
    for (lower, upper) in boundaries:
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")

        mask = cv.inRange(img, lower, upper)

        output = cv.bitwise_and(img, img, mask = mask)


    # Convert to grayscale.
    mask = np.zeros(img.shape, dtype=np.uint8)
    gray = cv.cvtColor(output,cv.COLOR_BGR2GRAY)
    kernel = np.ones((3, 3), np.float32) / 9
    blur = cv.filter2D(gray, -1, kernel)
    thresh = cv.threshold(blur, 250, 255, cv.THRESH_OTSU)[1]
    contours,hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)


    src = src
    valid_contours = True

    src.pop(0)
    src = np.float32(src)

    # Putting corner points into numpy array
    src = get_src_pts(src, img.shape[0], img.shape[1])
    h = 359
    w = 1392

    # keeps the area the same, pixels per key will be consistent 
    dst = np.float32([[0,0],[w,0],[0,h],[w,h]])
    H, _ = cv.findHomography(src, dst)
    warp = cv.warpPerspective(img, H, (w,h), flags=cv.INTER_LINEAR)

    return warp, H, src, valid_contours

def hands(H, output, src, sector):
    cap = cv.VideoCapture(0)

    mp_Hands = mp.solutions.hands
    hands = mp_Hands.Hands()

    num_fing = 5
    prev = time.time()
    while True:
        LhandList = []
        RhandList = []
        Ltext = ["thumb left", "index left", "middle left", "ring left", "pinky left"]
        Rtext = ["thumb right", "index right", "middle right", "ring right", "pinky right"]

        out = output.copy()
        success, image = cap.read()
        RGB_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        # print(src)
        rect = cv.minAreaRect(src)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        image = cv.drawContours(image,[box],0,(0,0,255),2)

        old_pts = np.float32([[[23, 340]]])
        new_pts = cv.perspectiveTransform(old_pts, H)
        cx, cy = round(new_pts[0][0][0]), round(new_pts[0][0][1])
        # print(cx,cy)
        cv.circle(out, (cx, cy), 5, (100, 255, 0), cv.FILLED)

        results = hands.process(RGB_image)
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
                        new_pts = cv.perspectiveTransform(old_pts, H)
                        cx, cy = round(new_pts[0][0][0]), round(new_pts[0][0][1])
                        cv.circle(out, (cx, cy), 5, (255, 255, 0), cv.FILLED)
                        if handLabel == "Left":
                            RhandList.append((cx, cy))
                        elif handLabel == "Right":
                            LhandList.append((cx, cy))

        cur = time.time()
        if cur-prev >= 1:
            prev = cur
            if len(LhandList) > 0:
                for i in range(num_fing):
                    px = LhandList[i][0]
                    py = LhandList[i][1]
                    print(px,py)
                    if px >= output.shape[1] or py >= output.shape[0] or px < 0 or py < 0:
                        print("error out of bounds")
                    else:
                        value = output[py,px]
                        d = sector.index(value)
                        print("%s: (%d,%d), value: %d, sector: %d" % (Ltext[i], px, py, value, d))
                print("-------------------------")
            if len(RhandList) > 0:
                for i in range(num_fing):
                    px = RhandList[i][0]
                    py = RhandList[i][1]
                    print(px,py)
                    if px >= output.shape[1] or py >= output.shape[0] or px < 0 or py < 0:
                        print("error out of bounds")
                    else:
                        value = output[py,px]
                        d = sector.index(value)
                        print("%s: (%d,%d), value: %d, sector: %d" % (Rtext[i], px, py, value, d))
                print("-------------------------")
            if len(LhandList) > 0 or len(RhandList) > 0:
                print(" ")
                print("**************************")
                print(" ")



    
# n = 11

#readin image
# img = cv.imread('test_images/test%d.jpg' % n)
# img = cv.imread('test_images/test%d.png' % n)
if __name__ == "__main__":
    valid_contours = False

    # while(not valid_contours):
    img = start_image()

        # img = re_size(img)
    cv.imshow('Chosen Image', img)
    cv.waitKey()
    cv.destroyAllWindows()

    #     # warping image
    #     warp, H, src, valid_contours = warping(img, valid_contours)

    img = cv.imread('nish_img.jpg')
# img = cv.imread('test_images/test%d.png' % n)

    #img = re_size(img)
    warp, H, src, valid_contours = warping(img, valid_contours)
    cv.imshow('warp', warp)
    cv.waitKey()
    cv.destroyAllWindows()
    # warp = img.copy()

    # warp = re_size(warp)

    #crop the image 
    crop = 20
    warp = warp[crop:-crop, crop:-crop]
    # cv.imshow('crop', warp)

    #border the image
    bor = 20
    col = 150
    warp = cv.copyMakeBorder(warp,bor,bor,bor,bor,cv.BORDER_CONSTANT,value=[col,col,col])
    # cv.imshow('border', warp)
    # cv.waitKey()
    # cv.destroyAllWindows()

    # threshold
    thresh, gray = filter(warp)
    cv.imshow('thresh', thresh)
    cv.waitKey()
    cv.destroyAllWindows()

    #segmentation
    output, totalSections, sector = segment(thresh, gray, warp)
    cv.imshow('output', output)
    cv.waitKey()
    cv.destroyAllWindows()

    # #Output sector with mouse cursor
    # mouse_sensing()

    #detect hands
    hands(H, output, src, sector)
