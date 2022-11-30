import mesa
import numpy as np

def get_grid(model):
    grid = np.zeros((model.grid.width, model.grid.height))

    for cell in model.grid.coord_inter():
        cell_content, x, y = cell

        for content in cell_content:
            pass

class CleaningAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.moves = 0

    def step(self):
        if self.model.is_clean(self.pos):
            self.move()
            return

        self.clean()

    def move(self):
        possible_moves = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_moves)
        self.model.grid.move_agent(self, new_position)
        self.moves += 1

    def clean(self):
        self.model.clean_cell(self.pos)

class Tile(mesa.Agent):
    DIRTY = 1
    CLEAN = 0

    def __init__(self, pos, model, state = CLEAN):
        super().__init__(pos, model)
        self.x, self.y = pos
        self.state = state
        self.next_state = None

class CleaningModel(mesa.Model):
    def __init__(self, num_agents, width, height, percentage):
        #Variables to initialize our MESA Model
        self.num_agents = num_agents
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)

        #Variables to keep track of clean and dirty cells
        self.dirty_cells = int((width * height) * percentage)
        self.clean_cells = (width * height) - self.dirty_cells
        #Auxiliary grid to keep track of clean and dirty cells
        self.clean_grid = [[True for j in range(width)] for i in range(height)]

        #We make random cells 'dirty' according to the percentage given
        dirty = 0
        while dirty < self.dirty_cells:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)

            #If the selected cell is clean, we make it dirty
            if self.clean_grid[x][y]:
                self.clean_grid[x][y] = False
                dirty += 1

        #We add the agents to our scheduler
        for i in range(num_agents):
            agent = CleaningAgent(i, self)
            self.schedule.add(agent)
            self.grid.place_agent(agent, (1, 1))

        self.datacollector = mesa.DataCollector(
            model_reporters={"CleanP": self.get_clean_percentage},
            agent_reporters={"Moves", "moves"}
        )

    #Function to step our model
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
    
    #Function to 'clean' a cell, given its position
    def clean_cell(self, pos):
        self.clean_grid[pos[0]][pos[1]] = True
        self.clean_cells += 1
        self.dirty_cells -= 1

    #Function to show grid in a table format
    def show_grid(self):
        for i in self.clean_grid:
            print(i)
    
    #Function to generate and show the positions of the agents within the grid
    def show_agents(self):
        agents_positions = [['-' for j in range(self.grid.width)] for i in range(self.grid.height)]

        for agent in self.schedule.agents:
            agents_positions[agent.pos[0]][agent.pos[1]] = agent.unique_id

        for i in agents_positions:
            print(i)

    #Function to show how many 'clean' and 'dirty' cells are left
    def show_status(self):
        print("Clean cells: {}\nDirty cells: {}".format(self.clean_cells, self.dirty_cells))

    def get_clean_percentage(self):
        return self.clean_cells / (self.grid.width * self.grid.height)

    #Funtion to sum the move count of all the agents
    def get_total_moves(self):
        total_moves = 0

        for agent in self.schedule.agents:
            total_moves += agent.moves

        return total_moves

    def is_grid_clean(self):
        return self.dirty_cells == 0

    def is_clean(self, pos):
        return self.clean_grid[pos[0]][pos[1]]
