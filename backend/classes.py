
# create an arry of bndbx objects from annotations

import numpy as np

from PySide2.QtGui import QPixmap, QImage
from PIL import Image , ImageDraw

from matplotlib import cm

# bndbx contains the second ,bndbx and the part of the image specified by the bndbx
class BndBx:
    spatial_grp_ref = None

    def __init__(self, second, bndbx, img_crop):
        self.second = second
        self.bndbx = bndbx
        self.img_crop = np.array(img_crop)


class TemporalGroup:
    def __init__(self):
        self.visited = False
        self.grp_bndbxes = []
        self.start = []
        self.reconstructed_bndbx = []
        self.reconstructed_img = []


class SpatialGroup:

    def __init__(self):
        self.grp_bndbxes = []
        self.temporal_grps = []

    def add_bndbx(self, bndbx_obj):
        self.grp_bndbxes.append(bndbx_obj)

    def absorb_grp(self, spatial_grp):
        c = 0
        for bndbx_obj in spatial_grp.grp_bndbxes:
            # print("stuck: ", c)
            c += 1
            self.add_bndbx(bndbx_obj)
            bndbx_obj.spatial_grp_ref = self

class SummaryObj:
    def __init__(self):
        self.bndbxes=[]
        self.bndbx_timestamps=[]
        self.img=[]

    # call this after bndbxes are filled
    def set_img(self,img):
        self.shape = img.shape

        image = Image.fromarray(np.uint8(cm.gist_earth(img) * 255))

        for x,box in enumerate(self.bndbxes):
            draw = ImageDraw.Draw(image)
            draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="black",width=5)
            # cv2.imwrite('backend/summary/' + str(i) +"_"+str(s.bndbx_timestamps[x]) +".jpg",im_np[box[1]:box[3],box[0]:box[2]])
        self.img =image.convert('L')
        self.img=np.array(np.array(self.img))

        print(self.shape)
        # img = np.transpose(img, (1, 0, 2)).copy()
        qimage = QImage(self.img, self.shape[1], self.shape[0],
                        QImage.Format_Grayscale8)

        self.img = QPixmap(qimage)

def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

