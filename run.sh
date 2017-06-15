#!/bin/bash

declare directory='Mars_Files_SUB_'
declare directory2='Mars_SUB_'
declare filename='phits_bash.sh'
declare DirEND=2
declare FileEND=2

for H in $(seq 0 $DirEND)
do
	echo $directory$H
	cd $directory$H
	for G in $(seq 0 $FileEND);
	do
		echo $directory2$G
		cd $directory2$G
        echo 'Submitting' $filename
        qsub $filename
		cd ..
	done
	cd ..
done
