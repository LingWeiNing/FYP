import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import random
import time
import pygame.mixer
from buttonScene import show_game_over_screen, show_win_screen, show_pause_screen, draw_pause_button
from EndingScene import start_ending
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

def cut_image(image, rows, cols):
    img_height, img_width = image.get_height(), image.get_width()
    piece_width = img_width // cols
    piece_height = img_height // rows
    pieces = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)
            piece = image.subsurface(rect)
            pieces.append(piece)
    return pieces, piece_width, piece_height

def shuffle_pieces(pieces, rows, cols):
    positions = [(i % cols, i // cols) for i in range(len(pieces))]
    random.shuffle(positions)
    return positions

def draw_grid(screen, rows, cols, piece_width, piece_height, x_offset, y_offset):
    for row in range(rows + 1):
        start_pos = (x_offset, y_offset + row * piece_height)
        end_pos = (x_offset + cols * piece_width, y_offset + row * piece_height)
        pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 2)

    for col in range(cols + 1):
        start_pos = (x_offset + col * piece_width, y_offset)
        end_pos = (x_offset + col * piece_width, y_offset + rows * piece_height)
        pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 2)

def level_four_scene():
    pygame.init()
    pygame.mixer.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    puzzle_image = pygame.image.load("assets/Bg/museum.jpg")
    puzzle_image = pygame.transform.scale(puzzle_image, (450, 350))
    rows, cols = 3, 3 
    pieces, piece_width, piece_height = cut_image(puzzle_image, rows, cols)

    puzzleclipped_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")
    BG_music = pygame.mixer.Sound("assets/Music/OperationDO.mp3")
    BG_music.play()
    BG_music.play(-1)

    praising_image = pygame.image.load("assets/goodjob/GoodJobBunny.png")
    praising_rect = praising_image.get_rect(center=(600, 500))

    tutorial_image_paths = [
        "assets/goodjob/tutorialBunnyPuzzle1.png",
        "assets/goodjob/tutorialBunnyPuzzle2.png",
        "assets/goodjob/tutorialBunnyPuzzle3.png"
    ]

    tutorial_images = [pygame.image.load(path) for path in tutorial_image_paths]
    tutorial_images = [pygame.transform.scale(image, (int(image.get_width()), int(image.get_height()))) for image in tutorial_images]
    tutorial_image_rect = tutorial_images[0].get_rect(center=(width // 2 - 270, height // 2 + 150))

    shuffled_positions = shuffle_pieces(pieces, rows, cols)

    piece_positions = [(x * piece_width, y * piece_height) for x, y in shuffled_positions]
    correct_positions = [(i % cols * piece_width, i // cols * piece_height) for i in range(len(pieces))]

    selected_piece = None

    correctly_placed = [False] * len(pieces)

    clock = pygame.time.Clock()

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    img = cv2.flip(img, 1)

    start_time = pygame.time.get_ticks()
    countdown_time = 600

    show_praising_image = False
    praising_image_display_time = 0

    threshold = 200

    font_timer = pygame.font.Font(None, 36)

    def snap_piece(piece_idx):
        x, y = piece_positions[piece_idx]
        correct_x, correct_y = correct_positions[piece_idx]
        if abs(x - correct_x) < piece_width // 3 and abs(y - correct_y) < piece_height // 3:
            piece_positions[piece_idx] = (correct_x, correct_y)
            correctly_placed[piece_idx] = True
            puzzleclipped_sound.play()
            global show_praising_image, praising_image_display_time
            show_praising_image = True
            praising_image_display_time = pygame.time.get_ticks()

    x_offset = 190 
    y_offset = 130 

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    tutorial_start_time = time.time()
    tutorial_durations = [5, 5, 5] 
    total_tutorial_time = sum(tutorial_durations)

    slider_pos = (10, 40)
    slider_size = (200, 20)
    slider_min_val = 0
    slider_max_val = 255

    cx_left, cy_left, cx_right, cy_right = None, None, None, None
    
    # main game loop
    while True:
        mouse_pos = None
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_x, mouse_y = event.pos
                    if selected_piece is None:
                        for i, (x, y) in enumerate(piece_positions):
                            if correctly_placed[i]:
                                continue
                            rect = pygame.Rect(x + x_offset, y + y_offset, piece_width, piece_height)
                            if rect.collidepoint(mouse_x, mouse_y):
                                selected_piece = i
                                break
                    else:
                        snap_piece(selected_piece)
                        selected_piece = None
                if pause_button_rect.collidepoint(event.pos):
                    paused = True
                    pause_start_time = pygame.time.get_ticks()
                    resume_button, quit_button = show_pause_screen(width, height, screen)
                    while paused:
                        event = pygame.event.wait()
                        if event.type == QUIT:
                            cap.release()
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if resume_button.collidepoint(event.pos):
                                paused = False
                                elapsed_paused_time += pygame.time.get_ticks() - pause_start_time
                            elif quit_button.collidepoint(event.pos):
                                cap.release()
                                level_four_scene()
                                BG_music.stop() 
                                sys.exit()

        slider_rect, handle_rect = draw_slider(screen, slider_pos, slider_size, threshold, slider_min_val, slider_max_val)

        if mouse_pos and slider_rect.collidepoint(mouse_pos):
            value = int((mouse_pos[0] - slider_pos[0]) / slider_size[0] * (slider_max_val - slider_min_val) + slider_min_val)
            threshold = max(min(value, slider_max_val), slider_min_val)

        if not paused:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time - elapsed_paused_time
            remaining_time = max(countdown_time - int(elapsed_time / 1000), 0)

            screen.fill((0, 0, 0))

            # Draw the red grid
            draw_grid(screen, rows, cols, piece_width, piece_height, x_offset, y_offset)

            for i, (x, y) in enumerate(piece_positions):
                screen.blit(pieces[i], (x + x_offset, y + y_offset))

            draw_pause_button(screen, pause_button_rect)

            minutes = remaining_time // 60
            seconds = remaining_time % 60
            font = pygame.font.Font(None, 36)

            timer_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
            screen.blit(timer_text, (320, 30))

            if show_praising_image:
                screen.blit(praising_image, praising_rect)
                if current_time - praising_image_display_time >= 3000:
                    show_praising_image = False

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
                            level_four_scene()

            if all(correctly_placed):
                next_button = show_win_screen(width, height, screen)
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
                            start_ending()

            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)

            cx_left, cy_left, cx_right, cy_right = detect_eyes(detector, predictor, frame, threshold)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)

            if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
                avg_eye_x = (cx_left + cx_right) // 2
                avg_eye_y = (cy_left + cy_right) // 2

                screen_eye_x = int(avg_eye_x * width / img.shape[1])
                screen_eye_y = int(avg_eye_y * height / img.shape[0])

                if selected_piece is not None and not correctly_placed[selected_piece]:
                    piece_positions[selected_piece] = (screen_eye_x - piece_width // 2, screen_eye_y - piece_height // 2)

            current_time = time.time()
            if current_time - tutorial_start_time < total_tutorial_time:
                elapsed_tutorial_time = current_time - tutorial_start_time
                for i, duration in enumerate(tutorial_durations):
                    if elapsed_tutorial_time < sum(tutorial_durations[:i + 1]):
                        screen.blit(tutorial_images[i], tutorial_image_rect)
                        break

            slider_rect, handle_rect = draw_slider(screen, slider_pos, slider_size, threshold, slider_min_val, slider_max_val)
        
            threshold_text = font.render("Threshold Slider", True, (255, 255, 255))
            screen.blit(threshold_text, (10, 10))

            pygame.display.flip()

            clock.tick(60)

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    level_four_scene()

