import os
import cv2
import numpy as np
from multiprocessing import Process, Queue
from pathlib import Path
from itertools import chain
from utils.realsense import read_rs_camera

def image_stream(queue, imagedir, calib, stride, skip=0):
    """ image generator """

    calib = np.loadtxt(calib, delimiter=" ")
    fx, fy, cx, cy = calib[:4]

    K = np.eye(3)
    K[0,0] = fx
    K[0,2] = cx
    K[1,1] = fy
    K[1,2] = cy

    img_exts = ["*.png", "*.jpeg", "*.jpg"]
    image_list = sorted(chain.from_iterable(Path(imagedir).glob(e) for e in img_exts))[skip::stride]

    print("Image List: ", image_list)

    for t, imfile in enumerate(image_list):
        image = cv2.imread(str(imfile))
        if len(calib) > 4:
            image = cv2.undistort(image, K, calib[4:])

        if 0:
            image = cv2.resize(image, None, fx=0.5, fy=0.5)
            intrinsics = np.array([fx / 2, fy / 2, cx / 2, cy / 2])

        else:
            intrinsics = np.array([fx, fy, cx, cy])
            
        h, w, _ = image.shape
        image = image[:h-h%16, :w-w%16]

        queue.put((t, image, intrinsics))

    queue.put((-1, image, intrinsics))


def video_stream(queue, imagedir, calib, stride, skip=0):
    """ video generator """

    calib = np.loadtxt(calib, delimiter=" ")
    fx, fy, cx, cy = calib[:4]

    K = np.eye(3)
    K[0,0] = fx
    K[0,2] = cx
    K[1,1] = fy
    K[1,2] = cy

    cap = cv2.VideoCapture(imagedir)

    t = 0

    for _ in range(skip):
        ret, image = cap.read()

    while True:
        # Capture frame-by-frame
        for _ in range(stride):
            ret, image = cap.read()
            # if frame is read correctly ret is True
            if not ret:
                break

        if not ret:
            break

        if len(calib) > 4:
            image = cv2.undistort(image, K, calib[4:])

        image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        h, w, _ = image.shape
        image = image[:h-h%16, :w-w%16]

        intrinsics = np.array([fx*.5, fy*.5, cx*.5, cy*.5])
        queue.put((t, image, intrinsics))

        t += 1

    queue.put((-1, image, intrinsics))
    cap.release()

def camera_stream(queue, camera_idx, calib, stride, skip=0):
    """ video generator """

    calib = np.loadtxt(calib, delimiter=" ")
    fx, fy, cx, cy = calib[:4]

    K = np.eye(3)
    K[0,0] = fx
    K[0,2] = cx
    K[1,1] = fy
    K[1,2] = cy

    cap = cv2.VideoCapture(camera_idx)

    t = 0

    for _ in range(skip):
        ret, image = cap.read()

    while True:
        # Capture frame-by-frame
        for _ in range(stride):
            ret, image = cap.read()
            # if frame is read correctly ret is True
            if not ret:
                break

        if not ret:
            break

        if len(calib) > 4:
            image = cv2.undistort(image, K, calib[4:])

        image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        h, w, _ = image.shape
        image = image[:h-h%16, :w-w%16]

        intrinsics = np.array([fx*.5, fy*.5, cx*.5, cy*.5])
        queue.put((t, image, intrinsics))

        # Check for 'Q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        t += 1

    queue.put((-1, image, intrinsics))
    cap.release()


# TODO: Extend this method to take any camera, not just RealSense

def realsense_stream(queue, pipeline, align, calib, stride, skip=0):
    """ stream generator from realsense camera - pipeline and align are generated by calling init_rs_camera"""

    calib = np.loadtxt(calib, delimiter=" ")
    fx, fy, cx, cy = calib[:4]

    K = np.eye(3)
    K[0,0] = fx
    K[0,2] = cx
    K[1,1] = fy
    K[1,2] = cy

    t = 0

    for _ in range(skip):
        image, _, _ = read_rs_camera(
            pipeline, align
        )

    while True:
        # Capture frame-by-frame
        for _ in range(stride):
            image, _, _ = read_rs_camera(
                pipeline, align
            )

        if len(calib) > 4:
            image = cv2.undistort(image, K, calib[4:])

        image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        h, w, _ = image.shape
        image = image[:h-h%16, :w-w%16]

        intrinsics = np.array([fx*.5, fy*.5, cx*.5, cy*.5])
        queue.put((t, image, intrinsics))

        t += 1

