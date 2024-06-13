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
    pygame.mixer.init()

    item_found_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")
    lose_life_sound = pygame.mixer.Sound("assets/SoundEffect/lose_life.mp3")
    BG_music = pygame.mixer.Sound("assets/Music/207.mp3")

    # Set up the Pygame window
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    # Load background image and set its rectangle
    background_image = pygame.image.load("assets/Bg/maze.png").convert_alpha()  # Load with alpha channel
    background_image = pygame.transform.scale(background_image, (int(background_image.get_width() * 0.7), int(background_image.get_height() * 0.7)))
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

    # Load key images and set their rectangles
    key_image = pygame.image.load("assets/Items/key.png")
    key_image = pygame.transform.scale(key_image, (int(key_image.get_width() * 0.6), int(key_image.get_height() * 0.6)))
    key_rect = key_image.get_rect()
    key_position = (220, 430) 
    key_rect.center = key_position
    key_rect = key_image.get_rect(center=key_position)

    keyTwo_image = pygame.image.load("assets/Items/key2.png")
    keyTwo_image = pygame.transform.scale(keyTwo_image, (int(keyTwo_image.get_width() * 0.6), int(keyTwo_image.get_height() * 0.6)))
    keyTwo_rect = keyTwo_image.get_rect()
    keyTwo_position = (220, 165) 
    keyTwo_rect.center = keyTwo_position
    keyTwo_rect = keyTwo_image.get_rect(center=keyTwo_position)

    portalone_image = pygame.image.load("assets/Portal/portalOne/portalOne.png").convert_alpha()
    portalone_image = pygame.transform.scale(portalone_image, (int(portalone_image.get_width()/8), int(portalone_image.get_height()/8)))
    portalone_rect = portalone_image.get_rect(center=(width // 2 + 185, height // 2 + 140)) #185, 140

    portaltwo_image = pygame.image.load("assets/Portal/portalTwo/portalTwo.png").convert_alpha()
    portaltwo_image = pygame.transform.scale(portaltwo_image, (int(portaltwo_image.get_width()/8), int(portaltwo_image.get_height()/8)))
    portaltwo_rect = portaltwo_image.get_rect(center=(width // 2 + 30, height // 2 - 10)) #30, -10

    tutorial_image_paths = [
        "assets/goodjob/tutorialBunnyMaze1.png",
        "assets/goodjob/tutorialBunnyMaze2.png",
        "assets/goodjob/tutorialBunnyMaze3.png"
    ]

    tutorial_images = [pygame.image.load(path) for path in tutorial_image_paths]
    tutorial_images = [pygame.transform.scale(image, (int(image.get_width()), int(image.get_height()))) for image in tutorial_images]
    tutorial_image_rect = tutorial_images[0].get_rect(center=(width // 2 - 270, height // 2 + 60))

    initial_key_position = key_position
    initial_keyTwo_position = keyTwo_position

    fading_portalone = False
    fading_portaltwo = False
    portal_fade_speed = 5 
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

    # Set up Pygame clock
    clock = pygame.time.Clock()

    threshold = 80

    dragging_key = False
    dragging_keyTwo = False

    offset_x_key, offset_y_key = 0, 0
    offset_x_keyTwo, offset_y_keyTwo = 0, 0

    lives = 3
    font = pygame.font.Font(None, 36)

    cooldown_time = 3 
    last_key_collision = 0
    last_keyTwo_collision = 0

    eye_on_key_time = 0
    eye_on_key_threshold = 1

    eye_on_keyTwo_time = 0

    last_crosshair_x, last_crosshair_y = width // 2, height // 2

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    show_good_job = False
    good_job_start_time = 0
    good_job_display_duration = 2

    tutorial_start_time = time.time()
    tutorial_durations = [3, 5, 3]  # Durations in seconds for each tutorial image
    total_tutorial_time = sum(tutorial_durations)

    BG_music.play()

    while True:
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
                if key_rect.collidepoint(mouse_pos):
                    dragging_key = True
                    offset_x_key = key_rect.x - mouse_pos[0]
                    offset_y_key = key_rect.y - mouse_pos[1]
                elif keyTwo_rect.collidepoint(mouse_pos):
                    dragging_keyTwo = True
                    offset_x_keyTwo = keyTwo_rect.x - mouse_pos[0]
                    offset_y_keyTwo = keyTwo_rect.y - mouse_pos[1]
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                dragging_key = False
                dragging_keyTwo = False
            elif event.type == MOUSEMOTION:
                if dragging_key:
                    mouse_pos = pygame.mouse.get_pos()
                    key_rect.x = mouse_pos[0] + offset_x_key
                    key_rect.y = mouse_pos[1] + offset_y_key
                elif dragging_keyTwo:
                    mouse_pos = pygame.mouse.get_pos()
                    keyTwo_rect.x = mouse_pos[0] + offset_x_keyTwo
                    keyTwo_rect.y = mouse_pos[1] + offset_y_keyTwo

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

        ret, img = cap.read()

        # Horizontally flip the webcam feed
        img = cv2.flip(img, 1)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 1)

        cx_left, cy_left, cx_right, cy_right = None, None, None, None

        eyes_detected = False

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

            if keyTwo_rect.collidepoint(screen_eye_x, screen_eye_y):
                eye_on_keyTwo_time += clock.get_time() / 1000.0 
                if eye_on_keyTwo_time >= eye_on_key_threshold:
                    dragging_keyTwo = True
                    #item_found_sound.play()
                    offset_x_keyTwo = keyTwo_rect.x - screen_eye_x
                    offset_y_keyTwo = keyTwo_rect.y - screen_eye_y
            else:
                eye_on_keyTwo_time = 0

        if eyes_detected:
            if dragging_key:
                key_rect.x = last_crosshair_x + offset_x_key
                key_rect.y = last_crosshair_y + offset_y_key

            if dragging_keyTwo:
                keyTwo_rect.x = last_crosshair_x + offset_x_keyTwo
                keyTwo_rect.y = last_crosshair_y + offset_y_keyTwo

        current_time = time.time()
        if keyTwo_visible and (current_time - last_keyTwo_collision > cooldown_time):
            keyTwo_mask = pygame.mask.from_surface(keyTwo_image)
            offset = (keyTwo_rect.x - background_rect.x, keyTwo_rect.y - background_rect.y)
            if background_mask.overlap(keyTwo_mask, offset):
                lives -= 1  
                lose_life_sound.play() 
                last_keyTwo_collision = current_time 
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
                                level_three_scene()

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

        if keyTwo_rect.colliderect(portaltwo_rect) and keyTwo_visible:
            keyTwo_visible = False
            keyTwo_collected = True
            fading_portaltwo = True
            portaltwo_alpha = 255
            last_keyTwo_collision = time.time()
            item_found_sound.play()
            show_good_job = True
            good_job_start_time = time.time()

        current_time = time.time()

        if fading_portalone:
            portalone_alpha = max(portalone_alpha - portal_fade_speed, 0)
            portalone_image.set_alpha(portalone_alpha)
            if portalone_alpha == 0:
                fading_portalone = False

        if fading_portaltwo:
            portaltwo_alpha = max(portaltwo_alpha - portal_fade_speed, 0)
            portaltwo_image.set_alpha(portaltwo_alpha)
            if portaltwo_alpha == 0:
                fading_portaltwo = False

        if not key_visible and not keyTwo_visible and not fading_portalone and not fading_portaltwo:
            win = True

        if win:
            restart_button = show_win_screen(width, height, screen)
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
                        start_level_four()
                        
        # Blit
        screen.blit(characterBG_image, characterBG_rect)
        screen.blit(background_image, background_rect)

        screen.blit(top_image, top_rect)

        screen.blit(portalone_image, portalone_rect)
        screen.blit(portaltwo_image, portaltwo_rect)

        if keyTwo_visible:
            screen.blit(keyTwo_image, keyTwo_rect)

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

if __name__ == "__main__":
    level_three_scene()
