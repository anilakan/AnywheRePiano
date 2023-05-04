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
    # cv.imshow('blur', blur)
    # cv.waitKey()

    # dst = cv.Canny(blur, 50, 200, None, 3)
    # cv.imshow('grad', dst)
    # cv.waitKey()


    grad_x = cv.Sobel(blur, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    grad_y = cv.Sobel(blur, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    
    abs_grad_x = cv.convertScaleAbs(grad_x)
    abs_grad_y = cv.convertScaleAbs(grad_y)
    
    
    grad = cv.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    # cv.imshow('grad', grad)
    # cv.waitKey()

    thresh = cv.threshold(grad, 15, 255, cv.THRESH_BINARY_INV)[1]
    # thresh = cv.bitwise_not(thresh)
    


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
        
        # Show the final images
        cv.imshow("Image", new_img)
        cv.imshow("Individual Component", component)
        cv.imshow("Filtered Components", output)
        cv.waitKey()
        cv.destroyAllWindows()

    return output, totalSections, sector


class choose_points:
    def __init__(self, img):
        self.counter = 0
        self.src = [[]]
        self.img = img
        cv.namedWindow('Choose Points')
        cv.setMouseCallback('Choose Points', self.get_mouse_pts)
        print("Please choose 4 corner points in order from top to bottom and left to right:\n")

        #Do until esc pressed
        while(1):
            cv.imshow('Choose Points', img)
            if cv.waitKey(20) & 0xFF == 27 or self.counter == 4:
                print('Get Corner Points Completed.')
                break
        #if esc pressed, finish.
        cv.destroyAllWindows()

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

def warping(img, valid_contours):
    boundaries = [
        ([60, 60, 140], [120, 120, 205]), #red
        # ([0, 0, 45], [60, 60, 230]), #red
        ]
    for (lower, upper) in boundaries:
        # create NumPy arrays from the boundaries 
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv.inRange(img, lower, upper)
        # cv.imshow("images", mask)
        # cv.waitKey()

        output = cv.bitwise_and(img, img, mask = mask)


    # Convert to grayscale.
    mask = np.zeros(img.shape, dtype=np.uint8)
    gray = cv.cvtColor(output,cv.COLOR_BGR2GRAY)

    kernel = np.ones((3, 3), np.float32) / 9
    blur = cv.filter2D(gray, -1, kernel)
    # cv.imshow('blur', blur)

    
    thresh = cv.threshold(blur, 250, 255, cv.THRESH_OTSU)[1]
    # thresh = cv.bitwise_not(thresh)
    # cv.imshow('thresh1', thresh)
    # cv.waitKey()
    # cv.destroyAllWindows()

    contours,hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)


    src = [[]]
    if (len(contours) != 4):
        print("# of Contours: ", len(contours))
        if len(contours) < 4:
            print("WARNING: Please re-adjust camera lighting to be brighter")
            ans = input("Do you wish to insert points manually? (Y/N)\t")
            if (ans == "N"): 
                print("Returning to choose another image") 
                return img,None,src,valid_contours
            if (ans == "Y"): 
                choosing = choose_points(img)
                src = choosing.src
                valid_contours = True

        if len(contours) > 4:
            print("WARNING: Please re-adjust camera lighting to be darker")
            ans = input("Do you wish to insert points manually? (Y/N)\t")
            if (ans == "N"): 
                print("Returning to choose another image") 
                return img,None,src,valid_contours
            if (ans == "Y"): 
                choosing = choose_points(img)
                src = choosing.src
                valid_contours = True

    else:
        valid_contours = True
        for cnt in contours:
            M = cv.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            # print(cx, cy)
            src += [[cx,cy]]
            # img = cv.circle(img, (cx,cy), radius=0, color=(255, 0, 0), thickness=-1)

    
        for cnt in contours:
            cv.drawContours(img, cnt, -1, (0, 255, 0), 3) 
        # cv.imshow('contours', img)
        # cv.waitKey()

    src.pop(0)
    src = np.float32(src)

    # Putting corner points into numpy array
    src = get_src_pts(src, img.shape[0], img.shape[1])
    # print(src)
    # w = int(max(src[:,0]) - min(src[:,0]))
    # h = int(max(src[:,1]) - min(src[:,1]))
    h = 359
    w = 1392

    # keeps the area the same, pixels per key will be consistent 
    # print(h,w)

    dst = np.float32([[0,0],[w,0],[0,h],[w,h]])
    # print(dst)

    H, _ = cv.findHomography(src, dst)

    warp = cv.warpPerspective(img, H, (w,h), flags=cv.INTER_LINEAR)

    return warp, H, src, valid_contours

def re_size(img):
    #resize image
    r = img.shape[0]
    c = img.shape[1]
    # print(r,c)

    factor = 1/((r*c)/500000)**(1/2)
    img = cv.resize(img, None, fx = factor, fy = factor, interpolation= cv.INTER_AREA)

    return img

def mouseValue(event,x,y,flags,param):
    # if event == cv.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        value = output[y,x]
        s = sector.index(value)
        print("sector: ", s)
        print("value: ",  value)
        print("Coordinates of pixel: X: ",x,"Y: ",y)

def mouse_sensing():
    cv.namedWindow('mouseValue')
    cv.setMouseCallback('mouseValue',mouseValue)
    
    #Do until esc pressed
    while(1):
        cv.imshow('mouseValue',output)
        if cv.waitKey(20) & 0xFF == 27:
            break
    #if esc pressed, finish.
    cv.destroyAllWindows()

def hands(H, output, src, sector):
    cap = cv.VideoCapture(0)

    mp_Hands = mp.solutions.hands
    hands = mp_Hands.Hands()
    # mpDraw = mp.solutions.drawing_utils
    # mp_drawing_styles = mp.solutions.drawing_styles

    # finger_Coord = [(8, 6), (12, 10), (16, 14), (20, 18)]
    # thumb_Coord = (4,2)

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
                # mpDraw.draw_landmarks(image, handLms, mp_Hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
                for idx, lm in enumerate(handLms.landmark):
                    if idx % 4 == 0 and idx != 0: #finger = 5
                        # only save coordinates that are for the fingers here, change this conditional
                    # if idx == 4: #finger = 1
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

            # for point in handList:
        cv.imshow("viewing fingers", image)
        cv.imshow('mouseValue', out)

        cur = time.time()
        if cur-prev >= 1:
        # if True:
            prev = cur
            if len(LhandList) > 0:
                # print("thumb left: ", LhandList[0])
                # print("index left: ", LhandList[1])
                # print("middle left: ", LhandList[2])
                # print("ring left: ", LhandList[3])
                # print("pinky left: ", LhandList[4])
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
                # print("thumb right: ", RhandList[0])
                # print("index right: ", RhandList[1])
                # print("middle right: ", RhandList[2])
                # print("ring right: ", RhandList[3])
                # print("pinky right: ", RhandList[4])
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

        key = cv.waitKey(1)
        if key == 27:  # click esc key to exit
            break
    cap.release()
    cv.destroyAllWindows()

def start_image():
    cap = cv.VideoCapture(0)

    # if (cap.isOpened()): 
    while(cap.isOpened()):
        print("hi")
        ret, img = cap.read()
        if ret == True:
        # Display the resulting frame
            cv.imshow('Frame', img)
            
        # # Press Q on keyboard to exit
        #     if cv.waitKey(25) & 0xFF == ord('q'):
        #         break

        # Press SPACE BAR on keyboard to exit
            if cv.waitKey(32) & 0xFF == ord(' '):
                #cv.imwrite("nish_img.jpg", img)
                break
    
    # Break the loop
        else:
            break

    cap.release()
    cv.destroyAllWindows()

    return img
    
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

# img = cv.imread('test_images/test%d.png' % n)

    #img = re_size(img)
    warp, H, src, valid_contours = warping(img, valid_contours)
    cv.imwrite("warped1.jpg", warp)
    print(warp, H, src, valid_contours)
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

    cv.imwrite("warpafter1.jpg", warp)
    cv.imwrite("thresh1.jpg", thresh)
    cv.imwrite("grey1.jpg", gray)
    #segmentation
    output, totalSections, sector = segment(thresh, gray, warp)
    cv.imwrite("output1.jpg", output)
    print(output, totalSections, sector)
    cv.imshow('output', output)
    cv.waitKey()
    cv.destroyAllWindows()

    # #Output sector with mouse cursor
    # mouse_sensing()

    #detect hands
    hands(H, output, src, sector)
