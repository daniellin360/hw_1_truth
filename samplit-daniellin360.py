import sys
import random

file = sys.argv[1]

with open(file, "r") as file:
    for line in file:
        if random.random() < 0.01:
            print(line, end="")