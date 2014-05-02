#!/usr/bin/perl

use strict;
use warnings;

open(my $fi, $ARGV[0]) or die();

my ($dis_ab, $dis_ba, $ident, $a_in_b, $b_in_a, $overlap, $a_then_b, $b_then_a, $ab_sequential, $ba_sequential) = (0,0,0,0,0,0,0,0,0,0);

while(my $line = <$fi>){
    chomp($line);
    my @a = split(/\t/, $line);
    die if($a[1]>$a[2]);
    die if($a[4]>$a[5]);
    $a[1]++;
    $a[4]++;

    if($a[1] < $a[4] && $a[2] < $a[4]){
        #disjoint [ A ] -- [ B ]
        $dis_ab++;
        print $line,"\n";
    }
    elsif($a[4] < $a[1] && $a[5] < $a[1]){
        #disjoint [ B ] -- [ A ]
        $dis_ba++;
    }
    elsif($a[1] == $a[4] && $a[2] == $a[5]){
        #identical [ A ]
        #          [ B ]
        $ident++;
    }
    elsif($a[1] > $a[4] && $a[2] < $a[5]){
        #a contained b   [ A ]
        #              [   B   ]
        $a_in_b++;
    }
    elsif($a[4] > $a[1] && $a[5] < $a[2]){
        #b contained a   [ B ]
        #              [   A   ]
        $b_in_a++;
    }
    else{
        #some kind of weird overlap
        $overlap++;
        if($a[1] == $a[4]){
            die("case found\n$line\n");
        }
        elsif($a[2] == $a[5]){
            die("case found\n");
        }
        elsif($a[4] > $a[1] && $a[4] < $a[2] && $a[5] > $a[2]){
            $a_then_b++;
        }
        elsif($a[1] > $a[4] && $a[1] < $a[5] && $a[2] > $a[5]){
            $b_then_a++;
        }
        elsif($a[2] == $a[4]){
            $ab_sequential++;
        }
        elsif($a[5] == $a[1]){
            $ba_sequential++;
        }
        else{
            print "WTF\t$line\n";
        }
    }
}

print STDERR "$dis_ab\t$dis_ba\t$ident\t$a_in_b\t$b_in_a\t$a_then_b\t$b_then_a\t$ab_sequential\t$ba_sequential\n";
