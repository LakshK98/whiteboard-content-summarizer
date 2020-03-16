from .classes import *
import time

def create_bndbx_objs(all_frames, annotations):
    all_bndbxes = []
    for frame_number, bndbxes in enumerate(annotations):
        img = all_frames[frame_number]

        if not isinstance(bndbxes, list):
            bndbxes = [bndbxes]
        for bndbx in bndbxes:
            #         converting from left top width heigth to x,y,xmax,ymax
            # temp_bndbx = [0] * 4
            # temp_bndbx[0] = bndbx[0]
            # temp_bndbx[1] = bndbx[1]
            # temp_bndbx[2] = bndbx[0] + bndbx[2]
            # temp_bndbx[3] = bndbx[1] + bndbx[3]
            #         Bounding box must not exceed 1920*1080
            # temp_bndbx[2] = min(temp_bndbx[2], 1920)
            # temp_bndbx[3] = min(temp_bndbx[3], 1080)
            # img_crop = img[temp_bndbx[1]:temp_bndbx[3], temp_bndbx[0]:temp_bndbx[2]]
            img_crop = img[bndbx[1]:bndbx[3], bndbx[0]:bndbx[2]]

            # bx)

            all_bndbxes.append(BndBx(frame_number, bndbx, img_crop))

    print("all bndbxes len", len(all_bndbxes))
    return all_bndbxes


# Create spatialtemporal groups  CALL
def create_spatiotemporal_groups(all_frames, annotations):
    time_start=time.time()
    all_bndbxes = create_bndbx_objs(all_frames, annotations)
    for i in range(len(all_bndbxes) - 1):

        if all_bndbxes[i].spatial_grp_ref is None:
            all_bndbxes[i].spatial_grp_ref = SpatialGroup()
            all_bndbxes[i].spatial_grp_ref.add_bndbx(all_bndbxes[i])
        for j in range(i + 1, len(all_bndbxes)):
            if bb_intersection_over_union(all_bndbxes[i].bndbx, all_bndbxes[j].bndbx) > 0.4 and (
            not (all_bndbxes[i].spatial_grp_ref is all_bndbxes[j].spatial_grp_ref)):

                if all_bndbxes[j].spatial_grp_ref is None:
                    all_bndbxes[i].spatial_grp_ref.add_bndbx(all_bndbxes[j])
                    all_bndbxes[j].spatial_grp_ref = all_bndbxes[i].spatial_grp_ref

                elif len(all_bndbxes[i].spatial_grp_ref.grp_bndbxes) > len(all_bndbxes[j].spatial_grp_ref.grp_bndbxes):
                    all_bndbxes[i].spatial_grp_ref.absorb_grp(all_bndbxes[j].spatial_grp_ref)
                else:
                    all_bndbxes[j].spatial_grp_ref.absorb_grp(all_bndbxes[i].spatial_grp_ref)

    all_spatial_grps = set()
    for bndbx_obj in all_bndbxes:
        all_spatial_grps.add(bndbx_obj.spatial_grp_ref)
    # len("Number of spatial groups:", all_spatial_grps)

    for spatial_grp in all_spatial_grps:
        spatial_grp.grp_bndbxes.sort(key=lambda x: x.second)
        limit = spatial_grp.grp_bndbxes[0].second
        temporal_grp = TemporalGroup()
        for bndbx in spatial_grp.grp_bndbxes:
            #  If bndbx is within 10 second then add it to temporal group or else create a new one
            if limit < bndbx.second:
                spatial_grp.temporal_grps.append(temporal_grp)
                temporal_grp = TemporalGroup()
            limit = bndbx.second + 10
            temporal_grp.grp_bndbxes.append(bndbx)
        #   add the last tempral grp to array
        spatial_grp.temporal_grps.append(temporal_grp)

    # start and end values for temporal grps
    for spatial_grp in all_spatial_grps:
        for temporal_grp in spatial_grp.temporal_grps:
            temporal_grp.start = temporal_grp.grp_bndbxes[0].second
            temporal_grp.end = temporal_grp.grp_bndbxes[-1].second


    time_end = time.time()
    print("It took %d seconds for spatiotemporal group." % (time_end - time_start))

    return all_spatial_grps
