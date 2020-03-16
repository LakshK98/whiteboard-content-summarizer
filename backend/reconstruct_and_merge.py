import cv2
from PIL import Image
from .imagehash import *
import numpy as np
# from classes import *

import time
# Reconstruct frames in temporal groups and save them to file

def reconstruct_frames(all_spatial_grps):
    for spatial_group in all_spatial_grps:

        for temporal_grp in spatial_group.temporal_grps:
            bndbx_list = np.array([x.bndbx for x in temporal_grp.grp_bndbxes])
            #         get min and max x,y coordinates to get a bndbx that can include all other bndbxes
            temporal_grp.reconstructed_bndbx = [np.amin(bndbx_list[:, 0]), np.amin(bndbx_list[:, 1]),
                                                np.amax(bndbx_list[:, 2]), np.amax(bndbx_list[:, 3])]
            width = temporal_grp.reconstructed_bndbx[2] - temporal_grp.reconstructed_bndbx[0]
            height = temporal_grp.reconstructed_bndbx[3] - temporal_grp.reconstructed_bndbx[1]
            temporal_grp.reconstructed_img = np.full([height, width], 0, np.uint32)
            avg_divisors = np.full([height, width], 0, np.uint32)
            for bndbx_obj in temporal_grp.grp_bndbxes:
                #             calculate offset of bndbxes inside the larger bndbx
                xmin = bndbx_obj.bndbx[0] - temporal_grp.reconstructed_bndbx[0]
                ymin = bndbx_obj.bndbx[1] - temporal_grp.reconstructed_bndbx[1]
                xmax = bndbx_obj.bndbx[2] - temporal_grp.reconstructed_bndbx[0]
                ymax = bndbx_obj.bndbx[3] - temporal_grp.reconstructed_bndbx[1]
                #             add values at the offset to the reconstructed img
                temporal_grp.reconstructed_img[ymin:ymax, xmin:xmax] = np.add(
                    temporal_grp.reconstructed_img[ymin:ymax, xmin:xmax], bndbx_obj.img_crop)
                #             count number of times a value is added to a pixel location
                avg_divisors[ymin:ymax, xmin:xmax] = np.add(avg_divisors[ymin:ymax, xmin:xmax],
                                                            np.full(bndbx_obj.img_crop.shape, 1, np.uint16))

            #         divide to get average
            temporal_grp.reconstructed_img = np.divide(temporal_grp.reconstructed_img, avg_divisors,
                                                       where=avg_divisors != 0)
            temporal_grp.reconstructed_img = temporal_grp.reconstructed_img.astype('uint8')
            temporal_grp.avg_divisors = avg_divisors
            #         make pixels where no addition is done(some edge locations of the large bndbx) white(255)
            temporal_grp.reconstructed_img = np.where(avg_divisors == 0, 255, temporal_grp.reconstructed_img)
    return all_spatial_grps



def check_temporal_grp_similarity(tem1, tem2):
    bndbx1 = tem1.reconstructed_bndbx
    bndbx2 = tem2.reconstructed_bndbx

    overlap_xmin = max(bndbx1[0], bndbx2[0])
    overlap_ymin = max(bndbx1[1], bndbx2[1])
    overlap_xmax = min(bndbx1[2], bndbx2[2])
    overlap_ymax = min(bndbx1[3], bndbx2[3])

    img1 = tem1.reconstructed_img[overlap_ymin - bndbx1[1]:overlap_ymax - bndbx1[1],
           overlap_xmin - bndbx1[0]:overlap_xmax - bndbx1[0]:]

    img2 = tem2.reconstructed_img[overlap_ymin - bndbx2[1]:overlap_ymax - bndbx2[1],
           overlap_xmin - bndbx2[0]:overlap_xmax - bndbx2[0]]

    hash1 = average_hash(Image.fromarray(img1))
    hash2 = average_hash(Image.fromarray(img2))

    return hash1 - hash2 <= 10


# Merging similiar temporal groupps
def merge_similar_temporal_grps(all_spatial_grps):
    time_start=time.time()
    print("merging",len(all_spatial_grps))
    for sp_num,spatial_group in enumerate(all_spatial_grps):
        merged_temporal_grps = []
        # debug
        if(sp_num==14):
            print("14b",len(spatial_group.temporal_grps))
            for tgi,tg in enumerate(spatial_group.temporal_grps):
                cv2.imwrite("backend/14b/" + str(tgi) + ".jpg", tg.reconstructed_img )

        new_temp_grp = spatial_group.temporal_grps[0]
        for i in range(1, len(spatial_group.temporal_grps)):

            if check_temporal_grp_similarity(new_temp_grp, spatial_group.temporal_grps[i]):
                new_temp_grp.end = spatial_group.temporal_grps[i].end
                new_temp_grp.grp_bndbxes = new_temp_grp.grp_bndbxes[:] + spatial_group.temporal_grps[i].grp_bndbxes[:]

                temp_bndbx1 = new_temp_grp.reconstructed_bndbx
                temp_bndbx2 = spatial_group.temporal_grps[i].reconstructed_bndbx
                new_bndbx = [min(temp_bndbx1[0], temp_bndbx2[0]), min(temp_bndbx1[1], temp_bndbx2[1]),
                             max(temp_bndbx1[2], temp_bndbx2[2]), max(temp_bndbx1[3], temp_bndbx2[3])]
                new_reconstructed_img = np.full([new_bndbx[3] - new_bndbx[1], new_bndbx[2] - new_bndbx[0]], 0,
                                                np.uint32)
                new_avg_divisors = np.full([new_bndbx[3] - new_bndbx[1], new_bndbx[2] - new_bndbx[0]], 0, np.uint32)
                for temporal_grp in [new_temp_grp, spatial_group.temporal_grps[i]]:
                    bndbx = temporal_grp.reconstructed_bndbx
                    xmin = bndbx[0] - new_bndbx[0]
                    ymin = bndbx[1] - new_bndbx[1]
                    xmax = bndbx[2] - new_bndbx[0]
                    ymax = bndbx[3] - new_bndbx[1]

                    new_reconstructed_img[ymin:ymax, xmin:xmax] = np.add(new_reconstructed_img[ymin:ymax, xmin:xmax],
                                                                         temporal_grp.reconstructed_img * temporal_grp.avg_divisors)
                    new_avg_divisors[ymin:ymax, xmin:xmax] = np.add(new_avg_divisors[ymin:ymax, xmin:xmax],
                                                                    temporal_grp.avg_divisors)

                new_reconstructed_img = np.divide(new_reconstructed_img, new_avg_divisors, where=new_avg_divisors != 0)
                new_reconstructed_img = new_reconstructed_img.astype('uint8')
                #         make pixels where no addition is done(some edge locations of the large bndbx) white(255)
                new_reconstructed_img = np.where(new_avg_divisors == 0, 255, new_reconstructed_img)
                new_temp_grp.reconstructed_img = new_reconstructed_img
                new_temp_grp.reconstructed_bndbx = new_bndbx
                new_temp_grp.avg_divisors = new_avg_divisors

            #             merged_temporal_grps.append(spatial_group.temporal_grps[i+1])
            else:

                merged_temporal_grps.append(new_temp_grp)
                new_temp_grp = spatial_group.temporal_grps[i]
        merged_temporal_grps.append(new_temp_grp)

        spatial_group.temporal_grps = merged_temporal_grps
        if (sp_num == 14):
            print("14a", len(spatial_group.temporal_grps))
            for tgi, tg in enumerate(spatial_group.temporal_grps):
                cv2.imwrite("backend/14a/" + str(tgi) + ".jpg", tg.reconstructed_img)

    time_end = time.time()
    print("It took %d seconds for reconstruct and merging" % (time_end - time_start))
    return all_spatial_grps

