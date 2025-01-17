import pygame
import pygame.mixer
import sys

pygame.mixer.init()

def darken_background(screen, width, height, alpha=128):
    darken_surface = pygame.Surface((width, height))
    darken_surface.fill((0, 0, 0))
    darken_surface.set_alpha(alpha)  # Set the transparency level
    screen.blit(darken_surface, (0, 0))

def show_game_over_screen(width, height, screen):
    darken_background(screen, width, height)
    
    pygame.mixer.music.load("assets/Music/Fade-Out.mp3")
    pygame.mixer.music.play()

    gameOver_image = pygame.image.load("assets/Bg/investigationFailed.png")
    gameOver_image = pygame.transform.scale(gameOver_image, (int(gameOver_image.get_width()), int(gameOver_image.get_height())))
    gameOver_rect = gameOver_image.get_rect()
    gameOver_rect.center = (width // 2, 250)
    screen.blit(gameOver_image, gameOver_rect)

    restart_button = pygame.Rect(width // 2 - 100, height // 2 + 150, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), restart_button)
    font_restart = pygame.font.Font(None, 36)
    text_restart = font_restart.render("Restart", True, (0, 0, 0))
    screen.blit(text_restart, (width // 2 - text_restart.get_width() // 2, height // 2 + 160))

    pygame.display.flip()

    return restart_button

def show_win_screen(width, height, screen):
    darken_background(screen, width, height)

    pygame.mixer.music.load("assets/Music/Party-Time.mp3")
    pygame.mixer.music.play()

    win_image = pygame.image.load("assets/Bg/investigationComplete.png")
    win_image = pygame.transform.scale(win_image, (int(win_image.get_width()), int(win_image.get_height())))
    win_rect = win_image.get_rect()
    win_rect.center = (width // 2, 250)
    screen.blit(win_image, win_rect)

    next_button = pygame.Rect(width // 2 - 100, height // 2 + 150, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), next_button)
    font_next = pygame.font.Font(None, 36)
    text_next = font_next.render("Next Level", True, (0, 0, 0))
    screen.blit(text_next, (width // 2 - text_next.get_width() // 2, height // 2 + 160))

    pygame.display.flip()

    return next_button

def show_pause_screen(width, height, screen):
    darken_background(screen, width, height)
    
    font_pause = pygame.font.Font(None, 100)
    text_pause = font_pause.render("Paused", True, (255, 255, 255))
    screen.blit(text_pause, (width // 2 - text_pause.get_width() // 2, height // 2 - text_pause.get_height() // 2 - 100))

    resume_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), resume_button)
    font_resume = pygame.font.Font(None, 36)
    text_resume = font_resume.render("Resume", True, (0, 0, 0))
    screen.blit(text_resume, (width // 2 - text_resume.get_width() // 2, height // 2 + 10))

    quit_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), quit_button)
    font_quit = pygame.font.Font(None, 36)
    text_quit = font_quit.render("Restart Level", True, (0, 0, 0))
    screen.blit(text_quit, (width // 2 - text_quit.get_width() // 2, height // 2 + 80))

    pygame.display.flip()

    return resume_button, quit_button

def draw_pause_button(screen, pause_button_rect):
    pygame.draw.rect(screen, (255, 255, 255), pause_button_rect)
    font_pause = pygame.font.Font(None, 36)
    text_pause = font_pause.render("Pause", True, (0, 0, 0))
    screen.blit(text_pause, (pause_button_rect.x + 5, pause_button_rect.y + 10))