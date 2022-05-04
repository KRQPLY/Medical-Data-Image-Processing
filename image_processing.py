import cv2 as cv
import numpy as np
import os
import sys


os.system("cls")
cv.namedWindow("Window")
cv.namedWindow("Post")
cv.namedWindow("Filters", cv.WINDOW_NORMAL)
cv.namedWindow("Contours", cv.WINDOW_NORMAL)

catalog = './staw_biodrowy'
prefix = 'IMA'
postfix = '.png'
fi0 = 80
fi1 = 89
dfi = 1
di = 0
i = fi0

fn = catalog + '/' + prefix + str(i) + postfix
fn2 =  "nr" + str(i)
if not os.path.exists(fn):
    sys.exit('File does not exist')
img = cv.imread(fn, 0)
iROI = img.copy()

def nothing(x):
    pass

def filter():
    global thr
    th = cv.getTrackbarPos('thresh', 'Filters')
    image = img.copy()
    if cv.getTrackbarPos('blur1', 'Filters') == 1:
        image = cv.blur(image, (3,3))
    if cv.getTrackbarPos('Gaussian', 'Filters') == 1:
        image = cv.GaussianBlur(image, [5,5], 0)
    _, thr = cv.threshold(image, th , 255, cv.THRESH_BINARY )
    if cv.getTrackbarPos('blur2', 'Filters') == 1:
        thr = cv.blur(thr, [3,3])
    if cv.getTrackbarPos('medianBlur', 'Filters') == 1:
        thr = cv.medianBlur(thr, 5)
    kernel = np.ones((cv.getTrackbarPos('kernel', 'Filters')*2+1,cv.getTrackbarPos('kernel', 'Filters')*2+1), np.uint8)
    if cv.getTrackbarPos('erosion', 'Filters') == 1:
        thr = cv.erode(thr, kernel, iterations=cv.getTrackbarPos('iterations', 'Filters'))
    if cv.getTrackbarPos('dilation', 'Filters') == 1:
        thr = cv.dilate(thr, kernel, iterations=cv.getTrackbarPos('iterations', 'Filters'))
    if cv.getTrackbarPos('Canny', 'Filters') == 1:
        thr = cv.Canny(thr, 50, 250)
    cv.setWindowTitle('Window', fn2 + "   " + str(th))
    cv.imshow('Window', img)

def set_roi():
    global iROI
    global x1, y1
    x1 = cv.getTrackbarPos('x1', 'Filters')
    x2 = cv.getTrackbarPos('x2', 'Filters')
    y1 = cv.getTrackbarPos('y1', 'Filters')
    y2 = cv.getTrackbarPos('y2', 'Filters')
    if x1 >= x2:
        if x1 > 256:
            x1 = x2 - 10
        else:
            x2 = x1 + 10
    if y1 >= y2:
        if y1 > 256:
            y1 = y2 - 10
        else:
            y2 = y1 + 10
    iROI = thr[y1:y2,x1:x2]
    cv.imshow('Post', iROI)

def click_event(event, x, y, flags, param):
    global array, contour_x, contour_y
    if event == cv.EVENT_RBUTTONDOWN:
        array = 0
        contour_x = 0
        contour_y = 0
        contours, _ = cv.findContours(iROI, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        contoursLength = len(contours)
        contoursSorted = sorted(contours, key = cv.contourArea , reverse = True)
        biggestContours = list()
        numberOfContoursWanted = cv.getTrackbarPos('contours', 'Contours')
        if contoursLength >= numberOfContoursWanted:
            for i in range(numberOfContoursWanted):
                maxContour = contoursSorted[i]
                biggestContours.append(maxContour)
            if cv.getTrackbarPos('deleteCont', 'Contours') == 1:
                contIndx1 = cv.getTrackbarPos('cont1', 'Contours')
                contIndx2 = cv.getTrackbarPos('cont2', 'Contours')
                contIndx3 = cv.getTrackbarPos('cont3', 'Contours')
                contIndx4 = cv.getTrackbarPos('cont4', 'Contours')
                contIndcs = {contIndx1, contIndx2, contIndx3, contIndx4}
                contIndcsSorted = sorted(contIndcs, reverse = True)
                for contIndx in contIndcsSorted:
                    if contIndx < numberOfContoursWanted:
                        biggestContours.pop(contIndx)
            for contour in biggestContours:
                if cv.getTrackbarPos('hole', 'Contours') == 1:
                    negative = 1
                    extLeft = contour[contour[:, :, 0].argmin()][0][0]
                    extRight = contour[contour[:, :, 0].argmax()][0][0]
                    extTop = contour[contour[:, :, 1].argmin()][0][1]
                    extBot = contour[contour[:, :, 1].argmax()][0][1]
                    for contour2 in biggestContours:
                        extLeft2 = contour2[contour2[:, :, 0].argmin()][0][0]
                        extRight2 = contour2[contour2[:, :, 0].argmax()][0][0]
                        extTop2 = contour2[contour2[:, :, 1].argmin()][0][1]
                        extBot2 = contour2[contour2[:, :, 1].argmax()][0][1]
                        if extLeft > extLeft2 and extRight < extRight2 and extTop > extTop2 and extBot < extBot2:
                            negative = -1
                            break
                else:
                    negative = 1
                moment = cv.moments(contour)
                array1 = moment['m00']
                contour1_x = x1 + moment['m10']/(moment['m00'] + 1e-5)
                contour1_y = y1 + moment['m01']/(moment['m00'] + 1e-5)
                array = array + negative * array1
                contour_x = (array * contour_x + negative * array1 * contour1_x)/(array + negative * array1 + 1e-5)
                contour_y = (array * contour_y + negative * array1 * contour1_y)/(array + negative * array1 + 1e-5)
            os.system("cls")
            print('Array: ', str(array), 'x: ',str(contour_x), "y: ", str(contour_y))
        else:
            os.system("cls")
            print('Not enough contours')
        for contour in biggestContours:
            cv.drawContours(img, contour, -1, (255, 255, 255), 1, offset = (x1, y1))
        cv.imshow("okno2", img)
    if event == cv.EVENT_LBUTTONDOWN:
        os.system("cls")
        sortedKeys = sorted(contours_params.keys())
        for number in sortedKeys:
            print("Slice number: " + str(number))
            print("Array: " + str(contours_params[number]["array"]))
            print("x: " + str(contours_params[number]["x"]))
            print("y: " + str(contours_params[number]["y"]))


cv.createTrackbar('thresh', 'Filters', 80, 255, nothing)
cv.createTrackbar('x1','Filters', 0, 512, nothing)
cv.createTrackbar('x2','Filters', 512, 512, nothing)
cv.createTrackbar('y1', 'Filters', 0, 512, nothing)
cv.createTrackbar('y2', 'Filters', 512, 512, nothing)
cv.createTrackbar('blur1', 'Filters', 0, 1, nothing)
cv.createTrackbar('Gaussian', 'Filters', 0, 1, nothing)
cv.createTrackbar('blur2', 'Filters', 0, 1, nothing)
cv.createTrackbar('medianBlur', 'Filters', 0, 1, nothing)
cv.createTrackbar('erosion', 'Filters', 0, 1, nothing)
cv.createTrackbar('dilation', 'Filters', 0, 1, nothing)
cv.createTrackbar('Canny', 'Filters', 0, 1, nothing)
cv.createTrackbar('kernel', 'Filters', 1, 5, nothing)
cv.createTrackbar('iterations', 'Filters', 1, 5, nothing)
cv.createTrackbar('contours','Contours', 1, 10, nothing)
cv.createTrackbar('deleteCont','Contours', 0, 1, nothing)
cv.createTrackbar('cont1','Contours', 0, 10, nothing)
cv.createTrackbar('cont2','Contours', 1, 10, nothing)
cv.createTrackbar('cont3','Contours', 2, 10, nothing)
cv.createTrackbar('cont4','Contours', 3, 10, nothing)
cv.createTrackbar('hole','Contours', 0, 1, nothing)
cv.setMouseCallback('Post', click_event)

contours_params = dict()

filter()
set_roi()

while True:
    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break
    elif chr(k) == ']':
        di = dfi
    elif chr(k) == '[':
        di =- dfi
    elif k == 32:
        if 'array' in globals():
            if str(i) not in contours_params:
                contours_params[i] = {}
                contours_params[i]["array"] =  array
                contours_params[i]["x"] = contour_x
                contours_params[i]["y"] = contour_y
                print("Contours saved")
    elif k == 8:
        if 'array' in globals():
            if i in contours_params.keys():
                contours_params.pop(i)
                print("Contours removed")
    else:
        pass

    i = i + di
    if i > fi1:
        i = fi1
        
    if i < fi0:
        i = fi0
    
    fn = catalog+'/'+prefix+str(i)+postfix
    fn2 = 'nr' + str(i)
    img = cv.imread(fn, 0)
    if img is None:
        os.system("cls")
        print('Nie ma pliku o nazwie '+ fn)
        i = i + di
        fn = catalog + '/' + prefix + str(i) + postfix
        fn2 =  "nr" + str(i)
        img = cv.imread(fn, 0)
    filter()
    set_roi()
    di = 0

cv.destroyAllWindows()