#!/usr/bin/env python

from multiprocessing import Pool, cpu_count

import xbox360
import xbox
import ps4
import cex

def process(func):
    func()

def main():
    generator = [xbox.generate, xbox360.generate, ps4.generate, cex.generate]
    pool = Pool(processes=3)
    pool.map(process, generator)

if __name__ == '__main__':
    main()
