#!/bin/bash

# Name:    pair_to_pair_concordance.sh
#
# Purpose: Calculate true pos, false pos, and false neg from a bedpe
#          truth set and a test file
#
# Usage:   pair_to_pair_concordance.sh [options] 
#
# Options:
#    -t <truth.bedpe>       [REQUIRED]
#    -b <test.bedpe>        [REQUIRED]
#    -s <bedtools_dir>      [DEFAULT:`which pairToPair`]
#    -h HELP
#
# Author:   David Jenkins
# Date:     Created 20140512
# History:
#
###########################################################################

usage() {
cat >&2 <<EOF

usage: $0 options

Calculate true pos, false pos, and false neg from a bedpe truth set and a test file

Options:
    -t <truth.bedpe>       [REQUIRED]
    -b <test.bedpe>        [REQUIRED]
    -s <bedtools_dir>      [DEFAULT:`dirname $(which pairToPair)`]
    -h HELP

EOF
exit 1
}

PAIRTOPAIR=`dirname $(which pairToPair)`/pairToPair

while getopts "ht:b:s:" OPTION
do
    case $OPTION in
    h)
        usage
        ;;
    t)
        TRUTH=$OPTARG
        ;;
    b)
        TEST=$OPTARG
        ;;
    s)
        PAIRTOPAIR=$OPTARG/pairToPair
        ;;
    esac
done

if [[ -z $TRUTH ]] || [[ -z $TEST ]] || [[ ! -x $PAIRTOPAIR ]]
then
    echo "" >&2
    echo "PROBLEM WITH INPUTS!" >&2
    usage
fi

CONC1=$(pairToPair -is -a $TEST -b $TRUTH | cut -f1-10 | sort | uniq | wc -l)
CONC2=$(pairToPair -is -b $TEST -a $TRUTH | cut -f1-10 | sort | uniq | wc -l)
FP=$(pairToPair -is -type notboth -a $TEST -b $TRUTH | wc -l)
FN=$(pairToPair -is -type notboth -b $TEST -a $TRUTH | wc -l)

echo '| Category        | Count |'
echo '|-----------------|-------|'
echo "| concordant (1)  | $CONC1 |"
echo "| concordant (2)  | $CONC2 |"
echo "| discordant (FN) | $FN |"
echo "| discordant (FP) | $FP |"

pairToPair -a $TEST -b $TRUTH | cut -f1-15 | sort | uniq -c | awk '$1>1' >&2

if [[ -f conc.ab.bedpe ]]
then
    echo "conc.ab.bedpe already exists"
else
    pairToPair -is -a $TEST -b $TRUTH > ${TEST%.bedpe}.conc.ab.bedpe
fi

if [[ -f conc.ba.bedpe ]]
then
    echo "conc.ba.bedpe already exists"
else
    pairToPair -is -b $TEST -a $TRUTH > ${TEST%.bedpe}.conc.ba.bedpe
fi

if [[ -f disc.fp.bedpe ]]
then
    echo "disc.fp.bedpe already exists"
else
    pairToPair -is -type notboth -a $TEST -b $TRUTH > ${TEST%.bedpe}.disc.fp.bedpe
fi

if [[ -f disc.fn.bedpe ]]
then
    echo "disc.fn.bedpe already exists"
else
    pairToPair -is -type notboth -b $TEST -a $TRUTH > ${TEST%.bedpe}.disc.fn.bedpe
fi
