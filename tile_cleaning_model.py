import mesa
import numpy as np

#Funcion para generar una matriz indicando el estado de cada casilla, y si se
#encuentra un agente en ella
def get_grid(model):
    grid = np.zeros((model.grid.width, model.grid.height))

    for cell in model.grid.coord_iter():
        cell_content, x, y = cell

        for content in cell_content:
            #Si encontramos un agente en la casilla
            if isinstance(content, CleaningAgent):
                grid[x][y] = 2
            #Si es una casilla, mostramos su estado (limpia/sucia)
            else:
                grid[x][y] = content.state

    return grid

#Agente de limpieza
class CleaningAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.new_position = None #Variable para guardar el siguiente movimiento del agente
        self.moves = 0

    def step(self):
        #Obtenemos los vecinos del agente, incluyendo la casilla actual
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=True
        )

        for neighbor in neighbors:
            #Si los vecinos son una casilla de 'piso' y el agente se encuentra sobre ella
            if isinstance(neighbor, Tile) and neighbor.pos == self.pos:
                #Evaluamos el estado actual de esa casilla
                neighbor.next_state = neighbor.state
                
                #Limpiamos la casilla, de ser necesario y dejamos al agente en la misma casilla
                if neighbor.next_state == neighbor.DIRTY:
                    neighbor.next_state = neighbor.CLEAN
                    self.new_position = self.pos
                #Si no es necesario limpiar, movemos a nuestro agente
                else:
                    self.move()
                break

    #Funcion para asignar una nueva posicion aleatoria para el agente
    def move(self):
        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(neighborhood)
        self.new_position = new_position

    #Funcion de MESA para actualizar los datos despues del step
    def advance(self):
        #Obtenemos los vecinos
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=False,
            include_center=True
        )

        #Actualizamos el valor de la casilla que el agente limpio
        for neighbor in neighbors:
            if isinstance(neighbor, Tile) and neighbor.pos == self.pos:
                neighbor.state = neighbor.next_state
                break

        #Si se asigno una nueva posision diferente, agregamos a la variable de moviemientos
        if self.pos != self.new_position:
            self.moves += 1

        #Movemos el agente a la nueva posicion asignada
        self.model.grid.move_agent(self, self.new_position)

#Agente auxiliar para representar el estado de una casilla
class Tile(mesa.Agent):
    #Constantes para determinar el estado de la casilla
    DIRTY = 1
    CLEAN = 0

    #Definimos su posicion, estado, y estado siguiente
    def __init__(self, pos, model, state=CLEAN):
        super().__init__(pos, model)
        self.x, self.y = pos
        self.state = state
        self.next_state = None

#Modelo
class CleaningModel(mesa.Model):
    def __init__(self, num_agents, width, height, percentage):
        #Variables para incializar nuestro modelo MESA
        self.num_agents = num_agents
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.SimultaneousActivation(self)
        #Porcentajes de casillas sucias y limpias
        self.dirty_percentage = percentage
        self.clean_percentage = 1 - percentage

        #Asignamos casillas sucias de manera aleatoria en casillas vacias
        dirty_cells = int((width * height) * percentage)
        empty_cells = list(self.grid.empties)
        for cell in range(dirty_cells):
            empty_cell = self.random.choice(empty_cells)
            tile = Tile(empty_cell, self)
            tile.state = tile.DIRTY
            self.grid.place_agent(tile, empty_cell)
            self.schedule.add(tile)
            empty_cells.remove(empty_cell)

        #Asignamos el resto de casillas como limpias
        empty_cells = list(self.grid.empties)
        for cell in empty_cells:
            tile = Tile(cell, self)
            self.grid.place_agent(tile, cell)
            self.schedule.add(tile)

        #Agregamos los agentes a nuestro espacio
        for i in range(num_agents):
            cleaning_agent = CleaningAgent(i, self)
            self.grid.place_agent(cleaning_agent, (1, 1))
            self.schedule.add(cleaning_agent)

        #Definimos un datacollector para guardar la informacion de nuestro modelo
        self.datacollector = mesa.DataCollector(
            model_reporters={'Grid' : get_grid},
            agent_reporters={'Moves' : lambda a: getattr(a, 'moves', None)}
        )

    #Funcion para que nuestro modelo avance
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        
    #Funcion para evaluar si se ha limpiado el espacio por completo
    def is_grid_clean(self):
        clean_cells = 0

        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            
            for content in cell_content:
                if isinstance(content, Tile) and content.state == content.CLEAN:
                    clean_cells += 1

        #Actualizamos el porcentaje de casillas limpias
        self.clean_percentage = clean_cells / (self.grid.width * self.grid.height)

        #Si se tiene un 100% de casillas limpias
        if self.clean_percentage == 1:
            return True
        
        return False
