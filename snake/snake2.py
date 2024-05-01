import pygame
import time
import random
import psycopg2

# Initialize database connection
def initialize_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="StopDomesticViolence"
        )
        cur = conn.cursor()
        return conn, cur
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)

# Create user table if not exists
def create_user_table(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS snake_scores (id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE, user_score INTEGER)")

# Update user score
def update_user_score(cur, conn, username, score):
    cur.execute("SELECT * FROM snake_scores WHERE username = %s", (username,))
    user = cur.fetchone()
    if user:
        cur.execute("UPDATE snake_scores SET user_score = %s WHERE username = %s", (score, username))
    else:
        cur.execute("INSERT INTO snake_scores (username, user_score) VALUES (%s, %s)", (username, score))
    conn.commit()

# Display user level
def show_user_level(username, cur):
    cur.execute("SELECT user_score FROM snake_scores WHERE username = %s", (username,))
    user_score = cur.fetchone()
    if user_score:
        print(f"Welcome back, {username}! Your current level is {user_score[0]}.")
    else:
        print(f"Welcome, {username}! You are a new player.")

# Initialize game
def init_game():
    pygame.init()
    pygame.display.set_caption('Snakes')

# Show score
def show_score(score):
    font = pygame.font.SysFont('times new roman', 20)
    score_surface = font.render('Score : ' + str(score), True, white)
    score_rect = score_surface.get_rect()
    game_window.blit(score_surface, score_rect)

# Game over screen
def game_over():
    font = pygame.font.SysFont('times new roman', 50)
    game_over_surface = font.render('Your Score is : ' + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (window_x/2, window_y/4)
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()

# Game stop screen
def game_stop():
    game_over()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    time.sleep(2)
                    pygame.quit()
                    quit()
                if event.key == pygame.K_c:
                    return

# Main game function
def main_game():
    global direction, snake_position, snake_body, fruit_spawn, score

    while True:
        for event in pygame.event.get():
            handle_events(event)

        update_direction()
        update_snake_position()
        handle_fruit_collision()
        handle_boundary_collision()
        handle_self_collision()
        
        draw_elements()

        pygame.display.update()
        fps.tick(snake_speed)

# Handle keyboard events
def handle_events(event):
    global change_to
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            change_to = 'UP'
        elif event.key == pygame.K_DOWN:
            change_to = 'DOWN'
        elif event.key == pygame.K_LEFT:
            change_to = 'LEFT'
        elif event.key == pygame.K_RIGHT:
            change_to = 'RIGHT'
        elif event.key == pygame.K_SPACE:
            update_user_score(cur, conn, username, score)
            print("Game Over! Your final score is:", score)
            game_stop()

# Update snake direction
def update_direction():
    global direction, change_to
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    elif change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    elif change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    elif change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

# Update snake position
def update_snake_position():
    global snake_position, snake_body
    if direction == 'UP':
        snake_position[1] -= 10
    elif direction == 'DOWN':
        snake_position[1] += 10
    elif direction == 'LEFT':
        snake_position[0] -= 10
    elif direction == 'RIGHT':
        snake_position[0] += 10

    snake_body.insert(0, list(snake_position))
    if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
        score += 10
        return True
    else:
        snake_body.pop()
        return False

# Handle fruit collision
def handle_fruit_collision():
    global fruit_spawn, fruit_position
    if not fruit_spawn:
        fruit_position = [random.randrange(1, (window_x//10)) * 10, 
                        random.randrange(1, (window_y//10)) * 10]
    fruit_spawn = True

# Handle boundary collision
def handle_boundary_collision():
    global score
    if snake_position[0] < 0 or snake_position[0] > window_x-10:
        update_user_score(cur, conn, username, 0)
        print("Game Over! Your final score is:", score)
        game_over()
    if snake_position[1] < 0 or snake_position[1] > window_y-10:
        update_user_score(cur, conn, username, 0)
        print("Game Over! Your final score is:", score)
        game_over()

# Handle self collision
def handle_self_collision():
    global score
    for block in snake_body[1:]:
        if snake_position[0] == block[0] and snake_position[1] == block[1]:
            update_user_score(cur, conn, username, 0)
            print("Game Over! Your final score is:", score)
            game_over()

# Draw game elements
def draw_elements():
    game_window.fill(black)
    show_score(score)
    for pos in snake_body:
        pygame.draw.rect(game_window, red, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

# Main execution
if __name__ == '__main__':
    # Initialize database
    conn, cur = initialize_db()
    create_user_table(cur)

    # Get user's username
    username = input("Enter your username: ")

    # Display user's current level
    show_user_level(username, cur)

    # Initialize game
    init_game()

    # Initialize game variables
    snake_speed = 10
    window_x = 700
    window_y = 700
    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)
    red = pygame.Color(255, 0, 0)
    green = pygame.Color(0, 255, 0)
    blue = pygame.Color(0, 0, 255)
    game_window = pygame.display.set_mode((window_x, window_y))
    fps = pygame.time.Clock()
    snake_position = [100, 50]
    snake_body = [[100, 50]]
    fruit_position = [random.randrange(1, (window_x//10)) * 10, 
                    random.randrange(1, (window_y//10)) * 10]
    change_to = direction = 'RIGHT'
    fruit_spawn = True
    score = show_user_level(username, cur)

    # Start game
    main_game()