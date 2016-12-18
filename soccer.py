import copy
import numpy as np

# Set a random seed if same results need to be replicated
# np.random.seed(10)


class Player:

    def __init__(self, x, y, has_ball, p_id=None):
        self.p_id = p_id
        self.x = x
        self.y = y
        self.has_ball = has_ball

    def update_state(self, x, y, has_ball):
        self.x = x
        self.y = y
        self.has_ball = has_ball

    def update_x(self, x):
        self.x = x

    def update_y(self, y):
        self.y = y

    def update_ball_pos(self, has_ball):
        self.has_ball = has_ball


class World:
    """ Soccer environment simulator class. """

    def __init__(self):
        """ Method that initializes the World class with class variables to be used in the class methods. """

        self.cols = None
        self.rows = None
        self.goal_r = {}
        self.players = {}
        self.goals = {}
        self.grid = []
        self.actions = ['N', 'S', 'E', 'W', 'ST']
        self.commentator = False

    def init_grid(self):
        """ Initializes grid for plotting.

        Returns
        -------
            list: List of strings with the data to plot.

        """

        grid = [['**'] * (self.cols + 2)]

        for i in xrange(self.rows):
            grid.append(['**', 'gA'] + ['  '] * (self.cols - 2) + ['gB', '**'])

        grid.append(['**'] * (self.cols + 2))

        return grid

    def set_commentator_on(self):
        self.commentator = True

    def set_world_size(self, x, y):
        self.cols = x
        self.rows = y

    def set_goals(self, goal_r, goal_col, player_id):
        """ Method that sets the goal configurations.

        Args:
            goal_r (int): Reward value assigned in the event of a goal.
            goal_col (int): Column representing the goal area.
            player_id (str): Player id that will receive this reward.

        """
        self.goal_r[player_id] = goal_r
        self.goals[player_id] = goal_col

    def place_player(self, player, player_id):
        self.players[player_id] = copy.copy(player)

    def get_state_id(self, player):
        return str(player.y * self.cols + player.x)

    def map_player_state(self):
        """ Method that maps the players current state to the key used in a Q table.

        Returns
        -------
            str: Q table dict key that shows the current world state.

        """

        player_a = self.players['A']
        player_b = self.players['B']

        key = player_a.p_id if player_a.has_ball else player_b.p_id

        key += self.get_state_id(player_a)
        key += self.get_state_id(player_b)

        return key

    def get_players_states(self):
        return [self.players[p] for p in self.players]

    def plot_grid(self):
        """ Method that prints the current world state. """

        self.grid = self.init_grid()

        if len(self.players.keys()) > 0:

            for p_id in self.players:
                player = self.players[p_id]

                if player.has_ball:
                    cell = p_id + '+'

                else:
                    cell = p_id + ' '

                self.grid[player.y + 1][player.x + 1] = cell

        for r in self.grid:
            print ' | '.join(r)

        print ''

    def check_collision(self, new_pos, moving_player, other_players):
        """ Method that verifies if there is a collision between two players.

        Parameters
        ----------
            new_pos (Player): Player class instance that represents the new active player's position.
            moving_player (Player): Player class instance of the player that is moving.
            other_players (list): List of player class instances representing the other players in the game.

        Returns
        -------
            bool: True if a collision occurred, False otherwise.

        """

        collision = False

        for op_id in other_players:
            other_p = self.players[op_id]

            if new_pos.x == other_p.x and new_pos.y == other_p.y:

                if self.commentator:
                    print '{} collided with {}'.format(moving_player.p_id, other_p.p_id)

                collision = True

                if new_pos.has_ball:
                    other_p.update_ball_pos(True)
                    moving_player.update_ball_pos(False)

                    if self.commentator:
                        print "{} steals from {}".format(other_p.p_id, moving_player.p_id)

        return collision

    def check_goal(self, moving_player, player_order):
        """ Method that verifies if a goal has been scored.

        Parameters
        ----------
            moving_player (Player): Player class instance
            player_order (list): List with the order in which each agent moves

        Returns
        -------
            tuple : 2-element tuple containing
                r (int): reward obtained from scoring a goal
                goal (bool): flag that indicates a goal has been scored

        """

        goal = False
        other_players = set(player_order) - set(moving_player.p_id)
        r = {k: 0 for k in player_order}

        if moving_player.x == self.goals[moving_player.p_id] and moving_player.has_ball:

            if self.commentator:
                print "{} scored a goal!!".format(moving_player.p_id)

            goal = True
            r[moving_player.p_id] = self.goal_r[moving_player.p_id]

            for op_id in other_players:
                r[op_id] = -self.goal_r[moving_player.p_id]

        else:
            other_goal = {op_id: moving_player.x == self.goals[op_id] and moving_player.has_ball
                          for op_id in player_order}

            if sum(other_goal.values()) > 0:

                if self.commentator:
                    print "{} scored an own goal!!".format(moving_player.p_id)

                goal = True

                for k in other_goal.keys():

                    if other_goal[k]:
                        r[k] = self.goal_r[k]

                    else:
                        r[k] = -self.goal_r[k]

        return r, goal

    def move(self, a):
        """ Method that simulates a single step move command.

        Parameters
        ----------
            a (dict): actions for both players identified by the player id

        Returns
        -------
            tuple : Three-element tuple containing
                map_player_state (str): Players state after the move operation
                r (dict): rewards for each player. i.e. {A: r_a, B: r_b}
                goal (bool): flag that shows if a goal has been scored

        """

        r = None
        goal = False

        player_order = a.keys()
        np.random.shuffle(player_order)
        new_pos = Player(0, 0, False)

        for p_id in player_order:
            moving_player = self.players[p_id]
            other_players = set(player_order) - set(p_id)
            new_pos.update_state(moving_player.x, moving_player.y, moving_player.has_ball)
            action = self.actions[a[p_id]]

            if action == 'N' and new_pos.y != 0:
                new_pos.update_y(new_pos.y - 1)

            elif action == 'E' and new_pos.x < self.cols - 1:
                new_pos.update_x(new_pos.x + 1)

            elif action == "W" and new_pos.x > 0:
                new_pos.update_x(new_pos.x - 1)

            elif action == 'S' and new_pos.y != self.rows - 1:
                new_pos.update_y(new_pos.y + 1)

            collision = self.check_collision(new_pos, moving_player, other_players)

            if not collision:
                moving_player.update_state(new_pos.x, new_pos.y, new_pos.has_ball)

            r, goal = self.check_goal(moving_player, player_order)

            if goal:
                break

            r, goal = self.check_goal(self.players[list(other_players)[0]], player_order)

            if goal:
                break

        if self.commentator:
            print 'Player Order: {}'.format(player_order)
            print 'Actions: {}'.format(a)
            print 'A location: ({}, {})'.format(self.players['A'].x, self.players['A'].y)
            print 'B location: ({}, {})'.format(self.players['B'].x, self.players['B'].y)
            print ""

        return self.map_player_state(), r, goal
