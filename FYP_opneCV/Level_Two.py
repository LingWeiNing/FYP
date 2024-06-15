import cv2
import dlib
import numpy as np
import pygame
from pygame.locals import *
import sys
import random
import pygame.mixer
from buttonScene import show_game_over_screen, show_win_screen, show_pause_screen, draw_pause_button
from LevelSelection import start_level_three

class Mosquito(pygame.sprite.Sprite):
    taunting_mosquito = None

    def __init__(self, images, taunt_images, x, y, speed, scale_factor):
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

        # Taunt related attributes
        self.taunt_images = [pygame.image.load(image) for image in taunt_images]
        self.show_taunt = False
        self.taunt_image = None
        self.taunt_start_time = 0
        self.taunt_duration = 3000
        self.next_taunt_time = pygame.time.get_ticks() + random.randint(5000, 8000) 

        self.cooldown_duration = 8000 
        self.last_taunt_time = 0

    def update(self):
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        self.rect.x += self.dx
        self.rect.y += self.dy

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

        velocity_x = self.rect.x - self.prev_x

        if velocity_x > 0:
            self.images = [pygame.transform.flip(image, True, False) for image in self.original_images]
        elif velocity_x < 0:
            self.images = self.original_images.copy()

        self.image = self.images[self.index]

        self.prev_x = self.rect.x
        self.prev_y = self.rect.y

        # Taunt logic
        current_time = pygame.time.get_ticks()
        if self.show_taunt and current_time - self.taunt_start_time > self.taunt_duration:
            self.show_taunt = False
            Mosquito.taunting_mosquito = None
            self.last_taunt_time = current_time
            self.next_taunt_time = current_time + random.randint(5000, 8000)
            print(f"Taunt ended. Next taunt time: {self.next_taunt_time}")

        if not self.show_taunt and current_time >= self.next_taunt_time:
            if current_time - self.last_taunt_time >= self.cooldown_duration and Mosquito.taunting_mosquito is None:
                self.show_taunt = True
                self.taunt_image = random.choice(self.taunt_images)
                self.taunt_start_time = current_time
                Mosquito.taunting_mosquito = self
                print(f"Taunt started. Taunt duration: {self.taunt_duration}")

    def display_taunt(self, screen):
        if self.show_taunt and self.taunt_image:
            taunt_rect = self.taunt_image.get_rect(center=(self.rect.centerx + 40, self.rect.top - 20))  # Adjust the Y position to be above the mosquito
            screen.blit(self.taunt_image, taunt_rect)


def spawn_mosquitoes(num_mosquitoes, images, taunt_images, scale_factor):
    mosquitoes = pygame.sprite.Group()
    for _ in range(num_mosquitoes):
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        speed = random.uniform(1, 3)
        mosquito = Mosquito(images, taunt_images, x, y, speed, scale_factor)
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
    pygame.mixer.init()

    item_found_sound = pygame.mixer.Sound("assets/SoundEffect/Bling.mp3")

    BG_music = pygame.mixer.Sound("assets/Music/Unwelcome-School.mp3")

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("FYP Game")

    background_image = pygame.image.load("assets/Bg/gym.jpg")
    background_rect = background_image.get_rect()
    background_rect.center = (width // 2, height // 2)

    top_image = pygame.image.load("assets/Bg/top.png")
    top_rect = top_image.get_rect()
    top_rect.center = (width // 2, 70)

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor/shape_predictor_68_face_landmarks.dat')
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    cap = cv2.VideoCapture(0)
    ret, img = cap.read()
    img = cv2.flip(img, 1)

    clock = pygame.time.Clock()

    mosquito_images = [
        "assets/Items/mosquito1.png",
        "assets/Items/mosquito2.png"
    ]

    mosquitoTaunt_images = [
        "assets/Dialogue/mosquitoTaunt1.png",
        "assets/Dialogue/mosquitoTaunt2.png",
        "assets/Dialogue/mosquitoTaunt3.png",
        "assets/Dialogue/mosquitoTaunt4.png"
    ]

    mosquitoes = spawn_mosquitoes(5, mosquito_images, mosquitoTaunt_images, (100, 100))

    mosquito_counter = 0

    praising_image = pygame.image.load("assets/goodjob/GoodJobChief.png")
    praising_rect = praising_image.get_rect(center=(600, 500))

    show_praising_image = False
    praising_image_display_time = 0

    threshold = 80

    mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    start_time = pygame.time.get_ticks()
    countdown_duration = 100

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    BG_music.play()

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if pause_button_rect.collidepoint(mouse_pos):
                    paused = True
                    pause_start_time = pygame.time.get_ticks()
                elif mask_surface.get_rect().collidepoint(mouse_pos):
                    if cx_left is not None and cy_left is not None and cx_right is not None and cy_right is not None:
                        dist_to_center = ((mouse_pos[0] - cx_right) ** 2 + (mouse_pos[1] - cy_left) ** 2) ** 0.5
                        if dist_to_center < mask_radius:
                            for mosquito in mosquitoes:
                                if mosquito.rect.collidepoint(mouse_pos):
                                    mosquitoes.remove(mosquito)
                                    mosquito_counter += 1
                                    item_found_sound.play()
                                    new_mosquito = Mosquito(mosquito_images, mosquitoTaunt_images, random.randint(0, 800), random.randint(0, 600), random.uniform(1, 3), (100, 100))
                                    mosquitoes.add(new_mosquito)
                                    show_praising_image = True
                                    praising_image_display_time = pygame.time.get_ticks()
                                    break
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if not paused:
                        paused = True
                        pause_start_time = pygame.time.get_ticks()
        
        if paused:
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

        if not paused:
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
                mask_surface.fill((0, 0, 0, 255))
                mask_radius = 60
                pygame.draw.circle(mask_surface, (0, 0, 0, 128), (cx_right, cy_left), mask_radius)
                pygame.draw.circle(mask_surface, (0, 0, 0, 0), (cx_right, cy_left), mask_radius - 10)

            screen.blit(background_image, background_rect)

            mosquitoes.update()
            mosquitoes.draw(screen)

            

            screen.blit(mask_surface, (0, 0))

            screen.blit(top_image, top_rect)

            font = pygame.font.Font(None, 36)
            counter_text = font.render(f'Mosquitoes removed: {mosquito_counter} /25', True, (255, 255, 255))
            screen.blit(counter_text, (230, 10))

            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time - elapsed_paused_time
            remaining_time = max(countdown_duration - int(elapsed_time / 1000), 0)

            minutes = remaining_time // 60
            seconds = remaining_time % 60

            font = pygame.font.Font(None, 36)
            text_surface = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
            screen.blit(text_surface, (320, 50))

            if show_praising_image:
                screen.blit(praising_image, praising_rect)
                if current_time - praising_image_display_time >= 3000:
                    show_praising_image = False

            for mosquito in mosquitoes:
                mosquito.display_taunt(screen)
                

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
                            level_two_scene()

            if mosquito_counter >= 3:
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
                            pygame.mixer.music.stop()
                            start_level_three()
        

                            
        draw_pause_button(screen, pause_button_rect)

        pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    level_two_scene()
