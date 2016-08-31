import random
import numpy as np
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.actions = Environment.valid_actions
        self.randomness = 0.4
        self.randomness_decrease = self.randomness/100
        self.learning_rate = 0.4
        self.learning_rate_decrease = self.learning_rate/100
        self.state = None
        self.Q = {}
        self.Q_init = 5
        self.total_reward = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.randomness = max(self.randomness - self.randomness_decrease, 0)
        self.learning_rate = max(self.learning_rate - self.learning_rate_decrease, 0)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Update state
        self.state = (inputs['light'], inputs['oncoming'], inputs['left'], self.next_waypoint)

        # Make variables easier to refer to
        actions = self.actions
        Q = self.Q
        state = self.state
        learning_rate = self.learning_rate

        # Initialize Q-values as they come up
        for action in actions:
            if (state, action) not in Q:
                Q[state, action] = self.Q_init

        # Create array of relative weights of rewards for actions taken
        action_weights = np.array( [float(max(Q[state, action], 0)) for action in actions] )
        action_weights /= action_weights.sum().astype(float)

        if random.random() < self.randomness:
            action = np.random.choice(actions, p = action_weights)
            # action = random.choice(actions)
        else:    
            action = actions[np.argmax(action_weights)]

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.total_reward += reward

        # Learn policy based on state, action, reward
        Q[(state, action)] = Q[state, action]*(1 - learning_rate) + reward*learning_rate

        #print("deadline = {}, inputs = {}, action = {}, reward = {}, total_reward = {}".format(deadline, inputs, action, reward, self.total_reward))  # [debug]

    def get_state(self):
        return self.state


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0, display=False)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    print(a.total_reward)


if __name__ == '__main__':
    run()