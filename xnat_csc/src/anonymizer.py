import subprocess as sb
import pathlib as p
import pandas as pd
from enum import Enum

# Set path of resources directory and create if it doesn't already exist
resources_dir = p.Path(__file__).resolve().parent.parent / 'resources'
resources_dir.mkdir(parents=True, exist_ok=True)
# All DICOM tags i.e., to be downloaded as JSON from  https://github.com/innolitics/dicom-standard
dicom_standard = f'{resources_dir}/attributes.json'
# TODO: Upload CSC-specific anonymization rules e.g., based on manual review as a CSV
# DICOM tags assigned CSC-specific anonymization rules e.g., based on manual review
csc_dicom_tags = f'{resources_dir}/csc_dicom_tags.csv'
# DICOM tags identified by DICOM Supplement 142 along with recommended anonymization downloaded from
# https://wiki.cancerimagingarchive.net/display/Public/De-identification+Knowledge+Base
# https://wiki.cancerimagingarchive.net/download/attachments/3539047/PS-3.15-AnnexE-2011_ClinicalTrials_De-Identification.xlsx?api=v2
dicom_supplement_142 = f'{resources_dir}/dicom_supplement_142_table_e1_1.csv'

# Curl command to get DICOM Standard JSON from https://github.com/innolitics/dicom-standard
curl_cmd = ['curl',
            'https://raw.githubusercontent.com/innolitics/dicom-standard/master/standard/attributes.json',
            '-o',
            dicom_standard]


class Anonymizer:
    def __init__(self):
        self.anonymize = True
        # self.functions = Enum()
        self.supplement_142_df = pd.read_csv(p.Path(dicom_supplement_142))

        try:
            sb.run(curl_cmd, check=True, text=True)
            print("DICOM Standard JSON retrieved successfully.")
            self.dicom_standard_df = pd.read_json(p.Path(dicom_standard))
            self.anonymizer_tag_reference_df = pd.merge(self.dicom_standard_df, self.supplement_142_df, left_on='tag',
                                                        right_on='Tag')
            self.anonymizer_tag_reference_df = self.anonymizer_tag_reference_df[['tag', 'name', 'retired',
                                                                                 'Basic Profile']]
            self.anonymizer_tag_reference_df = self.anonymizer_tag_reference_df.rename(columns={
                'tag': 'Tag', 'name': 'Attribute Name', 'retired': 'Retired',
                'Basic Profile': 'DICOM Supplement 142 Basic Action'})
        except sb.CalledProcessError as e:
            print(f"Error running curl command: {e}")

    def create_anonymization_report(self, filepath: str, project: str):
        """
        Create anonymization report which includes anonymization approach based on project-requested tags, CSC DICOM
        tags, and DICOM Supplement 142.
        :param project: Filename of anonymization report i.e.
        :param filepath: Filepath to CSV containing project-requested tags.
        :return:
        """
        # TODO: Add function to check format of project-requested DICOM tags CSV e.g., column names, DICOM tags are
        #  double-quoted, etc.
        requested_tags_df = pd.read_csv(filepath)
        anonymization_report_df = pd.merge(requested_tags_df, self.supplement_142_df, left_on=['Tag'],
                                           right_on=['Tag'])
        anonymization_report_df = anonymization_report_df[['Tag', 'Attribute Name_x', 'Action', 'Basic Profile']]
        anonymization_report_df.rename(columns={'Attribute Name_x': 'Attribute Name',
                                                'Action': 'Requested Action',
                                                'Basic Profile': 'DICOM Supplement 142 Basic Action'
                                                })
        # Create anonymization report
        anonymization_report_df.to_csv(filepath=p.Path.cwd() / f'{project}_anonymization_tags')

        return anonymization_report_df

    def create_anonymization_script(self, filepath: str):
        pass

    # TODO: Move container run here
    def facemask(self, filepath: str):
        pass

    # TODO: Move pixel_cleaning.py here
    def remove_burnt_in_data(self, filepath: str):
        pass


class DICOMSupplement142(Enum):
    # -(xxxx,yyyy)
    D = 'Replace with a non-zero length value that may be a dummy value and consistent with the VR'
    Z = 'Replace with a zero length value, or a non-zero length value that may be a dummy value and consistent with ' \
        'the VR '
    X = 'Remove'

    K = 'Keep (unchanged for non-sequence attributes, cleaned for sequences)'
    C = 'Clean, that is replace with values of similar meaning known not to contain identifying information and ' \
        'consistent with the VR '

    # hashUID[(xxxx,yyyy)]
    U = 'Replace with a non-zero length UID that is internally consistent within a set of Instances'

    ZD = 'Z unless D is required to maintain IOD conformance (Type 2 versus Type 1)'
    XZ = 'X unless Z is required to maintain IOD conformance (Type 3 versus Type 2)'
    XD = 'X unless D is required to maintain IOD conformance (Type 3 versus Type 1)'
    XZD = 'X unless Z or D is required to maintain IOD conformance (Type 3 versus Type 2 versus Type 1)'
    XZU = 'X unless Z or replacement of contained instance UIDs (U) is required to maintain IOD conformance (Type 3 ' \
          'versus Type 2 versus Type 1 sequences containing UID references) '

    # CSC-specific
    E = 'Expose (unchanged for both non-sequence attributes and sequences)'


if __name__ == '__main__':
    project_anonymizer = Anonymizer()
