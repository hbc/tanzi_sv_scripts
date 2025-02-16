#!/n/hsphS10/hsphfs1/chb/biodata/anaconda/bin/python

"""
Name:    vcf_to_bedpe.py

Purpose: Convert a well formatted vcf with SVTYPE and CIPOS into a bedpe file

Input:   vcf file with SVs

Output:  BEDPE records to describe the same SVs

Usage:   vcf_to_bedpe.py [OPTIONS]
"""

import os
import sys
import argparse
import vcf

def main(vcf_file):
    #open vcf to parse
    samples_w = []
    for s in get_samples(vcf_file):
        wfile = os.path.splitext(vcf_file.replace('.gz', ''))[0] + '.' + s + '.bedpe'
        if os.path.exists(wfile):
            raise IOError("file %s exists" % wfile)
        f = open(wfile, 'w')
        samples_w.append(f)
    vcf_reader = vcf.Reader(open(vcf_file, 'r'))
    for record in vcf_reader:
        if len(record.FILTER) > 0:
            continue
        if missing_fields(record):
            continue
        print_bedpe_record(record, samples_w)

def get_samples(v_file):
    vcf_reader = vcf.Reader(open(v_file, 'r'))
    sam = vcf_reader.next()
    samples = []
    for s in sam:
        samples.append(s.sample)
    return samples

def missing_fields(v_line):
    for i in ['SVTYPE','END','CIPOS','CIEND']:
        try:
            curr = v_line.INFO[i]
        except KeyError:
            sys.stderr.write('requrired vcf INFO field %s not present at %s:%s, call will be skipped\n' % (i,v_line.CHROM,v_line.POS))
            return True
    return False

def print_bedpe_record(vcf_line, sam_fh):
    i = -1
    for sam in vcf_line.samples:
        i += 1
        if vcf_line.is_sv and sam.is_variant:
            if vcf_line.INFO['SVTYPE'] in ['INS', 'CNV', 'BND']:
                sys.stderr.write('Unsupported SV type %s in file, it will be skipped!\n' % vcf_line.INFO['SVTYPE'])
                continue
            #if vcf_line.INFO['SVTYPE'] != 'DEL':
            #    continue
            try:
                if sam['FT'] != "PASS":
                    continue
            except AttributeError:
                pass
            chrom1  = vcf_line.CHROM
            chrom2  = vcf_line.CHROM
            score   = sam['GQ'] 
            if vcf_line.INFO['SVTYPE'] == 'DEL':
                strand1 = '+'
                strand2 = '-'
                svtype  = "TYPE:DELETION"
            elif vcf_line.INFO['SVTYPE'] == 'INV':
                strand1 = '+'
                strand2 = '+'
                svtype  = "TYPE:INVERSION"
            elif vcf_line.INFO['SVTYPE'] == 'DUP':
                strand1 = '-'
                strand2 = '+'
                svtype  = "TYPE:DUPLICATION"
            try:
                name = vcf_line.INFO['DBVARID']
            except KeyError:
                name = vcf_line.ID
            if vcf_line.is_sv_precise:
                start1 = vcf_line.POS - 1
                end1   = vcf_line.POS
                start2 = vcf_line.INFO['END'] -1
                end2   = vcf_line.INFO['END']
                precision = 'PRECISE'
            else:
                start1 = vcf_line.POS + vcf_line.INFO['CIPOS'][0]
                end1   = vcf_line.POS + vcf_line.INFO['CIPOS'][1]+1
                start2 = vcf_line.INFO['END'] + vcf_line.INFO['CIEND'][0]-1
                end2   = vcf_line.INFO['END'] + vcf_line.INFO['CIEND'][1]
                precision = 'IMPRECISE'
            sam_fh[i].write("\t".join(str(x) for x in [chrom1, start1, end1, chrom2, start2, end2, name, score, strand1, strand2, svtype, precision]))
            sam_fh[i].write('\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Convert a well formatted vcf with SVTYPE and CIPOS flags into a bedpe file.")
    parser.add_argument('vcf', help='the vcf file to convert to bedpe')
    args = parser.parse_args()
    main(args.vcf)
