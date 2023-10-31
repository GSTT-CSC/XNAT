"""
Submodules to manage projects e.g., check submitted folder structure, submission YAML, XNAT ingestion file, etc.

The proposed folder structure is:

- new_project_request
    - cohort
        - xnat_ingest.csv
    - approvals
        - ig_approval.pdf
        - iras_form.pdf
    - anonymisation
        - DICOM_tags.csv
    - submission.yaml

* Apart from the files in the 'approvals' subdirectory, all subdirectory and filenames are required as-is.

"""

import pathlib as p
import yaml
import pandas as pd

# Set path of projects directory and create if it doesn't already exist
projects_dir = p.Path(__file__).resolve().parent.parent / 'projects'
test_directory = p.Path(__file__).resolve().parent.parent / 'tests'
projects_dir.mkdir(parents=True, exist_ok=True)
allowed_files = {'submission.yaml', 'submission.yml'}
allowed_subdirectories = {'cohort', 'approvals', 'anonymisation'}
required_key_values = {'project name', 'project shortname', 'project '
                                                            'id', 'project type', 'opt out required',
                       'qips approval number', 'anonymisation required', 'team', 'pi forename', 'pi surname', 'users',
                       'cohort'}
required_subkey_values = {'owners', 'size', 'key', 'inclusion criteria'}  # Subset of required_key_values
max_depth = 1
# TODO: Add requirement for NHS Number
required_xnat_ingestion_columns = {'patient id', 'accession number', 'study date'}
projectA = p.Path(__file__).resolve().parent.parent / 'tests/data/projectA'


def is_directory(filepath: p.Path) -> bool:
    if filepath.is_dir():
        return True
    else:
        return False


def check_directory_depth(project_directory: p.Path) -> bool:
    def calculate_max_depth(path, current_depth):
        if path.is_dir():
            # If it's a directory, iterate over its contents
            depths = []
            for item in path.iterdir():
                if item.is_dir():  # Check if the item is a directory
                    depths.append(calculate_max_depth(item, current_depth + 1))
            return max(depths) if depths else current_depth
        else:
            return current_depth

    if calculate_max_depth(project_directory, current_depth=0) == 1:
        return True
    else:
        return False


def is_valid_directory(project_directory: p.Path) -> bool:
    if not check_directory_depth(project_directory):
        return False
    else:
        for item in project_directory.iterdir():
            if item.is_dir():
                if item.name not in allowed_subdirectories:
                    print(f"Error: {item.name} is not an allowed subdirectory.")
                    return False
                if not any(item.iterdir()):
                    print(f"Error: {item.name} is empty.")
                    return False
            else:
                if item.name not in allowed_files:
                    print(f"Error: {item.name} is not an allowed file.")
                    return False
    return True


def is_valid_submission(project_directory: p.Path) -> bool:
    submission_file = list(project_directory.glob('submission.yml')) + list(project_directory.glob('submission.yaml'))
    if not any(submission_file):
        print('Submission file does not exist.')
        return False
    else:
        with open(f'{project_directory}/submission.yml', 'r') as file:
            submission_dict = yaml.load(file, Loader=yaml.FullLoader)
        for key in required_key_values:
            if key in submission_dict and submission_dict[key] is None or submission_dict[key] == '':
                return False
            else:
                if key in submission_dict and isinstance(submission_dict[key], list) and isinstance(
                        submission_dict[key][0], dict):
                    for subdict in submission_dict[key]:
                        for subkey, subvalue in subdict.items():
                            if subkey in required_subkey_values and subdict[subkey] is None or subdict[subkey] == '':
                                return False
    return True


def is_valid_xnat_ingestion_file(filepath: p.Path) -> bool:
    xnat_ingest_file = filepath
    # Check if xnat_ingest.csv exists and is a normal file e.g., not a directory, symlink, etc.
    if xnat_ingest_file.exists() and xnat_ingest_file.is_file():
        try:
            xnat_ingest_df = pd.read_csv(xnat_ingest_file)
        # Empty file
        except pd.errors.EmptyDataError:
            return False
    else:
        return False

    # Check if there are exactly 3 columns
    if len(xnat_ingest_df.columns) != 3:
        return False

    # Change columns to lowercase for easy checks
    xnat_ingest_df.columns = xnat_ingest_df.columns.str.lower()

    # TODO: Raise helpful errors
    if required_xnat_ingestion_columns != set(xnat_ingest_df.columns):
        return False

    # Check if Patient ID is empty or has values with less than 8 characters
    if xnat_ingest_df['patient id'].isna().all() or xnat_ingest_df["patient id"].astype(str).str.len().min() < 8:
        return False

    # Check if both Study Date and Accession Number are empty
    if (xnat_ingest_df["study date"].isna().all() & xnat_ingest_df["accession number"].isna()).all():
        return False

    # Check if Study Date is empty or in YYYYMMDD format
    if xnat_ingest_df["study date"].notna().all() and xnat_ingest_df["accession number"].isna().all():
        try:
            # Check if dates are valid
            xnat_ingest_df['study date'] = pd.to_datetime(xnat_ingest_df['study date'], format='%Y%m%d').dt.strftime(
                '%Y%m%d')
        except ValueError:
            return False
    return True


class ProjectManager:
    def __init__(self, project_directory: p.Path):
        # First basic check
        if not is_directory(project_directory):
            raise NotADirectoryError(f'{project_directory.name} is not a directory.')
        # Check if any function returns False
        else:
            self._valid_directory = is_valid_directory(project_directory)
            self._valid_submission = is_valid_submission(project_directory)
            self._valid_xnat_ingestion_file = is_valid_xnat_ingestion_file(project_directory)

    def check_project(self):
        validity_checks = [self._valid_directory, self._valid_submission, self._valid_xnat_ingestion_file]
        if any(not item for item in validity_checks):
            return False
        else:
            return True

    def create_config(self):
        pass


class InvalidProjectSubmissionError(Exception):
    def __init__(self, specific_error='Please review and re-submit'):
        self.message = f'Invalid project submission. {specific_error}.'
        super().__init__(self.message)


