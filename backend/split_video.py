import cv2
import time
import os


def video_to_frames(input_loc):

    # Log the time
    time_start = time.time()
    # Start capturing the feed
    cap = cv2.VideoCapture(input_loc)
    # Find the number of frames
    print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print("Number of frames: ", video_length)
    count = 0
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    print(fps)
    print("Converting video..\n")
    all_frames = []
    # Start converting the video
    while cap.isOpened():
        # Extract the frame
        ret, frame = cap.read()
        # Write the results back to output location.
        if (count % fps == 0):
            #             cv2.imwrite(output_loc + "/%#05d.jpg" % (count+1), frame)
            all_frames.append(frame)

        count = count + 1
        # If there are no more frames left
        if (count > (video_length - 1) ):
            # Log the time again
            time_end = time.time()
            # Release the feed
            cap.release()
            # Print stats
            print("Done extracting frames.\n%d frames extracted" % count)
            print("It took %d seconds for conversion." % (time_end - time_start))

            break
    return all_frames
