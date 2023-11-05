from flask import Flask, render_template, jsonify
import random
import json
import heapq

app = Flask(__name__, template_folder='templates')


def createMaze(boxSize, start_x, start_y):

    connect_prob = 0.80
    maze = [['#'] * (2 * boxSize - 1) for _ in range(2 * boxSize - 1)]


    def is_valid(x, y):
        return 0 <= x < boxSize and 0 <= y < boxSize

    def generate(x, y):
        maze[y * 2][x * 2] = ' '

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if is_valid(nx, ny) and maze[ny * 2][nx * 2] == '#':
                maze[y * 2 + dy][x * 2 + dx] = ' '
                generate(nx, ny)

        # Introduce random dead-end branches
        if random.random() < 0.5:
            for _ in range(2):
                d = random.choice(directions)
                nx, ny = x + d[0], y + d[1]
                if is_valid(nx, ny) and maze[ny * 2][nx * 2] == '#':
                    if random.random() < connect_prob:
                        # Randomly connect the dead-end branch back to the main path
                        mx, my = x, y
                        while mx != nx or my != ny:
                            maze[my * 2][mx * 2] = ' '
                            mx += d[0]
                            my += d[1]
                    else:
                        maze[y * 2 + d[1]][x * 2 + d[0]] = ' '
    generate(start_x, start_y)
    #print(start_x, start_y)
    #print(find_longest_path(maze))
    return maze


def checkMaze(maze):
    for row in maze:
        for cell in row:
            if cell == '#':
                print('#', end=' ')
            else:
                print(' ', end=' ')
        print()


def find_longest_path(maze):
    def is_valid(x, y):
        return 0 <= x < len(maze[0]) and 0 <= y < len(maze)

    def neighbors(x, y):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if is_valid(new_x, new_y) and maze[new_y][new_x] == ' ':
                yield (new_x, new_y)

    max_length = 0

    for start_y in range(len(maze)):
        for start_x in range(len(maze[0])):
            if maze[start_y][start_x] == ' ':
                queue = [(0, start_x, start_y)]
                visited = set()

                while queue:
                    length, x, y = heapq.heappop(queue)
                    if (x, y) in visited:
                        continue
                    visited.add((x, y))
                    max_length = max(max_length, length)

                    for nx, ny in neighbors(x, y):
                        heapq.heappush(queue, (length + 1, nx, ny))

    return max_length


@app.route('/')
def display_maze():
    boxSize = 10  # Adjust the maze size as needed
    start_coords = (random.randint(0, boxSize - 1), random.randint(0, boxSize - 1))
    start_x, start_y = start_coords
    maze = createMaze(boxSize, start_x, start_y)
    length_to_find = find_longest_path(maze)
    maze_json = json.dumps(maze)
    return render_template('maze.html', maze_json=maze_json,
                           longest_path_length=length_to_find)

@app.route('/reset')
def redisplay_maze():
    boxSize = 10  # Adjust the maze size as needed
    start_coords = (random.randint(0, boxSize - 1), random.randint(0, boxSize - 1))
    start_x, start_y = start_coords
    maze = createMaze(boxSize, start_x, start_y)
    length_to_find = find_longest_path(maze)
    data = {
        'maze_json': json.dumps(maze),
        'longest_path_length': length_to_find,
    }

    return jsonify(data)  # Return JSON response

if __name__ == '__main__':
    #start_coords = (random.randint(0, 7 - 1), random.randint(0, 7 - 1))
    #start_x, start_y = start_coords
    #checkMaze(createMaze(7, start_x, start_y))
    app.run()
