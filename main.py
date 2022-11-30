import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tile_cleaning_model import CleaningModel

#Inicializamos el modelo
model = CleaningModel(10, 100, 100, 0.1)
max_exec_time = 0.5

#Realizamos la simulacion mientras no se limpie por completo el espacio o se acabe el tiempo
init_time = time.time()
while not model.is_grid_clean() and time.time() - init_time < max_exec_time:
    model.step()
end_time = time.time()
execution_time = end_time - init_time

print("Execution time: {}".format(execution_time))
print("Clean percentage: {}".format(model.clean_percentage))

#Obtenemos la informacion generada por el modelo
data = model.datacollector.get_model_vars_dataframe()

#Graficamos la informacion y generamos una animacion de su evolucion
figure, axis = plt.subplots(figsize=(7,7))
axis.set_xticks([])
axis.set_yticks([])
patch = plt.imshow(data.iloc[0][0], cmap='Greys')

def animate(i):
    patch.set_data(data.iloc[i][0])

anim = animation.FuncAnimation(figure, animate, frames=len(data))
plt.show()
