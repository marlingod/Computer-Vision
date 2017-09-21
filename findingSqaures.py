# create function that will print answers and questions:
def firstPageAnswers(img):
    # read the image in cv2 format
    imgcv2 = cv2.imread(img)
    imgGray = cv2.cvtColor(imgcv2, cv2.COLOR_BGR2GRAY)
    answers= []
    filename, file_extension = os.path.splitext(img)
    contractNumber = str((filename.split("-")[0]).strip())
    # get the sorted questions
    # to do: if the total numbers of questions is not equal to 32 then move mark the file as unreadable
    sortedQ = sortedQuestions(img)
    paper = cv2.threshold(imgGray , 0, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)[1]
    mask = np.zeros(paper.shape, dtype="uint8")
    mask = cv2.bitwise_and(paper, paper, mask=mask)
    thecontours2 = cv2.drawContours(imgcv2.copy(), sortedQ, -1, (0,127,255),2)
    #cv2.imwrite('thecontour_001el.png',thecontours1)
    #cv2.imwrite('thecontour_mask.png',mask)
    colorfile = contractNumber +'.jpeg'
    cv2.imwrite(colorfile,thecontours2)
    
    for (q, i) in enumerate(np.arange(0, len(sortedQ), 2),1): # a
        # sort the contours for the current question from
        # left to right, then initialize the index of the
        # bubbled answer
        cnts = contours.sort_contours(sortedQ[i:i + 2])[0]
        bubbled = None
            # loop over the sorted contours
        # array to store the index and the index and the total 
        theloop= []
        que = []
        for (j, c) in enumerate(cnts):
            # construct a mask that reveals only the current
            # "bubble" for the question
            mask = np.zeros(paper.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            # apply the mask to the thresholded image, then
            # count the number of non-zero pixels in the
            # bubble area
            mask = cv2.bitwise_and(paper, paper, mask=mask)
            total = cv2.countNonZero(mask)
            #(x, y, w, h) = cv2.boundingRect(c)
            #sqaure = (x, y, w, h)

            # if the current total has a larger number of total
            # non-zero pixels, then we are examining the currently
            # bubbled-in answer
            #bubbled = (total, j)
            #que.append(bubbled)
            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)

                        #print bubbled
        #color = (0, 0, 255)
            if bubbled[1] ==0:
                a = 'Y'
            else:
                a ='N'
        answer = (q, a)
        ques = (q, answer)
        answers.append(answer)
        questionFile = contractNumber+ '.txt'
        completeN =os.path.join('path',questionFile)
        with open(completeN, 'wb') as file_save:
            file_save.write(str(answers))
            
        answerto = contractNumber+'-'+ str(len(sortedQ))+'.txt'
        completeN =os.path.join('path',answerto)
        with open(completeN, 'wb') as answer_save:
            answer_save.write(str(len(sortedQ)))
        #print que
    #return answers
    #return len(sortedQ)
