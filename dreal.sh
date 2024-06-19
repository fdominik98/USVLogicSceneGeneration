#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file.smt2> <output_file.txt>"
    exit 1
fi

# Assign arguments to variables
input_file=$1
output_file=$2

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found!"
    exit 1
fi

# Run dreal with the input file and write output to the output file
DREAL_VERSION=4.21.06.2
/opt/dreal/${DREAL_VERSION}/bin/dreal --precision 0.05 "$input_file" > "$output_file"

# Check if dreal ran successfully
if [ "$?" -eq 0 ]; then
    echo "dreal ran successfully. Output written to '$output_file'."
else
    echo "Error: dreal encountered an issue."
fi
