#!/n/hsphS10/hsphfs1/chb/biodata/anaconda/bin/python

"""
Name:    bedpe_to_sv_summary.py

Purpose: Convert a bedpe file to a high level report of called svs

Input:   bedpe lumpy output or bedpe converted from some other format

Output:  CSV of SV results with the following information:
              -SV Type
              -Breakpoint 1
              -Closest Gene(s) 1
              -Cytoband 1
              -Breakpoint 2
              -Closest Gene(s) 2
              -Cytoband 2
              -Size
              -Overlapping Repeat Elements

Usage:   bedpe_to_sv_summary.pl [OPTIONS]
"""

import os
import argparse
import tempfile
from subprocess import call

def main(bedpe_input, cytobands, repeats, genes):
    #intersect bedpe result with cytobands
    cyto_intersect = intersect_to_temp(bedpe_input, cytobands, True)
    repeats_intersect = intersect_to_temp(bedpe_input, repeats, False)
    closest_l, closest_r = closest_to_temp(bedpe_input, genes)
    r_dict = create_dict(repeats_intersect, -3)
    left_dict = create_closest_dict(closest_l, -2)
    right_dict = create_closest_dict(closest_r, -2)
    prev_line = cyto_intersect.readline().rstrip("\n").split("\t")
    print "{0}".format("\t".join(str(x) for x in ["#SV Type", "Breakpoint 1", "Closest Gene(s) 1", "Breakpoint 2",
                                                  "Closet Gene(s) 2", "Cytoband(s)", "Size", "Overlapping Repeats"]))
    if len(prev_line) == 17:
        curr_cytobands = ["_".join([prev_line[-4],prev_line[-1]])]
    else:
        curr_cytobands = ['n/a']
    for line in cyto_intersect:
        curr_line = line.rstrip("\n").split("\t")
        if curr_line[0:6] == prev_line[0:6]:
            if len(prev_line) == 17:
                curr_cytobands.append("_".join([curr_line[-4],curr_line[-1]]))
            else:
                curr_cytobands.append('n/a')
        else:
            uniq_cytos = sorted(set(curr_cytobands))
            print_result(prev_line, uniq_cytos, r_dict, left_dict, right_dict)
            prev_line = curr_line
            if len(prev_line) == 17:
                curr_cytobands = ["_".join([prev_line[-4],prev_line[-1]])]
            else:
                curr_cytobands = ['n/a']
    uniq_cytos = sorted(set(curr_cytobands))
    print_result(prev_line, uniq_cytos, r_dict, left_dict, right_dict)
     
def print_result(bedpe_line, uniq_cytos, re_dict, left_dict, right_dict):
    svtype  = bedpe_line[10].replace("TYPE:", "")
    bp1     = str(bedpe_line[0] + ':' + bedpe_line[1] + '-' + bedpe_line[2])
    try:
        clo1 = ",".join(sorted(set(left_dict["_".join(bedpe_line[0:3])])))
    except KeyError:
        clo1 = "none"
    bp2     = str(bedpe_line[3] + ':' + bedpe_line[4] + '-' + bedpe_line[5])
    try:
        clo2 = ",".join(sorted(set(right_dict["_".join(bedpe_line[3:6])])))
    except KeyError:
        clo2 = "none"
    cytos   = ",".join(uniq_cytos)
    size    = int(bedpe_line[5]) - int(bedpe_line[1])
    try:
        repeats = ",".join(sorted(set(re_dict["_".join(bedpe_line[0:6])])))
    except KeyError:
        repeats = "n/a"
    print "{0}".format("\t".join(str(x) for x in [svtype, bp1, clo1, bp2, clo2, cytos, size, repeats]))
 
def create_dict(intersect_result, index):
    r_dict = {}
    for line in intersect_result:
        line_a = line.rstrip("\n").split("\t")
        try:
            r_dict["_".join(line_a[0:6])].append(line_a[index])
        except KeyError:
            r_dict["_".join(line_a[0:6])] = [line_a[index]]
    return r_dict

def create_closest_dict(closest_result, index):
    r_dict = {}
    for line in closest_result:
        line_a = line.rstrip("\n").split("\t")
        try:
            r_dict["_".join(line_a[0:3])].append(line_a[index])
        except KeyError:
            r_dict["_".join(line_a[0:3])] = [line_a[index]]
    return r_dict

def intersect_to_temp(file1, file2, include_mismatches):
    temp_file = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    check_result(call(["pairToBed", "-a", file1, "-b", file2], stdout=temp_file))
    if include_mismatches:
        check_result(call(["pairToBed", "-type","neither","-a", file1, "-b", file2], stdout=temp_file))
    temp_file.seek(0)
    return temp_file

def closest_to_temp(file1, file2):
    left_bp_tmp = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    right_bp_tmp = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    result_l = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    result_r = tempfile.NamedTemporaryFile(dir='/tmp', suffix='.txt')
    check_result(call(["cut", "-f1-3", file1], stdout=left_bp_tmp))
    check_result(call(["cut", "-f4-6", file1], stdout=right_bp_tmp))
    check_result(call(["closestBed", "-d", "-a", left_bp_tmp.name, "-b", file2], stdout=result_l))
    check_result(call(["closestBed", "-d", "-a", right_bp_tmp.name, "-b", file2], stdout=result_r))
    result_l.seek(0)
    result_r.seek(0)
    return result_l, result_r

def check_result(ret_code):
    if ret_code != 0:
        raise RuntimeError("Subprocess failed %s" % ret_code)

def verify_file(file):
    if not os.path.isfile(file):
        raise IOError("The File %s does not exist!" % file)    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Convert a lumpy bedpe file to a high level report of called SVs.")
    parser.add_argument('input', help='Input BEDPE file containing calls')
    parser.add_argument('--cyto', '-c', help='BED file of Cytobands [REQUIRED]', required=True)
    parser.add_argument('--repeat', '-r', help='BED file of Repeats [REQUIRED]', required=True)
    parser.add_argument('--gene', '-g', help='BED file of Genes [REQUIRED]', required=True)
    args = parser.parse_args()
    verify_file(args.input)
    verify_file(args.cyto)
    verify_file(args.repeat)
    verify_file(args.gene)
    main(args.input, args.cyto, args.repeat, args.gene)
