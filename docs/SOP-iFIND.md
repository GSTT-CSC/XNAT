[![image](assets/transparent-CSC-logo.png)](https://github.com/GSTT-CSC/XNAT)

# iFIND

Tracked documentation on XNAT and its contribution to the <a href="https://www.ifindproject.com/">iFIND Project</a>

[View Repo](https://github.com/GSTT-CSC/XNAT) . [Report Error](https://github.com/GSTT-CSC/XNAT/issues) . [Request Feature](https://github.com/GSTT-CSC/XNAT/issues) . [Request Document](https://github.com/GSTT-CSC/XNAT/issues)


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
      </ul>
    </li>
    <li>
        <a href="#overview">Overview</a>
        <ul>
          <li><a href="#data-collection">Data collection</a></li>
          <li><a href="#copying-the-data">Copying the data</a></li>
          <li><a href="#processing-the-data">Processing the data</a></li>
          <li><a href="#downloading-the-data">Downloading the data</a></li>
          <li><a href="#checking-the-data">Checking the data</a></li>
          <li><a href="#sending-the-data">Sending the data</a></li>
        </ul>
    </li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
   <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

For more information on the Intelligent Fetal Imaging and Diagnosis (iFIND) project, please refer to their website [here](https://www.ifindproject.com/).

Ultrasound data provided for the project from Guy's and St Thomas' NHS Foundation Trust (GSTT) is done via GSTT's Clinical Scientific Computing (CSC) 
team with the use of XNAT and [other tools](https://github.com/GSTT-CSC/XNAT#tools).

### Prerequisites
Install all required tools listed [here](https://github.com/GSTT-CSC/XNAT#tools).

<!-- OVERVIEW -->
## Overview
> As this process is time-consuming and still in progress of being refined, please do take your time with following the steps in each stage. If at any point you face an issue or would like to double-check your next step, please reach out to [Dika](mailto:Dijana.Vilic@gstt.nhs.uk) or [Haleema](mailto:Haleema.AlJazzaf@gstt.nhs.uk).
> 
> **Before you begin, please ensure you have logged into the GSTT network and remain so for the entirety of the process.**

<!-- DATA COLLECTION -->
### Data collection
Please refer to the general data collection methods listed [here](https://github.com/GSTT-CSC/XNAT#data-collection). 

Currently, data for the iFIND project is collected by running the `import-tester.py` Python script.

<!-- COPYING THE DATA -->
### Copying the data
1. Open PuTTY and log into SP-PR-FLIPML01.
2. Change your user profile to root as you will need to have root privileges in order to run the following commands. To do so, type in `sudo -i` and enter the root password. 
> If your user is not in the sudoers file or you do not know how to log in as the hnadmin user, please reach out to [Dika](mailto:Dijana.Vilic@gstt.nhs.uk) for more information.
3. Navigate to the iFIND folder by typing in `cd /home/<yourusername>/iFIND`.
4. If the iFIND folder is **not** empty, make sure all the data has been de-identified before moving it to the destination folder. If the iFIND folder is empty, delete this and make a new one each time you run an ingestion.
> Please take care before running either of the following delete commands.
> 
> Remember: You are running them as the **root user** and **will not** be prompted before they are executed.
   - To delete can delete one folder at a time, you can run `rm <foldername>` when you are in the `/home/<yourusername>/iFIND` directory.
   - To delete the entire iFIND folder, go back to the previous directory, i.e. `cd /home/<yourusername>`, and run `rm -r iFIND`.
   
5. Make a new iFIND folder by going back to the user directory (if you are not there already) and run `mkdir iFIND`.
6. Copy the data from the XNAT Archive to the local iFIND folder by running `cp -r /home/hnadmin/xnat-data/xnat/archive/iFIND_2/*/440* /home/<yourusername>/iFIND`. This will take **a while** to run and so make you wait for the `>` to appear in the terminal before typing in the next command. This process copies each folder at a time since these are smaller and more easily manageable chunks. 
   - The `*` in `iFIND_2/*/` is a wildcard but will essentially look into the folders `arc001` and `arc002`
   - The `440*` in `iFIND_2/*/440*` is an example of copying all folders beginning with 440, so please make sure you change this as necessary.
7. Once you have copied all the data required, move on to the next step.

<!-- PROCESSING THE DATA -->
### Processing the data
This step includes the decompression, de-identification and recompression of the data.
1. Open WinSCP and log into SP-PR-FLIPML01.
   - If you face any issues with viewing the contents of any folders, this is likely due to the permissions inherited from the XNAT Archive. You can change this using `chmod` and run <a name="chmod"></a>`chmod -R 755 /home/<yourusername>/iFIND`. `chmod` controls accessibility and so you should be able to see the rights have changed in WinSCP. The `-R` applies the command recursively and `775` is the method of encryption.
> Note: WinSCP is not live and so you will need to refresh the window in order to see any updates.
2. Decompress the data, i.e. items in the _secondary_ folders only, which are typically DICOM multi-frame Cine images) by using the [GDCM Toolkit](https://gdcm.sourceforge.net/) and run `for i in /home/<yourusername>/iFIND/*/*/*/secondary/*; do gdcmconv --raw --force $i /$i; done`
   - You can confirm the success of this command by checking the file sizes within the secondary folders (most should be around 600MB after decompression). 
   - You can look into the folders by either using Midnight Commander via PuTTY or through the WinSCP. 
     - If the WinSCP does not allow you to view the contents in each folder, double-check you have run the `chmod` command in Step 1.
3. Once the decompression is complete, the `>` symbol will appear again, and you can now move on to de-identification of the data. Run `cd /home/<yourusername>` and then `python3 pixelcleaning.py /home/<yourusername>/iFIND/<foldername>/*`. You will see progress messages appear in the Terminal as each file is processed, such as `detect, clean, save` and the locations of each scan. 
   - New scans will have prefixes of `cleaned-` and will be located in the folder of the scan called `clean`. 
   - If it says `too many arguments!` when you run the above, it is because there are multiple folders within the selected folder. 
   - Some sessions come with a _logs_ folder and this currently is a known issue that causes the above command to fail. If this happens:
     - Navigate into the _iFIND_ folder
     - Remove the _logs_ folder by running `rm -r logs`
     - Navigate back to `/home/<yourusername>/` folder
     - Re-run the Python script.
   - If you also find _US-1_ folders, delete these, too.
4. You can now delete the scans which are not de-identified, which will be in Folder 1, by running `rm -r /home/<yourusername>/iFIND/*/SCANS/1`. 
5. Recompress the previously decompressed data by running `for i in /home/<yourusername>/iFIND/*/SCANS/clean/*; do gdcmconv -R --force $i /$i; done`. 
   - `gdcmconv` enables lossless recompression
   - This step will likely take some time and it is important to **wait** till the `>` appears before proceeding.
> Note: XNAT has an option to remove burnt-in personally-identifiable data, but this significantly increases the file sizes and causes issues when further processing the data. 


<!-- DOWNLOADING THE DATA -->
### Downloading the data
As the files are quite large, you have the option of either downloading them in batches or all at once to leave it running in the background. The former option is advised when you would like to keep an active eye on its progress, whereas the latter is convenient for when you are able to leave it running on a stable connection, e.g. in Citrix towards the end of the day. As an example, downloading 70 sessions took around 6 hours to complete. In either case, we recommend you download the files onto your desktop or another folder which will not impact anyone else and which will not autodelete, e.g. in the case of remote desktops.

1. Open WinSCP and log into SP-PR-FLIPML01 - this is the easiest way to download the data! 
   - If you are unable to download it due to permissions, double-check you have run the `chmod` command for the iFIND folder. Try again!
2. After the download is complete, you need to check at least one Cine image, e.g. typically any DICOM over 10MB, per imaging session to ensure that the de-identification was successful. We recommend using [MicroDicom](https://www.microdicom.com/) as the software for this as it is an easy, quick, and no installation required tool.
   - If you are checking a simple DICOM, i.e. a stationary screenshot, it will have a black rectangle on the top
   - If you are checking a cine, it will have a green rectangle on the top.
3. Once you confirm the data has been de-identified as expected, you need to sort the data into the folder by the subject name. The subject name can be seen in MicroDicom on the right-hand side and follows a specific naming convention, e.g. 4000_42_0__3_2.
> Note: Some subjects have multiple sessions and so make sure all of their associated data have been placed into the correct folders.
4. Move the data from WinSCP to your local folder in your user's local Citrix desktop.
5. Move the data from this folder into the MoveIT folder.
   - If you face any issues with accessing this folder, please request access from [Brian Fayemi](mailto:Brian.Fayemi@gstt.nhs.uk) or the Infrastructure team.
6. In each folder, create a new folder and name it using `Patient Name` in cine file 
   - If you open the folder and find another folder besides _clean_, e.g. 1-US1 or 1-SR, delete it.

>Voilá! You have just Gone Through It. Now it’s time to send it.


<!-- CHECKING THE DATA -->
### Checking the data
IN PROGRESS

<!-- SENDING THE DATA -->
### Sending the data
IN PROGRESS

<!-- RESOURCES -->
## Resources
* [XNAT](https://www.xnat.org/)
* [DICOM Standards Supplements](https://www.dicomstandard.org/supplements)

<!-- ROADMAP -->
## Roadmap
See the [open issues](https://github.com/GSTT-CSC/XNAT/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

<!-- CONTACT -->
## Contact

* [Dika Vilic](mailto:Dijana.Vilic@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Haleema Al Jazzaf](mailto:Haleema.AlJazzaf@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Project Link](https://github.com/GSTT-CSC/XNAT)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [README template by othneildrew](https://github.com/othneildrew/Best-README-Template)
* [Neuroinformatics Research Group at Washington University](https://www.mir.wustl.edu/research/research-centers/computational-imaging-research-center-circ/labs/marcus-lab)
