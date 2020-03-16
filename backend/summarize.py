from .classes import *
import cv2
import numpy as np
import time
import pickle
def get_summary(all_spatial_grps,last_second,height,width):
    time_start=time.time()

    # intervals between temporal groups(these are intervals where a split should occur so that there are no conflicts within a spatial group)
    split_intervals = []
    # count_intervals determines which interval resolves maximum number of conflicts
    count_intervals = [0] * (last_second + 1)

    for spatial_grp in all_spatial_grps:
        for i in range(len(spatial_grp.temporal_grps) - 1):
            split_intervals.append([spatial_grp.temporal_grps[i].end, spatial_grp.temporal_grps[i + 1].start])
            for j in range(split_intervals[-1][0], split_intervals[-1][1]):
                count_intervals[j] += 1

    split_indices = []

    # resolve conflicts by selecting proper split_indices
    while (True):
        max_count = -1
        split_index = 0
        for i in range(len(count_intervals)):
            if max_count < count_intervals[i]:
                split_index = i
                max_count = count_intervals[i]

        # print(max_count)
        if (max_count == 0):
            break
        split_indices.append(split_index)
        index = 0
        # print("split index", split_index)
        while index < len(split_intervals):
            # print("len_split_intervals", len(split_intervals))
            # print("interval", split_intervals[index])
            if split_intervals[index][0] <= split_index and split_intervals[index][1] > split_index:
                # print(split_intervals[index])
                for j in range(split_intervals[index][0], split_intervals[index][1]):
                    count_intervals[j] -= 1
                del (split_intervals[index])
            else:
                index += 1

    # print(split_indices)
    # for x in count_intervals:
    #     print(x, end=" ")

    split_indices.append(0)
    split_indices.append(last_second)

    split_indices = sorted(split_indices)

    # get summary images
    split_indices = sorted(split_indices)
    print(split_indices)
    print(len(split_indices))

    summary_obj_list=[]
    for i in range(len(split_indices) - 1):
        summary_obj=SummaryObj()
        summary_image = np.full([height, width], 255, np.uint8)
        for sp_num,spatial_grp in enumerate(all_spatial_grps):
            for tm_num,temporal_grp in enumerate(reversed(spatial_grp.temporal_grps)):
                split_duration = split_indices[i + 1] - split_indices[i]
                # print("start",temporal_grp.start)
                # print("end",temporal_grp.end)
                # print(split_indices[i])

                if (temporal_grp.start < split_indices[i + 1] and temporal_grp.end > split_indices[i]):
                    #   if a bndbx has been used in previous split , use it again only if it exists for more than 50% of current split duration
                    if not temporal_grp.visited or (temporal_grp.end - split_indices[i] > split_duration / 2):
                        temporal_grp.visited = True
                        bndbx = temporal_grp.reconstructed_bndbx
                        summary_image[bndbx[1]:bndbx[3], bndbx[0]:bndbx[2]] = np.minimum(summary_image[bndbx[1]:bndbx[3], bndbx[0]:bndbx[2]], temporal_grp.reconstructed_img)

                        summary_obj.bndbxes.append(bndbx)
                        summary_obj.bndbx_timestamps.append(temporal_grp.start)


                        # cv2.imshow("image", summary_image[bndbx[1]:bndbx[3], bndbx[0]:bndbx[2]] )
                        #
                        # cv2.waitKey(0)
                        # cv2.destroyWindow("image")

                        break

        # print("SUMMARY")
        summary_obj.set_img(summary_image)
        # summary_obj.img=summary_image

        summary_obj_list.append(summary_obj)
        # cv2.imwrite("backend/summary/"+ str(i) + ".jpg", summary_image)

    # pickle_out = open("backend/n1_summary.pickle", "wb")
    # pickle.dump(summary_obj_list, pickle_out)
    # pickle_out.close()
    time_end=time.time()

    print("It took %d seconds for summary ." % (time_end - time_start))
    return summary_obj_list

