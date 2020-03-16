import cv2
from .torch import *
#
# import torch
from .torchvision import *
# import .torch ,torchvision
import os
import time
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

def get_predictor():

    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
    cfg.MODEL.WEIGHTS = "model_final_1500.pth"
    return DefaultPredictor(cfg)


# Visualizing output

# v = Visualizer(im[:, :, ::-1], MetadataCatalog.get('../31141.jpg'), scale=1.2)
# v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
# cv2.imshow("marked",v.get_image()[:, :, ::-1])
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()


def get_annotations(all_frames=0):
    time_start=time.time()
    annotations=[]
    predictor=get_predictor()
    im = cv2.imread('../02491.jpg')
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1], MetadataCatalog.get('../31141.jpg'), scale=1.2)
    v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2.imshow("marked",v.get_image()[:, :, ::-1])

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # for second,frame in enumerate(all_frames):
    #     outputs = predictor(frame)
    #     boxes=[]
    #     print(second ,end=" ")
    #     for pred_box in outputs["instances"].pred_boxes:
    #
    #         # print(pred_box)
    #         pred_box = pred_box.int()
    #
    #         box = [pred_box[0].item(), pred_box[1].item(), pred_box[2].item(), pred_box[3].item()]
    #
    #         # print(box)
    #         boxes.append(box)
    #     annotations.append(boxes)
    # time_end=time.time()
    # print("It took %d seconds for annotation." % (time_end - time_start))

    return annotations

