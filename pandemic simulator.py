import numpy as np
import random
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation
from matplotlib.pyplot import plot, draw, show
draw()

population_size = int(input("population size: "))
duration = int(input("Duration for the simulation run in days: "))
rate = int(input("The reproduction number R: "))
death_rate = int(input("proberbility of death %: "))
days_infected = int(input("how many days are people infected for: "))
days_imune = int(input("how many days are people imune for: "))
start_number = int(input("The number of people infected at the start of the simulation: "))

death_rate = death_rate/days_infected
infection_record = np.array([None for y in range(duration)])
imune_record = np.array([None for y in range(duration)])
dead_record = np.array([None for y in range(duration)])


def random_nums(max_val, length):
    nums = []
    while len(nums) < length:
        nums += [random.randint(0,max_val)]
        nums = list(set(nums))
    return nums

def find_length(number):
  lowest_dif = number + 1
  lowest = number
  for y in range(number):
    try:
      if (number % y) == 0:
        if number/y - y < lowest_dif:
          if not (number/y - y < 0):
            lowest_dif = number/y - y
            lowest = y
    except:
      pass
  return int(number/lowest), lowest

def infect(cor):
  global population, rate, day
  if not (population["imune"][cor]) and (not population["dead"][cor]):
    population["infected"][cor] = True
    for y in range(rate):
      population["infection plan"][cor][y] = random.randint(day+1, day+days_infected+1)
    population["image"][cor][0] = 255
    population["image"][cor][1] = 255


def die(cor):
  population["dead"][cor] = True
  population["image"][cor][1] = 0
  population["infected"][cor] = False


def gain_imunity(cor):
  global population, rate
  if not population["dead"][cor]:
    population["imune"][cor] = True
    population["infected"][cor] = False
    population["days infected"][cor] = 0
    population["image"][cor][0] = 0
    population["image"][cor][1] = 255


def lose_imunity(cor):
  global population, rate
  population["imune"][cor] = False
  population["days imune"][cor] = 0
  population["image"][cor][1] = 0
  

class vaccine_roalout():
  def __init__(self, amount, period):
    self.amount = amount
    self.period = period
    self.day = 0
    self.index = 0
    self.vaccine_plan = [0 for y in range(period)]
    self.random_numbers = np.array(list(zip(random_nums(population_size_x, amount), random_nums(population_size_x, amount))))
  def roalout(self):
    if day < self.period:
      global population, rate, population_size_x, population_size_y
      y = self.index
      while y < (self.vaccine_plan[self.day]+self.index):
        gain_imunity(self.random_numbers[y])
        y += 1
      self.index = y
      self.day += 1


vaccine_roalouts = []

def begin_vaccine_roalout():
  amount = int(input("amount you whant to vaccinise: "))
  period = int(input("duration of vaccine roalout: "))
  vaccine_roalouts.append(vaccine_roalout(amount, period))

population_size_y,  population_size_x = find_length(population_size)


population = {"infected" : np.array([[False for y in range(population_size_y)] for y in range(population_size_x)]),
                          "days infected" : np.array([[0 for y in range(population_size_y)] for y in range(population_size_x)]),
                          "imune" : np.array([[False for y in range(population_size_y)] for y in range(population_size_x)]),
                          "infection plan" : np.array([[[0 for y in range(rate)] for y in range(population_size_y)] for y in range(population_size_x)]),
                          "image" : np.array([[[0 for y in range(3)] for y in range(population_size_y)] for y in range(population_size_x)]),
                          "dead" : np.array([[False for y in range(population_size_y)] for y in range(population_size_x)]),
                          "days imune" : np.array([[0 for y in range(population_size_y)] for y in range(population_size_x)])}

day = 0
random_numbers = []
for y in range(start_number):
  random_number = (random.randint(0, population_size_x-1), random.randint(0, population_size_y-1))
  while random_number in random_numbers:
    random_number = (random.randint(0, population_size_x-1), random.randint(0, population_size_y-1))
  random_numbers.append(random_number)
for cor in random_numbers:
  infect(cor)


for day in range(duration):
  print(f"[rate : {rate}    population_size : {population_size}    duration : {duration}    death rate : {death_rate}    days infected : {days_infected}    days imune : {days_imune}    start number : {start_number}]")
  print("day:", day)
  plt.imshow(population["image"])
  plt.show()
  plt.plot(infection_record, label = "infected")
  plt.plot(imune_record, label = "imune")
  plt.plot(dead_record, label = "dead")
  plt.show()
  total_infected = 0
  total_imune = 0
  total_dead = 0
  infect_today = 0
  for y in range(population_size_y):
    for x in range(population_size_x):
      if population["infected"][x][y] == True:
        total_infected += 1
        if population["days infected"][x][y] >= days_infected:
          gain_imunity((x, y))
        for date in population["infection plan"][x][y]:
          if date == day:
            infect_today += 1
        if random.randint(1, 100) <= death_rate:
          die((x, y))
        population["days infected"][x][y] += 1
      if population["imune"][x][y] == True:
        total_imune += 1
        population["days imune"][x][y] += 1
        if population["days imune"][x][y] >= days_imune:
          lose_imunity((x, y))
      if population["dead"][x][y] == True:
        total_dead += 1
  for x in range(infect_today):
    infect((random.randint(0, population_size_x-1), random.randint(0, population_size_y-1)))
  infection_record[day] = total_infected
  imune_record[day] = total_imune
  dead_record[day] = total_dead
  print("% infected ", (total_infected/population_size)*100)
  print("% imune ", (total_imune/population_size)*100)
  print("% dead ", (total_dead/population_size)*100)
  """inp = input(": ")
  if inp == "vacc":
    begin_vaccine_roalout()
  for y in range(len(vaccine_roalouts)):
    vaccine_roalouts[y].roalout()"""

plt.show()