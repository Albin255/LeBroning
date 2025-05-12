import pygame
import math
import random

# Initialisation
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(r"sounds\despicable-me.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)
strike_sound = pygame.mixer.Sound(r"sounds\wii-sports-strike.mp3")
strike_sound.set_volume(0.8)
spare_sound = pygame.mixer.Sound(r"sounds\wii-sports-spare.mp3")
spare_sound.set_volume(0.8)
launch_sound = pygame.mixer.Sound(r"sounds\hee-hee.mp3")
launch_sound.set_volume(0.8)
thwomp_sound = pygame.mixer.Sound(r"sounds\thwomp.mp3")
thwomp_sound.set_volume(3.2)

loose_sound = [
    pygame.mixer.Sound(r"sounds\fail-trumpet.mp3"),
    pygame.mixer.Sound(r"sounds\losing-horn.mp3")
]
for _ in range(len(loose_sound)):
    loose_sound[_].set_volume(0.5)

# Paramètres écran
fond = [
    r"images\fond jeu 1.jpg",
    r"images\fond jeu 2.jpg",
    r"images\fond jeu 3.png"
]

screen_width, screen_height = 1600, 900
screen = pygame.display.set_mode((screen_width, screen_height))
fond_index = random.randint(0, 2)  # Choix aléatoire avec index
background_image = pygame.transform.scale(
    pygame.image.load(fond[fond_index]).convert(),
    (screen_width, screen_height)
)
menu_image = pygame.image.load(r"images\fond_menu.jpg").convert()
pygame.display.set_caption("Mini Angry Birds")

if fond_index == 0:
    end_font_path = "fonts/EasterBunnyPersonalUse.ttf"
elif fond_index == 1:
    end_font_path = "fonts/TrickOrDead.ttf"
elif fond_index == 2:
    end_font_path = "fonts/RetroChrista.otf"
else:
    end_font_path = None



# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255,128,0)
PURPLE = (255, 0, 255)

# Balles (images, gravité, rebond)
ball_radius = 30
ball_options = [
    {"image_path": r"images\herisson.png", "gravity": 0.2, "bounce": 0.5},
    {"image_path": r"images\tomate.png", "gravity": 0.3, "bounce": 0.6},
    {"image_path": r"images\watermelon.png", "gravity": 0.15, "bounce": 0.4},
    {"image_path": r"images\football.png", "gravity": 0.25, "bounce": 0.7},
]

target_options = [
    r"images\target.png",
    r"images\lebron-james.png"
]

# Chargement images
for option in ball_options:
    surface = pygame.image.load(option["image_path"]).convert_alpha()
    option["surface"] = pygame.transform.scale(surface, (ball_radius * 2, ball_radius * 2))
    option["menu_surface"] = pygame.transform.scale(surface, (80, 80))

# Charger et redimensionner toutes les images
target_images = []
target_size = (40,40)
for target in target_options:
    img = pygame.image.load(target).convert_alpha()
    img = pygame.transform.scale(img, target_size)
    target_images.append(img)

selected_ball = 0
ball_image = ball_options[selected_ball]["surface"]
gravity = ball_options[selected_ball]["gravity"]
bounce_factor = ball_options[selected_ball]["bounce"]

# Position et vitesse balle
ball_x = screen_width // 16
ball_y = screen_height // 2
ball_speed_x = 0
ball_speed_y = 0
max_speed = 15

# Contrôles
menu_active = True
game_started = False
adjusting_speed = True
difficulty_menu_active = True
difficulty = "moyen"  # par défaut
help_menu_active = False

thwomp_image = pygame.image.load(r"images\thwomp détouré.webp").convert_alpha()
thwomp_image = pygame.transform.scale(thwomp_image, (70, 70))
thwomp_rect = pygame.Rect(700, 100, 70, 70)

thwomp_direction = 1  # 1 = descend, -1 = remonte
thwomp_speed = random.randint(2,4)
thwomp_range_top = 100
thwomp_range_bottom = 500

# Cibles
secure_random = random.SystemRandom()

def generate_targets():
    targets = []
    target_width, target_height = 40, 40

    if difficulty == "facile":
        count = secure_random.randint(2, 3)
    elif difficulty == "moyen":
        count = secure_random.randint(4, 5)
    elif difficulty == "difficile":
        count = secure_random.randint(6, 7)
    elif difficulty == "impossible":
        count = secure_random.randint(8, 10)
    else:
        count = 4

    attempts = 0
    max_attempts = 1000  # pour éviter une boucle infinie

    while len(targets) < count and attempts < max_attempts:
        x = secure_random.randint(screen_width - 400, screen_width - target_width - 20)
        y = secure_random.randint(screen_height - 500, screen_height - target_height - 150)
        new_rect = pygame.Rect(x, y, target_width, target_height)

        # Vérifie si ça chevauche une cible existante
        overlap = any(new_rect.colliderect(t["rect"]) for t in targets)

        if not overlap:
            image = random.choice(target_images)
            targets.append({"rect": new_rect, "image": image})
        attempts += 1

    return targets


# Score
remaining_shots = 2
score = 0

# Horloge
clock = pygame.time.Clock()

def draw_text(text, x, y, size=36, color=BLACK, font_path=None):
    if font_path:
        font = pygame.font.Font(font_path, size)
    else:
        font = pygame.font.Font(None, size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_menu():
    screen.blit(menu_image, (0, 0))
    draw_text("Choisissez votre balle avec les flèches GAUCHE et DROITE", 400, 200, 40)
    draw_text("Appuyez sur ENTRÉE pour commencer", 550, 260, 40)
    draw_text("Appuyez sur ESC pour revenir au menu", 550, 550, 40)

    for i, option in enumerate(ball_options):
        x = 400 + i * 250
        y = 400
        screen.blit(option["menu_surface"], (x - 40, y - 40))
        if i == selected_ball:
            pygame.draw.circle(screen, WHITE, (x, y), 50, 3)
        draw_text(f"Gravité: {option['gravity']}", x - 50, y + 50, 30)
        draw_text(f"Rebond: {option['bounce']}", x - 50, y + 80, 30)

def draw_difficulty_menu():
    screen.blit(menu_image, (0, 0))
    draw_text("Choisissez la difficulté :", 600, 250, 50)
    draw_text("Appuyez sur 1 pour FACILE", 600, 350, 40, GREEN)
    draw_text("Appuyez sur 2 pour MOYEN", 600, 410, 40, ORANGE)
    draw_text("Appuyez sur 3 pour DIFFICILE", 600, 470, 40, RED)
    draw_text("Appuyez sur 4 pour IMPOSSIBLE", 600, 530, 40, PURPLE )
    draw_text("Appuyez sur H pour connaître les commandes", 600, 600, 40, YELLOW)

def draw_help_menu():
    screen.blit(menu_image, (0, 0))
    draw_text("COMMENT JOUER", 600, 150, 60, YELLOW)
    draw_text("- Choisissez une balle avec la flèche gauche ou la flèche droite", 400, 250, 36)
    draw_text("- Appuyez sur ENTRÉE pour commencer", 400, 300, 36)
    draw_text("- Déplacez la flèche avec les flèches directionnelles", 400, 350, 36)
    draw_text("- Appuyez sur ESPACE pour tirer", 400, 400, 36)
    draw_text("- Détruisez toutes les cibles en 2 tirs maximum", 400, 450, 36)
    draw_text("- Plus vous restez appuyé plus la balle sera puissante", 400, 500, 36)
    draw_text("- Appuyez sur ESC pour revenir au menu", 400, 550, 36)


def reset_game():
    global menu_active, game_started, adjusting_speed
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    global ball_image, gravity, bounce_factor, selected_ball
    global targets, score, remaining_shots
    global difficulty_menu_active, background_image
    global fond_index, end_font_path  # AJOUT IMPORTANT

    menu_active = True
    game_started = False
    adjusting_speed = True
    difficulty_menu_active = True

    fond_index = random.randint(0, 2)  # NOUVEL index aléatoire
    background_image = pygame.transform.scale(
        pygame.image.load(fond[fond_index]).convert(),
        (screen_width, screen_height)
    )

    # Mettre à jour la police aussi !
    if fond_index == 0:
        end_font_path = "fonts/EasterBunnyPersonalUse.ttf"
    elif fond_index == 1:
        end_font_path = "fonts/TrickOrDead.ttf"
    elif fond_index == 2:
        end_font_path = "fonts/RetroChrista.otf"
    else:
        end_font_path = None

    ball_x = screen_width // 16
    ball_y = screen_height // 2
    ball_speed_x = 0
    ball_speed_y = 0

    selected_ball = 0
    ball_image = ball_options[selected_ball]["surface"]
    gravity = ball_options[selected_ball]["gravity"]
    bounce_factor = ball_options[selected_ball]["bounce"]

    targets = generate_targets()
    score = 0
    remaining_shots = 2

def draw_arrow(surface, start, end, color, width=5):
    pygame.draw.line(surface, color, start, end, width)
    angle = math.atan2(start[1] - end[1], end[0] - start[0])
    size = 15
    left = (end[0] - size * math.cos(angle + math.pi / 6), end[1] + size * math.sin(angle + math.pi / 6))
    right = (end[0] - size * math.cos(angle - math.pi / 6), end[1] + size * math.sin(angle - math.pi / 6))
    pygame.draw.line(surface, color, end, left, width)
    pygame.draw.line(surface, color, end, right, width)

    # Barre de puissance basée sur la vitesse
    bar_x, bar_y = 50, screen_height - 50
    bar_width, bar_height = 300, 20
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

    # Calcul du niveau de puissance
    speed_magnitude = math.hypot(ball_speed_x, ball_speed_y)
    fill_width = int((speed_magnitude / max_speed) * bar_width)
    fill_width = min(fill_width, bar_width)  # Ne dépasse jamais le rectangle
    pygame.draw.rect(screen, RED, (bar_x, bar_y, fill_width, bar_height))

    # Étiquette
    draw_text("Puissance", bar_x, bar_y - 30, 24, BLACK)


# Boucle principale
running = True
while running:
    screen.blit(background_image, (0, 0))
    keys = pygame.key.get_pressed()

    if help_menu_active:
        draw_help_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                help_menu_active = False
                difficulty_menu_active = True

    elif difficulty_menu_active:
        draw_difficulty_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = "facile"
                    difficulty_menu_active = False
                    menu_active = True
                elif event.key == pygame.K_2:
                    difficulty = "moyen"
                    difficulty_menu_active = False
                    menu_active = True
                elif event.key == pygame.K_3:
                    difficulty = "difficile"
                    difficulty_menu_active = False
                    menu_active = True
                elif event.key == pygame.K_4:
                    difficulty = "impossible"
                    difficulty_menu_active = False
                    menu_active = True
                elif event.key == pygame.K_h:
                    difficulty_menu_active = False
                    help_menu_active = True

    elif menu_active:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_LEFT:
                    selected_ball = (selected_ball - 1) % len(ball_options)
                elif event.key == pygame.K_RIGHT:
                    selected_ball = (selected_ball + 1) % len(ball_options)
                elif event.key == pygame.K_RETURN:
                    option = ball_options[selected_ball]
                    ball_image = option["surface"]
                    gravity = option["gravity"]
                    bounce_factor = option["bounce"]
                    targets = generate_targets()
                    menu_active = False
                elif event.key == pygame.K_ESCAPE:
                    menu_active = False
                    difficulty_menu_active = True

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if adjusting_speed:
            if keys[pygame.K_LEFT] and ball_speed_x > -max_speed : ball_speed_x -= 0.2
            if keys[pygame.K_RIGHT] and ball_speed_x < max_speed: ball_speed_x += 0.2
            if keys[pygame.K_UP] and ball_speed_y > -max_speed: ball_speed_y -= 0.2
            if keys[pygame.K_DOWN] and ball_speed_y < max_speed: ball_speed_y += 0.2

        if keys[pygame.K_SPACE] and adjusting_speed:

            game_started = True
            adjusting_speed = False
            launch_sound.play()

        if game_started:
            ball_speed_y += gravity
            ball_x += ball_speed_x
            ball_y += ball_speed_y

            # Rebonds
            if ball_x - ball_radius < 0:
                ball_x = ball_radius
                ball_speed_x *= -bounce_factor
            if ball_x + ball_radius > screen_width:
                ball_x = screen_width - ball_radius
                ball_speed_x *= -bounce_factor
            if ball_y + ball_radius >= screen_height - 138:
                ball_y = screen_height - ball_radius - 138
                ball_speed_y *= -bounce_factor
                ball_speed_x *= 0.98
                if abs(ball_speed_y) < 1:
                    ball_speed_y = 0
            if ball_y - ball_radius < 0:
                ball_y = ball_radius
                ball_speed_y *= -bounce_factor

        # Dessin balle (image)
        screen.blit(ball_image, (int(ball_x - ball_radius), int(ball_y - ball_radius)))

        # Flèche directionnelle
        if adjusting_speed:
            magnitude = math.hypot(ball_speed_x, ball_speed_y)
            if magnitude > 0:
                length = min(magnitude * 10, 150)
                end_x = ball_x + (ball_speed_x / magnitude) * length
                end_y = ball_y + (ball_speed_y / magnitude) * length
                draw_arrow(screen, (ball_x, ball_y), (end_x, end_y), WHITE, 5)

        # Collisions et score
        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
        hit = [t for t in targets if ball_rect.colliderect(t["rect"])]

        for t in hit:
            targets.remove(t)
            score += 100

        # Mouvement Thwomp en mode impossible (en dehors de la boucle)
        if difficulty == "impossible":
            thwomp_rect.y += thwomp_direction * thwomp_speed
            if thwomp_rect.y >= thwomp_range_bottom:
                thwomp_direction = -1
                thwomp_speed = random.randint(2,4)
            elif thwomp_rect.y <= thwomp_range_top:
                thwomp_direction = 1
                thwomp_speed = random.randint(2, 4)
            screen.blit(thwomp_image, (thwomp_rect.x, thwomp_rect.y))


        for target in targets:
            screen.blit(target["image"], (target["rect"].x, target["rect"].y))

        draw_text(f"Score : {score}", 30, 30, 36)
        draw_text(f"Tirs restants : {remaining_shots}", 30, 70, 36)

        # Fin de tir
        if game_started and not adjusting_speed:
            thwomp_collision = (
                    difficulty == "impossible"
                    and thwomp_range_top <= thwomp_rect.y <= thwomp_range_bottom
                    and ball_rect.colliderect(thwomp_rect)
            )

            if (abs(ball_speed_x) < 0.5 and ball_speed_y == 0) or ball_y > screen_height or thwomp_collision:
                if ball_rect.colliderect(thwomp_rect) and remaining_shots > 1:
                    thwomp_sound.play()
                remaining_shots -= 1
                if remaining_shots > 0:
                    adjusting_speed = True
                    game_started = False
                    ball_x = screen_width // 16
                    ball_y = screen_height // 2
                    ball_speed_x = 0
                    ball_speed_y = 0
                else:
                    draw_text("Fin du jeu ! Perdu!", 480, 350, 75, RED, end_font_path)
                    if difficulty == "impossible":
                        draw_text("DOMMAGE ! Mais bien essayé !", 400, 220, 60, (255, 0, 255), end_font_path)
                    random.choice(loose_sound).play()
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    reset_game()

        # Victoire
        if not targets:
            if remaining_shots == 2:
                draw_text("STRIKE", 670, 300, 100, YELLOW, end_font_path)
                if difficulty == "impossible":
                    draw_text("INCROYABLE ! Mode Impossible Réussi !", 400, 220, 60, PURPLE, end_font_path)
                strike_sound.play()
                score *= 5
            elif remaining_shots == 1:
                draw_text("SPARE", 670, 300, 100, YELLOW, end_font_path)
                if difficulty == "impossible":
                    draw_text("INCROYABLE ! Mode Impossible Réussi !", 400, 220, 60, (255, 0, 255), end_font_path)
                spare_sound.play()
                score *= 2
            draw_text(f"Score : {score}", 600, 400, 100, YELLOW, end_font_path)
            pygame.display.flip()
            pygame.time.wait(3000)
            reset_game()


    pygame.display.flip()
    clock.tick(60)

pygame.quit()