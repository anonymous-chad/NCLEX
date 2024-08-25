# I had a fun time coding this side project. My goal with this project was to make a fun-interactive way to study for the NCLEX.
# Please try it out and if you have coding experience... feel free to contribute. 
# If you cannot compile this by yourself... there will be a .exe (executable) version. 
# .exe file can be found here: https://nclex-coder.itch.io/nclex-content-game
# Credits = @anonymous-chad on GitHub!
# And, I will be adding more questions as time progresses. Feel free to add questions for yourself too. 
# Official Steam version in development (with different assets and advanced gameplay)
import pygame
import random
import json
import sys
import os
import subprocess
import webbrowser

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
MENU_FONT_SIZE = 18
PANEL_FONT_SIZE = 15
FPS = 60
FONT_PATH = os.path.join(os.path.dirname(__file__), 'assets/fonts/custom_font.ttf')
MENU_FONT = pygame.font.Font(FONT_PATH, MENU_FONT_SIZE)
PANEL_FONT = pygame.font.Font(FONT_PATH, PANEL_FONT_SIZE)

icon_path = os.path.join(os.path.dirname(__file__), 'assets/icon.png')
pygame.display.set_icon(pygame.image.load(icon_path))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NCLEX-RN Content Adventure")

clock = pygame.time.Clock()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

FONT_PATH = resource_path('assets/fonts/custom_font.ttf')
icon_path = resource_path('assets/icon.png')
background_img = pygame.image.load(resource_path('assets/img/Background/background.png')).convert_alpha()
panel_img = pygame.image.load(resource_path('assets/img/Icons/panel.png')).convert_alpha()
book_img = pygame.image.load(resource_path('assets/img/Book/book.png')).convert_alpha()

shopkeeper_images = []
for i in range(5):
    img_path = resource_path(f'assets/img/Shopkeeper/{i}.png')
    img = pygame.image.load(img_path).convert_alpha()
    shopkeeper_images.append(img)

default_progress = {
    'player_health': 100,
    'boss_health': 200,
    'player_score': 0,
    'inventory': {
        'potions': 0
    },
    'player_currency': 0,
    'levels_completed': {
        "Cardiovascular": False,
        "EKG": False,
        "Gastrointestinal": False,
        "Mental Health": False,
        "Respiratory: Pediatrics": False,
        "Adult Respiratory": False,
        "Neurology: Pediatrics": False,
        "Adult Neurology": False,
        "Endocrine": False,
        "Maternity": False,
    },
    'questions_correct': {
        "Cardiovascular": [],
        "EKG": [],
        "Gastrointestinal": [],
        "Mental Health": [],
        "Respiratory: Pediatrics": [],
        "Adult Respiratory": [],
        "Neurology: Pediatrics": [],
        "Adult Neurology": [],
        "Endocrine": [],
        "Maternity": []
    }
}

if not os.path.exists('progress.json'):
    with open('progress.json', 'w') as f:
        json.dump(default_progress, f)

def load_progress():
    global player_health, boss_health, player_score, inventory, player_currency, levels_completed, questions_correct
    try:
        with open('progress.json', 'r') as f:
            progress = json.load(f)
            player_health = progress.get('player_health', 100)
            boss_health = progress.get('boss_health', 200)
            player_score = progress.get('player_score', 0)
            inventory = progress.get('inventory', {'potions': 0})
            player_currency = progress.get('player_currency', 0)
            levels_completed = progress.get('levels_completed', default_progress['levels_completed'])
            questions_correct = progress.get('questions_correct', default_progress['questions_correct'])
    except FileNotFoundError:
        pass

def save_progress():
    progress = {
        'player_health': player_health,
        'boss_health': boss_health,
        'player_score': player_score,
        'inventory': inventory,
        'player_currency': player_currency,
        'levels_completed': levels_completed,
        'questions_correct': questions_correct,
    }
    with open('progress.json', 'w') as f:
        json.dump(progress, f)

def load_question_bank(selected_level):
    base_path = os.path.dirname(__file__)
    level_to_filename = {
        "Cardiovascular": "assets/data/cardiovascular_questions.json",
        "EKG": "assets/data/ekg_questions.json",
        "Gastrointestinal": "assets/data/gastrointestinal_questions.json",
        "Mental Health": "assets/data/mental_health_questions.json",
        "Respiratory: Pediatrics": "assets/data/pediatrics_respiratory_questions.json",
        "Adult Respiratory": "assets/data/adult_respiratory_questions.json",
        "Neurology: Pediatrics": "assets/data/pediatrics_neurology_questions.json",
        "Adult Neurology": "assets/data/adult_neurology_questions.json",
        "Endocrine": "assets/data/endocrine_questions.json",
        "Maternity": "assets/data/maternity_questions.json"
    }

    file_name = level_to_filename.get(selected_level, "")
    file_path = os.path.join(base_path, file_name)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            all_questions = json.load(file)
            if not all('id' in q for q in all_questions):
                for i, q in enumerate(all_questions):
                    q['id'] = i
            remaining_questions = [q for q in all_questions if q['id'] not in questions_correct[selected_level]]
            return remaining_questions
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def wrap_text(text, font, max_width):
    words = text.split(' ')
    wrapped_lines = []
    line = ""

    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            wrapped_lines.append(line)
            line = word + " "

    wrapped_lines.append(line)
    return wrapped_lines

def is_level_completed(level):
    question_bank = load_question_bank(level)
    return len(question_bank) == 0

class Fighter():
    def __init__(self, x, y, name, max_hp, strength):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  
        self.update_time = pygame.time.get_ticks()
        
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'assets/img/{self.name}/Idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'assets/img/{self.name}/Attack/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'assets/img/{self.name}/Hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'assets/img/{self.name}/Death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 85
        self.image = self.animation_list[self.action][self.frame_index]
        
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        damage = self.strength + random.randint(-5, 5)
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

def draw_bg():
    screen.blit(background_img, (0, 0))

def draw_panel():
    screen.blit(panel_img, (0, SCREEN_HEIGHT - 200))
    draw_text("Press 'H' to use an available potion", PANEL_FONT, WHITE, 70, SCREEN_HEIGHT - 230)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_potion_count(potions, x, y):
    text = f"Potions: {potions}"
    draw_text(text, PANEL_FONT, WHITE, x, y)

def show_feedback(is_correct, correct_answer=None):
    feedback_color = GREEN if is_correct else RED
    feedback_text = "Correct!" if is_correct else f"Incorrect! Correct answer: {correct_answer}"
    draw_text(feedback_text, PANEL_FONT, feedback_color, 500, SCREEN_HEIGHT - 232)
    pygame.display.flip()

def show_end_of_level_message():
    global selected_level
    levels_completed[selected_level] = True
    save_progress()
    screen.fill(BLACK)
    draw_text("All questions completed. Press 'M' for Main Menu", MENU_FONT, RED, 200, 150)
    pygame.display.flip()
    wait_for_main_menu()

def display_main_menu():
    load_progress()  
    total_questions = sum(len(load_question_bank(level)) for level in default_progress['levels_completed'].keys())
    total_answered = sum(len(questions_correct[level]) for level in questions_correct.keys())

    screen.fill(BLACK)
    book_rect = book_img.get_rect(center=(SCREEN_WIDTH // 2, book_img.get_height() // 2 + 50))
    screen.blit(book_img, book_rect.topleft)

    welcome_lines = [
        "Welcome to the NCLEX-RN Content Adventure!",
        "Choose a level:",
        "Press 'C' for Cardiovascular",
        "Press 'E' for EKG",
        "Press 'G' for Gastrointestinal",
        "Press 'M' for Mental Health",
        "Press 'P' for Respiratory: Pediatrics",
        "Press 'Y' for Adult Respiratory",
        "Press 'N' for Neurology: Pediatrics",
        "Press 'A' for Adult Neurology",
        "Press 'D' for Endocrine",
        "Press 'T' for Maternity",
        "Press 'Q' to Quit",
        "Press 'I' for Item Shop",
        "Press 'R' to Reset Progress",
        f"Your Currency: {player_currency}",
        f"Total Questions: {total_questions}",
        f"Questions Answered: {total_answered}",
        "Press 'V' to Study the Book of Contents"
    ]

    line_height = MENU_FONT.size(welcome_lines[0])[1]
    y_position = book_rect.bottom + 20  

    for line in welcome_lines:
        draw_text(line, MENU_FONT, WHITE, (SCREEN_WIDTH - MENU_FONT.size(line)[0]) // 2, y_position)
        y_position += line_height + 5

    pygame.display.flip()

def terminate_pygame():
    pygame.display.quit()
    pygame.quit()

def restart_pygame():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NCLEX-RN Content Adventure")

def main_menu():
    global selected_level, question_bank, player_health, boss_health, knight, bandit, question, answers, correct_answer, current_question_index, player_currency

    selected_level = None  

    in_main_menu = True
    while in_main_menu:
        display_main_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                terminate_pygame()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    selected_level = "Cardiovascular"
                elif event.key == pygame.K_e:
                    selected_level = "EKG"
                elif event.key == pygame.K_g:
                    selected_level = "Gastrointestinal"
                elif event.key == pygame.K_m:
                    selected_level = "Mental Health"
                elif event.key == pygame.K_p:
                    selected_level = "Respiratory: Pediatrics"
                elif event.key == pygame.K_y:
                    selected_level = "Adult Respiratory"
                elif event.key == pygame.K_n:
                    selected_level = "Neurology: Pediatrics"
                elif event.key == pygame.K_a:
                    selected_level = "Adult Neurology"
                elif event.key == pygame.K_d:
                    selected_level = "Endocrine"
                elif event.key == pygame.K_t:
                    selected_level = "Maternity"
                elif event.key == pygame.K_q:
                    save_progress()
                    terminate_pygame()
                    sys.exit()
                elif event.key == pygame.K_v:
                    show_pdf_viewer()
                elif event.key == pygame.K_i:
                    show_item_shop()
                elif event.key == pygame.K_r:
                    reset_progress()
                    main_menu()  

                if selected_level:
                    if levels_completed[selected_level]:
                        draw_text("All questions completed for this level.", MENU_FONT, RED, 200, 150)
                        pygame.display.flip()
                        pygame.time.delay(2000)
                        selected_level = None
                    else:
                        question_bank = load_question_bank(selected_level)
                        current_question_index = 0
                        load_next_question()  
                        player_health = 100
                        boss_health = 200
                        knight = Fighter(320, 232, 'Knight', 100, 10)
                        bandit = Fighter(500, 240, 'Bandit', 100, 6)
                        knight_health_bar = HealthBar(100, 20, knight.hp, knight.max_hp)
                        bandit_health_bar = HealthBar(550, 20, bandit.hp, bandit.max_hp)
                        in_main_menu = False
                        run_game()

def wait_for_main_menu():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                terminate_pygame()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    waiting = False
                    main_menu()

def reset_progress():
    if os.path.exists('progress.json'):
        os.remove('progress.json')
    with open('progress.json', 'w') as f:
        json.dump(default_progress, f)

def load_next_question():
    global question, answers, correct_answer, current_question_index, question_bank, in_battle
    if current_question_index < len(question_bank):
        question_data = question_bank[current_question_index]
        question = question_data['question']
        answers = question_data['options']
        correct_answer = question_data['correct_answer']
    else:
        in_battle = False
        if len(question_bank) == 0:
            show_end_of_level_message()
        else:
            draw_text("Some questions were answered incorrectly. Please try again.", MENU_FONT, RED, 200, 150)
            pygame.display.flip()
            pygame.time.delay(2000)
            main_menu()

def show_victory_screen():
    global in_battle
    draw_text("Victory! Press 'M' for Main Menu", MENU_FONT, GREEN, 200, 150)
    pygame.display.flip()

    victory = False
    while not victory:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                terminate_pygame()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    victory = True
                    in_battle = False  
                    main_menu()  

def run_game():
    global player_health, boss_health, knight, bandit, question, answers, correct_answer, current_question_index, player_currency, questions_correct, in_battle

    knight = Fighter(320, 272, 'Knight', 100, 10)
    bandit = Fighter(500, 230, 'Bandit', 100, 6)
    knight_health_bar = HealthBar(100, 20, knight.hp, knight.max_hp)
    bandit_health_bar = HealthBar(550, 20, bandit.hp, bandit.max_hp)

    if question_bank:
        load_next_question()

    in_battle = True
    knight_dead = False
    bandit_dead = False
    knight_death_done = False
    bandit_death_done = False
    death_start_time = 0
    feedback_shown = False

    while in_battle:
        clock.tick(FPS)
        screen.fill(BLACK)
        draw_bg()
        knight_health_bar.draw(knight.hp)
        bandit_health_bar.draw(bandit.hp)
        draw_panel()

        if 'question' in globals():
            wrapped_question = wrap_text(question, PANEL_FONT, SCREEN_WIDTH - 50)
            y_offset = SCREEN_HEIGHT - 185
            for line in wrapped_question:
                draw_text(line, PANEL_FONT, WHITE, 30, y_offset)
                y_offset += PANEL_FONT.size(line)[1] + 5

            for i, answer in enumerate(answers):
                wrapped_answer = wrap_text(answer, PANEL_FONT, SCREEN_WIDTH - 50)
                for line in wrapped_answer:
                    draw_text(line, PANEL_FONT, WHITE, 30, y_offset)
                    y_offset += PANEL_FONT.size(line)[1] + 5

        knight.update()
        knight.draw()
        bandit.update()
        bandit.draw()

        draw_potion_count(inventory.get('potions', 0), 100, 50)  

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                terminate_pygame()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and in_battle and len(question_bank) > 0:
                    if correct_answer == "A":
                        knight.attack(bandit)
                        show_feedback(True)
                        questions_correct[selected_level].append(question_bank[current_question_index]['id'])
                        question_bank.pop(current_question_index)  
                    else:
                        bandit.attack(knight)
                        show_feedback(False, correct_answer)
                    feedback_shown = True
                elif event.key == pygame.K_b and in_battle and len(question_bank) > 0:
                    if correct_answer == "B":
                        knight.attack(bandit)
                        show_feedback(True)
                        questions_correct[selected_level].append(question_bank[current_question_index]['id'])
                        question_bank.pop(current_question_index)  
                    else:
                        bandit.attack(knight)
                        show_feedback(False, correct_answer)
                    feedback_shown = True
                elif event.key == pygame.K_c and in_battle and len(question_bank) > 0:
                    if correct_answer == "C":
                        knight.attack(bandit)
                        show_feedback(True)
                        questions_correct[selected_level].append(question_bank[current_question_index]['id'])
                        question_bank.pop(current_question_index)  
                    else:
                        bandit.attack(knight)
                        show_feedback(False, correct_answer)
                    feedback_shown = True
                elif event.key == pygame.K_d and in_battle and len(question_bank) > 0:
                    if correct_answer == "D":
                        knight.attack(bandit)
                        show_feedback(True)
                        questions_correct[selected_level].append(question_bank[current_question_index]['id'])
                        question_bank.pop(current_question_index)  
                    else:
                        bandit.attack(knight)
                        show_feedback(False, correct_answer)
                    feedback_shown = True
                elif event.key == pygame.K_h and in_battle:
                    if inventory.get('potions', 0) > 0 and knight.hp < knight.max_hp:
                        knight.hp += 20
                        if knight.hp > knight.max_hp:
                            knight.hp = knight.max_hp
                        inventory['potions'] -= 1
                        save_progress()

        if feedback_shown:
            pygame.time.delay(2000)  
            feedback_shown = False
            if in_battle and len(question_bank) > 0:  
                current_question_index = (current_question_index + 1) % len(question_bank)
                load_next_question()
            elif len(question_bank) == 0:
                in_battle = False
                show_end_of_level_message()

        if not knight.alive and not knight_dead:
            knight_dead = True
            death_start_time = pygame.time.get_ticks()
        if not bandit.alive and not bandit_dead:
            bandit_dead = True
            death_start_time = pygame.time.get_ticks()

        if knight_dead and not knight_death_done:
            if pygame.time.get_ticks() - death_start_time > 1000:
                knight_death_done = True

        if bandit_dead and not bandit_death_done:
            if pygame.time.get_ticks() - death_start_time > 1000:
                bandit_death_done = True

        if knight_death_done:
            draw_text("Defeat! Press 'R' to Retry or 'M' for Main Menu", MENU_FONT, WHITE, 200, 150)
            pygame.display.flip()
            retry = False
            while not retry:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save_progress()
                        terminate_pygame()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            player_health = 100
                            boss_health = 200
                            knight = Fighter(320, 275, 'Knight', 100, 10)
                            bandit = Fighter(500, 230, 'Bandit', 100, 6)
                            knight_health_bar = HealthBar(100, 20, knight.hp, knight.max_hp)
                            bandit_health_bar = HealthBar(550, 20, bandit.hp, bandit.max_hp)
                            current_question_index = 0
                            if question_bank:
                                load_next_question()
                            knight_dead = False
                            bandit_dead = False
                            knight_death_done = False
                            bandit_death_done = False
                            retry = True
                        elif event.key == pygame.K_m:
                            in_battle = False
                            retry = True
                            main_menu()

        if bandit_death_done:
            player_currency += 10
            save_progress()
            show_victory_screen()

def show_pdf_viewer():
    running = True
    pdf_document = None
    try:
        import fitz  
        pdf_document = fitz.open('assets/document.pdf')
        total_pages = pdf_document.page_count

        pdf_page_width, pdf_page_height = 8.5 * 72, 11 * 72

        screen_width = int(pdf_page_width + 200)  
        screen_height = int(max(pdf_page_height, 600))  

        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('PDF Viewer')

        font_sizes = [20, 18, 16, 14, 12, 10]  
        default_font_size = 15
        font = pygame.font.Font(None, default_font_size)  

        page_ranges = {
            '-': (0, 1, "Cover Page"),
            '1': (2, 14, "Cardiovascular"),
            '2': (15, 20, "EKG"),
            '3': (21, 36, "Gastrointestinal"),
            '4': (37, 47, "Mental Health"),
            '5': (48, 50, "Pediatrics Respiratory"),
            '6': (50, 56, "Adult Respiratory"),
            '7': (56, 59, "Pediatrics Neurology"),
            '8': (59, 68, "Adult Neurology"),
            '9': (69, 79, "Endocrine"),
            '0': (80, 93, "Maternity"),
            '=': (94, 96, "Miscellaneous"),
        }

        current_section = None
        current_page = 1

        def render_page(page_number):
            page = pdf_document.load_page(page_number - 1)  
            pix = page.get_pixmap()

            page_width, page_height = pix.width, pix.height
            if page_width > pdf_page_width or page_height > pdf_page_height:
                scale_x = pdf_page_width / page_width
                scale_y = pdf_page_height / page_height
                scale = min(scale_x, scale_y)
                page_width = int(page_width * scale)
                page_height = int(page_height * scale)

            image = pygame.image.frombuffer(pix.samples, (pix.width, pix.height), 'RGB')

            scaled_image = pygame.transform.scale(image, (page_width, page_height))

            return scaled_image.convert()  

        def display_instructions():
            instructions = [
                "Use arrow keys to navigate:",
                "  Right/Down: Next page",
                "  Left/Up: Previous page",
                "",
                "Press keys on keyboard:",
                "  -: Cover Page",
                "  1: Cardiovascular",
                "  2: EKG",
                "  3: Gastrointestinal",
                "  4: Mental Health",
                "  5: Pediatrics Respiratory",
                "  6: Adult Respiratory",
                "  7: Pediatrics Neurology",
                "  8: Adult Neurology",
                "  9: Endocrine",
                "  0: Maternity",
                "  =: Miscellaneous",
                "",
                "R: Back to Main Menu"
            ]
            
            max_width = pdf_page_width - 40  
            max_height = screen_height - 40  
            
            for font_size in font_sizes:
                font = pygame.font.Font(None, font_size)
                text_height = sum(font.size(line)[1] for line in instructions)
                if text_height <= max_height:
                    break
            else:
                font = pygame.font.Font(None, default_font_size)  

            rendered_instructions = []
            for text in instructions:
                text_surface = font.render(text, True, (0, 0, 0))
                rendered_instructions.append(text_surface)
            
            return rendered_instructions

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    key_pressed = pygame.key.name(event.key)
                    if key_pressed in page_ranges:
                        start_page, end_page, section_name = page_ranges[key_pressed]
                        if key_pressed == '-':
                            current_page = 1  
                        elif section_name != current_section:
                            current_section = section_name
                            current_page = start_page
                        else:
                            current_page = min(max(start_page, current_page), end_page)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                        current_page = min(current_page + 1, total_pages)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                        current_page = max(current_page - 1, 1)
                    elif event.key == pygame.K_r:
                        running = False  

            screen.fill((255, 255, 255))  

            instructions = display_instructions()  
            instructions_x = pdf_page_width + 20
            instructions_y = 20
            for text_surface in instructions:
                screen.blit(text_surface, (instructions_x, instructions_y))
                instructions_y += text_surface.get_height() + 10

            current_page_image = render_page(current_page)
            pdf_page_x = (pdf_page_width - current_page_image.get_width()) // 2
            pdf_page_y = (pdf_page_height - current_page_image.get_height()) // 2

            screen.blit(current_page_image, (pdf_page_x, pdf_page_y))

            pygame.display.flip()

    except ImportError:
        print("PyMuPDF is not installed.")
    finally:
        if pdf_document:
            pdf_document.close()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  
        main_menu()  

def show_item_shop():
    global player_currency, inventory
    clock = pygame.time.Clock()
    frame_index = 0
    running = True

    while running:
        screen.fill(BLACK)

        current_image = shopkeeper_images[frame_index]
        screen.blit(current_image, (SCREEN_WIDTH // 2 - current_image.get_width() // 2, SCREEN_HEIGHT // 4 - current_image.get_height() // 4))

        welcome_message = "Welcome adventurer to my item shop... feel free to look around and buy!"
        draw_text(welcome_message, MENU_FONT, WHITE, 100, 450)
        draw_text(f"Press '1' to buy Health Potions - 20 currency", MENU_FONT, WHITE, 100, 480)
        draw_text(f"Press '2' to Access the Telegram Secret Chat - 100 currency", MENU_FONT, WHITE, 100, 510)

        draw_text(f"Currency: {player_currency}", MENU_FONT, WHITE, 20, 20)

        draw_text("Press 'M' to return to Main Menu", MENU_FONT, WHITE, 250, 550)

        pygame.display.flip()
        clock.tick(FPS)

        frame_index += 1
        if frame_index >= len(shopkeeper_images):
            frame_index = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    running = False
                elif event.key == pygame.K_1:  
                    if player_currency >= 20:
                        player_currency -= 20
                        inventory['potions'] += 1
                        save_progress()  
                        print("You bought a Health Potion!")
                    else:
                        print("Not enough currency to buy a Health Potion.")
                elif event.key == pygame.K_2:  
                    if player_currency >= 100:
                        player_currency -= 100
                        save_progress()  
                        webbrowser.open("https://t.me/+UZbeV1eYoVg2MGNh")
                        print("You now have access to the Telegram secret chat!")
                    else:
                        print("Not enough currency to access the Telegram secret chat.")

    main_menu()  

if __name__ == '__main__':
    main_menu()
