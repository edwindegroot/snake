import pygame
import random


class Game:
    width = None
    height = None
    sq_side = None
    x_steps = None
    y_steps = None

    screen = None
    clock = None
    running = None
    dt = None
    speed = None
    direction = None
    food_x = None
    food_y = None

    snake_length = None
    length_increment = None

    snake_segments = []
    border_points = []
    head = None
    tail = None
    thickness = None
    food_size = None
    score_font = None
    score = None
    best_score = None

    def init(self):
        pygame.init()
        self.width = 1280
        self.height = 720
        self.sq_side = 40
        self.x_steps = self.width / self.sq_side
        self.y_steps = self.height / self.sq_side

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.speed = 600
        self.direction = None
        self.food_x = random.randint(0, self.width - self.sq_side)
        self.food_y = random.randint(0, self.height - self.sq_side)

        self.snake_length = 50
        self.length_increment = 90

        self.snake_segments = []
        self.border_points = []
        self.head = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.tail = pygame.Vector2(self.head.x - self.snake_length, self.head.y)
        self.snake_segments.append(self.tail)
        self.snake_segments.append(self.head)
        self.thickness = 10
        self.food_size = 4 * self.thickness
        self.score_font = pygame.font.SysFont("monospace", 16)
        self.score = 0
        self.best_score = 0

    def reset(self):
        self.direction = None
        self.food_x = random.randint(0, self.width - self.sq_side)
        self.food_y = random.randint(0, self.height - self.sq_side)
        self.snake_length = 50
        self.snake_segments = []
        self.border_points = []
        self.head = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.tail = pygame.Vector2(self.head.x - self.snake_length, self.head.y)
        self.snake_segments.append(self.tail)
        self.snake_segments.append(self.head)
        if self.score > self.best_score:
            self.best_score = self.score
        self.score = 0

    def quit_on_x(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def length_correction(self, length):
        difference = length - self.snake_length
        self.move_tail(difference)

    def intersects(self, head_start, head_end, other_start, other_end):
        first_segment_horizontal = head_start.y == head_end.y
        second_segment_horizontal = other_start.y == other_end.y
        if first_segment_horizontal and second_segment_horizontal:
            if self.snake_length >= self.width and abs(head_start.y - other_start.y) <= self.thickness / 2:
                if other_start.x <= head_end.x <= other_end.x or other_end.x <= head_end.x <= other_start.x:
                    # Head-tail collision
                    return True
            return False
        if not first_segment_horizontal and not second_segment_horizontal:
            if self.snake_length >= self.height and abs(head_start.x - other_start.x) <= self.thickness / 2:
                if other_start.y <= head_end.y <= other_end.y or other_end.y <= head_end.y <= other_start.y:
                    # Head-tail collision
                    return True
            return False
        if min(other_start.y, other_end.y) > max(head_start.y, head_end.y) - 1:
            # Second segment lies above first
            return False
        if max(other_start.y, other_end.y) < min(head_start.y, head_end.y) + 1:
            # Second segment lies beneath first
            return False
        if min(other_start.x, other_end.x) > max(head_start.x, head_end.x) - 1:
            # Second segment lies right of first
            return False
        if max(other_start.x, other_end.x) < min(head_start.x, head_end.x) + 1:
            # Second segment lies left of first
            return False
        return True

    def draw_snake(self):
        if len(self.border_points) > 0 and self.snake_segments[0] == self.border_points[0]:
            border_point_to_remove = self.border_points[0]
            self.border_points.pop(0)
            self.snake_segments[:] = [x for x in self.snake_segments if x != border_point_to_remove]
        segments_count = len(self.snake_segments)

        last_segment_start = self.snake_segments[-2]
        last_segment_end = self.snake_segments[-1]

        index = 0
        length = 0
        while index < segments_count - 1:
            segment_start = self.snake_segments[index]
            if segment_start in self.border_points:
                index += 1
                continue
            segment_end = self.snake_segments[index + 1]
            pygame.draw.line(self.screen, 'yellow', segment_start, segment_end, self.thickness)
            if index < segments_count - 2 and self.intersects(last_segment_start, last_segment_end, segment_start, segment_end):
                return False
            length += pygame.math.Vector2(segment_start).distance_to(segment_end)
            index += 1
        self.length_correction(length)
        return True

    def tail_passes_corner(self, target):
        self.snake_segments[0] = target
        self.snake_segments.pop(1)

    def move_tail(self, diff):
        tail = self.snake_segments[0]
        target = self.snake_segments[1]
        if tail.x == target.x:
            if target.y > tail.y:
                tail.y += diff
                if target.y <= tail.y:
                    self.tail_passes_corner(target)
            else:
                tail.y -= diff
                if target.y >= tail.y:
                    self.tail_passes_corner(target)
        else:
            if target.x > tail.x:
                tail.x += diff
                if target.x <= tail.x:
                    self.tail_passes_corner(target)
            else:
                tail.x -= diff
                if target.x >= tail.x:
                    self.tail_passes_corner(target)

    def pass_border_set_segments(self, crossing_point, new_start):
        new_head = pygame.Vector2(new_start)
        self.snake_segments[-1] = pygame.Vector2(crossing_point)
        self.snake_segments.append(new_start)
        self.snake_segments.append(new_head)

    def pass_border_right(self, head):
        crossing_point = pygame.Vector2(self.width, head.y)
        self.border_points.append(crossing_point)
        new_start = pygame.Vector2(0, head.y)
        self.pass_border_set_segments(crossing_point, new_start)

    def pass_border_left(self, head):
        crossing_point = pygame.Vector2(0, head.y)
        self.border_points.append(crossing_point)
        new_start = pygame.Vector2(self.width, head.y)
        self.pass_border_set_segments(crossing_point, new_start)

    def pass_border_bottom(self, head):
        crossing_point = pygame.Vector2(head.x, 0)
        self.border_points.append(crossing_point)
        new_start = pygame.Vector2(head.x, self.height)
        self.pass_border_set_segments(crossing_point, new_start)

    def pass_border_top(self, head):
        crossing_point = pygame.Vector2(head.x, self.height)
        self.border_points.append(crossing_point)
        new_start = pygame.Vector2(head.x, 0)
        self.pass_border_set_segments(crossing_point, new_start)

    def move(self, diff):
        head = self.snake_segments[-1]
        if self.direction == 'up':
            head.y -= diff
            if head.y < 0:
                self.pass_border_bottom(head)
        if self.direction == 'down':
            head.y += diff
            if head.y > self.height:
                self.pass_border_top(head)
        if self.direction == 'left':
            head.x -= diff
            if head.x < 0:
                self.pass_border_left(head)
        if self.direction == 'right':
            head.x += diff
            if head.x > self.width:
                self.pass_border_right(head)
        self.move_tail(diff)

    def handle_changed_direction(self):
        copy_of_head = pygame.Vector2(self.snake_segments[-1])
        self.snake_segments.append(copy_of_head)

    def get_changed_direction(self, k):
        if k[pygame.K_w]:
            if self.direction != 'down':
                return 'up'
        if k[pygame.K_s]:
            if self.direction != 'up':
                return 'down'
        if k[pygame.K_a]:
            if self.direction != 'right':
                return 'left'
        if k[pygame.K_d]:
            if self.direction != 'left':
                return 'right'
        return self.direction

    def draw_food(self):
        pygame.draw.rect(self.screen, "red", [self.food_x, self.food_y, self.food_size, self.food_size])

    def hits_food(self):
        head = self.snake_segments[-1]
        return (self.food_x <= head.x <= self.food_x + self.food_size) and (self.food_y <= head.y <= self.food_y + self.food_size)

    def increment_length(self):
        self.move_tail(-self.length_increment)

    def run(self):
        while self.running:
            self.running = self.quit_on_x()

            difference = self.speed * self.dt
            self.screen.fill("black")

            if not self.draw_snake():
                game.reset()
            self.draw_food()
            if self.best_score > 0:
                score_text = self.score_font.render("Score = " + str(self.score) + ", best = " + str(self.best_score), 0, 'green')
            else:
                score_text = self.score_font.render("Score = " + str(self.score), 0, 'green')
            self.screen.blit(score_text, (self.width / 2 - 60, self.height - 20))
            if self.hits_food():
                self.score += 1
                self.increment_length()
                self.snake_length += self.length_increment
                self.food_x = random.randint(0, self.width - self.sq_side)
                self.food_y = random.randint(0, self.height - self.sq_side)

            keys = pygame.key.get_pressed()
            new_direction = self.get_changed_direction(keys)
            if new_direction != self.direction:
                self.handle_changed_direction()
                self.direction = new_direction

            if self.direction:
                self.move(difference)

            pygame.display.flip()
            self.dt = self.clock.tick(60) / 1000
    pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.init()
    game.run()
