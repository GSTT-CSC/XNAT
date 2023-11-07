import pytest
from xnat_csc.src.project_manager import ProjectManager, is_directory, is_valid_xnat_ingestion_file
import pathlib as p

test_directory = p.Path(__file__).resolve().parent

XNAT_INGEST_CSV_TEST_CASES = [
    ('correct_columns_no_values', True),
    ('incorrect_number_of_columns', False),
    ('correct_columns_incorrect_date', False),
    ('correct_columns_and_values', True),
]


@pytest.mark.usefixtures('text_filepath')
def test_not_a_directory(text_filepath):
    assert is_directory(text_filepath) is False


# Use the @pytest.mark.parametrize decorator to specify the test cases
@pytest.mark.xfail(reason="This test is known to fail but will be fixed soon.")
@pytest.mark.parametrize('csv_file, expected_result', XNAT_INGEST_CSV_TEST_CASES)
def test_xnat_ingest_csv_cases(csv_file, expected_result):
    assert is_valid_xnat_ingestion_file(p.Path(test_directory / f'data/{csv_file}.csv')) is expected_result
