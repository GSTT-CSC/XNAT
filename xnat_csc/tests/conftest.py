import pandas as pd
import pytest
import yaml
import pathlib as p

test_directory = p.Path(__file__).resolve().parent


@pytest.fixture
def text_filepath():
    file_path = test_directory / 'data/notadirectory.txt'
    with open(file_path, "w") as file:
        pass  # Create empty, non-directory file
    yield file_path  # Pass the filepath to test
    file_path.unlink()  # Clean up i.e., remove, after test


# Reusable CSV fixture
@pytest.fixture
def csv_file(test_case):
    data = None
    test_case_name = test_case.param
    if test_case_name == 'correct_columns_no_values':
        columns = ['Patient ID', 'Accession Number', 'Study Date']
        data = pd.DataFrame(columns=columns)

    elif test_case_name == 'incorrect_number_of_columns':
        columns = ['Patient ID', 'Accession Number']
        data = pd.DataFrame(columns=columns)

    elif test_case_name == 'correct_columns_incorrect_date':
        data = {
            'Patient ID': ['12345678'],
            'Accession Number': ['R123456789'],
            'Study Date': ['20230229'],
        }

    elif test_case_name == 'correct_columns_and_values':
        data = {
            'Patient ID': ['12345678'],
            'Accession Number': ['R123456789'],
            'Study Date': ['20230228'],
        }
    test_case_df = pd.DataFrame(data)
    filepath = p.Path(f'{test_directory}/data/{test_case_name}.csv')
    test_case_df.to_csv(filepath, index=False)
    yield filepath
    if filepath.exists():
        filepath.unlink()

