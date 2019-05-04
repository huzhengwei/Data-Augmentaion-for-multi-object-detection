# generate mask
import cv2
import numpy as np

import cv2 as cv

_MIN_AREA = 9
_ITER_COUNT = 5
_RECT_SHRINK = 3

def grabcut(img_path, bbox):
    """Use Grabcut to create a binary segmentation of an image within a bounding box
    Param:
        img: path to input image astype('uint8')
        bbox: bbox numpy array [y1, x1, y2, x2]
    Returns:
        mask with binary segmentation astype('uint8')
    Based on:
        https://docs.opencv.org/trunk/d8/d83/tutorial_py_grabcut.html
    """
    img = cv.imread(img_path)
    width, height = bbox[3] - bbox[1], bbox[2] - bbox[0]
    if width * height < _MIN_AREA:
        # OpenCV's Grabcut breaks if the rectangle is too small!
        # This happens with instance mask 2008_002212_4.png
        # Fix: Draw a filled rectangle at that location, making the assumption everything in the rectangle is foreground
        assert(width*height > 0)
        mask = rect_mask(img.shape[:2], bbox)
    elif width * height == img.shape[0] * img.shape[1]:
        # If the rectangle covers the entire image, grabCut can't distinguish between background and foreground
        # because it assumes what's outside the rect is background (no "outside" if the rect is as large as the input)
        # This happens with instance mask 2008_002638_3.png
        # Crappy Fix: Shrink the rectangle corners by _RECT_SHRINK on all sides
        # Use Grabcut to create a segmentation within the bbox
        rect = (_RECT_SHRINK, _RECT_SHRINK, width - _RECT_SHRINK * 2, height - _RECT_SHRINK * 2)
        gct = np.zeros(img.shape[:2], np.uint8)
        bgdModel, fgdModel = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv.grabCut(img, gct, rect, bgdModel,fgdModel, _ITER_COUNT, cv.GC_INIT_WITH_RECT)
        mask = np.where((gct == 2) | (gct == 0), 0, 1).astype('uint8')
    else:
        # Use Grabcut to create a segmentation within the bbox
        rect = (bbox[1], bbox[0], width, height)
        gct = np.zeros(img.shape[:2], np.uint8)
        bgdModel, fgdModel = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv.grabCut(img, gct, rect, bgdModel,fgdModel, _ITER_COUNT, cv.GC_INIT_WITH_RECT)
        mask = np.where((gct == 2) | (gct == 0), 0, 1).astype('uint8')
    return mask

f=open('product_train_bbox.txt','r')


lines = f.readlines()
sum_line = len(lines)
mask_dir = "./data/train_mask/"
for i in range(sum_line):
    if i < 3844:
        continue
    print(i)
    line1 = lines[i].split()
    path1 = line1[0]
    bbox1 = [int(int(cordi)/1.6) for cordi in line1[1:5]]
    mask1 = grabcut(path1, tuple(bbox1))
    dst_name = mask_dir + str(i) + '.jpg'
    cv2.imwrite(dst_name, mask1*255)