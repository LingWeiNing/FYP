import pygame
import sys
from pygame.locals import *
import pygame.mixer
from LevelSelection import start_level_one

pygame.init()
pygame.mixer.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Eye See You")

def render_dialogue_text(text, font, maxwidth):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if font.size(current_line + " " + word)[0] <= maxwidth:
            current_line += " " + word if current_line != "" else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def render_dialogue(screen, background, dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y):
    if dialogue_progress >= 0 and dialogue_progress < len(dialogue_texts):
        screen.blit(dialogue_backgrounds[dialogue_progress], (0, 0)) 
        font = pygame.font.SysFont(None, 30)
        lines = render_dialogue_text(dialogue_texts[dialogue_progress][0], font, maxwidth)
        for line in lines:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
            y += font.get_linesize()

class Button:
    def __init__(self, x, y, image_paths, click_image_paths, width, height, action, frame_rate=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.images = [pygame.transform.scale(pygame.image.load(image).convert_alpha(), (width, height)) for image in image_paths]
        self.click_images = [pygame.transform.scale(pygame.image.load(image).convert_alpha(), (width, height)) for image in click_image_paths]
        self.action = action
        self.current_frame = 0
        self.frame_rate = frame_rate
        self.frame_count = 0
        self.clicked = False
        self.click_animation_done = False

    def draw(self, screen):
        if self.clicked:
            if not self.click_animation_done:
                screen.blit(self.click_images[self.current_frame], self.rect)
                self.frame_count += 1
                if self.frame_count >= self.frame_rate:
                    self.frame_count = 0
                    self.current_frame += 1
                    if self.current_frame >= len(self.click_images):
                        self.click_animation_done = True
        else:
            screen.blit(self.images[self.current_frame], self.rect)
            self.frame_count += 1
            if self.frame_count >= self.frame_rate:
                self.frame_count = 0
                self.current_frame = (self.current_frame + 1) % len(self.images)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                self.current_frame = 0
                self.frame_count = 0
                self.click_animation_done = False
                return self.action
        return None

    def is_click_animation_done(self):
        return self.click_animation_done

Startbutton_images = [
    "assets/Buttons/Start1.png",
    "assets/Buttons/Start2.png",
    "assets/Buttons/Start3.png",
    "assets/Buttons/Start4.png"
]

StartClick_images = [
    "assets/Buttons/StartClick1.png",
    "assets/Buttons/StartClick2.png",
    "assets/Buttons/StartClick3.png"
]

start_button = Button(300, 400, Startbutton_images, StartClick_images, 200, 100, "Start_anim1", frame_rate=200)

def main_menu():
    animated_BG = [
        "assets/animationMenu/1.png",
        "assets/animationMenu/2.png",
        "assets/animationMenu/3.png",
        "assets/animationMenu/4.png",
        "assets/animationMenu/5.png",
        "assets/animationMenu/6.png",
        "assets/animationMenu/7.png",
        "assets/animationMenu/8.png",
        "assets/animationMenu/9.png",
        "assets/animationMenu/10.png",
        "assets/animationMenu/11.png",
        "assets/animationMenu/12.png",
        "assets/animationMenu/13.png",
        "assets/animationMenu/14.png",
        "assets/animationMenu/15.png",
        "assets/animationMenu/16.png",
        "assets/animationMenu/17.png",
        "assets/animationMenu/18.png",
        "assets/animationMenu/19.png",
        "assets/animationMenu/20.png",
        "assets/animationMenu/21.png",
        "assets/animationMenu/22.png",
        "assets/animationMenu/23.png",
        "assets/animationMenu/24.png",
        "assets/animationMenu/25.png",
        "assets/animationMenu/26.png",
        "assets/animationMenu/27.png",
        "assets/animationMenu/28.png",
        "assets/animationMenu/29.png",
        "assets/animationMenu/30.png",
        "assets/animationMenu/31.png",
        "assets/animationMenu/32.png",
        "assets/animationMenu/33.png"
    ]

    bg_images = [pygame.transform.scale(pygame.image.load(image).convert_alpha(), (width, height)) for image in animated_BG]
    current_bg_frame = 0
    bg_frame_rate = 140
    bg_frame_count = 0

    story_images = [
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_1.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_2.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_3.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_4.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_5.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_6.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_7.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/Comics/comic1_8.png"), (width, height))
    ]

    BG_music = pygame.mixer.Sound("assets/Music/MX-Adventure.mp3")
    BG_music.play()
    
    current_page = 0
    showing_story = False
    show_buttons = True
    clicked_button_action = None

    while True:
        screen.fill((0, 0, 0))

        screen.blit(bg_images[current_bg_frame], (0, 0))
        bg_frame_count += 1
        if bg_frame_count >= bg_frame_rate:
            bg_frame_count = 0
            current_bg_frame = (current_bg_frame + 1) % len(bg_images)

        if showing_story:
            screen.blit(story_images[current_page], (0, 0))
        else:
            if show_buttons:
                start_button.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if showing_story:
                    current_page += 1
                    if current_page >= len(story_images):
                        BG_music.stop() 
                        BG_music = None
                        start_level_one()
                        return 
                else:
                    action = start_button.handle_event(event)
                    if action:
                        clicked_button_action = action

        if clicked_button_action:
            if start_button.is_click_animation_done():
                if clicked_button_action == "Start_anim1":
                    showing_story = True
                    current_page = 0
                    show_buttons = False
                clicked_button_action = None

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()