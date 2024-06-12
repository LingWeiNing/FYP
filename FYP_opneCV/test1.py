import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import pygame.mixer
from buttonScene import show_game_over_screen, show_win_screen
from Level_Two import level_two_scene

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

def display_explanation(screen, explanation_image, explanation_text):
    screen.blit(pygame.image.load(explanation_image), (0, 0))  # Display detective thinking image
    font = pygame.font.Font(None, 36)
    for line in explanation_text:
        text_surface = font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (410, 480))

    pygame.display.flip()

def level_one_scene():
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    item_found_sound = pygame.mixer.Sound("assets\SoundEffect\Bling.mp3")

    # Set up the Pygame window
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    tutorial_image_paths = [
        "assets/goodjob/tutorialBunny1.png",
        "assets/goodjob/tutorialBunny2.png",
        "assets/goodjob/tutorialBunny3.png"
    ]

    
    explanation_image_paths = [
        "assets/goodjob/detectiveThinking_hammer.png",
        "assets/goodjob/detectiveThinking_dumbells.png",
        "assets/goodjob/detectiveThinking_globe.png",
        "assets/goodjob/detectiveThinking_laptop.png",
        "assets/goodjob/detectiveThinking_mosquitoTrap.png",
        "assets/goodjob/detectiveThinking_socks.png",
        "assets/goodjob/detectiveThinking_tape.png"
        ]

    # Load tutorial images
    tutorial_images = [pygame.image.load(path) for path in tutorial_image_paths]
    tutorial_images = [pygame.transform.scale(image, (int(image.get_width()), int(image.get_height()))) for image in tutorial_images]
    tutorial_image_rect = tutorial_images[0].get_rect(center=(width // 2 - 270, height // 2 + 25))

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
        silhouette_rect = item_silhouettes[i].get_rect(center=(itemBox_rect.left + 100 + i * 100, itemBox_rect.top + 50))
        item_silhouettes_rects.append(silhouette_rect)

    # Boolean variables to track if the items are visible
    items_visible = [True] * len(items)

    explanation_images = [pygame.image.load(path) for path in explanation_image_paths]
    explanation_images = [pygame.transform.scale(explanation_image, (int(explanation_image.get_width()), int(explanation_image.get_height()))) for explanation_image in explanation_images]
    explanation_image_rect = explanation_images[0].get_rect(center=(width // 2 + 210, height // 2 + 35))

    # Initialize face detector and shape predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
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
    countdown_duration = 30

    praise_display_time = -5000

    hammer_clicked = False
    tutorial_image_1_time = 0

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
                                item_found_sound.play()

                                # Check if the hammer item is clicked
                                if image_path == "hammer.png":
                                    hammer_clicked = True  # Set hammer_clicked to True
                                    tutorial_image_1_time = pygame.time.get_ticks()
                                    praise_display_time = pygame.time.get_ticks()

                    else:
                        print("Player's eye position not detected.")

        if mouse_pos is not None and 0 <= mouse_pos[0] <= 800 and 0 <= mouse_pos[1] <= 600:
            if 50 <= mouse_pos[0] <= 250 and 50 <= mouse_pos[1] <= 250:
                screen.fill((0, 0, 0))


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

        # Display praise image for a short duration
        if pygame.time.get_ticks() - praise_display_time < 5000: 
            screen.blit(explanation_images[0], explanation_image_rect)

        if not hammer_clicked:
            if elapsed_time < 3000:
                screen.blit(tutorial_images[1], tutorial_image_rect)
            elif 3000 <= elapsed_time < 8000:
                screen.blit(tutorial_images[2], tutorial_image_rect)
        else:
            if pygame.time.get_ticks() - tutorial_image_1_time < 3000:  # Display tutorial image 1 for 3 seconds
                screen.blit(tutorial_images[0], tutorial_image_rect)

        if remaining_time <= 0:
            restart_button, quit_button = show_game_over_screen(width, height, screen)
            while True:
                event = pygame.event.wait()
                if event.type == QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_button.collidepoint(mouse_pos):
                        level_one_scene()
                    elif quit_button.collidepoint(mouse_pos):
                        cap.release()
                        pygame.quit()
                        sys.exit()

        if all(not visible for visible in items_visible):
            next_button, quit_button = show_win_screen(width, height, screen)
            while True:
                event = pygame.event.wait()
                if event.type == QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if next_button.collidepoint(mouse_pos):
                        level_two_scene()
                    elif quit_button.collidepoint(mouse_pos):
                        cap.release()
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()
        clock.tick(60)



if __name__ == "__main__":
    level_one_scene()