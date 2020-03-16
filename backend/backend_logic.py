from .split_video import *
from PIL import Image , ImageDraw

# from .annotate import *
from .binarize import *
from .classes import *
from .spatiotemporal import *
from .reconstruct_and_merge import *
from .summarize import *
import os
import pickle
import sys
import cv2
from matplotlib import cm

path=""
all_frames=[]
annotations=[]
all_spatial_grps=[]
def split_video_call(path1):
    global path,all_frames
    path =path1
    all_frames = video_to_frames(path)
    # print(os.getcwd())
    # pickle_in = open("backend/n1_binarized.pickle", "rb")
    # all_frames = pickle.load(pickle_in)
    # print(len(all_frames))
    # for i,frame in enumerate(all_frames):
    #     cv2.imwrite("backend/n1/split/" + str(i)+ ".jpg", frame)

    # print(os.getcwd())

    # pickle_out = open("backend/n1_split.pickle", "wb")
    # pickle.dump(all_frames, pickle_out)
    # pickle_out.close()
    return True

def annotate_call():
    global annotations

    # # pickle_in = open(os.path.join(os.path.dirname(sys.executable), "annotations/"+os.path.basename(path)[:-4]+".pickle"),"rb")
    pickle_in = open( "backend/annotations/"+os.path.basename(path)[:-4]+".pickle","rb")

    annotations = pickle.load(pickle_in)


    return True
# print(len(annotations))
# print(len(all_frames))


# annotations = get_annotations(all_frames)

def binarize_call():
    global all_frames
    all_frames = binarize_frames(all_frames)
    # pickle_in = open("backend/n1_binarized.pickle", "rb")
    # all_frames = pickle.load(pickle_in)

    # pickle_out = open("backend/n1_binarized.pickle", "wb")
    # pickle.dump(all_frames, pickle_out)
    # pickle_out.close()
    # for i,image in enumerate(all_frames):
    #     boxes=annotations[i]
    #     image=Image.fromarray(np.uint8(cm.gist_earth(image) * 255))
    #     for  box in boxes:
    #         draw = ImageDraw.Draw(image)
    #         draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="black")
    #     image = image.convert('RGB')
    #
    #     image.save('backend/annotate/' + str(i)+".jpg")

    # im=cv2.imread(all_frames[100])

    #
    return True

def spatiotemporal_call():
    global all_spatial_grps
    all_spatial_grps = create_spatiotemporal_groups(all_frames, annotations)

    return True


def reconstruct_and_merge_call():
    global all_spatial_grps
    all_spatial_grps = reconstruct_frames(all_spatial_grps)
    # for i,spatial_group in enumerate(all_spatial_grps):
    #
    #     for j,temporal_grp in enumerate(spatial_group.temporal_grps):
    #         cv2.imwrite("backend/reconstruct/" + str(i)+"_"+str(j) + ".jpg", temporal_grp.reconstructed_img )
    all_spatial_grps=merge_similar_temporal_grps(all_spatial_grps)
    # for i,spatial_group in enumerate(all_spatial_grps):
    #     for j,temporal_grp in enumerate(spatial_group.temporal_grps):
    #         cv2.imwrite("backend/merged/" + str(i)+"_"+str(j) + ".jpg", temporal_grp.reconstructed_img )

    return True



#
def summary_call():
    # summary_obj_list= get_summary(all_spatial_grps,len(all_frames),len(all_frames[0]),len(all_frames[0][0]))
    pickle_in = open("backend/n1_summary.pickle","rb")
    summary_obj_list = pickle.load(pickle_in)

    # print(len(summary_obj_list[0].img))
    # print(summary_obj_list[0].img.shape)
    for i,s in enumerate(summary_obj_list):
        # s.bndbxes.append([0,0,10,10])
        # s.bndbx_timestamps.append(0)
        # boxes =s.bndbxes
        #
        # im_np=s.img
        # image = Image.fromarray(np.uint8(cm.gist_earth(s.img) * 255))
        # for x,box in enumerate(boxes):
        #     draw = ImageDraw.Draw(image)
        #     draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="black",width=5)
        #     image = image.convert('RGB')
        #     # cv2.imwrite('backend/summary/' + str(i) +"_"+str(box[0])+"-"+str(box[1])+"_"+str(box[2])+"-"+str(box[3]) +".jpg",im_np[box[1]:box[3],box[0]:box[2]])
        #     # cv2.imwrite('backend/summary/' + str(i) +"_"+str(s.bndbx_timestamps[x]) +".jpg",im_np[box[1]:box[3],box[0]:box[2]])
        #
        # # image.save('backend/summary/with_bndbx_' + str(i) + ".jpg")
        # image=image.convert('L')
        # s.set_img(np.array(image))
        s.set_img(s.img)

        # s.set_img(s.img)

    return summary_obj_list


#
# get_summary(all_spatial_grps,len(all_frames),len(all_frames[0]),len(all_frames[0][0]))
#
