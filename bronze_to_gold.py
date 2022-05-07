import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

values = {
    'h' : 3,
    'k' : 2,
    'checkpoint_radius' : 600,
    'braking_distance' : 2000,
    'BOOST_angle' : 15,
    'drifting_min_speed' : 100
}

class Geometrics() : 

    @staticmethod
    def distance_checkpoints(checkpoint_A, checkpoint_B): 
        xA, yA = checkpoint_A[0], checkpoint_A[1]
        xB, yB = checkpoint_B[0], checkpoint_B[1]
        return math.sqrt((xA - xB)*(xA - xB) + (yA - yB)*(yA - yB))

    @staticmethod
    def vector_length(vector): 
        return math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])
        
class Pod():

    def __init__(self):
        self.vector_speed = [0 , 0]
        self.speed = 0
        self.position = { 'x' : 0, 'y' : 0 }
        self.angle = 0
        self.distance_next_checkpoint = 0
        self.current_checkpoint = None
        self.current_lap = 1
        self.boost_used = False
        self.next_checkpoint = [0,0]
    
    def update_angle(self, angle):
        self.angle = angle
    
    def update_position(self, x, y):
        self.position = { 'x' : x, 'y' : y }

    def update_vector_speed(self, x, y):
        if self.current_checkpoint:
            self.vector_speed = [x - self.position['x'],y - self.position['y']]

    def update_distance_next_checkpoint(self, dist):
        self.distance_next_checkpoint = dist

    def update_current_checkpoint(self, checkpoint):
        if checkpoint != self.current_checkpoint : 
            self.current_checkpoint = checkpoint
    
    def update_current_lap(self, isNewLap):
        if isNewLap: 
            self.current_lap += 1 

    
    def update_speed(self):
        self.speed = math.sqrt(self.vector_speed[0] * self.vector_speed[0] + self.vector_speed[1] * self.vector_speed[1])

    def update_pod(self, x, y, angle, checkpoint, dist):
        self.update_angle(angle)
        self.update_vector_speed(x, y)
        self.update_position(x, y)
        self.update_speed()
        self.update_current_checkpoint(checkpoint)
        self.update_distance_next_checkpoint(dist)

class Checkpoint():

    radius = 600

    def __init__(self, x, y):
        self.x = x 
        self.y = y 

class Game():

    def __init__(self):
        self.list_checkpoints = []
        self.list_checkpoints_completed = False
        self.amount_checkpoints = 0
        self.optimal_boost_checkpoint = None
    
    def isCheckpointInList(self, checkpoint):
        if [checkpoint.x, checkpoint.y] in self.list_checkpoints:
            return True
        else: return False
    
    def update_checkpoints_list(self, Pod, checkpoint) : 
        if Pod.current_checkpoint: 
            if not self.isCheckpointInList(checkpoint) and checkpoint.x != Pod.current_checkpoint.x and checkpoint.y != Pod.current_checkpoint.y:
                self.list_checkpoints.append([checkpoint.x, checkpoint.y])
                self.amount_checkpoints += 1
            elif checkpoint and self.isCheckpointInList(checkpoint) and checkpoint.x != Pod.current_checkpoint.x and checkpoint.y != Pod.current_checkpoint.y:
                self.list_checkpoints_completed = True
        else: 
            self.list_checkpoints.append([checkpoint.x, checkpoint.y])
            self.amount_checkpoints += 1

    def set_optimal_boost_checkpoint(self):
        distances = [Geometrics.distance_checkpoints(self.list_checkpoints[i], self.list_checkpoints[(i+1)%self.amount_checkpoints]) for i in range(self.amount_checkpoints)]
        self.optimal_boost_checkpoint = self.list_checkpoints[(distances.index(max(distances)) + 1)%self.amount_checkpoints]
    
    def isNewLap(self, Pod, checkpoint):
        if self.list_checkpoints_completed and self.list_checkpoints.index([Pod.current_checkpoint.x, Pod.current_checkpoint.y]) == 0 and checkpoint.x != Pod.current_checkpoint.x and checkpoint.y != Pod.current_checkpoint.y:
            return True
        else : return False

class Planner():

    def __init__(self):
        self.info = Game()
        self.Pod = Pod()

    def calculate_thrust(self):
        thrust = 100
        if abs(self.Pod.angle) < values['BOOST_angle'] and self.info.optimal_boost_checkpoint == [self.Pod.current_checkpoint.x, self.Pod.current_checkpoint.y]:
            thrust = 'BOOST'
            return thrust
        else : 
            if abs(self.Pod.angle) < 90:
                thrust *= (1 - abs(self.Pod.angle) / 90 )
            if self.Pod.distance_next_checkpoint < values['k']*values['checkpoint_radius'] :
                braking_factor = self.Pod.distance_next_checkpoint / (values['k']*values['checkpoint_radius'])
                print("braking factor : " + str(braking_factor), file=sys.stderr, flush=True)
                thrust *= braking_factor
            return str(int(thrust))
    
    def turn(self):
        thrust = self.calculate_thrust()
        if self.Pod.speed > values['drifting_min_speed']:
            next_x = self.Pod.current_checkpoint.x - values['h'] * self.Pod.vector_speed[0]
            next_y = self.Pod.current_checkpoint.y - values['h'] * self.Pod.vector_speed[1]
        else : 
            next_x = self.Pod.current_checkpoint.x
            next_y = self.Pod.current_checkpoint.y
        print(str(int(next_x)) + ' ' + str(int(next_y)) + ' ' + thrust)



Agent = Planner()


# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    checkpoint = Checkpoint(next_checkpoint_x, next_checkpoint_y)

    Agent.info.update_checkpoints_list(Agent.Pod, checkpoint)

    if Agent.info.isNewLap(Agent.Pod, checkpoint) and Agent.Pod.current_lap == 1:
        Agent.info.set_optimal_boost_checkpoint()

    Agent.Pod.update_current_lap(Agent.info.isNewLap(Agent.Pod, checkpoint))

    print('current-lap : ' + str(Agent.Pod.current_lap) , file=sys.stderr, flush=True)


    Agent.Pod.update_pod(x, y, next_checkpoint_angle, checkpoint, next_checkpoint_dist)

    
    print('Vecteur Vitesse : ' + str(Agent.Pod.vector_speed) , file=sys.stderr, flush=True)
    print('Vitesse : ' + str(Agent.Pod.speed) , file=sys.stderr, flush=True)
    print('x = ' + str(Agent.Pod.current_checkpoint.x) + ' y = '+ str(Agent.Pod.current_checkpoint.y), file=sys.stderr, flush=True)
    Agent.turn()

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    ## -------------------------------------------------------------------------------

    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"
