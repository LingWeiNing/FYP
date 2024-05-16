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

def level_one_scene():
    # Initialize Pygame
    pygame.init()

    # Set up the Pygame window
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    # Load background image and set its rectangle
    background_image = pygame.image.load("assets/Bg/Background.png")
    background_image = pygame.transform.scale(background_image, (int(background_image.get_width() * 1.2), int(background_image.get_height() * 1.2)))
    background_rect = background_image.get_rect()
    background_rect.topleft = (15, 40)

    itemBox_image = pygame.image.load("assets/Bg/itemBox.png")
    itemBox_image = pygame.transform.scale(itemBox_image, (int(itemBox_image.get_width() * 1.058), int(itemBox_image.get_height() * 0.6)))
    itemBox_rect = itemBox_image.get_rect()
    itemBox_rect.topleft = (0, 470)

    # Define image paths and positions
    items = [
        ("globe.png", (600, 400), 0.8),
        ("dumbells.png", (500, 320), 0.5),
        ("laptop.png", (150, 270), 1.0),
        ("socks.png", (220, 120), 0.1),
        ("mosquitoTrap.png", (560, 230), 0.10),
        ("tape.png", (300, 350), 0.6),
        ("hammer.png", (350, 240), 0.25)
    ]

    # Load images and set rectangles
    for item in items:
        image_path, position, scale = item
        image = pygame.image.load(fr"assets/Items/{image_path}")
        image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        image_rect = image.get_rect(center=position)
        globals()[f"{image_path.split('.')[0]}_image"] = image
        globals()[f"{image_path.split('.')[0]}_rect"] = image_rect

    # Create rectangles for collision detection
    for item in items:
        image_path, position, _ = item
        rect = globals()[f"{image_path.split('.')[0]}_image"].get_rect(center=position)
        globals()[f"{image_path.split('.')[0]}_rect"] = rect

    # Load silhouette images of items and set rectangles
    item_silhouettes = []
    for item in items:
        image_path, position, scale = item
        image = pygame.image.load(fr"assets/Items/{image_path}")
        image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        grayscale_image = pygame.Surface(image.get_size()).convert_alpha()
        grayscale_image.fill((0, 0, 0))  # Gray color
        grayscale_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        item_silhouettes.append(grayscale_image)

    # Create rectangles for item silhouettes
    item_silhouettes_rects = []
    for i, item in enumerate(items):
        image_path, position, _ = item
        silhouette_rect = item_silhouettes[i].get_rect(center=(itemBox_rect.left + 40 + i * 80, itemBox_rect.top + 30))
        item_silhouettes_rects.append(silhouette_rect)

    # Boolean variables to track if the items are visible
    items_visible = [True] * len(items)

    # Initialize face detector and shape predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor\shape_predictor_68_face_landmarks.dat')
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    # Set up Pygame clock
    clock = pygame.time.Clock()

    threshold = 80

    mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Countdown timer setup
    start_time = pygame.time.get_ticks()
    countdown_duration = 90

    # Main game loop
    while True:
        mouse_pos = None  # Initialize mouse_pos outside of the event loop
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

                        for i, item in enumerate(items):
                            image_path, _, _ = item
                            item_rect = globals()[f"{image_path.split('.')[0]}_rect"]

                            if dist_to_center < mask_radius and item_rect.collidepoint(mouse_pos) and items_visible[i]:
                                # Toggle the visibility of the item silhouette
                                items_visible[i] = False

                    else:
                        print("Player's eye position not detected.")

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

        screen.blit(background_image, background_rect)

        # Blit visible items
        for i, (visible, image, rect) in enumerate(zip(items_visible, [globals()[f"{item.split('.')[0]}_image"] for item, _, _ in items], [globals()[f"{item.split('.')[0]}_rect"] for item, _, _ in items])):
            if visible:
                screen.blit(image, rect)

        screen.blit(mask_surface, (0, 0))
        screen.blit(itemBox_image, itemBox_rect)

        # Blit item silhouettes
        for i, (silhouette, rect) in enumerate(zip(item_silhouettes, item_silhouettes_rects)):
            if items_visible[i]:
                screen.blit(silhouette, rect)

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        remaining_time = max(countdown_duration - int(elapsed_time / 1000), 0)

        minutes = remaining_time // 60
        seconds = remaining_time % 60

        font = pygame.font.Font(None, 36)
        text_surface = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

        # Check for win condition
        if remaining_time >= 0 and all(not visible for visible in items_visible):
            restart_button, quit_button = show_win_screen(width, height, screen)
            break  # Exit the game loop

        # Check for losing condition
        if remaining_time <= 0:
            restart_button, quit_button = show_game_over_screen(width, height, screen)
            break  # Exit the game loop

        pygame.display.flip()
        clock.tick(60)

    # Game over event loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if restart_button.collidepoint(mouse_pos):
                    return level_one_scene()
                elif quit_button.collidepoint(mouse_pos):
                    cap.release()
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

if __name__ == "__main__":
    level_one_scene()