#!/bin/bash

#This script subsamples a bam file to a region of interest and copies it to a
#remote server for visualization.  Use this for large bam files and visualizing
#on a local machine.

USER=$1
SERVER=$2
FILE_PATH=$3
BAM=$4
POS=$5

if [[ $# -ne 5 ]]
then
    echo ""
    echo "ERROR: please provide the correct arguments"
    echo "Usage: $0 <user> <server> <dest_path> <in.bam> <chr:start-stop>"
    echo ""
    exit 1
fi

SSH_LOC=$USER'@'$SERVER':'$FILE_PATH

FILE=$(mktemp -p ./)

echo "Subsetting file to only include $POS"
samtools view -h $BAM $POS | samtools view -Sb - > $FILE

mv $FILE ${FILE}.bam

echo "Indexing File"
samtools index ${FILE}.bam

outname=$(echo $POS | sed -r 's/\:/_/g')
bn=$(basename $BAM)

echo "Copying files to destination"
scp ${FILE}.bam ${SSH_LOC}/${bn%.bam}.${outname}.bam
scp ${FILE}.bam.bai ${SSH_LOC}/${bn%.bam}.${outname}.bam.bai

rm -f $FILE*
echo "done"
