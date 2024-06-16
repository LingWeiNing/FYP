import pygame
import sys
import pygame.mixer
from LevelSelection import start_level_one
from EyeSeeYou import main_menu

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

def render_dialogue(screen, dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y):
    if dialogue_progress >= 0 and dialogue_progress < len(dialogue_texts):
        screen.blit(dialogue_backgrounds[dialogue_progress], (0, 0)) 
        font = pygame.font.SysFont(None, 30)
        lines = render_dialogue_text(dialogue_texts[dialogue_progress], font, maxwidth)
        for line in lines:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
            y += font.get_linesize()

def start_ending():
    pygame.init()
    pygame.mixer.init()
    
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    
    x, y, maxwidth = 410, 480, 400
    dialogue_progress = 0

    BG_music = pygame.mixer.Sound("assets/Music/Usagi-Flap-EmoCosin.mp3")
    BG_music.play()

    dialogue_texts = [
        "Detective! The Chief! He had been taken by the thief!",
        "He was trying to go to the toilet but the thief snatched him away!",
        "We must hurry, the thief must have gone to the next location as shown in the puzzle!",
        "(The thief must have taken the Chief to the museum! We must hurry!)",
    ]

    dialogue_backgrounds = [
        pygame.image.load("assets/Dialogue/dialogueAssistantPanic1.png"),
        pygame.image.load("assets/Dialogue/dialogueAssistantPanic1.png"),
        pygame.image.load("assets/Dialogue/dialogueAssistantPanic1.png"),
        pygame.image.load("assets/Dialogue/detectiveThinking6.png")
    ]

    story_images = [
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/1.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/2.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/3.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/4.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/5.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/6.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/7.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/8.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/9.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/10.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/11.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/12.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/13.png"), (width, height)),
        pygame.transform.scale(pygame.image.load("assets/ComicsEnd/14.png"), (width, height))
    ]

    current_page = 0
    showing_story = False

    while True:
        screen.fill((0, 0, 0))

        if showing_story:
            screen.blit(story_images[current_page], (0, 0))
        else:
            render_dialogue(screen, dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if showing_story:
                    current_page += 1
                    if current_page >= len(story_images):
                        BG_music.stop() 
                        BG_music = None
                        main_menu()  
                        return
                else:
                    dialogue_progress += 1
                    if dialogue_progress >= len(dialogue_texts):
                        showing_story = True
                        current_page = 0 

        pygame.display.flip()

if __name__ == "__main__":
    start_ending()