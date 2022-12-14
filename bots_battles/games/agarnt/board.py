from typing import Tuple

from numpy.random import default_rng


class Board:
    def __init__(self, max_food_number: int, max_size: Tuple[int, int]):
        self.max_size = max_size
        self.__max_food_number = max_food_number
        self.__rng = default_rng()
        self.foods = self.__rand_foods(max_food_number)

    def __rand_foods(self, n):
        x = (self.__rng.random(n) * self.max_size[0]).astype(int).tolist()
        y = (self.__rng.random(n) * self.max_size[1]).astype(int).tolist()
        return list(zip(x, y))

    def refill_food(self):
        eaten_food_number = self.__max_food_number - len(self.foods)
        self.foods += self.__rand_foods(eaten_food_number)
