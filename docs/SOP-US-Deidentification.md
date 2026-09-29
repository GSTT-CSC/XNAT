[![image](https://github.com/GSTT-CSC/XNAT/blob/main/assets/CSC-logo-trans-sm.png?raw=true)](https://github.com/GSTT-CSC/XNAT)

# Guide for the De-identification of Ultrasound DICOM Images

This SOP describes the process for removing burnt-in annotations (overlaid patient information) from ultrasound DICOM images using the deid Python library with a custom configuration.

[View Repo](https://github.com/GSTT-CSC/XNAT) . [Report Error](https://github.com/GSTT-CSC/XNAT/issues) . [Request Feature](https://github.com/GSTT-CSC/XNAT/issues) . [Request Document](https://github.com/GSTT-CSC/XNAT/issues)

| | |
|---|---|
| **Document Status** | Draft |
| **Scanners** | GE, Siemens, Hitachi, Philips |
| **Scripts Last Updated** | 25 June 2026 — Kristina Zeljic |

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#preparing-the-data-collection-and-copying">Preparing the Data (Collection and Copying)</a></li>
    <li><a href="#folder-structure">Folder Structure</a></li>
    <li>
      <a href="#inspecting-the-dataset-before-processing">Inspecting the Dataset Before Processing</a>
      <ul>
        <li><a href="#identify-all-manufacturers-present">Identify All Manufacturers Present</a></li>
        <li><a href="#find-a-specific-scanner-file-for-testing-optional">Find a Specific Scanner File for Testing (Optional)</a></li>
        <li><a href="#check-image-properties-of-a-file">Check Image Properties of a File</a></li>
      </ul>
    </li>
    <li>
      <a href="#the-de-identification-script-pixelcleaningpy">The De-identification Script (pixelcleaning.py)</a>
      <ul>
        <li><a href="#running-the-script">Running the Script</a></li>
        <li><a href="#rgb-conversion">RGB Conversion</a></li>
      </ul>
    </li>
    <li><a href="#the-configuration-file-deidcustom">The Configuration File (deid.custom)</a></li>
    <li><a href="#adding-a-new-scanner">Adding a New Scanner</a></li>
    <li><a href="#troubleshooting">Troubleshooting</a></li>
    <li>
      <a href="#uploading-de-identified-data-back-to-xnat">Uploading De-identified Data Back to XNAT</a>
      <ul>
        <li><a href="#label-behaviour">Label Behaviour</a></li>
        <li><a href="#running-the-upload-script">Running the Upload Script</a></li>
      </ul>
    </li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- OVERVIEW -->
## Overview

This SOP describes the process for removing burnt-in annotations (overlaid patient information) from ultrasound DICOM images using the deid Python library with a custom configuration. The pipeline handles multiple scanner manufacturers with different locations of burnt-in annotations.

The workflow has two parts: first copying the relevant ultrasound sessions out of the XNAT archive into a personal working directory (see [Preparing the Data](#preparing-the-data-collection-and-copying)), then running the de-identification scripts against that copy (see [Inspecting the Dataset Before Processing](#inspecting-the-dataset-before-processing) onward). Two files are involved in de-identification itself:

- `pixelcleaning.py` — the main Python script that processes each DICOM file
- `deid.custom` — the configuration file that defines which pixel regions to blank for each scanner type

These files can be found at: [https://github.com/GSTT-CSC/XNAT/tree/main/csc_xnat](https://github.com/GSTT-CSC/XNAT/tree/main/csc_xnat)

<!-- PREREQUISITES -->
## Prerequisites

**For running the script:**

| Tool | Purpose |
| --- | --- |
| Python 3 | Runtime for the de-identification script |
| deid | DICOM de-identification library |
| pydicom | Reading and writing DICOM files |
| numpy | Image array manipulation (RGB conversion) |
| xnat_batch_upload | Reuploading de-identified images to XNAT |

**For data checks:**

| Tool | Purpose |
| --- | --- |
| dcmtk | Command-line DICOM inspection tools |
| MicroDICOM | Windows DICOM viewer for verifying output |
| WinSCP + Notepad++ | Remote file editing |

<!-- PREPARING THE DATA -->
## Preparing the Data (Collection and Copying)

Log in to the server via PuTTY, then complete both the archive lookup and the copy as follows:

1. Open PuTTY and log in to the server with your admin account.

2. Navigate to the relevant project inside the archive:

   ```bash
   cd /home/hnadmin/xnat-data/xnat/archive/<projectname>
   ```

3. Identify the ultrasound sessions using either the folder naming convention or file type. Only these folders should be selected for processing.

4. Create a personal working folder in your home directory:

   ```bash
   mkdir /home/<yourusername>/<yourfolder>/<projectname>
   ```

5. Copy only the identified ultrasound sessions into your working directory (for example, in the PharosAI project, ultrasound images have 'US' in their filename):

   ```bash
   cp -r /home/hnadmin/xnat-data/xnat/archive/<projectname>/arc001/PH_*US* /home/<yourusername>/<projectname>
   ```

6. Restrict access to the copied data so that only your user account can access potentially identifiable data:

   ```bash
   chmod -R 700 /home/<yourusername>/<projectname>
   ```

> :warning: **Important:** All de-identification steps in this SOP (from [Inspecting the Dataset Before Processing](#inspecting-the-dataset-before-processing) onward) must be run against this working copy — never against the original data in the XNAT archive. Note that `pixelcleaning.py` converts RGB images to grayscale in place, overwriting the file it's given (see [RGB Conversion](#rgb-conversion)).

<!-- FOLDER STRUCTURE -->
## Folder Structure

The expected input folder structure is:

```text
<ProjectFolder>/
  PatientFolder1/
    SCANS/          <-- original DICOM files go here
  PatientFolder2/
    SCANS/
  clean/            <-- this folder is created by the script and de-identified
                        images are automatically written here
  ...
```

The script is run against the top-level folder (e.g. `ProjectFolder`), not the `SCANS` subfolder.

The `clean/` output mirrors the subfolder structure found under the input folder, so `PatientFolder1/SCANS/sub1/file.dcm` is written to `clean/PatientFolder1/sub1/file.dcm`. The script also automatically skips anything already inside `clean/`.

<!-- INSPECTING THE DATASET BEFORE PROCESSING -->
## Inspecting the Dataset Before Processing

<!-- IDENTIFY ALL MANUFACTURERS PRESENT -->
### Identify All Manufacturers Present

Before running de-identification on a new dataset, check which scanner manufacturers are present in your data. This ensures the `deid.custom` config has the right rules for all scanners.

**Step 1** — Index all DICOM files:

```bash
find /path/to/<ProjectFolder> -name "*.dcm" > /tmp/dcmlist.txt
```

**Step 2** — Extract and list unique manufacturers:

```bash
find /path/to/<ProjectFolder> -type f -name "*.dcm" -exec dcmdump {} + 2>/dev/null | grep "(0008,0070)" | sort | uniq
```

This prints the Manufacturer DICOM field (tag `0008,0070`) for every unique value found. Example output:

```text
(0008,0070) LO [GE Healthcare]              # Manufacturer
(0008,0070) LO [Siemens Medical Systems]    # Manufacturer
(0008,0070) LO [Hitachi Medical Corporation] # Manufacturer
(0008,0070) LO [Philips Medical Systems]    # Manufacturer
```

If an unexpected manufacturer appears (e.g. Bioptics), check its modality before adding a rule to the `deid.custom` script. It may be a non-ultrasound scanner caught by accident.

<!-- FIND A SPECIFIC SCANNER FILE FOR TESTING -->
### Find a Specific Scanner File for Testing (Optional)

To find a file from a specific manufacturer for testing:

```bash
grep -il philips $(cat /tmp/dcmlist.txt)
```

Replace `philips` with any manufacturer name. This returns the full file paths of matching files.

<!-- CHECK IMAGE PROPERTIES OF A FILE -->
### Check Image Properties of a File

To check a file's photometric interpretation, dimensions, or other properties:

```bash
dcmdump /path/to/file.dcm 2>/dev/null | grep -i photometric
dcmdump /path/to/file.dcm 2>/dev/null | grep -iE "rows|columns"
```

Or open the file in MicroDICOM and check the metadata panel.

<!-- THE DE-IDENTIFICATION SCRIPT -->
## The De-identification Script (pixelcleaning.py)

The script walks through all DICOM files in a given folder, detects RGB images and converts them to grayscale if needed, then applies the deid cleaning rules.

<!-- RUNNING THE SCRIPT -->
### Running the Script

Command line:

```bash
python3 /path/to/pixelcleaning.py /path/to/PatientFolder
```

Or run it with no arguments for an interactive prompt:

```bash
python3 /path/to/pixelcleaning.py
Enter the input directory containing DICOM files: /path/to/PatientFolder
```

> :information_source: **Setup requirement:** `deid.custom` is a configuration (recipe) file saved in the **bash** folder.

<!-- RGB CONVERSION -->
### RGB Conversion

Some scanners (e.g. Siemens) save images as RGB (3 colour channels) rather than grayscale.

The script detects this automatically by checking the `PhotometricInterpretation` DICOM field. If it is RGB, it converts to grayscale in memory and saves it back over the original file (`ds.save_as(fullpath)`) before running the deid cleaning step.

<!-- THE CONFIGURATION FILE -->
## The Configuration File (deid.custom)

This file defines which rectangular regions to blank for each scanner. Coordinates are in the format `x1,y1,x2,y2` from the top-left corner of the image.

| Scanner | Coordinates Blanked |
| --- | --- |
| GE | 0,0 to 1600,120 (top strip, widened from earlier version) |
| Siemens | 0,0 to 1000,55 (top strip, enlarged from earlier version) |
| Hitachi | 0,0 to 1024,77 (top strip, full width — unchanged) |
| Philips | 0,0 to 1023,75 (top strip, full width — unchanged) |

> :information_source: The file keeps a commented-out catch-all rule (`LABEL Blank Image` / coordinates `all`) as a reference for why a blanket rule isn't used — enabling it blanks entire images for scanners that lack a `SequenceOfUltrasoundRegions` field, such as Siemens.

<!-- ADDING A NEW SCANNER -->
## Adding a New Scanner

To add support for a new scanner manufacturer:

1. Find a sample file using: `grep -il manufacturername $(cat /tmp/dcmlist.txt)`
2. Open the file in MicroDICOM and note the image dimensions and how many pixels of overlay appear at the top.
3. Add a new `LABEL` block to `deid.custom` (in the same folder as `pixelcleaning.py`) with the correct coordinates.
4. Run the script on a test file and verify in MicroDICOM that the overlay is blanked and the image is otherwise intact.

The RGB conversion in the Python script will automatically handle any new RGB scanner without any changes needed to the script.

<!-- TROUBLESHOOTING -->
## Troubleshooting

| Problem | Likely Cause / Fix |
| --- | --- |
| Wrong area of image is blanked | Coordinates in `deid.custom` are incorrect. Open a sample file in MicroDICOM, measure the overlay region, and update the coordinates. |
| "Invalid directory" error on startup | The path passed in (or typed at the interactive prompt) doesn't exist or is misspelled. Re-check the path and try again. |
| Script errors that it can't find `deid.custom` | `deid.custom` must be saved in the same folder as `pixelcleaning.py`. |
| Syntax error / invalid character | Likely caused by smart quotes or other characters introduced by WinSCP's built-in editor. Use Notepad++ instead and retype any quote characters manually. |
| New manufacturer not being cleaned | Add a `LABEL` block to `deid.custom`. Check the exact Manufacturer string first using `dcmdump`. |

<!-- UPLOADING DE-IDENTIFIED DATA BACK TO XNAT -->
## Uploading De-identified Data Back to XNAT

`xnat_batch_upload.sh` batch-uploads cleaned session folders (the `clean/` output from `pixelcleaning.py`) back into XNAT's prearchive via the REST API. It logs in once, then loops through a range of session folders, zipping each one's DICOM files and uploading it.

Ensure that you review the prearchive and archive manually in the XNAT web UI after running this script.

<!-- LABEL BEHAVIOUR -->
### Label Behaviour

- **Session label** = the local folder name itself. Rename the folder first if you need a different session label in XNAT.
- **Subject label** = read automatically from the `PatientID` tag (`0010,0020`) of the first `.dcm` file in the folder — not typed in. Check with `dcmdump` beforehand if unsure what value is there.
- **Batch range** is by index, based on alphabetical folder order — run `ls` on the base directory first to confirm which folder is which index.

<!-- RUNNING THE UPLOAD SCRIPT -->
### Running the Upload Script

```bash
./xnat_batch_upload.sh
```

You'll be prompted for XNAT credentials, project name, base directory, and a start/end index (defaults to 1–50), then asked to confirm before anything uploads.

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

* [Kristina Zeljic Cozma](mailto:kristina.cozma@nhs.net) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Dika Vilic](mailto:Dijana.Vilic@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Project Link](https://github.com/GSTT-CSC/XNAT)
