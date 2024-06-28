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
from eye_detection import detect_eyes

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

        self.taunt_images = [pygame.image.load(image) for image in taunt_images]
        self.show_taunt = False
        self.taunt_image = None
        self.taunt_start_time = 0
        self.taunt_duration = 3000
        self.next_taunt_time = pygame.time.get_ticks() + random.randint(1000, 3000)  # Shorter interval

        self.cooldown_duration = 3000  # Shorter cooldown
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
            self.next_taunt_time = current_time + random.randint(1000, 3000)  # Shorter interval
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
    
    def restart_taunt(self):
        if not self.show_taunt:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_taunt_time >= self.cooldown_duration and Mosquito.taunting_mosquito is None:
                self.show_taunt = True
                self.taunt_image = random.choice(self.taunt_images)
                self.taunt_start_time = current_time
                Mosquito.taunting_mosquito = self
                print(f"Taunt restarted. Taunt duration: {self.taunt_duration}")

def spawn_mosquitoes(num_mosquitoes, images, taunt_images, scale_factor):
    mosquitoes = pygame.sprite.Group()
    for _ in range(num_mosquitoes):
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        speed = random.uniform(3, 7)
        mosquito = Mosquito(images, taunt_images, x, y, speed, scale_factor)
        mosquitoes.add(mosquito)
    return mosquitoes
    
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

    mosquitoes = spawn_mosquitoes(7, mosquito_images, mosquitoTaunt_images, (100, 100))

    mosquito_counter = 0

    praising_image = pygame.image.load("assets/goodjob/GoodJobChief.png")
    praising_rect = praising_image.get_rect(center=(600, 500))

    show_praising_image = False
    praising_image_display_time = 0

    threshold = 30

    mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    start_time = pygame.time.get_ticks()
    countdown_duration = 120

    pause_button_rect = pygame.Rect(width - 100, 10, 80, 40)
    paused = False
    pause_start_time = 0

    elapsed_paused_time = 0 

    slider_pos = (10, 40)
    slider_size = (200, 20)
    slider_min_val = 0
    slider_max_val = 255

    BG_music.play()
    BG_music.play(-1)

    cx_left, cy_left, cx_right, cy_right = None, None, None, None

    # Main game loop
    while True:
        mouse_pos = None
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

            mosquitoes.update()
            mosquitoes.draw(screen)

        
            screen.blit(mask_surface, (0, 0))

            screen.blit(top_image, top_rect)

            font = pygame.font.Font(None, 36)
            counter_text = font.render(f'Mosquitoes removed: {mosquito_counter} /20', True, (255, 255, 255))
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

            if mosquito_counter >= 20:
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
            
            if cx_left is None or cy_left is None or cx_right is None or cy_right is None:
                if elapsed_time < 5000:
                    warning_text = font.render("Eyes not detected. Please adjust your camera or eye position.", True, (255, 0, 0))
                    screen.blit(warning_text, (width // 2 - warning_text.get_width() // 2, height // 2))
            

        slider_rect, handle_rect = draw_slider(screen, slider_pos, slider_size, threshold, slider_min_val, slider_max_val)
        
        threshold_text = font.render("Threshold Slider", True, (255, 255, 255))
        screen.blit(threshold_text, (10, 10))
                            
        draw_pause_button(screen, pause_button_rect)

        pygame.display.flip()

        clock.tick(30)

if __name__ == "__main__":
    level_two_scene()
