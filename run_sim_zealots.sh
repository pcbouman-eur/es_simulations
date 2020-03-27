#!/bin/bash

# 1st argument = starting number of zealots
# 2nd argument = ending number of zealots
# 3rd argument = number of simulations for each number of zealots

# example run command from terminal: ./run_sim_zealots.sh 0 5 10

for (( zn=$1; zn<=$2; zn++ ))
do
   echo Starting main simulation with number of zealots: zn = $zn
   python3 main.py -zn $zn -s $3
done