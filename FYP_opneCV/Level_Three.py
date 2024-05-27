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
    
def level_three_scene():
    # Initialize Pygame
    pygame.init()

    # Set up the Pygame window
    width, height = 640, 480
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    # Load background image and set its rectangle
    background_image = pygame.image.load("assets\Bg\maze.png").convert_alpha()  # Load with alpha channel
    background_rect = background_image.get_rect()
    background_rect.center = (width // 2, height // 2)
    #mask
    background_mask = pygame.mask.from_surface(background_image)

    # Load globe image and set its rectangle
    globe_image = pygame.image.load("assets\Items\key.png")
    globe_rect = globe_image.get_rect()

    globe_position = (100, 420) 
    globe_rect.center = globe_position

    # Load dumbbells image and set its rectangle
    dumbells_image = pygame.image.load("assets\Items\key2.png")
    dumbells_rect = dumbells_image.get_rect()

    dumbells_position = (40, 140) 
    dumbells_rect.center = dumbells_position

    # Create rectangles for collision detection
    globe_rect = globe_image.get_rect(center=globe_position)
    dumbells_rect = dumbells_image.get_rect(center=dumbells_position)

    initial_globe_position = globe_position
    initial_dumbells_position = dumbells_position

    # Boolean variables to track if the globe and dumbbell are visible
    globe_visible = True
    dumbells_visible = True


    # Initialize face detector and shape predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor\shape_predictor_68_face_landmarks.dat')
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

    # Initialize variables to track dragging state
    dragging_globe = False
    dragging_dumbells = False

    # Store offset between mouse click position and top-left corner of the sprite
    offset_x_globe, offset_y_globe = 0, 0
    offset_x_dumbells, offset_y_dumbells = 0, 0

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if globe_rect.collidepoint(mouse_pos):
                    dragging_globe = True
                    offset_x_globe = globe_rect.x - mouse_pos[0]
                    offset_y_globe = globe_rect.y - mouse_pos[1]
                elif dumbells_rect.collidepoint(mouse_pos):
                    dragging_dumbells = True
                    offset_x_dumbells = dumbells_rect.x - mouse_pos[0]
                    offset_y_dumbells = dumbells_rect.y - mouse_pos[1]
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                dragging_globe = False
                dragging_dumbells = False
            elif event.type == MOUSEMOTION:
                if dragging_globe:
                    mouse_pos = pygame.mouse.get_pos()
                    globe_rect.x = mouse_pos[0] + offset_x_globe
                    globe_rect.y = mouse_pos[1] + offset_y_globe
                elif dragging_dumbells:
                    mouse_pos = pygame.mouse.get_pos()
                    dumbells_rect.x = mouse_pos[0] + offset_x_dumbells
                    dumbells_rect.y = mouse_pos[1] + offset_y_dumbells

                

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
            mask = eye_on_mask(mask, left, shape)
            mask = eye_on_mask(mask, right, shape)
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

    #collision
        if dumbells_visible:
            dumbells_mask = pygame.mask.from_surface(dumbells_image)
            offset = (dumbells_rect.x - background_rect.x, dumbells_rect.y - background_rect.y)
            if background_mask.overlap(dumbells_mask, offset):
                print("Collision with background detected for dumbbells!")
                dumbells_rect.center = initial_dumbells_position
                # Handle collision action here

        if globe_visible:
            globe_mask = pygame.mask.from_surface(globe_image)
            offset = (globe_rect.x - background_rect.x, globe_rect.y - background_rect.y)
            if background_mask.overlap(globe_mask, offset):
                print("Collision with background detected for globe!")
                globe_rect.center = initial_globe_position


        if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:

            mask_surface.fill((0, 0, 0, 255))
            mask_radius = 60
            pygame.draw.circle(mask_surface, (0, 0, 0, 128), (cx_right, cy_left), mask_radius )
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (cx_right, cy_left), mask_radius - 10)

        #blit
        screen.blit(background_image, background_rect)

        if dumbells_visible:
                screen.blit(dumbells_image, dumbells_rect)

        if globe_visible:
            screen.blit(globe_image, globe_rect)

        screen.blit(mask_surface, (0, 0))

        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Release the webcam and close the Pygame window
    cap.release()
    pygame.quit()

if __name__ == "__main__":
    level_three_scene()
