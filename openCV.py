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


#All openCV functions are cited from the openCV API: https://opencv.org/

def mouseValue(event,x,y,flags,param):
    # if event == cv.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        value = output[y,x]
        s = sector.index(value)
        print("sector: ", s)
        # print("value: ",  value)
        # print("Coordinates of pixel: X: ",x,"Y: ",y)

def warp(img, img_gray, template):
    
    # cv.imshow('gray', img_gray)
    # cv.waitKey()

    template = cv.cvtColor(template,cv.COLOR_BGR2GRAY)

    w, h = template.shape[::-1] 
  
    # Apply template matching
    res = cv.matchTemplate(img_gray, template,
                           cv.TM_CCOEFF_NORMED)
  
    threshold = 0.3
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
  
    return img

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
    cv.imshow('grad', grad)
    cv.waitKey()

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

    return output, totalSections, sector

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

def warping(img):
    boundaries = [
        ([60, 60, 150], [120, 120, 205]), #red
        # ([0, 0, 45], [60, 60, 230]), #red
        ]
    for (lower, upper) in boundaries:
        # create NumPy arrays from the boundaries 
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv.inRange(img, lower, upper)
        output = cv.bitwise_and(img, img, mask = mask)
        # show the images
        # cv.imshow("images", output)
        # cv.waitKey()

    # Convert to grayscale.
    mask = np.zeros(img.shape, dtype=np.uint8)
    gray = cv.cvtColor(output,cv.COLOR_BGR2GRAY)

    kernel = np.ones((3, 3), np.float32) / 9
    blur = cv.filter2D(gray, -1, kernel)
    # cv.imshow('blur', blur)
    thresh = cv.threshold(blur, 250, 255, cv.THRESH_OTSU)[1]
    # thresh = cv.bitwise_not(thresh)
    cv.imshow('thresh1', thresh)
    cv.waitKey()

    # cnts = cv.findContours(thresh, cv.RETR_TREE  , cv.CHAIN_APPROX_SIMPLE)[0]
    contours,hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # x,y,w,h = cv.boundingRect(cnt)
    # cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

    src = [[]]
    for cnt in contours:
        M = cv.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        # print(cx, cy)
        src += [[cx,cy]]
        img = cv.circle(img, (cx,cy), radius=0, color=(255, 0, 0), thickness=-1)

    src.pop(0)
    src = np.float32(src)

    # cnt = sorted(cnts, key=cv.contourArea, reverse=True)[0]

    # print(cnts)

    # epsilon = 0.02 * cv.arcLength(cnt, True)
    # approx_corners = cv.approxPolyDP(cnt, epsilon, True)
    # approx_corners = approx_corners[:4]
    # approx_corners = sorted(np.concatenate(approx_corners).tolist())
    for cnt in contours:
        cv.drawContours(img, cnt, -1, (0, 255, 0), 3) 
    # cv.imshow('contours', img)
    # cv.waitKey()


    # Putting corner points into numpy array
    src = get_src_pts(src, img.shape[0], img.shape[1])
    # print(src)
    # w = int(max(src[:,0]) - min(src[:,0]))
    # h = int(max(src[:,1]) - min(src[:,1]))
    h = 245
    w = 950
    # print(h,w)

    dst = np.float32([[0,0],[w,0],[0,h],[w,h]])
    # print(dst)

    matrix = cv.getPerspectiveTransform(src,dst)

    # H, extra = cv.findHomography(srcPoints=src, dstPoints=dst, method=cv.RANSAC, ransacReprojThreshold=3.0)

    warp = cv.warpPerspective(img, matrix, (w,h), flags=cv.INTER_LINEAR)

    cv.imshow('warp', warp)
    cv.waitKey()
    cv.destroyAllWindows()

    return warp

# for n in range(1, 11):
    
n = 11

#readin image
img = cv.imread('test_images/test%d.jpg' % n)
# img = cv.imread('test_images/test.png')
# img = cv.imread('capture%d.png' % n)

#resize image
r = img.shape[0]
c = img.shape[1]
# print(r,c)

factor = 1/((r*c)/500000)**(1/2)
img = cv.resize(img, None, fx = factor, fy = factor, interpolation= cv.INTER_AREA)
# cv.imshow('resize', warp)
# r = img.shape[0]
# c = img.shape[1]
# print(r,c)

cv.imshow('img', img)
cv.waitKey()

# warping image
warp = warping(img)
# warp = img.copy()


#resize image
r = warp.shape[0]
c = warp.shape[1]
# print(r,c)

factor = 1/((r*c)/500000)**(1/2)
warp = cv.resize(warp, None, fx = factor, fy = factor, interpolation= cv.INTER_AREA)
# cv.imshow('resize', warp)
r = warp.shape[0]
c = warp.shape[1]
# print(r,c)

#crop the image 
crop = 20
warp = warp[crop:-crop, crop:-crop]
# cv.imshow('crop', warp)

#border the image
bor = 20
col = 150
warp= cv.copyMakeBorder(warp,bor,bor,bor,bor,cv.BORDER_CONSTANT,value=[col,col,col])
cv.imshow('border', warp)
cv.waitKey()
cv.destroyAllWindows()

# threshold
thresh, gray = filter(warp)
cv.imshow('thresh', thresh)
cv.waitKey()
cv.destroyAllWindows()

#segmentation
output, totalSections, sector = segment(thresh, gray, warp)
cv.waitKey()
cv.destroyAllWindows()

#Output sector with mouse cursor
mouse_sensing()
