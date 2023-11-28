#!/bin/bash
#SBATCH --image=smithsg84/pftest:latest
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH -t 01:00:00
#SBATCH -o output.o%j

source /global/homes/u/u9563/global-parflow/perlmutter-v3.9.0-2023-10-24/setenv.sh

size=$1

for study_name in 'container' 'native'
do
   for s in $(seq 3)
   do
      nx=$(( size * 100 ))
      num_procs=$(( size * size ))

      case $study_name in
	 native)
	    time srun -n $num_procs parflow results/${study_name}/${nx}_${nx}_20/${s}/default_richards
	    ;;

	 container)
	    # srun -n 4 python3 hello_world.py
	    time srun -n $num_procs shifter --entrypoint=parflow -- results/${study_name}/${nx}_${nx}_20/${s}/default_richards
	    ;;
      esac

      sleep 20
   done
done

