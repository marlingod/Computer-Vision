
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import matplotlib as plt

def angleCos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def findSquares(img):
    img= cv2.imread(img)
    #img = cv2.GaussianBlur(img, (5, 5), 0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    squares = []
    _retval, bin = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)
    bin, contours, _hierarchy = cv2.findContours(bin, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    
    hierarchy = _hierarchy[0]
    
    for comp in zip(contours, hierarchy):
        currentContour = comp[0]
        currentHierachy = comp[1]
        if currentHierachy[3] == -1 :
            cnt_len = cv2.arcLength(currentContour, True)
            currentContour = cv2.approxPolyDP(currentContour, 0.03*cnt_len, True)
            if len(currentContour) == 4 and cv2.contourArea(currentContour) < 990 and cv2.contourArea(currentContour) > 399 and cv2.isContourConvex(currentContour):
                currentContour = currentContour.reshape(-1, 2)
                max_cos = np.max([angleCos( currentContour[i], currentContour[(i+1) % 4], currentContour[(i+2) % 4] ) for i in xrange(4)])
                if max_cos < 0.2:
                    squares.append(currentContour)
    return squares

# create a function that take image and create and ordered top to bottom array of questions
def sortedQuestions(img):
    questions_ord =[]
    questions =[]
    squareTotal = findSquares(img)
    for c in squareTotal:
        # compute the bounding box of the contour, then use the
        # bounding box to derive the aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        a = np.sum(cv2.boundingRect(c))
        # in order to label the contour as a question, region
        # should be sufficiently wide, sufficiently tall, and
        # have an aspect ratio approximately equal to 1+
        if (w > 20 and w<= 35 and h >20 and h <= 35 and ar >=0.8 and ar <=1.2 and y > 200 and x > 500): # and  if (range(a-4, a+4) not in sumOf):
            questions.append(c)  
    questions_ord= contours.sort_contours(questions, method="top-to-bottom")[0]
    return questions_ord
