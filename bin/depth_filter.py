# depth_filter.py filters depth file by a sequence name in ref

import argparse


############
# argparse #
############

parser = argparse.ArgumentParser(description="Filter depth file by seq name")
parser.add_argument("-i", "--input", required=True,
	help="Path to input depth file")
parser.add_argument("-o", "--output", required=True,
	help="Path to output filtered file")
parser.add_argument("--seq", required=True,
	help="Sequence name to filter by")
args = parser.parse_args()


########
# main #
########

input_file = args.input
output_file = args.output
filter_seq = args.seq

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
	for line in infile:
		parts = line.split('\t')
		if parts and parts[0] == filter_seq:
			outfile.write(line)
