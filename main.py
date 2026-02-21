import pygame
from pygame.locals import *
import random
import asyncio

async def wait_ms(ms):
    await asyncio.sleep(ms / 1000)#une fonction pour faire pause sans sleep qui fait crash sur le web

credit_start_time = 0 #pour faire le temps de la page de credit
tutorial_start_time = 0#temps de la page de tutorial
game_over_start_time = 0#temps de la page de game over
pygame.init()

global font
font=pygame.font.Font(None,200)#mes polices d'écritures pour les différentes pages du jeu
font2=pygame.font.Font(None,50)
fenetre = pygame.display.set_mode((900, 600), pygame.RESIZABLE)

cell_size = 60 #taille des cellules
grid = [[None for _ in range(8)] for _ in range(8)] #definir une grille en 8x8 vide dans des listes de listes
wich_block = -1 #on sélectionne pas de block au début
global score
score = 0#variable score
line_cleared = False
konami_seq = [K_UP, K_UP, K_DOWN, K_DOWN, K_LEFT, K_RIGHT, K_LEFT, K_RIGHT, K_b, K_a] #secret
konami_index = 0
konami = False
global color
color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))#on définit une couleur aléatoire pour le secret pour éviter des bugs

clear_queue = []
last_clear_time = 0
CLEAR_DELAY = 50

dragging = False#pour le drag and drop
drag_block = -1

# le gui et tt le bazar

smallfont = pygame.font.SysFont('Corbel', 35) #une autre police

text1 = smallfont.render('start', True, color) #tout les boutons du début
text2 = smallfont.render('quit', True, color)
text3 = smallfont.render('credit', True, color)
text4 = smallfont.render('how to play', True, color)
start = False
width = fenetre.get_width()
height = fenetre.get_height()

def collect_full_line_cells(grid): #collecte les cellules à effacer pour les lignes et colonnes complètes
    global line_cleared
    size = len(grid)
    full_rows = [r for r in range(size) if all(grid[r][c] is not None for c in range(size))]
    full_cols = [c for c in range(size) if all(grid[r][c] is not None for r in range(size))]

    cells = []
    for r in full_rows:
        for c in range(size):
            cells.append((r, c))#modifier
    for c in full_cols:
        for r in range(size):
            cells.append((r, c))

    return cells

def place_shape(shape, base_r, base_c, grid, color): #place une forme sur la grille en coloriant les cellules correspondantes
    for dr, dc in shape:
        r = base_r + dr
        c = base_c + dc
        if 0 <= r < 8 and 0 <= c < 8:
            grid[r][c] = color

def can_place(shape, base_r, base_c, grid): #vérification qu'on peut placer une forme à une position donnée sans dépasser les limites ou chevaucher d'autres formes
    for dr, dc in shape:
        r = base_r + dr
        c = base_c + dc

        if r < 0 or r >= 8:
            return False
        if c < 0 or c >= 8:
            return False
        if grid[r][c] is not None:
            return False

    return True

def has_any_move(shapes, grid):#vérifie si on a perdue en pouvant placer les blocks
    for shape in shapes:
        if not shape:
            continue
        for r in range(8):
            for c in range(8):
                if can_place(shape, r, c, grid):
                    return True
    return False

def blocks(grid):#on définit nos blocks
    shapes =[
    [(0,1), (1,0), (1,1), (1,2)],
    [(0,0), (0,1), (0,2), (1,1)],
    [(0,0), (0,1), (1,1), (0,2)],
    [(0,1), (1,0), (1,1), (2,1)],
    [(0,0), (0,1), (1,1), (1,2)],
    [(1,0), (1,1), (0,1), (0,2)],
    [(0,0),(1,0),(1,1),(1,2)],
    [(1,0),(1,1),(0,1),(0,2)],
    [(0,0),(1,0),(2,0),(2,1)],
    [(0,1),(1,1),(2,1),(2,0)],
    [(0,0),(0,1),(0,2),(1,2)],
    [(0,0),(1,0),(0,1),(0,2)],
    [(0,0),(1,0),(2,0),(2,1),(2,2)],
    [(0,2),(1,2),(2,2),(2,1),(2,0)],
    [(0,0),(0,1),(0,2),(1,2),(2,2)],
    [(0,0),(0,1),(0,2),(1,0),(2,0)],
    [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)],
    [(0,0),(1,0),(2,0),(3,0),(4,0)],
    [(0,0),(0,1),(0,2),(0,2),(0,3),(0,4)],
    [(0,0),(1,0),(2,0),(3,0)],
    [(0,0),(0,1),(0,2),(0,2),(0,3)],
    ]
    global current_blocks, block_positions, block_colors
    current_blocks = random.sample(shapes, 3)#on en choisit 3
    block_colors = [
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))#on met les couleurs aléatoires pour les blocks
        for _ in range(3)
    ]
    block_positions = [(1, 9), (4, 9), (7, 9)]#on met les positions des blocks au début sur le coté
    return current_blocks

continuer = True

blocks(grid)

async def main():  # Mettre tout dans une fonction async
    global start, wich_block, score, konami_index, konami, grid
    global credit_start_time, tutorial_start_time, game_over_start_time
    global clear_queue, last_clear_time, dragging, drag_block
    global current_blocks, block_positions, block_colors, continuer
    global line_cleared, color

    while continuer:  #début de la boucle principale
        for event in pygame.event.get():
            if start == False:#on vérifie si on a démarée start et sinon on affiche le gui
                    if event.type == pygame.MOUSEBUTTONDOWN:

                        # if the mouse is clicked on the
                        # button the game is terminated
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if start_rect.collidepoint(mouse):#bouton de démarrage
                                start = True
                            elif quit_rect.collidepoint(mouse):#pour quitter
                                pygame.quit()
                            elif credit_rect.collidepoint(mouse):#les credits
                                fenetre.fill((0, 0, 0))
                                fenetre.blit(smallfont.render("un grand merci à", True, "blue"), (width // 2-100, height // 2))
                                fenetre.blit(smallfont.render("toute ma classe", True, "blue"), (width // 2-100, height // 2+30))
                                fenetre.blit(smallfont.render("à tout ceux qui m'ont aidé", True, "blue"), (width // 2-100, height // 2+60))
                                fenetre.blit(smallfont.render("a mes professeurs", True, "blue"), (width // 2-100, height // 2+90))
                                fenetre.blit(smallfont.render("code de Hugo LAFABRIE", True, "blue"), (width // 2-100, height // 2+120))
                                pygame.display.update()
                                await asyncio.sleep(5)
                                credit_start_time = pygame.time.get_ticks()
                                start = True
                            elif explain_rect.collidepoint(mouse):#explication du jeu
                                fenetre.fill((0, 0, 0))
                                fenetre.blit(smallfont.render("to select a shape you need to click", True, "white"), (width // 2-100, height // 2))
                                fenetre.blit(smallfont.render("on 1, 2 or 3 and to deplace them you", True, "white"), (width // 2-100, height // 2+30))
                                fenetre.blit(smallfont.render("can use ZQSD or arrows", True, "white"), (width // 2-100, height // 2+60))

                                pygame.display.update()
                                await asyncio.sleep(5)
                                credit_start_time = pygame.time.get_ticks()
                                start = True
            if start == True:#démarage du jeu
                if start == True:
                    if event.type == pygame.MOUSEBUTTONDOWN:#fonction ppour pouvoir déplacer les blocks a la sourie
                        mx, my = event.pos #pos de la sourie sur les cases
                        col = mx // cell_size
                        row = my // cell_size

                        for i, shape in enumerate(current_blocks):#on vérifie si on a cliqué sur un block sélectionnable en vérifiant toutes leur cases
                            if len(shape) > 0:
                                base_r, base_c = block_positions[i]
                                for dr, dc in shape:
                                    if row == base_r + dr and col == base_c + dc:
                                        dragging = True
                                        drag_block = i
                                        break

                    elif event.type == pygame.MOUSEMOTION and dragging:#on bouge les pièces avec la sourie si elle sont sélectionnées
                        mx, my = event.pos
                        block_positions[drag_block] = (my // cell_size, mx // cell_size)

                    elif event.type == pygame.MOUSEBUTTONUP and dragging: #quand on relache la sourie on essaye de placer le block sélectionné
                        shape = current_blocks[drag_block]
                        base_r, base_c = block_positions[drag_block]

                        if can_place(shape, base_r, base_c, grid):#si on peut le placer on le place et on ajoute les points et on l'enleve de la liste des 3 blocks
                            place_shape(shape, base_r, base_c, grid, block_colors[drag_block])
                            current_blocks[drag_block] = []
                            score += 5

                        dragging = False
                        drag_block = -1
                        if current_blocks == [[], [], []]:  # réaparition des blocks quand on les a tous placés
                            blocks(grid)

                if event.type == pygame.KEYDOWN:#on vérifie les touches pour sélectionner les blocks et les déplacer
                    if event.key == pygame.K_1:
                        wich_block = 0
                    elif event.key == pygame.K_2:
                        wich_block = 1
                    elif event.key == pygame.K_3:
                        wich_block = 2
                    if event.key == pygame.K_UP or event.key == pygame.K_z and wich_block != -1:
                        r, c = block_positions[wich_block]
                        block_positions[wich_block] = (r - 1, c)

                    if event.key == pygame.K_DOWN or event.key == pygame.K_s and wich_block != -1:
                        r, c = block_positions[wich_block]
                        block_positions[wich_block] = (r + 1, c)

                    if event.key == pygame.K_LEFT or event.key == pygame.K_q and wich_block != -1:
                        r, c = block_positions[wich_block]
                        block_positions[wich_block] = (r, c - 1)

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d and wich_block != -1:
                        r, c = block_positions[wich_block]
                        block_positions[wich_block] = (r, c + 1)

                    if event.key == pygame.K_RETURN and wich_block != -1:#si on appuie sur entrée on essaye de placer le block sélectionné
                        shape = current_blocks[wich_block]
                        base_r, base_c = block_positions[wich_block]
                        color = block_colors[wich_block]
                        if can_place(shape, base_r, base_c, grid):
                            place_shape(shape, base_r, base_c, grid, color)
                            current_blocks[wich_block] = []
                            wich_block = -1
                            score += 5
                    if current_blocks == [[], [], []]:#réaparition des blocks quand on les a tous placés
                        blocks(grid)
                    if event.key == konami_seq[konami_index]:#secret
                        konami_index += 1
                        if konami_index == len(konami_seq) and konami == False:
                            konami = True
                            konami_index = 0
                        if konami_index == len(konami_seq) and konami == True:
                            konami = False
                            konami_index = 0
                    else:
                        konami_index = 0

            if event.type == QUIT:#pour quitter
                continuer = False
            if event.type == pygame.MOUSEBUTTONDOWN and konami == True:#tj secret

                mx, my = pygame.mouse.get_pos()
                col = mx // cell_size
                row = my // cell_size
                if 0 <= row < 8 and 0 <= col < 8:
                    if grid[row][col] == color:
                        grid[row][col] = None
                    else:
                        grid[row][col] = color


            if line_cleared:#actualiser le score
                score += 20
                line_cleared = False
        if start == False:
            fenetre.fill((40, 40, 40))  #on nettoie l'écran

            mouse = pygame.mouse.get_pos()
            width, height = fenetre.get_size()
            #on place nos bouttons et on les fait apparaitres tant que le jeu a pas démarré
            start_rect = text1.get_rect(center=(width // 2, height // 2))
            quit_rect = text2.get_rect(center=(width // 2, height // 2 + 40))
            credit_rect = text3.get_rect(center=(width // 2, height // 2 + 80))
            explain_rect = text4.get_rect(center=(width // 2, height // 2 + 120))
            fenetre.blit(text1, start_rect)
            fenetre.blit(text2, quit_rect)
            fenetre.blit(text3, credit_rect)
            fenetre.blit(text4, explain_rect)

        if not clear_queue:#on définie les colones et ligne pour l'animation de nettoyage et l'actualisation du score
            clear_queue = collect_full_line_cells(grid)
            if clear_queue:
                score += 20
        now = pygame.time.get_ticks()
        if clear_queue and now - last_clear_time >= CLEAR_DELAY:#on efface les cellules à nettoyer une par une pour l'animation
            r, c = clear_queue.pop(0)
            grid[r][c] = None
            last_clear_time = now

        if start == True: #début du rendu du jeu
            fenetre.fill((30, 30, 30))
            for row in range(8):
                for col in range(8):
                    rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)# on dessine la grille et les blocks déjà placés
                    if grid[row][col] is not None:
                        pygame.draw.rect(fenetre, grid[row][col], rect)# colorier les cellules occupées
                    else:
                        pygame.draw.rect(fenetre, (50, 50, 50), rect)
                    pygame.draw.rect(fenetre, (200, 200, 200), rect, 1)

            for i, shape in enumerate(current_blocks):#dessiner les blocks sélectionnables sur le coté
                base_r, base_c = block_positions[i]
                for dr, dc in shape:
                    r = base_r + dr
                    c = base_c + dc
                    rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
                    pygame.draw.rect(fenetre, block_colors[i], rect)
                    pygame.draw.rect(fenetre, (200, 200, 200), rect, 1)
            if current_blocks != [[], [], []] and not has_any_move(current_blocks, grid):#affichage du menu perdu
                fenetre.blit(font.render("you Lost", True, "Red"), (300, 300))
                pygame.display.update()
                await asyncio.sleep(5)
                credit_start_time = pygame.time.get_ticks()
                grid = [[None for _ in range(8)] for _ in range(8)]
                score = 0
                wich_block = -1
                konami_index = 0
                konami = False
                blocks(grid)
                start = False
        fenetre.blit(font2.render(f"tu es a {str(score)}", True, '#55ff55'), (650,0))

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())  # Lancer le jeu
