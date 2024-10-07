# DMCTK upload script WIP
# 41 csvfile, $2 project
#storescp -aet XNAT -od /home/hnadmin/test_qr/incoming_data -ss diverter 105 &
#num=1
PACS="172.XX.XX.XX PORT" # example 172.11.2.11 7900
IN_DIR="${PWD}/incoming_data"
AEC="PACS_AET"
echo "making $IN_DIR"
mkdir "$IN_DIR"

while IFS=, read -r col1 col2 col3
do
        echo "Reading file - line $col1 $col2 $col3" 
	echo "findscu -aet XNAT -aec $AEC -v -S -k 0008,0052=STUDY -k 0008,0050=\"$col1\"  $PACS  -k 0020,000D" > in.sh
	./in.sh > out.log 2>&1
	while IFS= read -r line; do
		if [[ $line = *"StudyInstance"* ]]; then
			if [[ $line != *"no value"* ]]; then
				IFS=[ read var1 var2 <<< $line
     				IFS=] read var3 var4 <<< $var2
                                echo "found sessions study uid: $var3"  
                                #su - root -c "storescp aet XNAT -od $IN_DIR --s diverter 105" &
                                echo "movescu -aet XNAT -aec $AEC -aem XNAT -k 0008,0052=STUDY -k 0020,000D=$var3 172.31.2.61 7958" > move.sh
                                ./move.sh
                                
				sleep 180 
                                #dcmmodify....
                                echo "python3 modify_dicoms.py $col1 $col2 $col3 $2 $IN_DIR" >> mod.sh
                                python3 modify_dicoms.py $col1 $col2 $col3 $2 $IN_DIR &
                        fi
                fi
	done < out.log
done < $1
