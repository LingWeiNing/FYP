import cv2
import dlib
import numpy as np

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def eye_on_mask(mask, side, shape):
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask

def contouring(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key=cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        if right:
            cx += mid
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
        return cx, cy
    except:
        return None, None

def detect_eyes(detector, predictor, img, threshold=30):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)

    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    cx_left, cy_left, cx_right, cy_right = None, None, None, None

    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = eye_on_mask(mask, left, shape)
        mask = eye_on_mask(mask, right, shape)
        mask = cv2.dilate(mask, np.ones((9, 9), np.uint8), 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[39][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)
        thresh = cv2.medianBlur(thresh, 3)
        thresh = cv2.bitwise_not(thresh)
        cx_left, cy_left = contouring(thresh[:, 0:mid], mid, img)
        cx_right, cy_right = contouring(thresh[:, mid:], mid, img, True)

    return cx_left, cy_left, cx_right, cy_right
