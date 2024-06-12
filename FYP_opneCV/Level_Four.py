import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import random
import pygame.mixer
from buttonScene import show_game_over_screen, show_win_screen, show_pause_screen, draw_pause_button
from LevelSelection import start_ending

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

def level_four_scene():
    pygame.init()
    pygame.mixer.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    puzzle_image = pygame.image.load("assets/Bg/museum.jpg")
    rows, cols = 2, 2
    pieces, piece_width, piece_height = cut_image(puzzle_image, rows, cols)

    puzzleclipped_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")

    praising_image = pygame.image.load("assets/goodjob/GoodJobBunny.png")
    praising_rect = praising_image.get_rect(center=(600, 500))

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
    countdown_time = 1

    font_timer = pygame.font.Font(None, 36)

    def snap_piece(piece_idx):
        x, y = piece_positions[piece_idx]
        correct_x, correct_y = correct_positions[piece_idx]
        if abs(x - correct_x) < piece_width // 3 and abs(y - correct_y) < piece_height // 3:
            piece_positions[piece_idx] = (correct_x, correct_y)
            correctly_placed[piece_idx] = True

    x_offset = 80 
    y_offset = 80 

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    # main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
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
                        puzzleclipped_sound.play()
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
                                pygame.quit()
                                sys.exit()

        if not paused:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time - elapsed_paused_time
            remaining_time = max(countdown_time - int(elapsed_time / 1000), 0)

            screen.fill((0, 0, 0))
            for i, (x, y) in enumerate(piece_positions):
                if correctly_placed[i]:
                    screen.blit(pieces[i], (x + x_offset, y + y_offset))

            for i, (x, y) in enumerate(piece_positions):
                if not correctly_placed[i]:
                    screen.blit(pieces[i], (x + x_offset, y + y_offset))

            draw_pause_button(screen, pause_button_rect)

            timer_text = font_timer.render(f"Time: {int(remaining_time)}", True, (255, 255, 255))
            screen.blit(timer_text, (10, 10))

            if remaining_time <= 0:
                cap.release()
                show_game_over_screen(width, height, screen)
                pygame.display.flip()
                pygame.time.wait(2000)
                pygame.quit()
                sys.exit()

            if all(correctly_placed):
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
                            start_ending()
                        elif quit_button.collidepoint(mouse_pos):
                            cap.release()
                            pygame.quit()
                            sys.exit()

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

            if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
                avg_eye_x = (cx_left + cx_right) // 2
                avg_eye_y = (cy_left + cy_right) // 2

                screen_eye_x = int(avg_eye_x * width / img.shape[1])
                screen_eye_y = int(avg_eye_y * height / img.shape[0])

                if selected_piece is not None and not correctly_placed[selected_piece]:
                    piece_positions[selected_piece] = (screen_eye_x - piece_width // 2, screen_eye_y - piece_height // 2)

            pygame.display.flip()

            clock.tick(60)

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    level_four_scene()
