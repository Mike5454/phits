#!/bin/bash

## Specify RAM needed per core.  Default is 1G.
#$ -l mem=1G

## Specify maximum runtime.  Default is 1 hour (1:00:00)
#$ -l h_rt=72:00:00

## Require use of infiniband.  Default is FALSE.
##$ ib=FALSE

## Allow variable core assignment
#$ -binding linear

## CUDA directive.  Default is FALSE.
##$ -l cuda=FALSE

## Use the current working directory.
#$ -cwd

## Merge output and error text streams into a single stream
#$ -j y

## Name the job.
#$ -N phits.dat

## Parallel environment
#$ -pe mpi-fill "16-32"

## Make job killable
#$ -l killable

## Target elves
##$ -q mne-bahadori

## MPI execution
mpirun ~/phits/phits_LinIfort_MPI

## Send email when job is aborted (a), begins (b), or ends (e)
#$ -m abe

## Email address
#$ -M mike5454@ksu.edu
