import sys
import random

x = sys.argv[1]

with open(x, "r") as file:
    for line in file:
        if random.random() < 0.01:
            print(line, end="")