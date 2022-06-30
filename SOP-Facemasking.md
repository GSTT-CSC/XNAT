<!-- PROJECT HEADING -->
<br />
<p align="center">
<a href="https://github.com/GSTT-CSC/XNAT">
    <img src="https://raw.githubusercontent.com/GSTT-CSC/gstt-csc.github.io/main/assets/transparent-CSC-logo-cropped.png" alt="Logo" width="50%">
  </a>
<h1 align="center">Facemasking</h1>
<p align="center">
This SOP describes how to use facemasking and download the defaced data.
<br />

<br />
<a href="https://github.com/GSTT-CSC/XNAT">View repo</a>
·
<a href="https://github.com/GSTT-CSC/XNAT/issues">Report Error</a>
·
<a href="https://github.com/GSTT-CSC/XNAT/issues">Request Feature</a>
·
<a href="https://github.com/GSTT-CSC/XNAT/issues">Request Document</a>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#data-checking">Facemasking</a>
      <ul>
        <li><a href="#PII">SOP</a></li>
      </ul>
    </li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
   <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- FACEMASKING -->
## Facemasking

Facemasking process is the process of blurring the facial features in a DICOM. We do this because, in images with sufficient resolution,
volumes can be rendered in 3D. This is very useful for clinical diagnosis for various reasons, but the unfortunate side effect is that a high
resolution image of a head can be effectively rendered in 3D, thus reconstructing the subject's face in 3D. This can potentially identify
a patient. 

To prevent this, we apply facemasking. Our facemasking solution was developed by Marc Modat and is implemented as a container within XNAT.
The instructions on how to apply facemasking are below. NB. the results will be saved in nifti format (3D imaging format) which is not readily seen in
XNAT but is there - you'll see it under 'manage files' at session level.

<!-- SOP -->
### SOP
1. First, you need to import your high resolution head MRIs. To upload your data, follow the Data Import SOP.
2. Once your data is in XNAT, open your project. 
3. Click on 'Project Settings' on the right-hand side. The settings will open: you need to 'enable' the XNAT command called 'Run the defacing processing from a session'. 
Once enabled, go back to your project page.
4. You need to apply facemasking to each session individually. It is also good practice to download as you go.
5. Open the first subject and the first session. 
6. Under 'Scans' you will see a list of DICOMs contained within your session. Tick the checkbox on the left-hand side of the word 'Scan' in the 
top row. This will select all scans in the session.
7. On the row above the checkbox where it says 'Bulk Actions:' click on 'Run Container' and select 'Run the defacing processing from a session'.
8. A pop up will appear. It will select all images that fit the criteria. Click 'Run Container(s)'. A pop-up will appear that informs you of what started. Click 'OK'
9. This will trigger the facemasking process. It will work through each DICOM in the session and apply facemasking to those which can be effectively converted
to nifti and where the eyes can be found. It will then apply a square across the eyes.
10. You will see the process as it progresses lower on the page under 'History', and on the bottom-right-hand side in the 'Background Processes' pop-up. Remember that only
the DICOMS which are large enough in volume will be successfully processed, and the rest will fail: this is normal.
11. Once it is done refresh the page. Click on 'Manage Files'. You will see a folder for each DICOM in the session, some of which will now
also have a DEFACED_ folder. Those are the ones where the data has been masked. 
12. Now de-select everything you do not want to download, which are all the DICOMs that have successfully been processed (both copies are kept, you need to ensure
you do not download the original one but only the DEFACED one). Then click on 'Download' and the download will commence. 
13. If you don't need to download the data, ensure you only use the defaced folders for research. If necessary delete the original DICOMs and 
ensure that data processing method that will be employed can process the niftis. Remember: nifti files can only be viewed in XNAT under 'Manage Files' and you can 
see them when you go to download the data for the project, always prefixed with DEFACED.
14. Repeat as necessary. 

If you run into any problems, please speak to Haleema or Dika.

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
