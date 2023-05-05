#! /bin/env python3 

import argparse
import re

# Command line arguments
parser = argparse.ArgumentParser(description='Filter lines containing specified strings in a log file')
parser.add_argument('logfile', metavar='logfile', type=str, help='path to the log file')
parser.add_argument('-f', '--filter', metavar='filter', type=str, nargs='+', help='strings to filter for in the log file')
parser.add_argument('-e', '--excludes', metavar='exclude', type=str, nargs='+', default=[], help='strings to exclude from filtering in the log file')
parser.add_argument('-r', '--regex', metavar='regex', type=str,nargs='+',  help='regular expression to filter for in the log file')
parser.add_argument('-o', '--output', metavar='output_file', type=str, help='output file path')
args = parser.parse_args()

if not args.filter and not args.regex:
    parser.error("A filter or regex it required.")

   
# Found filter matches
filtered_lines = []

# Reading the log file
with open(args.logfile) as f:
    log = f.read().split("\n")

# Iterate through the log file
for line in log:
    
    # Ignoring any excludes
    if any(exclude in line for exclude in args.excludes):
        continue
    
    # Searching for any regex matches
    if args.regex:
        for regex in args.regex:
            try: 
                regex_filter = re.compile(regex)
            except Exception as e:
                print(f"[ERROR] {e}")
                exit()

            if regex_filter.search(line):
                filtered_lines.append(line)
    
    # Searching for any filter matches
    if args.filter:
        if any(include.lower() in line.lower() for include in args.filter):
            filtered_lines.append(line)


# Saving output to a file
if args.output:
    with open(args.output, 'w') as f:
        f.write('\n'.join(filtered_lines))
else:
    for line in filtered_lines:
        print(line)
