#!/usr/bin/env python

import math
import time

import unicornhat as unicorn
import random

print("""Rainbow
Displays a beautiful rainbow across your HAT/pHAT :D
If you're using a Unicorn HAT and only half the screen lights up, 
edit this example and  change 'unicorn.AUTO' to 'unicorn.HAT' below.
""")

unicorn.set_layout(unicorn.AUTO)
unicorn.rotation(0)
unicorn.brightness(1)
width,height=unicorn.get_shape()
i=0
x=0
while (i) < 7:
    while x < 7:

        unicorn.set_pixel