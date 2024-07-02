# 0 state - on ground, colliding   -->    replace onground variable
# 1 state - jumping  -->    replace is_jumping variable
# 2 state - freefall   -->   replace onground variable
# 10 menu_state  -->   start menu
# 11 menu_state  -->   game
# 12 menu_state  -->  end menu
# 0 ret (button state)   -->  start playing game
# 1 ret (button state)   --> back to start menu
# 2 ret (button state)  --> replay

import pygame
import random
from pygame import mixer
import time      # for score based on time

fps = 60  # frames per second
size = width, height = 1000, 800
black = (0, 0, 0)
white = (255, 255, 255)
orange = (255, 109, 5)

pygame.init()
music = pygame.mixer.music.load('Sounds/backgroundMusic.mp3')
pygame.mixer.music.play(-1)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)  # screen resolution
pygame.display.set_caption('Lava Game')
f70_font = pygame.font.Font('Images/alagard.ttf', 70)
f25font = pygame.font.Font('Images/alagard.ttf', 30)
f50_font = pygame.font.Font('Images/alagard.ttf', 50)

# dino class

class Dino(pygame.sprite.Sprite):  # defines class of sprite- Sprite
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.image_orig = img.copy()
        self.image_flip = pygame.transform.flip(img, True, False)  # (image, horizontal flip, vertical flip)
        self.image.set_colorkey(white)  # removes background colour
        self.rect = self.image.get_rect()  # calculates the rectangle that will enclose it
        self.rect.center = (width / 2, height / 2)
        self.rect.x, self.rect.y = 0, 0  # start position
        self.trajectory_x, self.trajectory_y = [], []
        self.trajectory_index = 0
        self.startx, self.starty = 0, 0
        self.left_pressed, self.right_pressed = False, False
        self.velX = 3
        self.velY = 0
        self.direction = 1
        self.gravity = 0.2
        self.x_collision = False
        self.state = 2  # initial state is freefall
        self.jump_ctr = 0
        self.max_jump_ctr = 30

    def move(self, diff):  # screen movement
        self.rect.y += diff

    def update(self):
        if not self.x_collision:
            if self.left_pressed and not self.right_pressed:  # left right movement
                self.rect.x -= self.velX
            if self.right_pressed and not self.left_pressed:
                self.rect.x += self.velX
        self.x_collision = False

        if (self.rect.x + self.rect.width) > width:
            self.rect.x = width - self.rect.width
        elif (self.rect.x) < 0:
            self.rect.x = 0

        # changes the side the dino faces
        if self.direction == -1:
            self.image = self.image_flip
        if self.direction == 1:
            self.image = self.image_orig

        if self.state == 1:  # jumping state
            self.velY = -5
            self.jump_ctr += 1
            if self.jump_ctr > self.max_jump_ctr:
                self.state = 2  # (free fall after jump completes)

        if self.state == 2:  # Free fall state
            self.velY += self.gravity

        if self.velY > 7:  # max free fall velocity
            self.velY = 7

        self.rect.y += self.velY


class Lava(pygame.sprite.Sprite):  # defines class of sprite- Sprite
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.maxH = height - 25  # 775, so that lava always stays on the screen
        self.rect.x, self.rect.y = 0, self.maxH
        self.velY = 0.2  # lava velocity
        self.diff = 0.0
        self.frame_count = 0
        self.frame_update_count = 6

    def move(self, diff):  # screen movement
        self.rect.y += diff

    def update(self):

        if self.rect.y > self.maxH:
            self.rect.y = self.maxH

        self.frame_count += 1
        if self.frame_count >= self.frame_update_count:
            self.rect.y -= 1
            self.frame_count = 0        # reset frame count after every 6 frames, used to change speed of lava



class Platforms(pygame.sprite.Sprite):  # defines class of sprite- Sprite
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def move(self, diff):
        self.rect.y += diff

def Generate(rect, screen, max_h=150, max_d=300):
    y = rect.y - random.randint(rect.height + 80, max_h)  # y of platform (80+50 - min height diff)
    mid = rect.x + (rect.width / 2)  # mid of platform

    rx = random.randint(100, max_d)  # difference between platforms' x
    if rect.x > (screen[1] - (rect.x + rect.width)):
        x = mid - rx - rect.width  # generates on left side
    else:
        x = mid + rx  # generates on right side

    return x, y

def Top_Bottom_Platform(p_group):
    s_p = sorted(p_group.sprites(), key=lambda x: x.rect.y)  # sorted list of platforms group
    return s_p[0], s_p[len(s_p) - 1]  # top platform, bottom platform

def display_score(score):
    stringc = 'Score: ' + str(score)
    score_surf = f50_font.render(stringc, False, white)
    score_rect = score_surf.get_rect(center=(800, 50))
    pygame.draw.rect(screen, (255, 109, 5), score_rect)
    screen.blit(score_surf, score_rect)
    return score

def start_menu():
    screen.fill(black)
    bg_clr = orange
    rk1_surface = pygame.image.load('Images/rockfinal.bmp').convert()
    b_surf = f70_font.render('  Start  ', False, white).convert()
    b_rect = b_surf.get_rect(center=(500, 500))
    title_surf = f70_font.render('Lava Game ', False, white).convert()
    title_rect = title_surf.get_rect(center=(500, 200))
    message_surf = f25font.render('Use Space Bar for jump & Arrow keys for Movement', False, white).convert()
    message_rect = message_surf.get_rect(center=(500, 350))
    message1_surf = f25font.render('Game by Medhini ,Ridhi and Nikita ', False, white).convert()
    message1_rect = message1_surf.get_rect(center=(500, 400))
    screen.blit(rk1_surface, (0, 0))
    pygame.draw.rect(screen, bg_clr, b_rect)
    pygame.draw.rect(screen, bg_clr, message_rect)
    pygame.draw.rect(screen, bg_clr, title_rect)
    pygame.draw.rect(screen, bg_clr, message1_rect)
    screen.blit(title_surf, title_rect)
    screen.blit(b_surf, b_rect)
    screen.blit(message_surf, message_rect)
    screen.blit(message1_surf, message1_rect)
    pygame.display.update()
    ret = False     # ret -- state variable for buttons
    run = True

    while run:
        for event1 in pygame.event.get():
            if event1.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event1.type == pygame.MOUSEBUTTONDOWN:
                if event1.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if b_rect.collidepoint((mx, my)):
                        ret = True
                        run = False
        clock.tick(40)

    return ret


def game():
    screen.fill(black)
    # platforms
    all_platforms = pygame.sprite.Group()
    score = 0
    start_time = time.time()
    rock_img = pygame.image.load("Images/rocky1.jpg").convert()  # loads image on screen
    rock_img = pygame.transform.scale(rock_img, (200, 50))

    plat = Platforms(rock_img, 790, 740)  # reference platform
    Platforms.add(plat)

    for i in range(8):
        x1, y1 = Generate(plat.rect, size)
        print(x1, y1)
        plat = Platforms(rock_img, x1, y1)
        all_platforms.add(plat)

    col_sprite = all_platforms.sprites()[0]

    top_p, bot_p = Top_Bottom_Platform(all_platforms)

    lava_img = pygame.image.load("Images/lava1.jpg").convert()  # loads image on screen
    lava_img = pygame.transform.scale(lava_img, (width, height))
    lava = Lava(lava_img)

    dino_img = pygame.image.load('Images/dino_img.png')  # loads image on screen
    dino_img = pygame.transform.scale(dino_img, (40, 40))
    dino = Dino(dino_img)

    dino.rect.x = bot_p.rect.x + 80
    dino.rect.y = bot_p.rect.y - dino.rect.height * 2

    lava_bg = pygame.image.load("Images/rockfinal.bmp")
    lava_bg = pygame.transform.scale(lava_bg, (width, height))
    all_sprites = pygame.sprite.Group()

    all_sprites.add(lava)
    all_sprites.add(dino)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # condition to end loop
                exit_all()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if dino.state == 0:
                        jump_sound = mixer.Sound('Sounds/jump.wav')
                        jump_sound.play()
                        dino.jump_ctr = 0  # jump counter, to control jump
                        dino.state = 1
                elif event.key == pygame.K_LEFT:
                    dino.left_pressed = True
                    dino.direction = -1
                elif event.key == pygame.K_RIGHT:
                    dino.right_pressed = True
                    dino.direction = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    dino.left_pressed = False
                elif event.key == pygame.K_RIGHT:
                    dino.right_pressed = False

        # moving screen up, platforms move down
        if dino.state == 1 and 100 < dino.rect.y < 200:
            for p in all_platforms:
                p.move(5)
            dino.move(5)
            lava.move(5)


        screen.fill(black)
        screen.blit(lava_bg, (0,0))
        all_sprites.update()

        all_platforms.draw(screen)
        all_sprites.draw(screen)
        display_score(score)
        pygame.display.flip()  # updates display,it is used when we finish drawing

        if lava.rect.y <= bot_p.rect.y:
            x1, y1 = Generate(top_p.rect, size, max_h=150, max_d=300)
            bot_p.rect.x = x1
            bot_p.rect.y = y1
            top_p, bot_p = Top_Bottom_Platform(all_platforms)
            print('Lava crossed', lava.rect.y)

        if not dino.state == 0:
            col_sprite = pygame.sprite.spritecollideany(dino, all_platforms)
            if col_sprite:
                if (dino.rect.x + dino.rect.width) in range(col_sprite.rect.x, col_sprite.rect.x + 4):  # left side
                    dino.x_collision = True     # (+ 4) since velx = 3
                elif (dino.rect.x) in range(col_sprite.rect.x + col_sprite.rect.width - 4,
                                            col_sprite.rect.x + col_sprite.rect.width):  # right side of platform
                    dino.x_collision = True
                else:
                    if dino.state == 2:
                        print(dino.state, dino.rect.y + dino.rect.height, col_sprite.rect.y)
                        if col_sprite.rect.y <= (dino.rect.y + dino.rect.height) <= col_sprite.rect.y + 10:
                            dino.rect.y = col_sprite.rect.y - dino.rect.height + 1
                            dino.state = 0
                            dino.velY = 0
                        else:
                            dino.rect.y = col_sprite.rect.y + col_sprite.rect.height
                            dino.velY = 0
                    elif dino.state == 1:
                        dino.rect.y = col_sprite.rect.y + col_sprite.rect.height
                        dino.velY = 0
                        dino.state = 2
        else:
            if col_sprite:
                if not pygame.sprite.collide_rect(dino, col_sprite):
                    dino.velY = 0
                    dino.state = 2

        if (dino.rect.y + dino.rect.height) >= lava.rect.y:
            die_sound = mixer.Sound('Sounds/die.wav')
            die_sound.play()
            time.sleep(2)        # delay of 2 secs
            run = False


        temp_score = int( time.time() - start_time )

        if temp_score != score:       # check for score
            score = temp_score
            period = 15
            if (score % period) == 0:
                if score <= (9 * period):
                    lava.frame_update_count = 1 if lava.frame_update_count < 2 else lava.frame_update_count - 1
                    print(lava.frame_update_count, score)   #frame count reduces (6,5,4,..1) so that speed increases

        clock.tick(fps)

    return score


def end_menu(score):
    screen.fill('Black')
    bg_clr = orange
    stringc = 'Score: ' + str(score)
    score_surf = f50_font.render(stringc, False, white)
    score_rect = score_surf.get_rect(center=(500, 500))
    rk1_surface = pygame.image.load('Images/rockfinal.bmp').convert()
    b_surf = f50_font.render('  Start Menu  ', False, white).convert()
    b_rect = b_surf.get_rect(center=(350, 600))
    r_surf = f50_font.render('  Replay  ', False, white).convert()
    r_rect = r_surf.get_rect(center=(650, 600))
    title_surf = f70_font.render('Lava Game ', False, white).convert()
    title_rect = title_surf.get_rect(center=(500, 200))
    endmessage_surf = f50_font.render(' GAME OVER ', False, white).convert()
    endmessage_rect = endmessage_surf.get_rect(center=(500, 400))
    screen.blit(rk1_surface, (0, 0))
    pygame.draw.rect(screen, bg_clr, b_rect)
    pygame.draw.rect(screen, bg_clr, r_rect)
    pygame.draw.rect(screen, bg_clr, endmessage_rect)
    pygame.draw.rect(screen, bg_clr, title_rect)
    pygame.draw.rect(screen, (255, 109, 5), score_rect)
    screen.blit(score_surf, score_rect)
    screen.blit(title_surf, title_rect)
    screen.blit(b_surf, b_rect)
    screen.blit(r_surf, r_rect)
    screen.blit(endmessage_surf, endmessage_rect)
    pygame.display.update()

    ret = 0           # start game
    run = True
    while run:
        for event1 in pygame.event.get():
            if event1.type == pygame.QUIT:
                exit_all()
            if event1.type == pygame.MOUSEBUTTONDOWN:
                if event1.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if b_rect.collidepoint((mx, my)):
                        ret = 1        # start menu button
                        run = False
                    if r_rect.collidepoint((mx, my)):
                        ret = 2        # replay game button
                        run = False
        clock.tick(fps)

    return ret

def exit_all():      # function to exit pygame
    pygame.quit()
    quit()

menu_state = 10

main_run = True
score = 1
while main_run:
    if menu_state == 10:
        ret = start_menu()
        if ret:
            menu_state = 11
    elif menu_state == 11:
        score = game()
        menu_state = 12
    elif menu_state == 12:
        ret = end_menu(score)
        if ret == 1:
            menu_state = 10
        elif ret == 2:
            menu_state = 11

pygame.quit()
