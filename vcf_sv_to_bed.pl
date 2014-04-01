#!/usr/bin/perl

use strict;
use warnings;
use Getopt::Std;
#
# Name:    
#
# Purpose: 
#         
#        
#
# Usage:   vcf_sv_to_bed.pl [options]
#
# Options: -v [FILE] valid VCF file
#
# Author:   David Jenkins
# Date:     Created 20140320
# History:  
#
###########################################################################
#read in options
my %opts;
  getopts('v:', \%opts);

sub usage(){
    die(qq/
Usage:   vcf_sv_to_bed.pl -v <in.vcf> > out.bed

Options: -v [FILE] VCF file of the database (ex. dbsnp)

\n/);
}

my $vcf_in;

if (defined $opts{v}){
    $vcf_in = $opts{v};
}
else{
    usage();
}

open(my $fi, $vcf_in) or usage();

my @format;
my @info;

VCF: while(my $vcf_line = <$fi>){
    chomp($vcf_line);
    if ($vcf_line =~ /^##FORMAT=<ID=([^,]+),/){
        push(@format, $1);
    }
    elsif ($vcf_line =~ /^##INFO=<ID=([^,]+),/){
        push(@info, $1);
    }
    elsif ($vcf_line =~ /^#CHROM/){
        $vcf_line =~ s/#//g;
        my @header = split(/\t/, $vcf_line);
        for(my $i = 0; $i < 7; $i++){
            #print $header[$i],",";
        }
        foreach(@info){
            #print $_,",";
        }
        for(my $i = 9; $i < scalar(@header); $i++){
            foreach(@format){
                #print $header[$i],"_",$_,",";
            }
        }
        #print "\n";
    }
    elsif ($vcf_line =~ /^#/){}
    else{
        my $print_line;
        my @curr_line = split(/\t/, $vcf_line);

        #chr  start(smallest if interval)  stop(largest if interval)  ID_precise/imprecise
        #chromosome
        $print_line .= $curr_line[0]."\t";

        for(my $i = 0; $i < 7; $i++){
            $curr_line[$i] =~ s/,/_/g;
            #print $curr_line[$i],",";
        }
        my @curr_info = split(/;/, $curr_line[7]);
        my %info_hash;
        foreach(@curr_info){
            my @keypair = split(/=/,$_);
            if (defined $keypair[1]){
                $info_hash{$keypair[0]} = $keypair[1];
            }
            else{
                $info_hash{$keypair[0]} = 1;
            }
        }
        my $precision;
        #if imprecise
        if(defined $info_hash{'IMPRECISE'}){
            $precision = 'imp';
            #use CI to calculate bed interval
            my @cp = split(/,/,$info_hash{'CIPOS'});
            my @ce = split(/,/,$info_hash{'CIEND'});
            $print_line .= ($curr_line[1]+$cp[0]) . "\t";
            $print_line .= ($info_hash{'END'}+$ce[1]) . "\t";
        }
        #its precise
        else{
            $precision = 'pre';
            #use pos as start 
            $print_line .= ($curr_line[1]) . "\t";
            if(defined $info_hash{'END'}){
                $print_line .= $info_hash{'END'} . "\t";
            }
            else{
                die("Precise sv doesn't have end tag\n");
            }
        }
        #id

        #if has a dbvar id
            #print it and the precision
        #else
            #print brkpoints id and the precision
   

        foreach(@info){
            if(defined $info_hash{$_}){
                $info_hash{$_} =~ s/,/_/g;
                #print $info_hash{$_},",";
            }
            else{
                #print ",";
            }
        }
        #only works on one sample right now
        if(scalar(@curr_line) > 10){
            die("Do you have multiple samples in the vcf file?\n");
        }
        my %format_hash;
        for(my $i = 9; $i < scalar(@curr_line); $i++){
            if($curr_line[$i] =~ /\.\/\./){
                next VCF;
                foreach(@format){
                    #print ",";
                }
            }
            elsif($curr_line[$i] =~ /0\/0/){
                next VCF;
            }
            else{
                my @curr_format = split(/:/, $curr_line[$i]);
                my @format_key = split(/:/, $curr_line[8]);

                for(my $j = 0; $j < scalar(@curr_format); $j++){
                    $format_hash{$format_key[$j]} = $curr_format[$j];
                }
                foreach(@format){
                    if(defined $format_hash{$_}){
                        $format_hash{$_} =~ s/,/_/g;
                        #print $format_hash{$_},",";
                    }
                    else{
                        #print ",";
                    }
                }
            }
        }
        my $zy;
        if ($format_hash{'GT'} eq '0/1'){
            $zy = 'het';
        }
        elsif($format_hash{'GT'} eq '1/1'){
            $zy = 'hom';
        }
        else{
            die("zygosity $format_hash{'GT'} not supported\n");
        }
        if(defined($info_hash{'DBVARID'})){
            $print_line .= $info_hash{'DBVARID'} . "_" . $zy;    
        }
        else{
            $print_line .= $curr_line[2] . "_" . $zy;
        }
        $print_line .= "_" . $precision;
        if(defined($info_hash{'VALIDATED'})){
            $print_line .= "_validated";
        }
        print $print_line,"\n";
    }
}
