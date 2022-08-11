#!/bin/bash
# Transfers, processes and zips iFIND data
#
# Usage:
# bash iFIND.sh <username> <destination folder>
#
# Example:
# Process sessions in the iFIND_processing folder in /mnt/vol_data_flipstor02
# and write log to haljazzaf's directory
#
# bash iFIND.sh haljazzaf iFIND_processing

shopt -s extglob nullglob
old="$IFS"
IFS='/'
IFS=$old
sourcedir="/home/hnadmin/xnat-data/xnat/archive/iFIND_2/*/"
destdir="/mnt/vol_data_flipstor02/$2"
homedir="/home/$1/"
date=$(date -u)
if [[ "$#" -ne 2 ]]; then
  echo "Incorrect number or format of arguments. Please try again."
  exit 0
else :
fi

# TODO: Replace user interaction with argparse
# Create array for source directory and subdirectories
array=($sourcedir/*)

if ((${#array[@]}<=1)); then
  printf "No subdirectories found. Exiting.\nExiting now...\n"
  sleep 1
  exit 0
else
  printf "\n%d subdirectories found.\n\n" "${#array[@]}"
  # Display the menu:
  printf "Please enter the start and end point from and to which you would like to process the data. Enter 0 to exit.\n"
  # Now wait for user input
  while true; do
      read -e -r -p "Your choice: " startpoint endpoint invalid
      # Exit if user enters "0"
      if [[ $startpoint -eq "0" ]]; then
        printf "\nGood bye.\n"
        exit 0
      # Check that user has entered two arguments
      elif [[ -z "$startpoint" || -z "$endpoint" || -n "$invalid" ]]; then
        printf "\nIncorrect number of arguments. Please try again.\n"
      # Check that user has entered valid arguments, i.e. these are valid numbers and are within number of subdirectories
      elif [[ $startpoint =~ [^0-9] || $startpoint -le 0 || $startpoint -gt ${#array[@]} || $startpoint =~ [^0-9] || $endpoint -le 0 || $endpoint -gt ${#array[@]} ]]; then
        printf "\nInvalid arguments. Please try again.\n"
      else
        # Force the number to be interpreted in radix 10
        ((startpoint=10#$startpoint)) && ((endpoint=10#$endpoint)) && break
        # Check that choice is a valid choice
        ((startpoint<${#array[@]})) && ((endpoint<${#array[@]})) && break
      fi
  done
  # Reconfirm user choices
  printf "\nYou chose to start from %i to %i of the %i of subdirectories, i.e. folders %s to %s. It's a good choice.\n\n" "$startpoint" "$endpoint" "${#array[@]}" "${array[$(( startpoint - 1 ))]}" "${array[$(( endpoint - 1 ))]}"
  # Give user chance to exit gracefully
  printf "Do you want to continue? [Y/N]: \n"
  read -e -r -p "Your choice: " choice
  # Case-insensitive string comparison
  shopt -s nocasematch
  if [[ $choice = "N" || $choice != "Y" ]]; then
    printf "\nGood bye.\n"
    exit 0
  else
    :
  fi
fi

newdirectory="${startpoint}_$endpoint"
mkdir -p $destdir/"$newdirectory"
newdestdir="$destdir/"$newdirectory""

# save below to log file
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3 15 RETURN
exec 1>"log-${startpoint}_${endpoint}_${date}.out" 2>&1

# Convert start and end points to array indices
start=$(( startpoint - 1 ))
end=$(( endpoint - 1 ))

#sleep 2

# Copy data
printf '################## COPYING DATA ##################\n\n'
for (( i=start; i<=end; i++ ));
do
  printf "Copying: %s \n" "$i"
  cp -r "${array[$i]}" "$newdestdir"
done

# Create array of subset of subdirectories
subset=($newdestdir/*)
# Length of subset of subdirectories array
length=${#subset[@]}

# sleep 2

# TODO: Update to support folders with unexpected folder structures
# Decompress data
printf '################## DECOMPRESSING DATA ##################\n\n'
for (( i=0; i<length; i++ )); do
  directory="${subset[i]}/SCANS/*/secondary/*"
  printf "Hello %s" "${subset[i]}"
  for j in $directory; do
    printf "Decompressing file: %s\n\n" "$j"
#    # Print out stderr to file
#    exec 3>&2
    gdcmconv --raw --force "$j" /"$j"
# 2>&1 >&3 | tee stderr-decompress-"$date"-"$startpoint"-"$endpoint".txt
  done
done

#sleep 2

# De-identify data
printf '################## STARTING DE-IDENTIFICATION ##################\n\n'
for i in $newdestdir/*; do
  for j in $i/*/; do
    python3 "$destdir/pixelcleaning.py" "$j"
  done
done

# sleep 2

# Delete original, patient-identifiable data
printf '################## STARTING FOLDER 1 CLEAN-UP ##################\n\n'
directory="$newdestdir/*/SCANS/1"
rm -r $directory
printf "################## FOLDER 1 CLEANED UP ##################\n\n"

# sleep 1

# Compress de-identified data
printf '################## COMPRESSING DATA ##################\n\n'
for (( i=0; i<length; i++ )); do
  directory="${subset[i]}/SCANS/clean/*"
  for j in $directory; do
    printf "Compressing file: %s\n\n" "$j"
    gdcmconv -R --force $j /$j
  done
done

# TODO: Investigate why some zipped folders are corrupted in bigger batches
# Zip folders
printf '################## ZIPPING FOLDERS ##################\n\n'
for (( i=0; i<length; i++ )); do
  directory="${subset[i]}"
  #clean_dir="${subset[i]}/SCANS/clean"
  zip_dir="fh-$(basename $directory).zip"
  printf "Zipping %s as %s" $directory "$newdestdir/$zip_dir"
  zip -r "$newdestdir/$zip_dir" $directory
  printf "Deleting folder %s" $directory
  rm -r $directory
done

printf '################## PROCESS COMPLETE ##################\n\n'
