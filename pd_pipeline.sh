#!/bin/bash

# Check number of arguments
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 INPUT_IMAGE_PATH OUTPUT_DIRECTORY FUEL_LIMIT [DEBUG]"
    exit 1
fi

INPUT_IMAGE_PATH="$1"
OUTPUT_DIRECTORY="$2"
FUEL_LIMIT="$3"
DEBUG="$4"  # May be empty if not provided

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIRECTORY"

# Step 1: Run detect_subjects.py and process output to cv_out.txt
python3 detect_subjects.py "$INPUT_IMAGE_PATH" templates | \
perl -n -e 's/_PD//; print if /center/;' | \
perl -p -e 'BEGIN { our $c = 0 } s/empty\.png/"empty" . ($c++ ? $c : "").".png"/ge' > "$OUTPUT_DIRECTORY/cv_out.txt"

# Step 2: Generate graph_input.txt from cv_out.txt
cat "$OUTPUT_DIRECTORY/cv_out.txt" | \
python3 find_branches.py | \
perl -n -e 'print if s/\s\[via.+$//;' > "$OUTPUT_DIRECTORY/graph_input.txt"

# Step 3: Call solver.py with or without DEBUG
if [ -n "$DEBUG" ]; then
    python3 solver.py "$OUTPUT_DIRECTORY/graph_input.txt" "$FUEL_LIMIT" "$DEBUG"
else
    python3 solver.py "$OUTPUT_DIRECTORY/graph_input.txt" "$FUEL_LIMIT"
fi
