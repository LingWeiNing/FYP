import pygame
import sys
from pygame.locals import *
from LevelSelection import lvlSelection


# Initialize Pygame
pygame.init()

# Set up the Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Main Menu")

# Button class definition
class Button:
    def __init__(self, x, y, image_path, width, height, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.image_orig = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image_orig, (width, height))
        self.action = action

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None

# Create buttons
buttons = [
    Button(300, 200, "assets\Buttons\play.png", 200, 100, "start_level_selection"),
    Button(300, 350, "assets\Buttons\quit.png", 200, 100, "quit_game")
]

# Load the image to be displayed for the level
level_image = pygame.image.load("assets\Comics\comic1_1.png")
level_image = pygame.transform.scale(level_image, (width, height))

def main_menu():
    # Load and scale story images to match the size of the Pygame window
    story_images = [
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_1.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_2.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_3.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_4.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_5.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_6.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_7.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets\Comics\comic1_8.png"), (width, height))
    ]
    
    current_page = 0
    showing_story = False
    show_buttons = True

    while True:
        screen.fill((0, 0, 0))

        if showing_story:
            screen.blit(story_images[current_page], (0, 0))
        else:
            if show_buttons:
                for button in buttons:
                    button.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if showing_story:
                    current_page += 1
                    if current_page >= len(story_images):
                        # Show level selection screen when the last page is reached
                        showing_story = False
                        show_buttons = False
                        lvlSelection()
                else:
                    for button in buttons:
                        action = button.handle_event(event)
                        if action:
                            if action == "start_level_selection":
                                showing_story = True
                                current_page = 0
                                show_buttons = False
                            elif action == "quit_game":
                                pygame.quit()
                                sys.exit()

        pygame.display.flip()

# Run the main menu
main_menu()

