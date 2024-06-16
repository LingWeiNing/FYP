import pygame
import sys
import pygame.mixer

pygame.mixer.init()

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

def start_level_one():
    import Level_One  # Import here to avoid circular import issues
    x, y, maxwidth = 410, 480, 400
    dialogue_progress = 0

    BG_music = pygame.mixer.Sound("assets/Music/Mischievious-step.mp3")
    BG_music.play()

    dialogue_texts = [
        "We have received reports that the thief sightings are in this house.",
        "You guys had come, the thief had messed up my room quite bad…",
        "I mean it’s cool and all but I can’t see anything.",
        "(can you even see anything with that hairstyle?)",
        "This is your time to show them your ability, detective!",
        "(Alright..Let's do our best...)"
    ]

    dialogue_backgrounds = [
        pygame.image.load("assets/Dialogue/dialogueAssistantCalm1.png"),
        pygame.image.load("assets/Dialogue/dialogueEmoCalm.png"),
        pygame.image.load("assets/Dialogue/dialogueEmoShrug.png"),
        pygame.image.load("assets/Dialogue/dialogueAssistantAnnoyed1.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHappy1.png"),
        pygame.image.load("assets/Dialogue/detectiveThinking1.png")
    ]

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    while True:
        screen.fill((0, 0, 0))
        render_dialogue(screen, dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dialogue_progress < len(dialogue_texts) - 1:
                    dialogue_progress += 1
                else:
                    BG_music.stop() 
                    BG_music = None
                    Level_One.level_one_scene()  

        pygame.display.flip()

def start_level_two():
    import Level_Two  # Import here to avoid circular import issues
    x, y, maxwidth = 410, 480, 400
    dialogue_progress = 0

    BG_music = pygame.mixer.Sound("assets/Music/Mischievious-step.mp3")
    BG_music.play()

    dialogue_texts = [
        "These clues from the kid’s room seem to be leading somewhere.",
        "(Hmm.. it does seem to link to the gym, but what's with the mosquitoes?)",
        "Ah *winks* I guess you already know! To the gym!",
        "Ah thank the gyms you are here officers! There was a guy sabotaging the gym and everything had turned dark!",
        "Detective! It must be the thief! Is there any information about the guy Gym Bro?",
        "I think the thief left something but…",
        "I AM SO SCARED OF THE MOSQUITOES FLYING AROUND THE GYM!!!!!",
        "*awkward*",
        "No worries! The detective will help! *winks* right?",
        "(We'll need to help catch the mosquitoes in the gym)"
    ]

    dialogue_backgrounds = [
        pygame.image.load("assets/Dialogue/dialogueChiefCalm1.png"),
        pygame.image.load("assets/Dialogue/detectiveThinking2.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefWink1.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroCalm1.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefCalm2.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroCalm1.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroShock.png"),
        pygame.image.load("assets/Dialogue/dialogueplayerwithAssistantAwkward.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefWink2.png"),
        pygame.image.load("assets/Dialogue/detectiveThinking3.png")
    ]

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    while True:
        screen.fill((0, 0, 0))
        render_dialogue(screen, dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dialogue_progress < len(dialogue_texts) - 1:
                    dialogue_progress += 1
                else:
                    BG_music.stop() 
                    BG_music = None
                    Level_Two.level_two_scene() 

        pygame.display.flip()

def start_level_three():
    import Level_Three
    x, y, maxwidth = 410, 480, 400
    dialogue_progress = 0

    BG_music = pygame.mixer.Sound("assets/Music/Mischievious-step.mp3")
    BG_music.play()

    dialogue_texts = [
        "Thank you so much for helping out! You guys are heroes!",
        "About the thief... I think he left something before he escaped.",
        "Ah here it is, I hope this is helpful for your search...",
        "(Hmm this is some kind of a key...)",
        "Ah, I know these keys! Let your best chief help you, detective!",
        "These are the keys to the national bank vault!",
        "(the national bank...??)",
        "Here is the vault!",
        "Oh no, it seems like that darn thief had made some modifications to the lock!",
        "I would love to help you detective but… I think I’m sick…",
        "So I had decided to put my trust in you detective!",
        "(Hmm... seems like we have to use our eye ability to navigate the keys this time)"
    ]

    dialogue_backgrounds = [
        pygame.image.load("assets/Dialogue/dialoguegymBroCalm2.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroCalm2.png"),
        pygame.image.load("assets/Dialogue/dialoguegymBroCalm3.png"),
        pygame.image.load("assets/Dialogue/detectiveThinking2.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefWink1.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHappy3.png"),
        pygame.image.load("assets/Dialogue/dialogueplayerwithAssistantAwkward2.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHappy2.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefCry2.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefCry2.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefWink3.png"),
        pygame.image.load("assets/Dialogue/detectiveThinking4.png")
    ]

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    while True:
        screen.fill((0, 0, 0))
        render_dialogue(screen, dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dialogue_progress < len(dialogue_texts) - 1:
                    dialogue_progress += 1
                else:
                    BG_music.stop() 
                    BG_music = None
                    Level_Three.level_three_scene() 

        pygame.display.flip()

def start_level_four():
    import Level_Four
    x, y, maxwidth = 410, 480, 400
    dialogue_progress = 0

    BG_music = pygame.mixer.Sound("assets/Music/Mischievious-step.mp3")
    BG_music.play()

    dialogue_texts = [
        "The vault has opened! As expected by our dear detective! Good job!",
        "What is in the middle? It’s a.. Box?",
        "It's a puzzle box?",
        "Heheh I’ll have to depend on your skills this time, Detective, good luck!",
        "(Hmm we'll have to take and move the puzzle pieces to their correct positions for a reveal..)"
    ]

    dialogue_backgrounds = [
        pygame.image.load("assets/Dialogue/dialogueChiefHappy4.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHuh1.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHuh1.png"),
        pygame.image.load("assets/Dialogue/dialogueChiefHappy4.png"),
        pygame.image.load("assets/Dialogue/detectiveThinking5.png")
    ]

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    while True:
        screen.fill((0, 0, 0))
        render_dialogue(screen, dialogue_texts, dialogue_backgrounds, dialogue_progress, maxwidth, x, y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dialogue_progress < len(dialogue_texts) - 1:
                    dialogue_progress += 1
                else:
                    BG_music.stop() 
                    BG_music = None
                    Level_Four.level_four_scene()  

        pygame.display.flip()




