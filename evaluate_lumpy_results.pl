#!/usr/bin/perl

use strict;
use warnings;
use File::Temp qw/ tempfile tempdir /;
use Getopt::Long;

#
# Name:   evaluate_lumpy_results.pl
#
# Purpose: Given a bed file of 1kg deletions and deletions from lumpy,
#          prints out each overlap and overlap stats, and overall
#          stats detailing found svs.
#
# Input:   lumpy bedpe file, 1kg bed file
#
# Output:  Details of overlap
# 
# Usage:   evaluate_lumpy_results.pl [OPTIONS]
#
############################################################################

my ($lumpy_file, $dels_file);

#read in options
sub usage()
{
    die(qq/
Usage:    evaluate_lumpy_results.pl [OPTIONS]

Options: --lumpy\/-l [FILE] lumpy bedpe file       [REQUIRED]
         --dels\/-d  [FILE] .bed file of deletions [REQUIRED]
\n/);
}

if ($#ARGV < 0){
    usage();
}

GetOptions('l|lumpy=s' => \$lumpy_file,
           'd|dels=s'  => \$dels_file);

if(not defined $lumpy_file || not defined $dels_file){
    print STDERR "\nProvide the required arguments\n";
    usage();
}

open(my $lumfi, $lumpy_file) or usage();

while(my $lumpy_line = <$lumfi>){
    #create a sub file with one lumpy result
    my ($lsfh, $ls) = tempfile('lumpy_sub_XXXX', DIR => '/tmp', SUFFIX => '.bedpe', UNLINK => 1);
    print $lsfh $lumpy_line;
    close($lsfh);
    #intersect it with all the 1kg calls
    my ($irfh, $ir) = tempfile('intersect_XXXX', DIR => '/tmp', SUFFIX => '.bedpe', UNLINK => 1);
    print "intersectBed -wao -a $ls -b $dels_file > $ir\n";
    system("intersectBed -wao -a $ls -b $dels_file > $ir");
    while(my $matchline = <$irfh>){
        print $matchline;
    }
    #foreach match
        #print out result of the overlap with the count and percent from below

    File::Temp::cleanup();
}

sub compare_1kg_lumpy{
    #takes in the positions of the sv calls and returns size of the lumpy
    #sv based on the 1kg overlap and the percent overlap
    my ($lum_l_l, $lum_l_r, $lum_r_l, $lum_r_r, $oneKg_l, $oneKg_r) = @_;
    if($lum_l_l < $oneKg_l && $lum_l_r > $oneKg_l){
        if($lum_r_l < $oneKg_r && $lum_r_r > $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:          [-----------------------]
            return (($oneKg_r - $oneKg_l),1);
        }
        elsif($lum_r_l > $oneKg_r && $lum_r_r > $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:          [---------------]
            return ((($lum_r_l+1)-$oneKg_l), ($oneKg_r-$oneKg_l)/(($lum_r_l+1)-$oneKg_l));
        }
        elsif($lum_r_l < $oneKg_r && $lum_r_r < $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:          [--------------------------------]
            return (($lum_r_r-$oneKg_l), ($lum_r_r-$oneKg_l)/($oneKg_r-$oneKg_l)); 
        }
        else{
            die("\nSomething is wrong with the comparison...\n");
        }
    }
    elsif($lum_l_l > $oneKg_l && $lum_l_r > $oneKg_l){
        if($lum_r_l < $oneKg_r && $lum_r_r > $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:  [-------------------------------]
            return ($oneKg_r-$lum_l_l, ($oneKg_r-$lum_l_l)/($oneKg_r-$oneKg_l)); 
        }
        elsif($lum_r_l > $oneKg_r && $lum_r_r > $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:  [-----------------------]
            return (($lum_r_l+1)-$lum_l_l, (($lum_r_l+1)-$lum_l_l)/(($lum_r_l+1)-$oneKg_l));
        }
        elsif($lum_r_l < $oneKg_r && $lum_r_r < $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:  [----------------------------------------]
            return ($lum_r_r-$lum_l_l, ($lum_r_r-$lum_l_l)/($oneKg_r-$oneKg_l));
        }
        else{
            die("\nSomething is wrong with the comparison...\n");
        }
    }
    elsif($lum_l_l < $oneKg_l && $lum_l_r < $oneKg_l){
        if($lum_r_l < $oneKg_r && $lum_r_r > $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:                  [---------------]
            return ($oneKg_r-($lum_l_r-1), ($oneKg_r-$oneKg_l)/($oneKg_r-($lum_l_r-1)));
        }
        elsif($lum_r_l > $oneKg_r && $lum_r_r > $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:                  [-------]
            return (($lum_r_l+1)-($lum_l_r-1), ($oneKg_r-$oneKg_l)/(($lum_r_l+1)-($lum_l_r-1)));
        }
        elsif($lum_r_l < $oneKg_r && $lum_r_r < $oneKg_r){
            #LUM:     [[[[[]]]]]---------------[[[[[]]]]]
            #1KG:                  [-----------------------]
            return ($lum_r_r-($lum_l_r-1), ($lum_r_r-($lum_l_r-1))/($oneKg_r-($lum_l_r-1)));
        }
        else{
            die("\nSomething is wrong with the comparison...\n");
        }
    }
    else{
        die("\nSomething is wrong with the comparison...\n");
    }
}
