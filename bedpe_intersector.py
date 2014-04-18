#!/n/hsphS10/hsphfs1/chb/biodata/anaconda/bin/python

"""
Name:    bedpe_intersector.py

Purpose: Intersect a prioritized list of bedpe files to find overlaps

Input:   CSV prioritized list of bedpe files to intersect

Output:  BEDPE like file that will contain potential CNVs and a list of sample_callers that made calls overlapping that position

Usage:   bedpe_intersector.py [OPTIONS]
"""

import sys
import time
import os
import argparse
import tempfile
from subprocess import call

def main(bedpe_list):
    if bedpe_list.readline() != "sample,caller,file\n":
        raise IOError("The config file doesn't appear to be formatted correctly")
    #first file is current file
    first = bedpe_list.readline().rstrip("\n").split(",")
    header = ['chr1', 'start1', 'end1', 'chr2', 'start2', 'end2']
    sys.stderr.write("Working on %s\n" % first[2])
    header.append(first[0] + '_' + first[1])
    master_file = prep_file(first[2], 10, True)
    count = 0
    for line in bedpe_list:
        count += 1
        line_a = line.rstrip("\n").split(",")
        sys.stderr.write("Working on %s\n" % line_a[2])
        header.append(line_a[0] + '_' + line_a[1])
        curr_file = prep_file(line_a[2], 10, False)
        new_file = pairtopair(master_file.name, curr_file.name, count)
        os.unlink(master_file.name)
        master_file = new_file
        os.unlink(curr_file.name)
    print '\t'.join(header)
    for line in master_file:
        l_a = line.rstrip("\n").split("\t")
        results = '\t'.join(l_a[10].split("*"))
        print "{0}".format("\t".join(str(x) for x in [l_a[0],l_a[1],l_a[2],l_a[3],l_a[4],l_a[5],results]))
    os.unlink(master_file.name)

def prep_file(source, cols, append_name):
    tfile = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.bedpe', delete=False)
    w = open(source)
    for line in w:
        a = line.rstrip("\n").split("\t")
        a = a[0:cols]
        if append_name:
            a.append(a[6]+"*")
        tfile.write('\t'.join(a) + '\n')
    tfile.close()
    return tfile

def pairtopair(filea, fileb, inception):
    return_file = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt', delete=False)
    result_file_b = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    check_result(call(["pairToPair","-a",filea,"-b",fileb], stdout=result_file_b))
    result_file_b.seek(0)
    prev_line_a = result_file_b.readline().rstrip("\n").split("\t")
    b1_s = [prev_line_a[1], prev_line_a[12]]
    b1_e = [prev_line_a[2], prev_line_a[13]]
    b2_s = [prev_line_a[4], prev_line_a[15]]
    b2_e = [prev_line_a[5], prev_line_a[16]]
    names = prev_line_a[17]
    for line in result_file_b:
        a = line.rstrip("\n").split("\t")
        if prev_line_a[0:10] == a[0:10]:
            b1_s.append(a[12])
            b1_e.append(a[13])
            b2_s.append(a[15])
            b2_e.append(a[16])
            names = names + ',' + a[17]
        else:
            prev_line_a[1] = min(b1_s)
            prev_line_a[2] = max(b1_e)
            prev_line_a[4] = min(b2_s)
            prev_line_a[5] = min(b2_e)
            return_file.write('\t'.join(prev_line_a[0:11]))
            return_file.write(names + '*\n')
            prev_line_a = a
            b1_s = [prev_line_a[1], prev_line_a[12]]
            b1_e = [prev_line_a[2], prev_line_a[13]]
            b2_s = [prev_line_a[4], prev_line_a[15]]
            b2_e = [prev_line_a[5], prev_line_a[16]]
            names = prev_line_a[17]
    prev_line_a[1] = min(b1_s)
    prev_line_a[2] = max(b1_e)
    prev_line_a[4] = min(b2_s)
    prev_line_a[5] = min(b2_e)
    return_file.write('\t'.join(prev_line_a[0:11]))
    return_file.write(names + '*\n')
    prev_line_a = a
    result_file_b.close()
    result_file_n1 = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    check_result(call(["pairToPair","-type","notboth","-a",filea,"-b", fileb], stdout=result_file_n1))
    result_file_n1.seek(0)
    for line in result_file_n1:
        return_file.write(line.rstrip("\n") + 'n/a*\n')
    result_file_n1.close()
    result_file_n2 = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    check_result(call(["pairToPair","-type","notboth","-a",fileb,"-b", filea], stdout=result_file_n2))
    result_file_n2.seek(0)
    for line in result_file_n2:
        line_a = line.rstrip("\n").split("\t")
        return_file.write(line.rstrip("\n") + '\t')
        for x in range(0,inception):
            return_file.write('n/a*')
        return_file.write(line_a[6]+'*\n')
    return_file.close()
    return_file_sorted = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt', delete=False)
    check_result(call(["sort","-k","1,1","-k","4,4","-k","2,2n","-k","5,5n","-k","3,3n","-k","6,6n",return_file.name], stdout=return_file_sorted))
    os.unlink(return_file.name)
    return_file_sorted.seek(0)
    return return_file_sorted
     
def check_result(ret_code):
    if ret_code != 0:
        raise RuntimeError("Subprocess failed %s" % ret_code)

def verify_file(file):
    if not os.path.isfile(file):
        raise IOError("The File %s does not exist!" % file)    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Intersect a list of bedpe files to find overlaps.")
    parser.add_argument('input', help='Input csv file "sample,caller,file"')
    args = parser.parse_args()
    verify_file(args.input)
    bedpe_list = open(args.input)
    main(bedpe_list)
