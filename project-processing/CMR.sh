#!/bin/bash
# Transfers, processes and zips CMR data
#
# Usage:
# source CMR.sh <username> <destination folder> <start position> <end position>
#
# Example:
# Process the first 100 sessions in the CMR folder in /mnt/vol_data_flipstor02
# and write log to haljazzaf's directory
#
# bash CMR.sh haljazzaf CMR 1 100 &

shopt -s extglob nullglob
old="$IFS"
IFS='/'
IFS=$old

# TODO: Split up script into functions and include user option for project
sourcedir="/home/hnadmin/xnat-data/xnat/archive/CMR-EA/*/"
destdir="/mnt/vol_data_flipstor02/$2"
alias changedir="cd $destdir"
homedir="/home/$1/"
date=$(date -u)
startpoint=$3
endpoint=$4

# Check if arguments are sufficient and valid
if [[ "$#" -ne 4 ]]; then
  echo "Incorrect number or format of arguments. Please try again."
  exit 0
else :
fi

# TODO: Start bg session at this point so that user does not need to pause and restart with bg %
# save below to log file
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3 15 RETURN
exec 1>"log-${startpoint}_${endpoint}_${date}.out" 2>&1

# TODO: Replace user interaction with argparse
# Create array for source directory and subdirectories
array=($sourcedir/*)

newdirectory="${startpoint}_$endpoint"
mkdir -p $destdir/"$newdirectory"
newdestdir="$destdir/"$newdirectory""

# Convert start and end points to array indices
start=$(( startpoint - 1 ))
end=$(( endpoint - 1 ))

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

# Zip folders
printf '################## ZIPPING FOLDERS ##################\n\n'
# Change directory, i.e. to user's destination directory
changedir

folder="$(basename -- $newdestdir)"
zip_dir="$folder.zip"
printf "Zipping directory %s in %s\n\n" $newdestdir $destdir
zip -r $newdirectory $newdirectory
printf "Deleting original directory %s\n\n" $newdestdir
rm -r $newdestdir
printf '################## PROCESS COMPLETE ##################\n\n'