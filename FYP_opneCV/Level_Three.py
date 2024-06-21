import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import time
import pygame.mixer
from buttonScene import show_game_over_screen, show_win_screen, show_pause_screen, draw_pause_button
from LevelSelection import start_level_four
from eye_detection import detect_eyes

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

def level_three_scene():
    # Initialize Pygame
    pygame.init()    
    pygame.mixer.init()
    BG_music = pygame.mixer.Sound("assets/Music/207.mp3")
    BG_music.play()

    item_found_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")
    lose_life_sound = pygame.mixer.Sound("assets/SoundEffect/lose_life.mp3")

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    background_image = pygame.image.load("assets/Bg/maze1.png").convert_alpha()  # Load with alpha channel
    background_image = pygame.transform.scale(background_image, (int(background_image.get_width()), int(background_image.get_height())))
    background_rect = background_image.get_rect()
    background_rect.center = (width // 2, height // 2)
    #mask
    background_mask = pygame.mask.from_surface(background_image)

    characterBG_image = pygame.image.load("assets/goodjob/mazeAnticipation.png")
    characterBG_image = pygame.transform.scale(characterBG_image, (int(characterBG_image.get_width()), int(characterBG_image.get_height())))
    characterBG_rect = characterBG_image.get_rect()
    characterBG_rect.center = (width // 2, height // 2)

    characterGJBG_image = pygame.image.load("assets/goodjob/mazeGoodJob.png")
    characterGJBG_image = pygame.transform.scale(characterGJBG_image, (int(characterGJBG_image.get_width()), int(characterGJBG_image.get_height())))
    characterGJBG_rect = characterGJBG_image.get_rect()
    characterGJBG_rect.center = (width // 2, height // 2)

    top_image = pygame.image.load("assets/Bg/top.png")
    top_rect = top_image.get_rect()
    top_rect.center = (width // 2, 40)

    key_image = pygame.image.load("assets/Items/key.png")
    key_image = pygame.transform.scale(key_image, (int(key_image.get_width()), int(key_image.get_height())))
    key_rect = key_image.get_rect()
    key_position = (180, 270) 
    key_rect.center = key_position
    key_rect = key_image.get_rect(center=key_position)

    portalone_image = pygame.image.load("assets/Portal/portalOne/portalOne.png").convert_alpha()
    portalone_image = pygame.transform.scale(portalone_image, (int(portalone_image.get_width()/5), int(portalone_image.get_height()/5)))
    portalone_rect = portalone_image.get_rect(center=(590, 280))

    tutorial_image_paths = [
        "assets/goodjob/tutorialBunnyMaze1.png",
        "assets/goodjob/tutorialBunnyMaze2.png",
        "assets/goodjob/tutorialBunnyMaze3.png"
    ]

    tutorial_images = [pygame.image.load(path) for path in tutorial_image_paths]
    tutorial_images = [pygame.transform.scale(image, (int(image.get_width()), int(image.get_height()))) for image in tutorial_images]
    tutorial_image_rect = tutorial_images[0].get_rect(center=(width // 2 - 270, height // 2 + 130))

    initial_key_position = key_position

    fading_portalone = False
    fading_portaltwo = False
    portal_fade_speed = 15
    portalone_alpha = 255
    portaltwo_alpha = 255
    win = False

    key_visible = True
    keyTwo_visible = True

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    img = cv2.flip(img, 1)

    crosshair_size = 20
    crosshair = pygame.Surface((crosshair_size, crosshair_size), pygame.SRCALPHA)
    pygame.draw.line(crosshair, (255, 0, 0), (crosshair_size // 2, 0), (crosshair_size // 2, crosshair_size))
    pygame.draw.line(crosshair, (255, 0, 0), (0, crosshair_size // 2), (crosshair_size, crosshair_size // 2))

    red_flash = pygame.Surface((width, height))
    red_flash.fill((255, 0, 0))
    red_flash_alpha = 0

    clock = pygame.time.Clock()

    threshold = 30

    dragging_key = False

    offset_x_key, offset_y_key = 0, 0

    lives = 1
    font = pygame.font.Font(None, 36)

    cooldown_time = 3 
    last_key_collision = 0

    eye_on_key_time = 0
    eye_on_key_threshold = 1

    last_crosshair_x, last_crosshair_y = width // 2, height // 2

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    show_good_job = False
    good_job_start_time = 0
    good_job_display_duration = 2

    tutorial_start_time = time.time()
    tutorial_durations = [5, 5, 3]
    total_tutorial_time = sum(tutorial_durations)

    slider_pos = (10, 40)
    slider_size = (200, 20)
    slider_min_val = 0
    slider_max_val = 255

    while True:
        mouse_pos = None
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if pause_button_rect.collidepoint(mouse_pos):
                    paused = not paused
                    if paused:
                        pause_start_time = time.time()
                    else:
                        elapsed_paused_time += time.time() - pause_start_time

        if paused:
            resume_button, quit_button = show_pause_screen(width, height, screen)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if resume_button.collidepoint(mouse_pos):
                        paused = False
                        elapsed_paused_time += time.time() - pause_start_time
                    elif quit_button.collidepoint(mouse_pos):
                        cap.release()
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()
            continue

        if mouse_pos and slider_rect.collidepoint(mouse_pos):
            value = int((mouse_pos[0] - slider_pos[0]) / slider_size[0] * (slider_max_val - slider_min_val) + slider_min_val)
            threshold = max(min(value, slider_max_val), slider_min_val)

        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        cx_left, cy_left, cx_right, cy_right = detect_eyes(detector, predictor, frame, threshold)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)

        eyes_detected = False

        if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
            eyes_detected = True
            avg_eye_x = (cx_left + cx_right) // 2
            avg_eye_y = (cy_left + cy_right) // 2

            screen_eye_x = int(avg_eye_x * width / img.shape[1])
            screen_eye_y = int(avg_eye_y * height / img.shape[0])

            last_crosshair_x, last_crosshair_y = screen_eye_x, screen_eye_y

            if key_rect.collidepoint(screen_eye_x, screen_eye_y):
                eye_on_key_time += clock.get_time() / 1000.0 
                if eye_on_key_time >= eye_on_key_threshold:
                    dragging_key = True
                    #item_found_sound.play()
                    offset_x_key = key_rect.x - screen_eye_x
                    offset_y_key = key_rect.y - screen_eye_y
            else:
                eye_on_key_time = 0

        if eyes_detected:
            if dragging_key:
                key_rect.x = last_crosshair_x + offset_x_key
                key_rect.y = last_crosshair_y + offset_y_key

        current_time = time.time()

        if key_visible and (current_time - last_key_collision > cooldown_time):
            key_mask = pygame.mask.from_surface(key_image)
            offset = (key_rect.x - background_rect.x, key_rect.y - background_rect.y)
            if background_mask.overlap(key_mask, offset):
                lives -= 1 
                lose_life_sound.play() 
                last_key_collision = current_time
                red_flash_alpha = 150 
                if lives <= 0:
                    BG_music.stop()
                    restart_button = show_game_over_screen(width, height, screen)
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
                                level_three_scene()

        if key_rect.colliderect(portalone_rect) and key_visible:
            key_visible = False
            key_collected = True
            fading_portalone = True
            portalone_alpha = 255
            last_key_collision = time.time()
            item_found_sound.play()
            show_good_job = True
            good_job_start_time = time.time()


        current_time = time.time()

        if fading_portalone:
            portalone_alpha = max(portalone_alpha - portal_fade_speed, 0)
            portalone_image.set_alpha(portalone_alpha)
            if portalone_alpha == 0:
                fading_portalone = False

        if not key_visible and not fading_portalone:
            win = True

        if win:
            pygame.mixer.music.stop()
            level_three_two_scene(BG_music)
                        
        # Blit
        screen.blit(background_image, background_rect)
        screen.blit(characterBG_image, characterBG_rect)
        screen.blit(top_image, top_rect)

        screen.blit(portalone_image, portalone_rect)
        if key_visible:
            screen.blit(key_image, key_rect)

        lives_text = font.render(f'Lives: {lives}', True, (255, 255, 255))
        screen.blit(lives_text, (350, 30))

        screen.blit(crosshair, (last_crosshair_x - crosshair_size // 2, last_crosshair_y - crosshair_size // 2))

        if red_flash_alpha > 0:
            red_flash.set_alpha(red_flash_alpha)
            screen.blit(red_flash, (0, 0))
            red_flash_alpha = max(red_flash_alpha - 10, 0)

        if show_good_job and current_time - good_job_start_time < good_job_display_duration:
            screen.blit(characterGJBG_image, characterGJBG_rect)
        else:
            show_good_job = False

        slider_rect, handle_rect = draw_slider(screen, slider_pos, slider_size, threshold, slider_min_val, slider_max_val)
        
        threshold_text = font.render("Threshold Slider", True, (255, 255, 255))
        screen.blit(threshold_text, (10, 10))

        draw_pause_button(screen, pause_button_rect)

        current_time = time.time()
        if current_time - tutorial_start_time < total_tutorial_time:
            elapsed_tutorial_time = current_time - tutorial_start_time
            for i, duration in enumerate(tutorial_durations):
                if elapsed_tutorial_time < sum(tutorial_durations[:i + 1]):
                    screen.blit(tutorial_images[i], tutorial_image_rect)
                    break

        pygame.display.flip()

        clock.tick(60)

def level_three_two_scene(BG_music):
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    item_found_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")
    lose_life_sound = pygame.mixer.Sound("assets/SoundEffect/lose_life.mp3")

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    background_image = pygame.image.load("assets/Bg/maze2.png").convert_alpha() 
    background_image = pygame.transform.scale(background_image, (int(background_image.get_width()), int(background_image.get_height())))
    background_rect = background_image.get_rect()
    background_rect.center = (width // 2, height // 2)
    #mask
    background_mask = pygame.mask.from_surface(background_image)

    characterBG_image = pygame.image.load("assets/goodjob/mazeAnticipation.png")
    characterBG_image = pygame.transform.scale(characterBG_image, (int(characterBG_image.get_width()), int(characterBG_image.get_height())))
    characterBG_rect = characterBG_image.get_rect()
    characterBG_rect.center = (width // 2, height // 2)

    characterGJBG_image = pygame.image.load("assets/goodjob/mazeGoodJob.png")
    characterGJBG_image = pygame.transform.scale(characterGJBG_image, (int(characterGJBG_image.get_width()), int(characterGJBG_image.get_height())))
    characterGJBG_rect = characterGJBG_image.get_rect()
    characterGJBG_rect.center = (width // 2, height // 2)

    top_image = pygame.image.load("assets/Bg/top.png")
    top_rect = top_image.get_rect()
    top_rect.center = (width // 2, 40)

    key_image = pygame.image.load("assets/Items/key.png")
    key_image = pygame.transform.scale(key_image, (int(key_image.get_width()), int(key_image.get_height())))
    key_rect = key_image.get_rect()
    key_position = (160, 360) 
    key_rect.center = key_position
    key_rect = key_image.get_rect(center=key_position)

    portalone_image = pygame.image.load("assets/Portal/portalOne/portalOne.png").convert_alpha()
    portalone_image = pygame.transform.scale(portalone_image, (int(portalone_image.get_width()/5), int(portalone_image.get_height()/5)))
    portalone_rect = portalone_image.get_rect(center=(575, 200)) #185, 140

    fading_portalone = False
    portal_fade_speed = 15
    portalone_alpha = 255
    win = False

    key_visible = True

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    img = cv2.flip(img, 1)

    crosshair_size = 20
    crosshair = pygame.Surface((crosshair_size, crosshair_size), pygame.SRCALPHA)
    pygame.draw.line(crosshair, (255, 0, 0), (crosshair_size // 2, 0), (crosshair_size // 2, crosshair_size))
    pygame.draw.line(crosshair, (255, 0, 0), (0, crosshair_size // 2), (crosshair_size, crosshair_size // 2))

    red_flash = pygame.Surface((width, height))
    red_flash.fill((255, 0, 0))
    red_flash_alpha = 0

    clock = pygame.time.Clock()

    threshold = 30

    dragging_key = False

    offset_x_key, offset_y_key = 0, 0

    lives = 2
    font = pygame.font.Font(None, 36)

    cooldown_time = 3 
    last_key_collision = 0

    eye_on_key_time = 0
    eye_on_key_threshold = 1


    last_crosshair_x, last_crosshair_y = width // 2, height // 2

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    show_good_job = False
    good_job_start_time = 0
    good_job_display_duration = 2

    bg_music_paused = False

    slider_pos = (10, 40)
    slider_size = (200, 20)
    slider_min_val = 0
    slider_max_val = 255

    cx_left, cy_left, cx_right, cy_right = None, None, None, None

    while True:
        mouse_pos = None
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if pause_button_rect.collidepoint(mouse_pos):
                    paused = not paused
                    if paused:
                        pause_start_time = time.time()
                    else:
                        elapsed_paused_time += time.time() - pause_start_time

        if paused:
            resume_button, quit_button = show_pause_screen(width, height, screen)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if resume_button.collidepoint(mouse_pos):
                        paused = False
                        elapsed_paused_time += time.time() - pause_start_time
                    elif quit_button.collidepoint(mouse_pos):
                        cap.release()
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()
            continue

        if mouse_pos and slider_rect.collidepoint(mouse_pos):
            value = int((mouse_pos[0] - slider_pos[0]) / slider_size[0] * (slider_max_val - slider_min_val) + slider_min_val)
            threshold = max(min(value, slider_max_val), slider_min_val)

        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        cx_left, cy_left, cx_right, cy_right = detect_eyes(detector, predictor, frame, threshold)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)

        eyes_detected = False


        if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
            eyes_detected = True
            avg_eye_x = (cx_left + cx_right) // 2
            avg_eye_y = (cy_left + cy_right) // 2

            screen_eye_x = int(avg_eye_x * width / img.shape[1])
            screen_eye_y = int(avg_eye_y * height / img.shape[0])

            last_crosshair_x, last_crosshair_y = screen_eye_x, screen_eye_y

            if key_rect.collidepoint(screen_eye_x, screen_eye_y):
                eye_on_key_time += clock.get_time() / 1000.0 
                if eye_on_key_time >= eye_on_key_threshold:
                    dragging_key = True
                    offset_x_key = key_rect.x - screen_eye_x
                    offset_y_key = key_rect.y - screen_eye_y
            else:
                eye_on_key_time = 0

        if eyes_detected:
            if dragging_key:
                key_rect.x = last_crosshair_x + offset_x_key
                key_rect.y = last_crosshair_y + offset_y_key

        current_time = time.time()

        if key_visible and (current_time - last_key_collision > cooldown_time):
            key_mask = pygame.mask.from_surface(key_image)
            offset = (key_rect.x - background_rect.x, key_rect.y - background_rect.y)
            if background_mask.overlap(key_mask, offset):
                lives -= 1 
                lose_life_sound.play() 
                last_key_collision = current_time
                red_flash_alpha = 150 
                if lives <= 0:
                    BG_music.stop()
                    restart_button = show_game_over_screen(width, height, screen)
                    while True:
                        event = pygame.event.wait()
                        if event.type == QUIT:
                            cap.release()
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            if restart_button.collidepoint(mouse_pos):
                                BG_music.play() 
                                pygame.mixer.music.stop()
                                level_three_two_scene(BG_music)


        if key_rect.colliderect(portalone_rect) and key_visible:
            key_visible = False
            key_collected = True
            fading_portalone = True
            portalone_alpha = 255
            last_key_collision = time.time()
            item_found_sound.play()
            show_good_job = True
            good_job_start_time = time.time()


        current_time = time.time()

        if fading_portalone:
            portalone_alpha = max(portalone_alpha - portal_fade_speed, 0)
            portalone_image.set_alpha(portalone_alpha)
            if portalone_alpha == 0:
                fading_portalone = False


        if not key_visible and not fading_portalone:
            win = True

        if win:
            level_three_three_scene(BG_music)
             
        screen.blit(background_image, background_rect)
        screen.blit(characterBG_image, characterBG_rect)
        screen.blit(top_image, top_rect)

        screen.blit(portalone_image, portalone_rect)

        if key_visible:
            screen.blit(key_image, key_rect)

        lives_text = font.render(f'Lives: {lives}', True, (255, 255, 255))
        screen.blit(lives_text, (350, 30))

        screen.blit(crosshair, (last_crosshair_x - crosshair_size // 2, last_crosshair_y - crosshair_size // 2))

        if red_flash_alpha > 0:
            red_flash.set_alpha(red_flash_alpha)
            screen.blit(red_flash, (0, 0))
            red_flash_alpha = max(red_flash_alpha - 10, 0)

        if show_good_job and current_time - good_job_start_time < good_job_display_duration:
            screen.blit(characterGJBG_image, characterGJBG_rect)
        else:
            show_good_job = False

        slider_rect, handle_rect = draw_slider(screen, slider_pos, slider_size, threshold, slider_min_val, slider_max_val)
        
        threshold_text = font.render("Threshold Slider", True, (255, 255, 255))
        screen.blit(threshold_text, (10, 10))

        draw_pause_button(screen, pause_button_rect)

        pygame.display.flip()

        clock.tick(60)

def level_three_three_scene(BG_music):
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    item_found_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")
    lose_life_sound = pygame.mixer.Sound("assets/SoundEffect/lose_life.mp3")

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    background_image = pygame.image.load("assets/Bg/maze3.png").convert_alpha()  # Load with alpha channel
    background_image = pygame.transform.scale(background_image, (int(background_image.get_width()), int(background_image.get_height())))
    background_rect = background_image.get_rect()
    background_rect.center = (width // 2, height // 2)
    #mask
    background_mask = pygame.mask.from_surface(background_image)

    characterBG_image = pygame.image.load("assets/goodjob/mazeAnticipation.png")
    characterBG_image = pygame.transform.scale(characterBG_image, (int(characterBG_image.get_width()), int(characterBG_image.get_height())))
    characterBG_rect = characterBG_image.get_rect()
    characterBG_rect.center = (width // 2, height // 2)

    characterGJBG_image = pygame.image.load("assets/goodjob/mazeGoodJob.png")
    characterGJBG_image = pygame.transform.scale(characterGJBG_image, (int(characterGJBG_image.get_width()), int(characterGJBG_image.get_height())))
    characterGJBG_rect = characterGJBG_image.get_rect()
    characterGJBG_rect.center = (width // 2, height // 2)

    top_image = pygame.image.load("assets/Bg/top.png")
    top_rect = top_image.get_rect()
    top_rect.center = (width // 2, 40)

    key_image = pygame.image.load("assets/Items/key.png")
    key_image = pygame.transform.scale(key_image, (int(key_image.get_width()), int(key_image.get_height())))
    key_rect = key_image.get_rect()
    key_position = (130, 160) 
    key_rect.center = key_position
    key_rect = key_image.get_rect(center=key_position)

    portalone_image = pygame.image.load("assets/Portal/portalTwo/portalTwo.png").convert_alpha()
    portalone_image = pygame.transform.scale(portalone_image, (int(portalone_image.get_width()/5), int(portalone_image.get_height()/5)))
    portalone_rect = portalone_image.get_rect(center=(685, 400))


    fading_portalone = False
    portal_fade_speed = 15 
    portalone_alpha = 255
    win = False

    key_visible = True

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    img = cv2.flip(img, 1)

    crosshair_size = 20
    crosshair = pygame.Surface((crosshair_size, crosshair_size), pygame.SRCALPHA)
    pygame.draw.line(crosshair, (255, 0, 0), (crosshair_size // 2, 0), (crosshair_size // 2, crosshair_size))
    pygame.draw.line(crosshair, (255, 0, 0), (0, crosshair_size // 2), (crosshair_size, crosshair_size // 2))

    red_flash = pygame.Surface((width, height))
    red_flash.fill((255, 0, 0))
    red_flash_alpha = 0

    clock = pygame.time.Clock()

    threshold = 30

    dragging_key = False
    dragging_keyTwo = False

    offset_x_key, offset_y_key = 0, 0

    lives = 2
    font = pygame.font.Font(None, 36)

    cooldown_time = 3 
    last_key_collision = 0

    eye_on_key_time = 0
    eye_on_key_threshold = 1

    last_crosshair_x, last_crosshair_y = width // 2, height // 2

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    show_good_job = False
    good_job_start_time = 0
    good_job_display_duration = 2

    slider_pos = (10, 40)
    slider_size = (200, 20)
    slider_min_val = 0
    slider_max_val = 255

    while True:
        mouse_pos = None
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if pause_button_rect.collidepoint(mouse_pos):
                    paused = not paused
                    if paused:
                        pause_start_time = time.time()
                    else:
                        elapsed_paused_time += time.time() - pause_start_time

        if paused:
            resume_button, quit_button = show_pause_screen(width, height, screen)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if resume_button.collidepoint(mouse_pos):
                        paused = False
                        elapsed_paused_time += time.time() - pause_start_time
                    elif quit_button.collidepoint(mouse_pos):
                        cap.release()
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()
            continue

        if mouse_pos and slider_rect.collidepoint(mouse_pos):
            value = int((mouse_pos[0] - slider_pos[0]) / slider_size[0] * (slider_max_val - slider_min_val) + slider_min_val)
            threshold = max(min(value, slider_max_val), slider_min_val)

        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        cx_left, cy_left, cx_right, cy_right = detect_eyes(detector, predictor, frame, threshold)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)

        eyes_detected = False

        if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
            eyes_detected = True
            avg_eye_x = (cx_left + cx_right) // 2
            avg_eye_y = (cy_left + cy_right) // 2

            screen_eye_x = int(avg_eye_x * width / img.shape[1])
            screen_eye_y = int(avg_eye_y * height / img.shape[0])

            last_crosshair_x, last_crosshair_y = screen_eye_x, screen_eye_y

            if key_rect.collidepoint(screen_eye_x, screen_eye_y):
                eye_on_key_time += clock.get_time() / 1000.0 
                if eye_on_key_time >= eye_on_key_threshold:
                    dragging_key = True
                    #item_found_sound.play()
                    offset_x_key = key_rect.x - screen_eye_x
                    offset_y_key = key_rect.y - screen_eye_y
            else:
                eye_on_key_time = 0

        if eyes_detected:
            if dragging_key:
                key_rect.x = last_crosshair_x + offset_x_key
                key_rect.y = last_crosshair_y + offset_y_key

        current_time = time.time()

        if key_visible and (current_time - last_key_collision > cooldown_time):
            key_mask = pygame.mask.from_surface(key_image)
            offset = (key_rect.x - background_rect.x, key_rect.y - background_rect.y)
            if background_mask.overlap(key_mask, offset):
                lives -= 1 
                lose_life_sound.play() 
                last_key_collision = current_time
                red_flash_alpha = 150 
                if lives <= 0:
                    BG_music.stop()
                    restart_button = show_game_over_screen(width, height, screen)
                    while True:
                        event = pygame.event.wait()
                        if event.type == QUIT:
                            cap.release()
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            if restart_button.collidepoint(mouse_pos):
                                BG_music.play() 
                                pygame.mixer.music.stop()
                                level_three_three_scene(BG_music)

        if key_rect.colliderect(portalone_rect) and key_visible:
            key_visible = False
            key_collected = True
            fading_portalone = True
            portalone_alpha = 255
            last_key_collision = time.time()
            item_found_sound.play()
            show_good_job = True
            good_job_start_time = time.time()


        current_time = time.time()

        if fading_portalone:
            portalone_alpha = max(portalone_alpha - portal_fade_speed, 0)
            portalone_image.set_alpha(portalone_alpha)
            if portalone_alpha == 0:
                fading_portalone = False

        if not key_visible and not fading_portalone:
            win = True

        if win:
            BG_music.stop()
            restart_button = show_win_screen(width, height, screen)
            while True:
                event = pygame.event.wait()
                if event.type == QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_button.collidepoint(mouse_pos):
                        pygame.mixer.music.stop()
                        start_level_four()
                        
        # Blit
        screen.blit(background_image, background_rect)
        screen.blit(characterBG_image, characterBG_rect)
        screen.blit(top_image, top_rect)

        screen.blit(portalone_image, portalone_rect)

        if key_visible:
            screen.blit(key_image, key_rect)

        lives_text = font.render(f'Lives: {lives}', True, (255, 255, 255))
        screen.blit(lives_text, (350, 30))

        screen.blit(crosshair, (last_crosshair_x - crosshair_size // 2, last_crosshair_y - crosshair_size // 2))

        if red_flash_alpha > 0:
            red_flash.set_alpha(red_flash_alpha)
            screen.blit(red_flash, (0, 0))
            red_flash_alpha = max(red_flash_alpha - 10, 0)

        if show_good_job and current_time - good_job_start_time < good_job_display_duration:
            screen.blit(characterGJBG_image, characterGJBG_rect)
        else:
            show_good_job = False

        slider_rect, handle_rect = draw_slider(screen, slider_pos, slider_size, threshold, slider_min_val, slider_max_val)
        
        threshold_text = font.render("Threshold Slider", True, (255, 255, 255))
        screen.blit(threshold_text, (10, 10))

        draw_pause_button(screen, pause_button_rect)

        pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    level_three_scene()
