
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import matplotlib as plt
import os
from itertools import groupby


def angleCos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

# the function that an pic, find sqaures and 
#return the sqaures and return the x, y, contour, and parenthierachy
# sorted the list top to bottom and left to right
def findSquaresHier(img):
    ## rerun the whole process by draging the hierachy around
    img= cv2.imread(img)
    #img = cv2.GaussianBlur(img, (5, 5), 0)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    squares = []
    _retval, bin = cv2.threshold(imgGray, 0, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)
    bin, contours, _hierarchy = cv2.findContours(bin, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    hierarchy = _hierarchy[0]
    sqaures =[]
    contoursHier = []
    
    for comp in zip(contours, hierarchy):
        currentContour = comp[0]
        currentHierachy = comp[1]
        child = currentHierachy[2]
        parent = currentHierachy[3]
        #print currentContour , parent

        #if currentHierachy[3] == -1 and  currentHierachy[2] != -1 :
        cnt_len = cv2.arcLength(currentContour, True)
        currentContour = cv2.approxPolyDP(currentContour, 0.03*cnt_len, True)
        if len(currentContour) == 4 and cv2.contourArea(currentContour) < 1024 and cv2.contourArea(currentContour) > 200 and cv2.isContourConvex(currentContour):
            currentContour = currentContour.reshape(-1, 2)
            max_cos = np.max([angleCos( currentContour[i], currentContour[(i+1) % 4], currentContour[(i+2) % 4] ) for i in xrange(4)])
            if max_cos < 0.2:
                (x, y, w, h) = cv2.boundingRect(currentContour)
                squares.append(currentContour)
                ar = w / float(h)
                if (w > 22 and w<= 35 and h >22 and h <= 35 and ar >=0.8 and ar <=1.3 and y > 100 and x > 500): 
                    pt =(x+ y+ w+h)
                    coord = x+y       
                    cntHier = (y,x,coord, currentContour, parent)
                    contoursHier.append(cntHier)
                
    questions = sorted(contoursHier, key=lambda x: (x[0], x[1]))  
    return questions
    

# create that will create bin for the squares and group them
# if they are betwen +/- y ranges
# input: array of the squares
# output: Question number, (y,x,cnt, hier)
def GroupSquaresByAxis(arr):
    # Create the bin and get teh all the y values
    _bins = []
    yValues = []

    for i in  range(0, len(arr)):
        a= arr[i][0]
        yValues.append(a)
        if len(_bins) ==0:
            _bins.append(a+10)
        elif a not in range(0, _bins[-1]+4):
                _bins.append(a+10)


    # digitize the y values using the the  _bin array
    inds = np.digitize(yValues,np.array(_bins),right=True)

    # step six : zip the bin with the with the sorted the list from step three
    #squaresWithInds =[]
    squaresWithInds = zip(arr, inds)

    # group the elements by the bins
    squaresGroupedByInds=[]
    for key,valuesiter in groupby(squaresWithInds, key=lambda s:s[1]):
        somet = (key, list(v[0]for v in valuesiter))
        squaresGroupedByInds.append(somet)
    return squaresGroupedByInds 

# function to select only two squares by questions:
#input: result of the GroupSquaresByAxis function
# output :  Array of question, 2 questions+ hier
def selectTwoSquares(squaresGroupedByInds):
    # for sqaures with Ind:
    # if the number of hier -2 take the two element:
    # If not :

    twoSquares =[]
    squareSize = len(squaresGroupedByInds)
    #hier_ext = [0]* squareSize
    #hier_int = [0]* squareSize
    for i in range(len(squaresGroupedByInds)):
        q =squaresGroupedByInds[i][0]
        theArr = squaresGroupedByInds[i][1] # list of the array in the questions
        arrSize = len(theArr)
        theContours =[]
        #print  q, hier, y, x, pt
        #print j
        # if the number of array >2:
            # if the total number of hier -1 is 2 take them.
            # if the number hier(-1) is 1: check if the number of the inside is2 :if it is 2 then take them

        # if the number of array is 2:
            #check if different x: Add the array
            # if the same x # mark the question as unsawerable:
        # get the count number hier(-1)
        #hier_ext = [0]* squareSize
        hier_ext =0
        hier_int =0
        #hier_int = [0]* squareSize
        for j in range(len(theArr)):
            hier = theArr[j][4]
            if hier ==-1   : hier_ext += 1
            elif hier !=-1 : hier_int +=1
        # get the count number hier(not -1)
        #print hier_int
        if arrSize ==3  : # check if the size is more than 2

            if hier_ext !=2: # check if the ext size is 2

                for j in theArr:
                    contour =j[3]
                    y = j[0]
                    x = j[1]
                    pt = j[2]
                    hier =j[4]
                    asso = (contour,x, hier)
                    if hier != -1 :theContours.append(asso)
                    #print theContours
                da = (q,theContours)
                twoSquares.append(da)
            if hier_ext ==2: # check if the ext size is 2

                for j in theArr:
                    contour =j[3]
                    y = j[0]
                    x = j[1]
                    pt = j[2]
                    hier =j[4]
                    asso = (contour,x, hier)
                    if hier == -1 :theContours.append(asso)
                    #print theContours
                da = (q,theContours)
                twoSquares.append(da)
        elif arrSize == 4  : # check if the size is more than 2
                for j in theArr:
                    contour =j[3]
                    y = j[0]
                    x = j[1]
                    pt = j[2]
                    hier =j[4]
                    asso = (contour,x, hier)
                    if hier == -1 :theContours.append(asso)
                    #print theContours
                da = (q,theContours)
                twoSquares.append(da)
        elif arrSize == 2:
            xvalue1 = theArr[0][1]
            xvalue2 = theArr[1][1]
            if abs(xvalue1 - xvalue2) < 6:
                da = (q, []) 
                twoSquares.append(da)

            if abs(xvalue1 - xvalue2) > 6:
                for j in theArr:
                    contour =j[3]
                    y = j[0]
                    x = j[1]
                    pt = j[2]
                    hier =j[4]
                    asso = (contour, x,hier)
                    theContours.append(asso)
                    #print theContours
                da = (q,theContours)
                twoSquares.append(da)

    return  twoSquares

# create  a function that will take image and ouput an array of answer:

def secondPageAnswers(img):
    imgcv2 = cv2.imread(img)
    imgGray = cv2.cvtColor(imgcv2, cv2.COLOR_BGR2GRAY)
    paper = cv2.threshold(imgGray , 0, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)[1]

    #mask the image with zeros
    mask = np.zeros(paper.shape, dtype="uint8")
    mask = cv2.bitwise_and(paper, paper, mask=mask)
    answers= []
    filename, file_extension = os.path.splitext(img)
    contractNumber = str((filename.split("-")[0]).strip())
    # get the sorted questions
    # to do: if the total numbers of questions is not equal to 32 then move mark the file as unreadable

    # Squares Finder:
    squareFind = findSquaresHier(img)

    # group by Axis:
    groupByAxis = GroupSquaresByAxis(squareFind)

    #print len(groupByAxis)
    # get only two squares per questions:
    twoSquares  = selectTwoSquares (groupByAxis)
    #print twoSquares[1]

    answers =[]
    que = []
    for (j,v) in twoSquares:
        vSorted = sorted(v, key=lambda x: x[1])
        siz = len(vSorted)
        result =[]
        bub =None
        if siz ==2:
            for (k,a) in enumerate(vSorted):
                cnt =  a[0]
                x = a[1]
                hier = a[2]
                #print j,cnt,x
                mask = np.zeros(paper.shape, dtype="uint8")
                cv2.drawContours(mask, [cnt], -1, 255, -1)
                mask = cv2.bitwise_and(paper, paper, mask=mask)
                total = cv2.countNonZero(mask)
                _result = (k,total)
                #if bub is None or 
                result.append(_result)
            #print result
            ##get the result
            if abs(result[0][1]- result[1][1]) >50:
                if result[0][1] > result[1][1]:
                    res ='Y'
                    YAnwser =(j,res)
                    answers.append(YAnwser)
                else : 
                    res ='N'
                    NAnwser =(j,res)
                    answers.append(NAnwser)
                #print j, res
            else:
                NullAnswer =(j,"Null")
                answers.append(NullAnswer)
        else:
            cant =(j, "cant answer")
            answers.append(cant)
    return answers   
    
       
