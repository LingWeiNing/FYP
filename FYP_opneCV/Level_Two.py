import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import random

class Mosquito(pygame.sprite.Sprite):
    def __init__(self, images, x, y, speed, scale_factor):
        super().__init__()
        self.original_images = [pygame.transform.scale(pygame.image.load(image), scale_factor) for image in images]
        self.images = self.original_images.copy()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_count = 0
        self.speed = speed
        self.dx = random.uniform(-1, 1) * self.speed
        self.dy = random.uniform(-1, 1) * self.speed
        self.prev_x = x
        self.prev_y = y
        self.visible = True

    def update(self):
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        # Update position
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Boundary checks and direction change
        if self.rect.left < 0:
            self.rect.left = 0
            self.dx = abs(self.dx)
        if self.rect.right > 800:
            self.rect.right = 800
            self.dx = -abs(self.dx)
        if self.rect.top < 0:
            self.rect.top = 0
            self.dy = abs(self.dy)
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.dy = -abs(self.dy)

        # Calculate velocity
        velocity_x = self.rect.x - self.prev_x

        # Flip the sprite based on the x velocity
        if velocity_x > 0:
            self.images = [pygame.transform.flip(image, True, False) for image in self.original_images]
        elif velocity_x < 0:
            self.images = self.original_images.copy()

        # Update image with correct flip
        self.image = self.images[self.index]

        # Update previous position
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y

def spawn_mosquitoes(num_mosquitoes, images, scale_factor):
    mosquitoes = pygame.sprite.Group()
    for _ in range(num_mosquitoes):
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        speed = random.uniform(1, 3)
        mosquito = Mosquito(images, x, y, speed, scale_factor)
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
    
def show_game_over_screen(width, height, screen):
    # Game Over text
    font_game_over = pygame.font.Font(None, 100)
    text_game_over = font_game_over.render("Game Over", True, (255, 0, 0))
    screen.blit(text_game_over, (width // 2 - text_game_over.get_width() // 2, height // 2 - text_game_over.get_height() // 2 - 100))

    # Restart button
    restart_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), restart_button)
    font_restart = pygame.font.Font(None, 36)
    text_restart = font_restart.render("Restart", True, (0, 0, 0))
    screen.blit(text_restart, (width // 2 - text_restart.get_width() // 2, height // 2 + 10))

    # Quit button
    quit_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), quit_button)
    font_quit = pygame.font.Font(None, 36)
    text_quit = font_quit.render("Quit", True, (0, 0, 0))
    screen.blit(text_quit, (width // 2 - text_quit.get_width() // 2, height // 2 + 80))

    pygame.display.flip()

    return restart_button, quit_button

def show_win_screen(width, height, screen):
    # Game Over text
    font_game_over = pygame.font.Font(None, 100)
    text_game_over = font_game_over.render("Good Job!", True, (255, 0, 0))
    screen.blit(text_game_over, (width // 2 - text_game_over.get_width() // 2, height // 2 - text_game_over.get_height() // 2 - 100))

    # Restart button
    restart_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), restart_button)
    font_restart = pygame.font.Font(None, 36)
    text_restart = font_restart.render("Next Level", True, (0, 0, 0))
    screen.blit(text_restart, (width // 2 - text_restart.get_width() // 2, height // 2 + 10))

    # Quit button
    quit_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), quit_button)
    font_quit = pygame.font.Font(None, 36)
    text_quit = font_quit.render("Quit", True, (0, 0, 0))
    screen.blit(text_quit, (width // 2 - text_quit.get_width() // 2, height // 2 + 80))

    pygame.display.flip()

    return restart_button, quit_button

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
        "assets/Items/mosquito1.png",
        "assets/Items/mosquito2.png",
    ]

    mosquitoes = spawn_mosquitoes(5, mosquito_images, (100, 100))

    # Initialize the mosquito counter
    mosquito_counter = 0

    threshold = 80

    mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    start_time = pygame.time.get_ticks()
    countdown_duration = 20

    # Main game loop
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
                            for mosquito in mosquitoes:
                                if mosquito.rect.collidepoint(mouse_pos):
                                    mosquitoes.remove(mosquito)
                                    mosquito_counter += 1  # Increment the mosquito counter
                                    new_mosquito = Mosquito(mosquito_images, random.randint(0, 800), random.randint(0, 600), random.uniform(1, 3), (100, 100))
                                    mosquitoes.add(new_mosquito)
                                    break

        ret, img = cap.read()
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
            pygame.draw.circle(mask_surface, (0, 0, 0, 128), (cx_right, cy_left), mask_radius)
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (cx_right, cy_left), mask_radius - 10)

        # Blit the background image onto the screen
        screen.blit(background_image, background_rect)

        mosquitoes.update()
        mosquitoes.draw(screen)

        # Blit the updated transparent black mask surface onto the screen
        screen.blit(mask_surface, (0, 0))

        # Display the mosquito counter
        font = pygame.font.Font(None, 36)
        counter_text = font.render(f'Mosquitoes removed: {mosquito_counter} /15', True, (255, 255, 255))
        screen.blit(counter_text, (10, 10))

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        remaining_time = max(countdown_duration - int(elapsed_time / 1000), 0)

        minutes = remaining_time // 60
        seconds = remaining_time % 60

        font = pygame.font.Font(None, 36)
        text_surface = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(text_surface, (10, 50))

        # Check for win condition
        if mosquito_counter >= 5:  # Check if 15 mosquitoes have been removed
            restart_button, quit_button = show_win_screen(width, height, screen)
            break  # Exit the game loop

        # Check for losing condition
        if remaining_time <= 0:
            restart_button, quit_button = show_game_over_screen(width, height, screen)
            break  # Exit the game loop

        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Release the webcam and close the Pygame window
    cap.release()
    pygame.quit()

if __name__ == "__main__":
    level_two_scene()
