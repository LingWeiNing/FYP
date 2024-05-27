import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import random

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def eye_on_mask(mask, side):
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

# Function to cut the image into pieces
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

# Function to shuffle pieces
def shuffle_pieces(pieces):
    positions = [(i % cols, i // cols) for i in range(len(pieces))]
    random.shuffle(positions)
    return positions

# Initialize Pygame
pygame.init()

# Set up the Pygame window
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("FYP Game")

# Load background image and cut it into pieces
puzzle_image = pygame.image.load("assets/Bg/museum.jpg")
rows, cols = 3, 4
pieces, piece_width, piece_height = cut_image(puzzle_image, rows, cols)

# Shuffle pieces
shuffled_positions = shuffle_pieces(pieces)

# Store pieces' current positions
piece_positions = [(x * piece_width, y * piece_height) for x, y in shuffled_positions]
correct_positions = [(i % cols * piece_width, i // cols * piece_height) for i in range(len(pieces))]

# Initialize selected piece variable
selected_piece = None

# Initialize list to track correctly placed pieces
correctly_placed = [False] * len(pieces)

# Set up Pygame clock
clock = pygame.time.Clock()

# Initialize face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
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

# Define a function to snap pieces into place
def snap_piece(piece_idx):
    x, y = piece_positions[piece_idx]
    correct_x, correct_y = correct_positions[piece_idx]
    if abs(x - correct_x) < piece_width // 3 and abs(y - correct_y) < piece_height // 3:
        piece_positions[piece_idx] = (correct_x, correct_y)
        correctly_placed[piece_idx] = True

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
                    # Select a piece if not already selected
                    for i, (x, y) in enumerate(piece_positions):
                        if correctly_placed[i]:
                            continue  # Skip already placed pieces
                        rect = pygame.Rect(x, y, piece_width, piece_height)
                        if rect.collidepoint(mouse_x, mouse_y):
                            selected_piece = i
                            break
                else:
                    # Place the piece down and snap it into place if close to the correct position
                    snap_piece(selected_piece)
                    selected_piece = None

    # Draw the puzzle pieces
    screen.fill((255, 255, 255))
    for i, (x, y) in enumerate(piece_positions):
        screen.blit(pieces[i], (x, y))

    # Check if all pieces are correctly placed
    if all(correctly_placed):
        # Display the win screen
        win_screen = True
        while win_screen:
            for event in pygame.event.get():
                if event.type == QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_x, mouse_y = event.pos
                        if restart_button.collidepoint(mouse_x, mouse_y):
                            # Restart the game
                            win_screen = False
                            # Reset puzzle positions
                            shuffled_positions = shuffle_pieces(pieces)
                            piece_positions = [(x * piece_width, y * piece_height) for x, y in shuffled_positions]
                            correctly_placed = [False] * len(pieces)
                        elif quit_button.collidepoint(mouse_x, mouse_y):
                            # Quit the game
                            cap.release()
                            pygame.quit()
                            sys.exit()

            # Show win screen
            screen.fill((255, 255, 255))
            restart_button, quit_button = show_win_screen(width, height, screen)
            pygame.display.flip()
            clock.tick(60)

    # Webcam processing for eye tracking
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)

    cx_left, cy_left, cx_right, cy_right = None, None, None, None

    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = eye_on_mask(mask, left)
        mask = eye_on_mask(mask, right)
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
        # Calculate the average eye position
        avg_eye_x = (cx_left + cx_right) // 2
        avg_eye_y = (cy_left + cy_right) // 2

        # Map the average eye position to screen coordinates
        screen_eye_x = int(avg_eye_x * width / img.shape[1])
        screen_eye_y = int(avg_eye_y * height / img.shape[0])

        # Move the selected puzzle piece with eye gaze
        if selected_piece is not None and not correctly_placed[selected_piece]:
            piece_positions[selected_piece] = (screen_eye_x - piece_width // 2, screen_eye_y - piece_height // 2)

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Release the webcam and close the Pygame window
cap.release()
pygame.quit()

