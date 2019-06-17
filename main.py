import sys
import random
import math
import tkinter
from tkinter import ttk


nodes = None
drawed_nodes = None
distances = None
pheromones = None
alpha = None
beta = None
rho = None
base_pheromone = None
model = None
ant_number = None
cycles_number = None
shortest_path = None
shortest_path_length = None
last_path = None
running = False


def city_to_city_score(city_1_id, city_2_id):
    global pheromones
    global distances
    global alpha
    global beta
    try:
        value = min(max((pheromones[city_1_id][city_2_id] ** alpha) * ((1.0 / distances[city_1_id][city_2_id]) ** beta),
                        sys.float_info.min),
                    sys.float_info.max)
    except OverflowError:
        value = pheromones[city_1_id][city_2_id] / distances[city_1_id][city_2_id]
    return value

def load_file(file_name):
    try:
        global running
        if running:
            return
        global nodes
        global pheromones
        global distances
        global drawed_nodes
        global last_path
        global shortest_path
        global shortest_path_length

        progress_label['text'] = 'Progress:'
        shortest_path_label['text'] = 'Shortest path:'
        shortest_path_value_label['text'] = ''
        last_path = None
        shortest_path = None
        shortest_path_length = None
        file = open("test_files\\" + file_name + ".tsp", "r", encoding="utf8")
        coords_lim = [sys.float_info.max, sys.float_info.max, -sys.float_info.max, -sys.float_info.max]
        nodes = []
        file.readline()
        dimension = int(file.readline().split()[-1])
        for di in range(dimension):
            line = file.readline().split()
            nodes.append((float(line[1]), float(line[2])))
            coords_lim[0] = min(coords_lim[0], float(line[1]))
            coords_lim[1] = min(coords_lim[1], float(line[2]))
            coords_lim[2] = max(coords_lim[2], float(line[1]))
            coords_lim[3] = max(coords_lim[3], float(line[2]))
        file.close()
        distances = [[((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5 for p1 in nodes] for p2 in nodes]
        pheromones = [[1 for p1 in nodes] for p2 in nodes]
        x_diff = coords_lim[2] - coords_lim[0]
        y_diff = coords_lim[3] - coords_lim[1]
        scale = 620 / max(x_diff, y_diff)
        pivot_point = 320 - (x_diff / 2) * scale, 320 - (y_diff / 2) * scale
        drawed_nodes = [(math.floor(pivot_point[0] + (node[0] - coords_lim[0]) * scale),
                         math.floor(pivot_point[1] + (node[1] - coords_lim[1]) * scale))
                        for node in nodes]
        window.update()
        draw()
    except IOError:
        exit()


def draw():
    global last_path
    global shortest_path
    global drawed_nodes
    global running
    draw_board.delete('all')
    if drawed_nodes:
        for node in drawed_nodes:
            draw_board.create_oval(node[0] - 4, node[1] - 4, node[0] + 4, node[1] + 4, fill='yellow')
        if last_path:
            for it in range(len(last_path) - 1, 0, -1):
                n1 = drawed_nodes[last_path[it]]
                n2 = drawed_nodes[last_path[it - 1]]
                draw_board.create_line(n1[0], n1[1], n2[0], n2[1], fill='dark grey', dash=(5, 5))
        if shortest_path:
            for it in range(len(shortest_path) - 1, 0, -1):
                n1 = drawed_nodes[shortest_path[it]]
                n2 = drawed_nodes[shortest_path[it - 1]]
                draw_board.create_line(n1[0], n1[1], n2[0], n2[1], fill='orange', width=2)
    window.update()


def close():
    global running
    running = False
    window.destroy()


def stop():
    global running
    global last_path
    running = False
    last_path = None
    draw()


def start():
    global running
    global nodes
    global distances
    global pheromones
    global base_pheromone
    global alpha
    global beta
    global rho
    global model
    global ant_number
    global cycles_number
    global last_path
    global shortest_path
    global shortest_path_length
    if nodes is None\
            or pheromones is None\
            or distances is None:
        return
    else:
        try:
            alpha = alpha_slider.get()
            beta = beta_slider.get()
            rho = rho_slider.get()
            base_pheromone = int(base_pheromone_entry.get())
            ant_number = int(ant_count_entry.get())
            cycles_number = int(cycles_count_entry.get())
            if base_pheromone == 0 or ant_number == 0 or cycles_number == 0:
                return
            model = cycle_models_box.get()
            shortest_path_length = sys.float_info.max
            distances = [[((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5 for p1 in nodes] for p2 in nodes]
            pheromones = [[random.random()*base_pheromone for p1 in nodes] for p2 in nodes]
        except ValueError:
            return
        running = True

        try:
            ants = []
            for i in range(ant_number):
                ants.append(Ant())
            last_path = None
            shortest_path = None
            shortest_path_length = sys.float_info.max

            best_path_file_out = open("TSP_ACO_wyniki_best.txt", "w")
            best_path_file_out.write("# Alpha: " + str(alpha) + "\n")
            best_path_file_out.write("# Beta: " + str(beta) + "\n")
            best_path_file_out.write("# Rho: " + str(rho) + "\n")
            best_path_file_out.write("# Base pheromone: " + str(base_pheromone) + "\n")
            best_path_file_out.write("# Transition rule: " + model + "\n")
            best_path_file_out.write("# Best path at the time\n")
            best_path_file_out.write("# Cycle\t #Path_length\n")

            best_temp_path_file_out = open("TSP_ACO_wyniki_temp.txt", "w")
            best_temp_path_file_out.write("# Alpha: " + str(alpha) + "\n")
            best_temp_path_file_out.write("# Beta: " + str(beta) + "\n")
            best_temp_path_file_out.write("# Rho: " + str(rho) + "\n")
            best_temp_path_file_out.write("# Base pheromone: " + str(base_pheromone) + "\n")
            best_temp_path_file_out.write("# Transition rule: " + model + "\n")
            best_temp_path_file_out.write("# Best path per iteration\n")
            best_temp_path_file_out.write("# Cycle\t #Path_length\n")
            progress_label['text'] = 'Preparing'
            for cycle_id in range(cycles_number):
                cycle_best_path_length = sys.float_info.max
                if not running:
                    best_path_file_out.close()
                    best_temp_path_file_out.close()
                    return
                draw()
                for ant_id in range(len(ants)):
                    if not running:
                        best_path_file_out.close()
                        best_temp_path_file_out.close()
                        return
                    progress_label['text'] = 'Progress: Cycle ' + str(cycle_id + 1) + '/' + str(cycles_number) \
                                             + '  Ant ' + str(ant_id + 1) + '/' + str(ant_number)
                    shortest_path_value_label['text'] = str(round(shortest_path_length, 8))
                    ants[ant_id].find_path()
                    if shortest_path_length > ants[ant_id].path_length:
                        shortest_path_length = ants[ant_id].path_length
                        shortest_path = ants[ant_id].tabu_list
                    if cycle_best_path_length > ants[ant_id].path_length:
                        cycle_best_path_length = ants[ant_id].path_length
                    if not running:
                        best_path_file_out.close()
                        best_temp_path_file_out.close()
                        return
                    last_path = ants[ant_id].tabu_list
                    draw()
                pheromones = [[(1 - rho) * item for item in row] for row in pheromones]
                for ant_id in range(len(ants)):
                    ants[ant_id].leave_trace()
                best_path_file_out.write(str(cycle_id + 1) + "\t" + str(shortest_path_length) + "\n")
                best_temp_path_file_out.write(str(cycle_id + 1) + "\t" + str(cycle_best_path_length) + "\n")
            best_path_file_out.close()
            best_temp_path_file_out.close()
            running = False
        except IOError:
            print("Cannot open file")
            running = False
            exit()
    last_path = None
    draw()


class Ant:
    def __init__(self):
        global nodes
        self.starting_node = random.randint(0, len(nodes) - 1)
        self.tabu_list = []
        self.path_length = 0

    def find_path(self):
        global nodes
        #self.starting_node = random.randint(0, len(nodes) - 1)
        self.tabu_list = []
        self.path_length = 0
        self.tabu_list.append(self.starting_node)
        current_node_id = self.starting_node

        global distances
        for it in range(len(nodes) - 1):
            scores = []
            score_total = 0
            for node_id in range(0, len(nodes)):
                if node_id in self.tabu_list:
                    continue
                else:
                    score = city_to_city_score(current_node_id, node_id)
                    scores.append((score, node_id))
                    score_total += score
            probabilities = []
            for score in scores:
                probability = (score[0] / score_total, score[1])
                probabilities.append(probability)
            random_choice = random.random()
            choice = 0.0
            next_node_id = current_node_id
            for probability in probabilities:
                if choice + probability[0] > random_choice:
                    next_node_id = probability[1]
                    break
                else:
                    choice += probability[0]
            self.tabu_list.append(next_node_id)
            self.path_length += distances[current_node_id][next_node_id]
            current_node_id = next_node_id
        self.path_length += distances[self.tabu_list[-1]][self.starting_node]
        self.tabu_list.append(self.starting_node)

    def leave_trace(self):
        global model
        global pheromones
        global base_pheromone
        for it in range(len(self.tabu_list) - 1, 0, -1):
            if model == 'Cycle':
                #  ANT-Cycle model: bazowa / długość całej trasy
                pheromones[self.tabu_list[it]][self.tabu_list[it - 1]] += (base_pheromone / self.path_length)
                pheromones[self.tabu_list[it - 1]][self.tabu_list[it]] += (base_pheromone / self.path_length)
            elif model == 'Density':
                #  ANT-Density model: stała ilosć feromonów dodawana na ścieżkach
                pheromones[self.tabu_list[it]][self.tabu_list[it - 1]] += (base_pheromone)
                pheromones[self.tabu_list[it - 1]][self.tabu_list[it]] += (base_pheromone)
            elif model == 'Quantity':
                #  ANT-Quantity model: bazowa / długość odcinka
                pheromones[self.tabu_list[it]][self.tabu_list[it - 1]] += \
                        (base_pheromone / pheromones[self.tabu_list[it]][self.tabu_list[it - 1]])
                pheromones[self.tabu_list[it - 1]][self.tabu_list[it]] += \
                    (base_pheromone / pheromones[self.tabu_list[it - 1]][self.tabu_list[it]])
            else:
                print(model)
                print("bad input value")
                exit(-1)
        self.tabu_list = []


window = tkinter.Tk()
window.title("ACO for TSP")
window.resizable(width=False, height=False)
window.geometry('%dx%d+%d+%d' % (860, 640, window.winfo_screenwidth() / 2 - 430, window.winfo_screenheight() / 2 - 320))
window.protocol("WM_DELETE_WINDOW", close)

file_names = ['bays29', 'berlin52', 'dantzig42', 'random100Reinelt', 'reinelt1084', 'square36', 'tsp225']
file_names_box = ttk.Combobox(window, values=file_names, width=18, state='readonly')
file_names_box.bind("<<ComboboxSelected>>", file_names_box.get())
file_names_box.current(0)
file_names_box.place(x=3, y=13)

load_file_button = tkinter.Button(window, text='Load file', width=10, command=lambda: load_file(file_names_box.get()))
load_file_button.place(x=138, y=10)

draw_board = tkinter.Canvas(window, width=640, height=640, bg='black')
draw_board.place(x=219, y=0)

alpha_slider_label = tkinter.Label(window, text='α')
alpha_slider_label.place(x=190, y=60)
alpha_slider = tkinter.Scale(window, length=160, from_=0, to=10, resolution=0.25, orient=tkinter.HORIZONTAL)
alpha_slider.set(5)
alpha_slider.place(x=20, y=40)

beta_slider_label = tkinter.Label(window, text='β')
beta_slider_label.place(x=190, y=100)
beta_slider = tkinter.Scale(window, length=160, from_=1, to=10, resolution=0.5, orient=tkinter.HORIZONTAL)
beta_slider.set(5)
beta_slider.place(x=20, y=80)

rho_slider_label = tkinter.Label(window, text='ρ')
rho_slider_label.place(x=190, y=140)
rho_slider = tkinter.Scale(window, length=160, from_=0, to=1, resolution=0.1, orient=tkinter.HORIZONTAL)
rho_slider.set(0.5)
rho_slider.place(x=20, y=120)

models = ['Cycle', 'Density', 'Quantity']
cycle_models_box = ttk.Combobox(window, values=models, width=8, state='readonly')
cycle_models_box.bind("<<ComboboxSelected>>", cycle_models_box.get())
cycle_models_box.current(0)
cycle_models_box.place(x=2, y=170)
cycle_model_label = tkinter.Label(window, text='Pheromone update model')
cycle_model_label.place(x=75, y=170)

base_pheromone_label = tkinter.Label(window, text='Pheromone')
base_pheromone_label.place(x=10, y=200)
base_pheromone_entry = tkinter.Entry()
base_pheromone_entry.place(x=90, y=200)

ant_count_entry_label = tkinter.Label(window, text='Ants total')
ant_count_entry_label.place(x=10, y=230)
ant_count_entry = tkinter.Entry()
ant_count_entry.place(x=90, y=230)

cycles_count_slider_label = tkinter.Label(window, text='Cycles total')
cycles_count_slider_label.place(x=10, y=260)
cycles_count_entry = tkinter.Entry()
cycles_count_entry.place(x=90, y=260)

start_button = tkinter.Button(window, text='Run', width=20, command=start)
start_button.place(x=35, y=300)

progress_label = tkinter.Label(window, text='Progress:')
progress_label.place(x=15, y=330)
shortest_path_label = tkinter.Label(window, text='Shortest path:')
shortest_path_label.place(x=15, y=360)
shortest_path_value_label = tkinter.Label(window, text='')
shortest_path_value_label.place(x=15, y=390)

stop_button = tkinter.Button(window, text='Stop', width=20, command=stop)
stop_button.place(x=35, y=420)

window.mainloop()
