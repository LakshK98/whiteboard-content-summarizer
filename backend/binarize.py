import cv2
import numpy as np
import time

def binarize_frames(all_frames):
    time_start=time.time()
    for frame_number,frame in enumerate(all_frames):
        print(frame_number,end=" ")
        img = frame
        bilateral = cv2.bilateralFilter(img, 15, 13.5, 4)
        medianBlur = cv2.medianBlur(bilateral, 33)

        # for x,a in medianBlur,img:

        image1 = np.int32(img)
        image2 = np.int32(medianBlur)
        # subbract medianblur from image
        subractedImage = np.subtract(image1, image2)
        # convert positive values to zero
        subractedImage[subractedImage > 0] = 0
        # convert negative values to positive
        subractedImage = np.negative(subractedImage)

        b, g, r = cv2.split(subractedImage)
        # max of 3 channels
        singleChannel = np.maximum.reduce([b, g, r])

        singleChannel = np.uint8(singleChannel)

        # cv2.imwrite('/Users/lakshkotian/Documents/ly_pipeline/binarization/singlChannel.jpg', singleChannel)

        # inverse colors
        # singleChannel = cv2.bitwise_not(singleChannel)
        thr, ret = cv2.threshold(singleChannel, 0, 255, cv2.THRESH_OTSU)

        thr, binaryImage = cv2.threshold(singleChannel, thr, 255, cv2.THRESH_BINARY_INV);

        all_frames[frame_number] = binaryImage

    time_end = time.time()
    print("It took %d seconds for binarize." % (time_end - time_start))

    return all_frames
