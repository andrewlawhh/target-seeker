'''
Script that uses genetic algorithm to find a path to a target
Heavily Inspired by @CodeBullet on Youtube

Python port + some changes in architecture
'''

# Set window dimensions
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 800

################################################################################

# Target class that wraps position
# Attributes : float x, float y
class Target:
    # Takes in an X and Y coordinate
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # Shows a circle to the screen where the goal is.
    def show(self):
        fill(0, 255, 255)
        ellipse(self.x, self.y, 10, 10)

# Initialize a goal object 
GOAL = Target(DISPLAY_WIDTH//2, 30)


####################################################################################################################

# Obstacle Class
# Attributes : int x, int y , int width, int height
class Obstacle:
    
    # Constructor
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.obst_width = w
        self.obst_height = h
    
    # Show obstacle instance
    def show(self):
        fill(255, 0, 0)
        rect(self.x, self.y, self.obst_width, self.obst_height) 

# List of obstacles
obstacle_list = []

# Initialize obstacles
o1 = Obstacle(100, 300, DISPLAY_WIDTH * 0.75, 30)
obstacle_list.append(o1)

# Method that shows all obstacles
def show_obstacles():
    for obstacle in obstacle_list:
        obstacle.show()
    
##########################################################

# AI Class
# Attributes: int size, boolean randomize (default = True)
class AI:
    def __init__(self, size, randomize = True):
        self.step = 0
        self.size = size
        self.directions = []
        
        # Fill the directions with RANDOM vectors
        def fillDirections():
            for i in range(self.size):
                self.directions.append(PVector.fromAngle(random(2*PI)))
        
        if randomize:
            fillDirections()
    
    # Clone directions into a new instance of AI
    def clone(self):
        new_ai = AI(len(self.directions), randomize = False)
        for direction in self.directions:
            new_ai.directions.append(PVector(direction.x, direction.y))
        return new_ai
##########################################################

# Unit class
# attributes : PVector pos, PVector vel, PVector acc, AI ai, boolean live, boolean reached_goal, boolean is_best
class Unit:
            
    # Constructor
    def __init__(self, is_best = False):
        self.pos = PVector(DISPLAY_WIDTH//2, DISPLAY_HEIGHT * 7.0/8.0)
        self.vel = PVector(0, 0)
        self.acc = PVector(0, 0)
        self.ai = AI(500)
        self.live = True 
        self.reached_goal = False
        self.is_best = is_best 
           
    # Show unit
    # params : self
    # return : None      
    def show(self):
        # Set unit color to black
        if not self.is_best:
            fill(0)
        # But if it is the best unit of the previous generation, set it to purple
        else:
            fill(255, 0, 255)
        # Draw an ellipse at the unit's position 
        ellipse(self.pos.x, self.pos.y, 4, 4)
        # Show the fitness of the unit
        # text(str(self.fitness()), self.pos.x, self.pos.y)
            
    # Move unit method
    # params : self
    # return : None
    def move(self):
        # Limit the unit's velocity
        self.vel.limit(5)
        # If the unit has directions left . . . 
        if self.ai.step < len(self.ai.directions):
            # set acceleration based on what's next in the AI object
            self.acc = self.ai.directions[self.ai.step]
            # increment AI step
            self.ai.step += 1
        # Else, the unit dies
        else:
            self.live = False
        # Update velocity and position vectors
        self.vel.add(self.acc)
        self.pos.add(self.vel)
   
    # Update unit method
    # params : self
    # return : None
    def update(self):
        # Update the unit's status if it is alive and hasn't reached the goal
        if self.live and not self.reached_goal:
            self.move()
            # If the unit touches the edge, it dies
            if  DISPLAY_WIDTH <= self.pos.x or self.pos.x <= 5 or self.pos.y <= 5 or DISPLAY_HEIGHT <= self.pos.y:
                self.live = False
            # If the unit touches the goal, it has reached_goal; set reached_goal to true
            elif dist(self.pos.x, self.pos.y, GOAL.x, GOAL.y) <= 10:
                self.reached_goal = True
            # If the unit touches an obstacle, it dies
            for obstacle in obstacle_list:
                if self.pos.x >= obstacle.x and self.pos.x <= obstacle.x + obstacle.obst_width and self.pos.y >= obstacle.y and self.pos.y <= obstacle.y + obstacle.obst_height:
                    self.live = False
                     
    # Return float fitness of the unit at current state 
    # params : self
    # return : float fitness
    def fitness(self):
        # Inverse square function for steps to goal
        if self.reached_goal:
            fitness = 1.0 / 16.0 + 1000.0 / (self.ai.step ** 2)
        # Inverse square function for distance to goal
        else:
            dist_to_goal = dist(self.pos.x, self.pos.y, GOAL.x, GOAL.y)
            fitness = 1.0 / float(dist_to_goal ** 2)
        return fitness
                    
    # Return an offspring of type Unit
    # params : self
    # return : Unit offspring
    def get_offspring(self):
        offspring = Unit()
        offspring.ai = self.ai.clone()
        return offspring
        
    # Mutate this unit instance's AI
    # params : self
    # return : None
    def mutate(self):
        # Set rate of mutation
        mutation_rate = 0.1
        # For each index in the list of directions of this unit's AI . . .
        for i in range(len(self.ai.directions)):
            # Get a random float from 0 to 1
            rand = random(1)
            # If it is less than the mutation_rate
            if rand < mutation_rate:
                # Reset the direction at the given index
                self.ai.directions[i] = PVector.fromAngle(random(2*PI))
                
        # FOLLOWING CODE FAILED BECAUSE DIRECTION DOES NOT DIRECTLY REFERENCE THE AI! CHANGING DIRECTION DID NOT CHANGE THE AI
        # for direction in self.ai.directions:
        #     rand = random(1)
        #     if rand < mutation_rate:
        #         direction = PVector.fromAngle(random(2*PI))
            #direction = PVector.fromAngle(random(2*PI))      
    
    # DEBUGGING METHOD
    def control_mutate(self):
        # Should completely change all directions
        self.ai = AI(500)
        
################################################################

# Population Class : Contains all the projectiles (population) 
# attributes : population, size, generation
class Population:

    '''
    CONSTRUCTOR
    params: size of population
    '''
    def __init__(self, size):
        self.population = []
        self.size = size
        self.generation = 0
        self.max_steps = 1000
        
        # Populate the list of units
        def populate_population():
            for i in range(self.size):
                self.population.append(Unit())
        populate_population()
        
    # Update all units in the population
    def update(self):
        for unit in self.population:
            # If the unit's step is greater than the max steps allowed, kill it
            if unit.ai.step > self.max_steps:
                unit.live = False
            # else, update it
            unit.update()
    
    # Show all units in the population
    def show(self):
        for unit in self.population:
            unit.show()
        
    # Returns boolean value based on whether all units have been terminated
    def finished(self):
        for unit in self.population:
            if unit.live and not unit.reached_goal:
                return False
        return True
    
    '''
    NATURAL SELECTION FUNCTION
    Upon extinction of a generation, repopulate the next 
    generation based on the fitnesses of the one that just died
    
    For each index in the population list *
    1. select a parent based on fitness
    2. get an offspring from that parent that is a new instance but has the same AI
    
    * - We should keep the best performing unit, so find it and put it at index 0
    '''
    def natural_selection(self):
        # Initialize new population list
        new_population = []  
        
        # List comprehension that puts the unit's fitness instead of the unit instance at each index        
        fitnesses = [unit.fitness() for unit in self.population]
        
        # Sum of the fitnesses
        fitnessSum = sum(fitnesses)
        
        # Get best performing Unit
        best_index = fitnesses.index(max(fitnesses))
        best_unit = self.population[best_index]
        # Get the maximum step allowed by setting it to the steps that the best unit took
        if best_unit.reached_goal:
            self.max_steps = best_unit.ai.step
        
        # Returns a unit based on fitness
        def selectParent():
            # This approach caches fitnesses so we only need to calculate it once!
            rando = random(fitnessSum)
            running_sum = 0
            index = 0
            for fitness in fitnesses:
                running_sum += fitness
                if running_sum > rando:
                    return self.population[index]
                index += 1
            
        # Use the best unit as the first parent!
        new_population.append(best_unit.get_offspring())
        new_population[0].is_best = True
        
        for _ in range(self.size - 1):
            parent = selectParent()
            offspring = parent.get_offspring()
            new_population.append(offspring)
        
        # self.population = new_population
        for i in range(len(self.population)):
            self.population[i] = new_population[i]
        self.generation += 1
                
    '''
    MUTATE POPULATION FUNCTION
    Mutate the AI of the population, except for the best unit
    '''
    def mutate_population(self):
        for thing in self.population[1:]:
            thing.mutate()
    
    # DEBUGGING FUNCTION
    def control_mutate_population(self):
        for thing in self.population:
            thing.control_mutate()
    
    # Returns the number of successful units ie. units that reached the goal
    def num_successful(self):
        return sum(map(lambda x : x.reached_goal, self.population))
    
    # Print metrics of the generation upon its extinction
    def print_metrics(self):
        print('Generation : ' + str(p.generation))
        print('Success Rate : ' + str(p.num_successful()) + '/' + str(p.size))
        print('--------------------------------')
        
# Initialize the population
p = Population(1000)

# Setup the window, load data
def setup():
    # Load the unit image
    # global unit_img
    # unit_img = loadImage("unit2.jpg")
    size(DISPLAY_WIDTH, DISPLAY_HEIGHT)

def draw():
    background(255)
    if p.finished():
        p.print_metrics()
        p.natural_selection()
        p.mutate_population()
    else:
        p.update()
        p.show()
        GOAL.show()
        show_obstacles()
