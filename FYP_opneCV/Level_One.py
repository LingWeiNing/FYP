import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import pygame.mixer
from buttonScene import show_game_over_screen, show_win_screen, show_pause_screen, draw_pause_button
from LevelSelection import start_level_two
from eye_detection import detect_eyes

def display_explanation(screen, explanation_image):
    screen.blit(explanation_image, (0, 0))
    pygame.display.flip()

def draw_slider(screen, pos, size, value, min_val, max_val):
    x, y = pos
    width, height = size
    slider_rect = pygame.Rect(x, y, width, height)
    handle_pos = ((value - min_val) / (max_val - min_val)) * width + x
    handle_rect = pygame.Rect(handle_pos - 5, y - 10, 10, height + 20)

    pygame.draw.rect(screen, (180, 180, 180), slider_rect)
    pygame.draw.rect(screen, (50, 50, 50), handle_rect)
    pygame.draw.line(screen, (0, 0, 0), (x, y + height // 2), (x + width, y + height // 2), 2)
    pygame.draw.circle(screen, (0, 0, 0), (int(handle_pos), y + height // 2), 10)

    return slider_rect, handle_rect

def level_one_scene():
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    item_found_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")

    BG_music = pygame.mixer.Sound("assets/Music/Shady-Girls.mp3")

    # Set up the Pygame window
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    tutorial_image_paths = [
        "assets/goodjob/tutorialBunny1.png",
        "assets/goodjob/tutorialBunny2.png",
        "assets/goodjob/tutorialBunny3.png"
    ]

    explanation_image_paths = {
        "hammer.png": "assets/goodjob/detectiveThinking_hammer.png",
        "dumbells.png": "assets/goodjob/detectiveThinking_dumbells.png",
        "globe.png": "assets/goodjob/detectiveThinking_globe.png",
        "laptop.png": "assets/goodjob/detectiveThinking_laptop.png",
        "mosquitoTrap.png": "assets/goodjob/detectiveThinking_mosquitoTrap.png",
        "socks.png": "assets/goodjob/detectiveThinking_socks.png",
        "tape.png": "assets/goodjob/detectiveThinking_tape.png"
    }

    tutorial_images = [pygame.image.load(path) for path in tutorial_image_paths]
    tutorial_images = [pygame.transform.scale(image, (int(image.get_width()), int(image.get_height()))) for image in tutorial_images]
    tutorial_image_rect = tutorial_images[0].get_rect(center=(width // 2 - 270, height // 2 + 25))

    background_image = pygame.image.load("assets/Bg/Background.png")
    background_image = pygame.transform.scale(background_image, (int(background_image.get_width() * 1.2), int(background_image.get_height() * 1.2)))
    background_rect = background_image.get_rect()
    background_rect.topleft = (15, 40)

    itemBox_image = pygame.image.load("assets/Bg/itemBox.png")
    itemBox_image = pygame.transform.scale(itemBox_image, (int(itemBox_image.get_width() * 1.058), int(itemBox_image.get_height() * 0.6)))
    itemBox_rect = itemBox_image.get_rect()
    itemBox_rect.topleft = (0, 470)

    items = [
        ("globe.png", (550, 400), 0.8),
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
        image = pygame.transform.scale(image, (int(image.get_width() * scale), (int(image.get_height() * scale))))
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

    item_silhouettes_rects = []
    for i, item in enumerate(items):
        image_path, position, _ = item
        silhouette_rect = item_silhouettes[i].get_rect(center=(itemBox_rect.left + 100 + i * 100, itemBox_rect.top + 50))
        item_silhouettes_rects.append(silhouette_rect)

    items_visible = [True] * len(items)

    explanation_images = {path: pygame.image.load(explanation_image_paths[path]) for path in explanation_image_paths}
    explanation_images = {path: pygame.transform.scale(explanation_images[path], (int(explanation_images[path].get_width()), int(explanation_images[path].get_height()))) for path in explanation_images}
    explanation_image_rects = {path: explanation_images[path].get_rect(center=(width // 2 + 210, height // 2 + 35)) for path in explanation_images}

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')

    cap = cv2.VideoCapture(0)

    clock = pygame.time.Clock()

    threshold = 30

    mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    start_time = pygame.time.get_ticks()
    countdown_duration = 120

    praise_display_time = -5000

    clicked_item = None  
    tutorial_image_1_time = 0
    hammer_clicked = False

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 
    BG_music.play()

    cx_left, cy_left, cx_right, cy_right = None, None, None, None

    font = pygame.font.Font(None, 36)

    slider_pos = (300, 50)
    slider_size = (200, 20)
    slider_min_val = 0
    slider_max_val = 255

    while True:
        mouse_pos = None
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                mouse_click = True

                if pause_button_rect.collidepoint(mouse_pos):
                    if not paused:
                        paused = True
                        pause_start_time = pygame.time.get_ticks()
                        resume_button, quit_button = show_pause_screen(width, height, screen)
                        while paused:
                            for event in pygame.event.get():
                                if event.type == QUIT:
                                    cap.release()
                                    pygame.quit()
                                    sys.exit()
                                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                                    if resume_button.collidepoint(event.pos):
                                        paused = False
                                        elapsed_paused_time += pygame.time.get_ticks() - pause_start_time
                                    elif quit_button.collidepoint(event.pos):
                                        cap.release()
                                        pygame.quit()
                                        sys.exit()
                else:
                    if mask_surface.get_rect().collidepoint(mouse_pos):
                        if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
                            for i, (image, rect) in enumerate(zip([globals()[f"{item.split('.')[0]}_image"] for item, _, _ in items], [globals()[f"{item.split('.')[0]}_rect"] for item, _, _ in items])):
                                if rect.collidepoint(mouse_pos):
                                    items_visible[i] = False
                                    item_found_sound.play()
                                    praise_display_time = pygame.time.get_ticks()
                                    clicked_item = [item for item, _, _ in items][i]
                                    if clicked_item == "hammer.png":
                                        hammer_clicked = True
                                        tutorial_image_1_time = pygame.time.get_ticks()
                                    break

        if mouse_pos and slider_rect.collidepoint(mouse_pos):
            value = int((mouse_pos[0] - slider_pos[0]) / slider_size[0] * (slider_max_val - slider_min_val) + slider_min_val)
            threshold = max(min(value, slider_max_val), slider_min_val)

        if not paused:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)

            cx_left, cy_left, cx_right, cy_right = detect_eyes(detector, predictor, frame, threshold)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)

            if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
                mask_surface.fill((0, 0, 0, 255))
                mask_radius = 60
                pygame.draw.circle(mask_surface, (0, 0, 0, 128), (cx_right, cy_left), mask_radius)
                pygame.draw.circle(mask_surface, (0, 0, 0, 0), (cx_right, cy_left), mask_radius - 10)
            else: 
                mask_surface.fill((0, 0, 0, 255))

            screen.blit(background_image, background_rect)

            for i, (visible, image, rect) in enumerate(zip(items_visible, [globals()[f"{item.split('.')[0]}_image"] for item, _, _ in items], [globals()[f"{item.split('.')[0]}_rect"] for item, _, _ in items])):
                if visible:
                    screen.blit(image, rect)

            screen.blit(mask_surface, (0, 0))
            screen.blit(itemBox_image, itemBox_rect)

            for i, (silhouette, rect) in enumerate(zip(item_silhouettes, item_silhouettes_rects)):
                if items_visible[i]:
                    screen.blit(silhouette, rect)

            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time - elapsed_paused_time
            remaining_time = max(countdown_duration - int(elapsed_time / 1000), 0)

            minutes = remaining_time // 60
            seconds = remaining_time % 60

            text_surface = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
            screen.blit(text_surface, (10, 10))

            if clicked_item and pygame.time.get_ticks() - praise_display_time < 5000:
                screen.blit(explanation_images[clicked_item], explanation_image_rects[clicked_item])

            if not hammer_clicked:
                if elapsed_time < 3000:
                    screen.blit(tutorial_images[1], tutorial_image_rect)
                elif 3000 <= elapsed_time < 8000:
                    screen.blit(tutorial_images[2], tutorial_image_rect)
            else:
                if pygame.time.get_ticks() - tutorial_image_1_time < 3000:
                    screen.blit(tutorial_images[0], tutorial_image_rect)

            if remaining_time <= 0:
                restart_button = show_game_over_screen(width, height, screen)
                BG_music.stop()
                while True:
                    event = pygame.event.wait()
                    if event.type == QUIT:
                        cap.release()
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        if restart_button.collidepoint(mouse_pos):
                            BG_music.stop() 
                            BG_music = None
                            pygame.mixer.music.stop()
                            level_one_scene()

            if all(not visible for visible in items_visible):
                next_button= show_win_screen(width, height, screen)
                BG_music.stop()
                while True:
                    event = pygame.event.wait()
                    if event.type == QUIT:
                        cap.release()
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        if next_button.collidepoint(mouse_pos):
                            BG_music.stop() 
                            BG_music = None
                            pygame.mixer.music.stop()
                            start_level_two()

        if cx_left is None or cy_left is None or cx_right is None or cy_right is None:
            if elapsed_time < 5000:
                warning_text = font.render("Eyes not detected. Please adjust your camera or eye position.", True, (255, 0, 0))
                screen.blit(warning_text, (width // 2 - warning_text.get_width() // 2, height // 2))

        slider_rect, handle_rect = draw_slider(screen, slider_pos, slider_size, threshold, slider_min_val, slider_max_val)
        threshold_text = font.render("Please Adjust Threshold", True, (255, 255, 255))
        threshold_text2 = font.render("for Suitable Eye Detection", True, (255, 255, 255))
        screen.blit(threshold_text, (260, 1))
        screen.blit(threshold_text2, (250, 20))

        draw_pause_button(screen, pause_button_rect)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    level_one_scene()
