import argparse
import datetime
import imutils
import math
import cv2
import numpy as np
import socketio


width = 800
heigth = 800

textIn = 0
textOut = 0

# creates a new Async Socket IO Server
socket = socketio.Client()
socket.connect('http://localhost:3000')

def testIntersectionIn(x, y):
    res = -450 * x + 400 * y + 157500
    if ((res >= -450) and (res <= 1000)):
        return True
    return False


camera = cv2.VideoCapture('test2.mp4')
#camera = cv2.VideoCapture(0)

firstFrame = None

while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    text = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 70, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 10000:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)

        # draw around abs diff on frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # draw threshold line to consider in
        cv2.line(frame, (width / 2 - 50, 0), (width / 2 - 50, heigth), (0, 0, 255))  # red line

        # draw red point on rectangle center
        rectagleCenterPont = ((x + x + w) / 2, (y + y + h) / 2)
        cv2.circle(frame, rectagleCenterPont, 1, (0, 0, 255), 5)

        # test if person in on store
        if (testIntersectionIn((x + x + w) / 2, (y + y + h) / 2)):
            textIn += 1
            socket.emit('entryPerson', {})

    # map the quit button
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.putText(frame, "In: {}".format(str(textIn)), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow("People Counter", frame)

socket.disconnect()
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
