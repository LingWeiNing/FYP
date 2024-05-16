import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import random

class Mosquito(pygame.sprite.Sprite):
    def __init__(self, images, x, y, speed):
        super().__init__()
        self.images = [pygame.image.load(image) for image in images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_count = 0
        self.speed = speed
        self.dx = random.uniform(-1, 1) * self.speed
        self.dy = random.uniform(-1, 1) * self.speed
        self.flip = False

    def update(self):
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.left < 0 or self.rect.right > 800:
            self.dx = -self.dx
            self.flip = not self.flip
        if self.rect.top < 0 or self.rect.bottom > 600:
            self.dy = -self.dy

        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

def spawn_mosquitoes(num_mosquitoes, images):
    mosquitoes = pygame.sprite.Group()
    for _ in range(num_mosquitoes):
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        speed = random.uniform(1, 3)
        mosquito = Mosquito(images, x, y, speed)
        mosquitoes.add(mosquito)
    return mosquitoes

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
    

def level_two_scene():
    # Initialize Pygame
    pygame.init()

    # Set up the Pygame window
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    # Load background image and set its rectangle
    background_image = pygame.image.load("assets/Bg/gym.jpg")
    background_rect = background_image.get_rect()
    background_rect.center = (width // 2, height // 2)

    # Initialize face detector and shape predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    img = cv2.flip(img, 1)

    # Set up Pygame clock
    clock = pygame.time.Clock()

    mosquito_images = [
        ("assets\Items\mosquito1.png"),
        ("assets\Items\mosquito2.png"),
    ]

    mosquitoes = spawn_mosquitoes(3, mosquito_images)

    threshold = 80

    mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # main game loop
    mosquito_spawn_timer = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Get the position of the mouse cursor
                mouse_pos = pygame.mouse.get_pos()

                # Check if the mouse cursor is within the circular mask
                if mask_surface.get_rect().collidepoint(mouse_pos):

                    if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
                        # Calculate the distance between the mouse cursor and the center of the circular mask
                        dist_to_center = ((mouse_pos[0] - cx_right) ** 2 + (mouse_pos[1] - cy_left) ** 2) ** 0.5

                        if dist_to_center < mask_radius:
                            break;
                                
                    else:
                        print("Player's eye position not detected.")

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

        # Only update the transparent black mask surface where the circular mask around the eyes overlaps with it
        if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
            # Create a circular mask around the eyes with a gradient effect
            mask_surface.fill((0, 0, 0, 255))
            mask_radius = 60
            pygame.draw.circle(mask_surface, (0, 0, 0, 128), (cx_right, cy_left), mask_radius )
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (cx_right, cy_left), mask_radius - 10)

        # Blit the background image onto the screen
        screen.blit(background_image, background_rect)

        mosquitoes.update()
        mosquitoes.draw(screen)

        # Blit the updated transparent black mask surface onto the screen
        screen.blit(mask_surface, (0, 0))

        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Release the webcam and close the Pygame window
    cap.release()
    pygame.quit()

if __name__ == "__main__":
    level_two_scene()
