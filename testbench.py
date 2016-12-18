from soccer import Player, World


def create_state_comb(p_a_states, p_b_states):
    """ Creates a dictionary that represents the state space possible combinations.

    Args:
        p_a_states (list): List with the numerical state labels for player A
        p_b_states (list): List with the numerical state labels for player B

    Returns:
        dict: Dictionary with the state space representation. Each element is labeled using the
            format [XYZ] where:
                - X: shows who has the ball, either A or B.
                - Y: state where player A is.
                - Z: state where player B is.

            The key values hold a numeric value using the counter id_q.

    """

    states = {}
    ball_pos = ['A', 'B']
    id_q = 0

    for b in ball_pos:

        for p_a in p_a_states:

            for p_b in p_b_states:

                if p_a != p_b:
                    states[b + str(p_a) + str(p_b)] = id_q
                    id_q += 1

    return states


def print_status(goal, new_state, rewards, total_states):
    print ""
    print "Players state label: {}".format(new_state)
    print "Players state in the numerical table: {}".format(total_states[new_state])
    print "Rewards for each player after move: {}".format(rewards)
    print "Goal status: {}".format(goal)
    print "-" * 20 + "\n"


def main():
    rows = 2
    cols = 4
    num_states = rows * cols

    total_states = create_state_comb(range(num_states), range(num_states))

    player_a = Player(x=2, y=0, has_ball=False, p_id='A')
    player_b = Player(x=1, y=0, has_ball=True, p_id='B')

    world = World()
    world.set_world_size(x=cols, y=rows)
    world.place_player(player_a, player_id='A')
    world.place_player(player_b, player_id='B')
    world.set_goals(100, 0, 'A')
    world.set_goals(100, 3, 'B')
    world.set_commentator_on()

    world.plot_grid()

    print "actions: [N: 0, S: 1, E: 2, W: 3, Stay: 4] \n"

    print "Case where the player B scores an own goal:"
    actions = {'A': 1, 'B': 1}
    new_state, rewards, goal = world.move(actions)
    print_status(goal, new_state, rewards, total_states)
    world.plot_grid()

    actions = {'A': 4, 'B': 3}
    new_state, rewards, goal = world.move(actions)
    world.plot_grid()
    print_status(goal, new_state, rewards, total_states)

    print "Case where player B scores while A doesn't move:"
    # After a goal the environment needs to be reset
    world.place_player(player_a, player_id='A')
    world.place_player(player_b, player_id='B')
    actions = {'A': 4, 'B': 1}
    world.move(actions)
    actions = {'A': 4, 'B': 2}
    world.move(actions)
    world.move(actions)
    world.plot_grid()
    print_status(goal, new_state, rewards, total_states)

    print "Case where the two player collide:"
    # After a goal the environment needs to be reset
    world.place_player(player_a, player_id='A')
    world.place_player(player_b, player_id='B')
    actions = {'A': 4, 'B': 2}
    new_state, rewards, goal = world.move(actions)
    world.plot_grid()
    print_status(goal, new_state, rewards, total_states)


if __name__ == '__main__':
    main()
