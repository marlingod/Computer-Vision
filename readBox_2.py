
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import matplotlib as plt
import os

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
    somes = []
    for comp in zip(contours, hierarchy):
        currentContour = comp[0]
        currentHierachy = comp[1]
        somes.append(comp)
        #if currentHierachy[3] == -1 and  currentHierachy[2] != -1 :
        cnt_len = cv2.arcLength(currentContour, True)
        currentContour = cv2.approxPolyDP(currentContour, 0.03*cnt_len, True)
        if len(currentContour) == 4 and cv2.contourArea(currentContour) < 1024 and cv2.contourArea(currentContour) > 200 and cv2.isContourConvex(currentContour):
            currentContour = currentContour.reshape(-1, 2)
            max_cos = np.max([angleCos( currentContour[i], currentContour[(i+1) % 4], currentContour[(i+2) % 4] ) for i in xrange(4)])
            if max_cos < 0.2:
                squares.append(currentContour)

    
    return squares
    #return somes

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
        if (w > 22 and w<= 35 and h >22 and h <= 35 and ar >=0.8 and ar <=1.3 and y > 100 and x > 500): # and  if (range(a-4, a+4) not in sumOf):
            questions.append(c)  
    questions_ord= contours.sort_contours(questions, method="top-to-bottom")[0]
    return questions_ord


# create function that take the squares boxes and output sorted y,x, and pts 
# of the squares box
def SquaresWithCoords(squares):
    squaresRec = []
    squareSorted =[]    
    for c in  range(0, len(squares)):
        (x, y, w, h) = cv2.boundingRect(squares[c])
        pt =(x+ y+ w+h)
        coord = x+y
        da = (y,x,coord, squares[c]) 

        squaresRec.append(da)
    squareSorted = sorted(squaresRec, key=lambda x: (x[0], x[2]))
        #step three : Sorted the list from step 2 by y ais and the sum of the x+y
    return squareSorted


# Create a function that will group squares by the y axis 
# assuming that y axis are withn 4 pixels
def SquaresGroupByYAxis(squareSorted):
    from itertools import groupby
    _bins   = [] # array to hold the unique y value that are not in range(4)pixels
    bins    = [] # create the bin with the y + 10      
    yValues = [] # get all the yvalue of the squares 
    squaresWithInds =[] # Assign index to the squars
    squaresGroupedByInds=[] # group the squares by the index
        #
    for i in  range(0, len(squareSorted)):
        a= squareSorted[i][0]
        if len(_bins) ==0:
            _bins.append(a)
        elif a not in range(0, _bins[-1]+4):
                _bins.append(a)

    # Substep 2: create a new list with is previous list + 3 which is now the bin

    for i in _bins:
        bins.append(i+10)
    #bins0=np.array(bins)
    
    # get all the y Value
    for i in squareSorted:
        yValues.append(i[0])


    #Step five: digit the step three list using the step four b bins
    inds = np.digitize(yValues,np.array(bins),right=True)

    # step six : zip the bin with the with the sorted the list from step three
    
    squaresWithInds = zip(squareSorted, inds)

    # step seven: group the bin value
   
    for key,valuesiter in groupby(squaresWithInds, key=lambda s:s[1]):
        somet = (key, list(v[0]for v in valuesiter))
        squaresGroupedByInds.append(somet)    
    
    # step eight: Select only the min and max value of  y + x of teh array 
    # to addd to the step eight: only add new value
    #if x value  not in range of the first save value
    realValuesWithInd =[]
    #rel =[]
    for i in squaresGroupedByInds:
        thing =[]
        realValue = []
        coords =[]
        for j in i[1]:
            thing.append(j[2])
        for z in i[1]:
            if z[2]==np.max(thing): 
                if z[2] not in coords: 
                    realValue.append(z[3])
                    coords.append(z[2])
            if z[2]==np.min(thing): 
                if z[2] not in coords: 
                    realValue.append(z[3])
                    coords.append(z[2])
            np.unique(realValue)

        val = (i[0], realValue) #val = (i[0], theother4) # 
        #rel.append(realValue)

        realValuesWithInd.append(val)  
    return realValuesWithInd

# create a function to ge the second page answer:

def secondpageAnswers(img):
    # apply the sorted function
    answers=[]
    sortedQ = sortedQuestions(img)
    
    # apply the sorted with y function
    Squareswithcoord = SquaresWithCoords(sortedQ)
    
    # apply the SquaresGroupByYAxis function
    squaresQuestions = SquaresGroupByYAxis(Squareswithcoord)

    # get the squares box n array
    boxArray = []
    for i in squaresQuestions:
        print i[1][0]
        boxArray.append(i[1][0])
        if len(i) ==2 :boxArray.append(i[1])

    squaresArray = []

    for (t,ds) in enumerate(squaresQuestions,1):
        sArray =(t, ds[1])
        squaresArray.append(sArray)
    # answers the questions
    imgcv2 = cv2.imread(img)
    imgGray = cv2.cvtColor(imgcv2, cv2.COLOR_BGR2GRAY)
    paper = cv2.threshold(imgGray , 0, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)[1]
    (head, tail) = os.path.split(img)
    (core_filename, ext) = os.path.splitext(tail)

    colorfile = core_filename + '.color.jpeg'

    if len(squaresQuestions) == 19:
        for  i in squaresArray:
            q = i[0]
            cnt = len(i[1])
            if cnt ==2:
                # sort left to right
                cnts = contours.sort_contours(i[1])[0]
                #cnts =sorted(i[1], key =lambda b: b[0][0])
                #cnts = i[1]
                squared = None
                squar =[]
                squar2 =[]
                for (j, c) in enumerate(cnts):


                    # construct a mask that reveals only the current
                    # "squared" for the question
                    (x,y,w,h) = cv2.boundingRect(c)
                    mask = np.zeros(paper.shape, dtype="uint8")
                    cv2.drawContours(mask, [c], -1, 255, -1)
                    #print (j, boundingBoxes)
                    # apply the mask to the thresholded image, then
                    # count the number of non-zero pixels in the
                    # squared area
                    mask = cv2.bitwise_and(paper, paper, mask=mask)
                    total = (cv2.countNonZero(mask))
                    #if w > 28: 
                        #total = (cv2.countNonZero(mask)) -200
                    #else : 
                        #total = (cv2.countNonZero(mask)) 
                    #print q, (j, w, x,y), total  
                    da = (w, total,x)
                    squar.append(da)
                    #print squar

                #print squar, squar[1][0], squar[0][0]
                if squar[1][0] ==squar[0][0]: # the with is the same
                    if squar[1][2]> squar[0][2] : a = 'N' # if the 
                    else : a = 'Y'
                elif squar[1][0] !=squar[0][0]:
                    if squar[0][0] == max(squar[1][0],squar[0][0]):
                        fav = (squar[0][2],squar[0][1] -150)
                        favo = (squar[1][2], squar[1][1])
                        squar2.append(fav)
                        squar2.append(favo )
                        if abs(squar2[1][1]- squar2[0][1]) <40: a ='Nothing'
                        elif squar2[1][1]> squar2[0][1] : a = 'N' # if the 
                        else : a = 'Y'                
                    elif squar[1][0] == max(squar[1][0],squar[0][0]):
                        fav = (squar[1][2],squar[1][1] -150)
                        favo = (squar[0][2], squar[0][1])
                        squar2.append(fav)
                        squar2.append(favo )  
                        if abs(squar2[1][1] - squar2[0][1]) < 40: a ='Nothing'
                        elif squar2[1][1]> squar2[0][1] : a = 'N' # if the 
                        else :  a = 'Y'               
                #print squar,squar2
                #if len(squar2)==2: print 
                answer = (q, a)
                ques = (q, answer)
                answers.append(answer)
            if cnt==1:
                answer =(q,'NA')
                answers.append(answer)

        # Save the result to a file
        questionFile = core_filename + '.txt'
        thepath  = os.path.join(outdir, 'Success/QA')
        if not os.path.exists(thepath): os.makedirs(thepath)
        completeN = os.path.join(thepath,questionFile)
        #save the answer
        with open(completeN, 'w') as file_save:
          file_save.write(str(answers))

        # write the debug jpeg file


        thecontours2 = cv2.drawContours(img.copy(), boxArray, -1, (0,127,255),2)
        thepath  = os.path.join(outdir, 'Success/Debug')
        if not os.path.exists(thepath): os.makedirs(thepath)
        debug_pathname = os.path.join(thepath, colorfile)
        cv2.imwrite(debug_pathname, thecontours2)

        return 0
    elif len(squaresQuestions) != 19:
        fileNotProcess = str(core_filename) + ' ==> : '  + str(len(sortedQ)) + ' Squares '
        questionFile = core_filename + '.txt'
        thepath  = os.path.join(outdir, 'Failed/QA')
        if not os.path.exists(thepath):
        os.makedirs(thepath)
        completeN = os.path.join(thepath,questionFile)

        with open(completeN, 'w') as file_save:
          file_save.write(str(fileNotProcess))

        # save the debug
        thecontours2 = cv2.drawContours(img.copy(), boxArray, -1, (0,127,255),2)
        thepath  = os.path.join(outdir, 'Failed/Debug')
        if not os.path.exists(thepath):
        os.makedirs(thepath)
        debug_pathname = os.path.join(thepath, colorfile)
        cv2.imwrite(debug_pathname, thecontours2)

        return 1


