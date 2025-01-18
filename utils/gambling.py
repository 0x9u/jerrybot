import hashlib
import random
import numpy as np

def sum_of_numbers_in_string(input_string):
  total = 0
  for char in input_string:
    if char.isdigit():  # Check if the character is a digit
      total += int(char)
  return total

def slot_gamble(bet: int):
  slot1 = (sum_of_numbers_in_string(
    str(hashlib.sha256(str(np.random.randint(1, 100)).encode()).hexdigest())
    ) + random.random() * 10) % 35
  
  slot2 = (sum_of_numbers_in_string(
    str(hashlib.sha256(str(np.random.randint(1, 100)).encode()).hexdigest())
    ) + random.random() * 10) % 36
  
  slot3 = (sum_of_numbers_in_string(
    str(hashlib.sha256(str(np.random.randint(1, 100)).encode()).hexdigest())
    ) + random.random() * 10) % 36
      
  if slot1 <= slot2 and slot2 <= slot3:
    return (10 * bet)
  else:
    return 0