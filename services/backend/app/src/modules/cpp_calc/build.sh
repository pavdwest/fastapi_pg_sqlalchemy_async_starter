#!/usr/bin/env bash

#  Convert library code to Object file
# g++ -c -o libccalc.o ccalc.c
gcc -c -fPIC -O3 -o libccalc.o ccalc.c

#  Create shared .SO library
gcc -shared -o libccalc.so libccalc.o
