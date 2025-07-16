import numpy as np
import random
import matplotlib.pyplot as plt
import time
import networkx as nx
import cv2
from math import sqrt
import sys
import multiprocessing
np.set_printoptions(threshold=sys.maxsize)

population_size = 5000
duration = 1000
rate = 20
death_rate = 10
days_infected = 10
days_imune = 10
start_number = 1

vertexes = []
connections = []
positions = {}
day = 0
death_rate = death_rate/days_infected
infection_record = np.array([None for y in range(duration)])
imune_record = np.array([None for y in range(duration)])
dead_record = np.array([None for y in range(duration)])

def create_image(path):
  divider = 8
  img_1 = np.array(cv2.imread(path), dtype=np.float64)
  img = np.array([[[0, 0, 0] for y in range(len(img_1[0])//divider)] for x in range(len(img_1)//divider)], dtype=np.float64)
  for y in range(len(img)):
    for x in range(len(img[0])):
      img[y][x][2] = img_1[y*divider][x*divider][0]
      img[y][x][1] = img_1[y*divider][x*divider][1]
      img[y][x][0] = img_1[y*divider][x*divider][2]
  return img

img = create_image(r"C:\Users\Gareth\Downloads\Untitled.png")

def inrange(data, num1, num2):
  return num1 < data and data < num2

def pixel_equal(pixel, coulor):
  acuracy = 90
  return inrange(pixel[2], coulor[0]-acuracy, coulor[0]+acuracy) and inrange(pixel[1], coulor[1]-acuracy, coulor[1]+acuracy) and inrange(pixel[0], coulor[2]-acuracy, coulor[2]+acuracy)

def get_cor(cor):
  global population
  return population.pointers[cor]

def get_cor_1(cor):
  global map
  return map.pointers[cor[1]][cor[0]]

infect_close_prob = 98

def find_infectie(cor):
  global map_x, map_y, infect_close_prob
  if random.randint(0, 100) <= infect_close_prob:
    cor_1 = get_cor(cor)
    distance = 10
    x = random.randint(cor_1[0]-distance, cor_1[0]+distance)
    y = random.randint(cor_1[1]-distance, cor_1[1]+distance)
    if x in range(map_x) and y in range(map_y):
      random_cor = [x, y]
      _new = get_cor_1(random_cor)
      if _new == cor:
        _new = find_infectie(cor)
      return _new
    else:
      return random.randint(0, population_size-1)
  else:
    return random.randint(0, population_size-1)


index = 0
population_size = 0
class Map:
  def __init__(self, image):
    self.k = 4
    self.density_map = np.array([[[255, 255, 255] for x in range(len(img[0])*self.k)] for y in range(len(img)*self.k)])
    self.land = np.array([[[255, 255, 255] for x in range(len(img[0])*self.k)] for y in range(len(img)*self.k)])
    self.people_map = np.array([[[255, 255, 255] for x in range(len(img[0])*self.k)] for y in range(len(img)*self.k)])
    self.pointers = [[None for y in range(len(image[0])*self.k)] for x in range(len(image)*self.k)]
    self.is_person = [[False for y in range(len(image[0])*self.k)] for x in range(len(image)*self.k)]
    for y in range(len(image)):
      for x in range(len(image[0])):
        for y1 in range(y*self.k, (y*self.k)+self.k):
          for x1 in range(x*self.k, (x*self.k)+self.k):
            self.density_map[y1][x1] = image[y][x]
            if self.get_num(image[y][x]) != 0:
              self.land[y1][x1] = [0, 0, 0]
        for p in range(self.get_num(image[y][x])):
          self.place_person((random.randint(y*self.k, (y*self.k)+self.k-1), random.randint(x*self.k, (x*self.k)+self.k-1)), p)
    self.main_image = self.land
  def place_person(self, cor, p):
    global index, population_size
    self.is_person[cor[0]][cor[1]] = True
    self.people_map[cor[0]][cor[1]] = [0, 0, 0]
    self.pointers[cor[0]][cor[1]] = index
    index += 1
    population_size += 1
  def get_num(self, pixel):
    acuracy = 50
    if pixel_equal(pixel, [0, 169, 229]):
      return 1
    if pixel_equal(pixel, [79, 231, 0]):
      return 2
    if pixel_equal(pixel, [255, 255, 0]):
      return 3
    if pixel_equal(pixel, [255, 171, 0]):
      return 4
    if pixel_equal(pixel, [255, 0, 0]):
      return 5
    if pixel_equal(pixel, [169, 0, 132]):
      return 6
    else:
      return 0
  def display(self, x):
    if x == 0:
      plt.imshow(self.main_image)
      plt.show()
    elif x == 1:
      plt.imshow(self.density_map)
      plt.show()
    elif x == 2:
      plt.imshow(self.people_map)
      plt.show()


map = Map(img)
map_x, map_y = len(map.main_image[0]), len(map.main_image)

class Population:
  def __init__(self):
    global map
    self.infected = np.array([False for y in range(population_size)])
    self.days_infected = np.array([0 for y in range(population_size)])
    self.imune = np.array([False for y in range(population_size)])
    self.days_imune = np.array([0 for y in range(population_size)])
    self.infection_plan = np.array([[0 for x in range(rate)] for y in range(population_size)])
    self.dead = np.array([False for y in range(population_size)])
    self.pointers = np.array([[0, 0] for y in range(population_size)])
    for y in range(len(map.pointers)):
      for x in range(len(map.pointers[0])):
        if map.pointers[y][x] != None:
          self.pointers[map.pointers[y][x]] = [x, y]
  def infect(self, cor, origin):
    global rate, day, vertexes, positions, connections, map_y, map_x, map
    if cor != None:
      if (not (self.imune[cor]) and (not self.dead[cor])):
        self.infected[cor] = True
        vertexes.append(cor)
        positions[cor] = (5*get_cor(cor)[1], 5*(map_y-get_cor(cor)[0]))
        if origin != None:
          connections.append((origin, cor, day))
        for y in range(rate):
          self.infection_plan[cor][y] = random.randint(day+1, day+days_infected+1)
        map.main_image[get_cor(cor)[1]][get_cor(cor)[0]][0] = 255
        map.main_image[get_cor(cor)[1]][get_cor(cor)[0]][1] = 255
  def die(self, cor):
    global map
    self.dead[cor] = True
    map.main_image[get_cor(cor)][1] = 0
    self.infected[cor] = False
  def gain_imunity(self, cor):
    global rate, map
    if not self.dead[cor]:
      self.imune[cor] = True
      self.infected[cor] = False
      self.days_infected[cor] = 0
      map.main_image[get_cor(cor)][0] = 0
      map.main_image[get_cor(cor)][1] = 255
  def lose_imunity(self, cor):
    global rate, map
    self.imune[cor] = False
    self.days_imune[cor] = 0
    map.main_image[get_cor(cor)][1] = 0


population = Population()
for y in range(start_number):
  population.infect(random.randint(0, population_size-1), None)


def main_loop():
  global vertexes
  count_down = 0
  for day in range(duration):
    print(f"[rate : {rate}    population_size : {population_size}    duration : {duration}    death rate : {death_rate}    days infected : {days_infected}    days imune : {days_imune}    start number : {start_number}]")
    print("day:", day)
    #for y in range(len(vaccine_roalouts)):
    #  vaccine_roalouts[y].roalout()
    map.display(0)
    plt.plot(infection_record, label = "infected")
    plt.plot(imune_record, label = "imune")
    plt.plot(dead_record, label = "dead")
    plt.show()
    total_infected = 0
    total_imune = 0
    total_dead = 0
    infect_today = 0
    for x in range(population_size):
      if population.infected[x] == True:
        total_infected += 1
        if population.days_infected[x] >= days_infected:
          population.gain_imunity(x)
        for date in population.infection_plan[x]:
          if date == day:
            infect_today += 1
            population.infect(find_infectie(x), x)
        if random.randint(1, 100) <= death_rate:
          population.die(x)
        population.days_infected[x] += 1
      if population.imune[x] == True:
        total_imune += 1
        population.days_imune[x] += 1
        if population.days_imune[x] >= days_imune:
          population.lose_imunity(x)
      if population.dead[x] == True:
        total_dead += 1
    infection_record[day] = total_infected
    imune_record[day] = total_imune
    dead_record[day] = total_dead
    print("% infected ", (total_infected/population_size)*100)
    print("% imune ", (total_imune/population_size)*100)
    print("% dead ", (total_dead/population_size)*100)
    if count_down <= 0:
      inp = input(": ")
      if inp == "vacc":
        #begin_vaccine_roalout()
        pass
      if inp == ">>":
        count_down = int(input(": "))
      if inp == "map":
        G = nx.DiGraph()
        G.add_nodes_from(np.array(vertexes))
        G.add_weighted_edges_from(np.array(connections))
        weight = nx.get_edge_attributes(G, "weight")
        #fig = plt.figure(1, figsize=(map_y, map_x), dpi=60)
        nx.draw_networkx(G, with_labels=True, pos=positions, node_size= 300, node_color="y", edge_color="g", arrowsize=25, font_size=8)
        nx.draw_networkx_edge_labels(G, positions, edge_labels=weight, font_size=10)
      if inp == "image":
        map.display(1)
        input("")
      if inp == "density":
        map.display(2)
        input("")
    else:
      count_down -= 1
      time.sleep(0.5)

main_loop()