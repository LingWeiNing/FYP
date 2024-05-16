import pygame
from pygame.locals import *
import sys
from Level_One import level_one_scene
from Level_Two import level_two_scene
from Level_Three import level_three_scene

# Initialize Pygame
pygame.init()

# Set up the Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Level Selection")

# Button class definition
class Button:
    def __init__(self, x, y, image_path, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.image_orig = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image_orig, (width, height))
        self.text = text
        self.action = action

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None

# Create buttons
buttons = [
    Button(50, 25, "assets\Bg\Background.png", 300, 250, "Level 1", "start_level_one"),  # Call the face detection scene when this button is pressed
    Button(450, 23, "assets\Bg\gym.jpg", 300, 250, "Level 2", "start_level_two"),  # Add more buttons for other levels
    Button(50, 320, "assets\Bg\maze.png", 300, 250, "Level 3", "start_level_three"),
    Button(450, 320, "assets\Bg\museum.jpg", 300, 250, "Level 4", "start_level_four")
]

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
        screen.blit(dialogue_backgrounds[dialogue_progress], (0, 0))  # Draw background image for dialogue
        font = pygame.font.SysFont(None, 30)
        lines = render_dialogue_text(dialogue_texts[dialogue_progress][0], font, maxwidth)
        for line in lines:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
            y += font.get_linesize()

def lvlSelection():
    x = 410
    y = 480
    maxwidth = 400
    selected_level = None
    dialogue_progress = -1  # Variable to track the progress of the dialogue
    dialogue_texts = [
        ["We have received reports that the thief sightings are in this room."],
        ["You guys had come, the thief had messed up my room quite bad…"],
        ["I mean it’s cool and all but I can’t see anything."],
        ["(can you even see anything with that hairstyle?)"],
        ["This is your time to show them your ability, detective!"]
    ]

    dialogue_texts_two = [
        ["These clues from the kid’s room seem to be leading somewhere."],
        ["Ah *winks* I guess you already know! To the gym!"],
        ["Ah thank the gyms you are here officers! There was a guy sabotaging the gym and everything had turned dark!"],
        ["Detective! It must be the thief! Is there any information about the guy Gym Bro?"],
        ["I think the thief left something but…"],
        ["I AM SO SCARED OF THE MOSQUITOES FLYING AROUND THE GYM!!!!!"],
        ["*awkward*"],
        ["No worries! The detective will help! *winks* right?"]
    ]

    dialogue_texts_three = [
        ["Here is the vault!"],
        ["Oh no, it seems like that darn thief had made some modifications to the lock!"],
        ["I would love to help you detective but… I think I’m sick…"],
        ["So I had decided to put my trust in you detective!"]
    ]

    dialogue_texts_four = [
        ["As expected, my intuition is right!"],
        ["What is in the middle? It’s a.. Box?"],
        ["A puzzle box?"],
        ["Heheh I’ll have to depend on your skills this time, Detective, good luck!"]
    ]


    button_clicked = False

    # Load background images for each dialogue
    dialogue_backgrounds = [
        pygame.image.load("assets/Dialogue/dialogueAssistantCalm.png"),
        pygame.image.load("assets/Dialogue/dialogueEmoCalm.png"),
        pygame.image.load("assets/Dialogue/dialogueEmoShrug.png"),
        pygame.image.load("assets/Dialogue/dialogueAssistantAnnoyed.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHappy.png")
    ]

    dialogue_backgrounds_two = [
        pygame.image.load("assets/Dialogue/dialogueChiefCalm.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefWink.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroCalm.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefCalm.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroCalm.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroShock.png"),
        pygame.image.load("assets/Dialogue/dialogueplayerwithAssistantAwkward.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefWink.png"),
    ]

    dialogue_backgrounds_three = [
        pygame.image.load("assets/Dialogue/dialogueChiefHappy.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefCry.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefCry.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefWink.png")
    ]

    dialogue_backgrounds_four = [
        pygame.image.load("assets/Dialogue/dialogueChiefHappy.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefCalm.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHuh.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHappy.png")
    ]
    

    while True:
        screen.fill((0, 0, 0))

        if not button_clicked:  # Only draw buttons if no button has been clicked
            for button in buttons:
                button.draw(screen)

        if selected_level == "start_level_one":
            render_dialogue(screen, dialogue_backgrounds[dialogue_progress], dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y)

        elif selected_level == "start_level_two":
            render_dialogue(screen, dialogue_backgrounds_two[dialogue_progress], dialogue_texts_two, dialogue_backgrounds_two, dialogue_progress, maxwidth, x, y)

        elif selected_level == "start_level_three":
            render_dialogue(screen, dialogue_backgrounds_three[dialogue_progress], dialogue_texts_three, dialogue_backgrounds_three, dialogue_progress, maxwidth, x, y)
        
        elif selected_level == "start_level_four":
            render_dialogue(screen, dialogue_backgrounds_four[dialogue_progress], dialogue_texts_four, dialogue_backgrounds_four, dialogue_progress, maxwidth, x, y)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not button_clicked:  # Only handle button clicks if no button has been clicked
                    for button in buttons:
                        action = button.handle_event(event)
                        if action:
                            button_clicked = True  # Set the flag to True when a button is clicked
                            selected_level = action  # Update selected_level regardless of its current value

                if selected_level == "start_level_one":
                    # Progress dialogue when the mouse is clicked
                    if dialogue_progress < len(dialogue_texts) - 1:
                        dialogue_progress += 1
                    else:
                        level_one_scene()  # Call the function to start the face detection scene

                if selected_level == "start_level_two":
                    # Progress dialogue when the mouse is clicked
                    if dialogue_progress < len(dialogue_texts_two) - 1:
                        dialogue_progress += 1
                    else:
                        level_two_scene()

                if selected_level == "start_level_three":
                    # Progress dialogue when the mouse is clicked
                    if dialogue_progress < len(dialogue_texts_three) - 1:
                        dialogue_progress += 1
                    else:
                        level_three_scene()

                if selected_level == "start_level_four":
                    # Progress dialogue when the mouse is clicked
                    if dialogue_progress < len(dialogue_texts_four) - 1:
                        dialogue_progress += 1
                    else:
                        lvlSelection()

        pygame.display.flip()

# Run the main menu
lvlSelection()
