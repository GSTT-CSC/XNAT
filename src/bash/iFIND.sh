#!/bin/bash
# Transfers, processes and zips iFIND data
#
# Usage:
# bash iFIND.sh <username> <destination folder> <start folder number> <end folder number>
#
# Example:
# Process all sessions between, and including, the 100th session and 200th in the iFIND_processing folder in
# /mnt/vol_data_flipstor02 and write log to haljazzaf's directory as a background process
#
# bash iFIND.sh haljazzaf iFIND_processing 100 200

shopt -s extglob nullglob
old="$IFS"
IFS='/'
IFS=$old
sourcedir="/home/hnadmin/xnat-data/xnat/archive/iFIND_2/*/"
destdir="/mnt/vol_data_flipstor02/$2"
homedir="/home/$1/"
startpoint=$3
endpoint=$4
date=$(date -u)

#TODO: Make error message more helpful
# If args are less than the required 4, or the folder start point is ahead of the end point, raise an error
if [ "$#" -ne 4 ] || [ $((startpoint)) -gt $((endpoint)) ]; then
  echo "Incorrect number or format of arguments. Please try again."
  exit 0
else :
fi

# Create array for source directory and subdirectories
array=($sourcedir/*)

if ((${#array[@]}<=1)); then
  printf "No subdirectories found. Exiting.\nExiting now...\n"
  sleep 1
  exit 0
else
  if [[ $startpoint -eq "0" ]]; then
    printf "\nGood bye.\n"
    exit 0
    # Check that user has entered valid arguments, i.e. these are valid numbers and are within number of subdirectories
    elif [[ $startpoint =~ [^0-9] || $startpoint -le 0 || $startpoint -gt ${#array[@]} || $startpoint =~ [^0-9] || $endpoint -le 0 || $endpoint -gt ${#array[@]} ]]; then
      printf "\nInvalid arguments. Please try again.\n"
      exit 0
      else
        # Force the number to be interpreted in radix 10
        ((startpoint=10#$startpoint)) && ((endpoint=10#$endpoint))
        # Check that choice is a valid choice
        ((startpoint<${#array[@]})) && ((endpoint<${#array[@]}))
      fi
  # Write print statements to log file
  exec 3>&1 4>&2
  trap 'exec 2>&4 1>&3' 0 1 2 3 15 RETURN
  exec 1>$homedir/"log-${startpoint}_${endpoint}_${date}.out" 2>&1
  # Confirm folders to be processed:
  printf "\nProcessing from %i to %i of the %i of subdirectories, i.e. folders %s to %s.\n\n" "$startpoint" "$endpoint" "${#array[@]}" "$(basename "${array[$(( startpoint - 1 ))]}")" "$(basename "${array[$(( endpoint - 1 ))]}")"
  fi

newdirectory="${startpoint}_$endpoint"
mkdir -p $destdir/"$newdirectory"
newdestdir="$destdir/"$newdirectory""

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

# To handle unexpected folder structures, delete all folders except for "1"
printf '################## STARTING FOLDER CLEAN-UP ##################\n\n'
for (( i=0; i<length; i++ )); do
  directory="${subset[i]}/SCANS"
  printf "Looking at folder: %s\n\n" "$directory"
#  printf "Hello %s" "${subset[i]}"
#  for j in $directory; do
#    printf "Looking at folder: %s\n\n" "$j"
# Deletes all folders that aren't "1" or "1-US1"
    rm -r $directory/!(1|1-US1)/
#  done
done

# Decompress data
printf '################## DECOMPRESSING DATA ##################\n\n'
for (( i=0; i<length; i++ )); do
  directory="${subset[i]}/SCANS/*/secondary/*"
  printf "Looking at %s" "${subset[i]}"
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

# Delete all folders except for "clean"
printf '################## STARTING FOLDER CLEAN-UP ##################\n\n'
for (( i=0; i<length; i++ )); do
  directory="${subset[i]}/SCANS"
  printf "Looking at folder: %s\n\n" "$directory"
    rm -r $directory/!(clean)/
done

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
  folder="$(basename -- $directory)"
  #dir_path="$(dirname "$directory")"
  #clean_dir="${subset[i]}/SCANS/clean"
  zip_dir="fh-$folder.zip"
  printf "Zipping directory %s as %s in %s\n\n" $directory $zip_dir $newdestdir
  # Zip in flat directory structure
  zip -r -j $newdestdir/$zip_dir $directory
  printf "Deleting original directory: %s\n\n" $directory
  rm -r $directory
done

printf '################## PROCESS COMPLETE ##################\n\n'
