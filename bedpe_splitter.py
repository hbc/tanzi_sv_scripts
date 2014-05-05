#!/n/hsphS10/hsphfs1/chb/biodata/anaconda/bin/python

"""
Name:    bedpe_splitter.py

Purpose: Take a bedpe file containing multiple samples and separate them by information in the ID column.  This script is meant to modify bedpe files created by lumpy

Input:   bedpe file with lumpy style ID column
         comma separated file of ids and associated sample names:
            10,NA12878
            11,NA12878
            20,NA12891
            21,NA12891
            30,NA12892
            31,NA12892
Output:  Separate BEDPE files for each of the samples

Usage:   bedpe_splitter.py [OPTIONS]
"""

import os
import re
import sys
import argparse

def main(bedpe_file, samples_file, minsupport):
    #open vcf to parse
    print_dict = create_print_dict(bedpe_file, samples_file)
    bedpe_fh = open(bedpe_file)
    for line in bedpe_fh:
        print_bedpe_line(line, print_dict, minsupport)

def create_print_dict(bedpe_file, samples_file):
    file_dict = {}
    print_dict = {}
    s = open(samples_file)
    for line in s:
        line_a = line.rstrip("\n").split(",")
        try:
            file_dict[line_a[0]] = print_dict[line_a[1]]
        except KeyError:
            wfile = os.path.splitext(bedpe_file)[0] + '.' + line_a[1] + '.bedpe'
            if os.path.exists(wfile):
                raise IOError("file %s exists" % wfile)
            f = open(wfile, 'w')
            file_dict[line_a[0]] = f
            print_dict[line_a[1]] = f
    return file_dict

def print_bedpe_line(line, print_dict, support):
    line_a = line.rstrip("\n").split("\t")
    if not re.match("IDS:", line_a[11]):
        raise Exception("Are you sure the file is a correctly formatted bedpe file?")
    ids = line_a[11].replace('IDS:', '').split(';')
    psum = {}
    toprint = set()
    for i in ids:
        toprint.add(print_dict[i.split(',')[0]])
        try:
            psum[print_dict[i.split(',')[0]]] = psum[print_dict[i.split(',')[0]]] + int(i.split(',')[1])
        except KeyError:
            psum[print_dict[i.split(',')[0]]] = int(i.split(',')[1])
    for fh in toprint:
        if psum[fh] >= support:
            fh.write(line)

def verify_file(file):
    if not os.path.isfile(file):
        raise IOError("The File %s does not exist!" % file)    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Take a bedpe file containing multiple samples and separate them by information in the ID column.  This script is meant to modify bedpe files created by lumpy")
    parser.add_argument('bedpe', help='the bedpe file to split')
    parser.add_argument('--samples', '-s', help='comma separated list of ID,Sample associations', required=True)
    parser.add_argument('--minsupport','-m',help='Minimum amount of support required for the deletion to be included in the bedpe output [%(default)s]',default=4)
    args = parser.parse_args()
    verify_file(args.bedpe)
    verify_file(args.samples)
    main(args.bedpe, args.samples, args.minsupport)

