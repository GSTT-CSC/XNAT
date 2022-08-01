#!/bin/bash
# Store user arguments
# Usage:
# bash iFIND.sh <username>
# Example: Process sessions in the hnadmin user iFIND directory
# bash iFIND.sh hnadmin


shopt -s extglob nullglob
old="$IFS"
IFS='/'
IFS=$old
SOURCEDIR="/home/hnadmin/xnat-data/xnat/archive/iFIND_2/*/"
DESTDIR="/home/$1/iFIND"
HOMEDIR="/home/$1/"
DATE=$(date -u)
if [[ "$#" -ne 1 ]]; then
  echo "Incorrect number or format of arguments. Please try again."
  exit 0
else :
fi

# Create array for source directory and subdirectories
ARRAY=($SOURCEDIR/*)

if ((${#ARRAY[@]}<=1)); then
  printf "No subdirectories found. Exiting.\nExiting now...\n"
  sleep 1
  exit 0
else
  printf "\n%d subdirectories found.\n\n" "${#ARRAY[@]}"
  # Display the menu:
  printf "Please enter the start and end point from and to which you would like to process the data. Enter 0 to exit.\n"
  # Now wait for user input
  while true; do
      read -e -r -p "Your choice: " STARTPOINT ENDPOINT INVALID
      # Exit if user enters "0"
      if [[ $STARTPOINT -eq "0" ]]; then
        printf "\nGood bye.\n"
        exit 0
      # Check that user has entered two arguments
      elif [[ -z "$STARTPOINT" || -z "$ENDPOINT" || -n "$INVALID" ]]; then
        printf "\nIncorrect number of arguments. Please try again.\n"
      # Check that user has entered valid arguments, i.e. these are valid numbers and are within number of subdirectories
      elif [[ $STARTPOINT =~ [^0-9] || $STARTPOINT -le 0 || $STARTPOINT -gt ${#ARRAY[@]} || $STARTPOINT =~ [^0-9] || $ENDPOINT -le 0 || $ENDPOINT -gt ${#ARRAY[@]} ]]; then
        printf "\nInvalid arguments. Please try again.\n"
      else
        # Force the number to be interpreted in radix 10
        ((STARTPOINT=10#$STARTPOINT)) && ((ENDPOINT=10#$ENDPOINT)) && break
        # Check that choice is a valid choice
        ((STARTPOINT<${#ARRAY[@]})) && ((ENDPOINT<${#ARRAY[@]})) && break
      fi
  done
  # Reconfirm user choices
  printf "\nYou chose to start from %i to %i of the %d of subdirectories. It's a good choice.\n\n" "$STARTPOINT" "$ENDPOINT" "${#ARRAY[@]}"
  # Give user chance to exit gracefully
  printf "Do you want to continue? [Y/N]: \n"
  read -e -r -p "Your choice: " CHOICE
  # Case-insensitive string comparison
  shopt -s nocasematch
  if [[ $CHOICE = "N" || $CHOICE != "Y" ]]; then
    printf "\nGood bye.\n"
    exit 0
  else
    :
  fi
fi

# Convert start and end points to array indices
START=$(( STARTPOINT - 1 ))
END=$(( ENDPOINT - 1 ))

#sleep 2

# Copy data
printf '################## COPYING DATA ##################\n\n'
for (( i=START; i<=END; i++ ));
do
  cp -r "${ARRAY[$i]}" "$DESTDIR"
done

# Create array of subset of subdirectories
SUBSET=($DESTDIR/*)
# Length of subset of subdirectories array
LENGTH=${#SUBSET[@]}

#sleep 2

# Decompress data
printf '################## DECOMPRESSING DATA ##################\n\n'
for (( i=0; i<LENGTH; i++ )); do
  DIR="${SUBSET[i]}/SCANS/*/secondary/*"
  printf "%s" "${SUBSET[i]}"
  for j in $DIR; do
    printf "Decompressing file: %s\n\n" "$j"
    # Print out stderr to file
    exec 3>&2
    gdcmconv --raw --force "$j" /"$j" 2>&1 >&3 | tee stderr-decompress-"$DATE".txt
  done
done

#sleep 2

# De-identify data
printf '################## STARTING DE-IDENTIFICATION ##################\n\n'
for i in $DESTDIR/*; do
  for j in $i/*/; do
    python3 "$HOMEDIR/pixelcleaning.py" "$j"
  done
done

#sleep 2

# Delete original, patient-identifiable data
printf '################## STARTING FOLDER 1 CLEAN-UP ##################\n\n'
DIR="$DESTDIR/*/SCANS/1"
rm -r $DIR
printf "################## FOLDER 1 CLEANED UP ##################\n\n"

#sleep 1

# Compress de-identified data
printf '################## COMPRESSING DATA ##################\n\n'
for (( i=0; i<LENGTH; i++ )); do
  DIR="${SUBSET[i]}/SCANS/clean/*"
  for j in $DIR; do
    printf "Compressing file: %s\n\n" "$j"
    gdcmconv -R --force $j /$j
  done
done