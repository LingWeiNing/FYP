import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def eye_on_mask(mask, side):
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

# Initialize Pygame
pygame.init()

# Set up the Pygame window
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("FYP Game")

# Load background image and set its rectangle
puzzle_image = pygame.image.load("puzzle.png")
puzzle_rect = puzzle_image.get_rect()
puzzle_rect.center = (width // 2, height // 2)



# Initialize face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat\shape_predictor_68_face_landmarks.dat')
left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

# Initialize the webcam
cap = cv2.VideoCapture(0)
ret, img = cap.read()
img = cv2.flip(img, 1)

# Create a crosshair surface
crosshair_size = 20
crosshair = pygame.Surface((crosshair_size, crosshair_size), pygame.SRCALPHA)
pygame.draw.line(crosshair, (255, 0, 0), (crosshair_size // 2, 0), (crosshair_size // 2, crosshair_size))
pygame.draw.line(crosshair, (255, 0, 0), (0, crosshair_size // 2), (crosshair_size, crosshair_size // 2))

# Set up Pygame clock
clock = pygame.time.Clock()

threshold = 80

mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

avg_eye_x = 0
avg_eye_y = 0
num_frames = 0

# Initialize a flag to track whether right-click is initiated
right_click_initiated = False

# main game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                # Left mouse button clicked
                # Handle left-click actions if needed
                pass
            elif event.button == 3:
                # Right mouse button clicked
                # Toggle between globe and dumbbell sprites
                if right_click_initiated:
                    # If right-click was initiated, switch to globe
                    globe_visible = True
                    dumbells_visible = False
                    right_click_initiated = False
                else:
                    # If right-click wasn't initiated, switch to dumbbell
                    globe_visible = False
                    dumbells_visible = True
                    right_click_initiated = True

    ret, img = cap.read()

    # Horizontally flip the webcam feed
    img = cv2.flip(img, 1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)

    cx_left, cy_left, cx_right, cy_right = None, None, None, None

    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = eye_on_mask(mask, left)
        mask = eye_on_mask(mask, right)
        mask = cv2.dilate(mask, np.ones((9, 9), np.uint8), 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[39][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(eyes_gray, 30, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)
        thresh = cv2.medianBlur(thresh, 3)
        thresh = cv2.bitwise_not(thresh)
        cx_left, cy_left = contouring(thresh[:, 0:mid], mid, img)
        cx_right, cy_right = contouring(thresh[:, mid:], mid, img, True)

    if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
        # Calculate the average eye position
        avg_eye_x = (cx_left + cx_right) // 2
        avg_eye_y = (cy_left + cy_right) // 2
        num_frames += 1


    # Blit the updated transparent black mask surface onto the screen
    screen.blit(mask_surface, (0, 0))

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Release the webcam and close the Pygame window
cap.release()
pygame.quit()