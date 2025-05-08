


import os
import pytest
import tempfile
from unittest.mock import patch, mock_open
import io
import sys

from main import (
    parse_arguments,
    read_csv,
    parse_csv_to_dicts,
    generate_payout_report,
    get_report_generator,
    main
)


def test_parse_arguments():
    """Test argument parsing"""
    with patch('sys.argv', ['main.py', 'file1.csv', 'file2.csv', '--report', 'payout']):
        args = parse_arguments()
        assert args.files == ['file1.csv', 'file2.csv']
        assert args.report == 'payout'


def test_read_csv():
    """Test reading CSV file"""
    csv_content = "id,name,department,hours_worked,hourly_rate\n1,John Doe,IT,160,50\n2,Jane Smith,HR,150,60"

    with patch('builtins.open', mock_open(read_data=csv_content)):
        headers, data = read_csv('dummy.csv')

    assert headers == ['id', 'name', 'department', 'hours_worked', 'hourly_rate']
    assert data == [['1', 'John Doe', 'IT', '160', '50'], ['2', 'Jane Smith', 'HR', '150', '60']]


def test_read_csv_empty_file():
    """Test reading empty CSV file"""
    with patch('builtins.open', mock_open(read_data="")):
        headers, data = read_csv('dummy.csv')

    assert headers == []
    assert data == []


def test_parse_csv_to_dicts():
    """Test parsing CSV to dictionaries"""
    csv_content = "id,name,department,hours_worked,hourly_rate\n1,John Doe,IT,160,50\n2,Jane Smith,HR,150,60"

    with patch('builtins.open', mock_open(read_data=csv_content)):
        result = parse_csv_to_dicts('dummy.csv')

    assert len(result) == 2
    assert result[0]['name'] == 'John Doe'
    assert result[0]['department'] == 'IT'
    assert result[0]['hours_worked'] == 160.0
    assert result[0]['hourly_rate'] == 50.0


def test_parse_csv_to_dicts_normalize_rate_column():
    """Test normalizing different rate column names"""
    csv_content = "id,name,department,hours_worked,rate\n1,John Doe,IT,160,50"

    with patch('builtins.open', mock_open(read_data=csv_content)):
        result = parse_csv_to_dicts('dummy.csv')

    assert result[0]['hourly_rate'] == 50.0

    csv_content = "id,name,department,hours_worked,salary\n1,John Doe,IT,160,50"

    with patch('builtins.open', mock_open(read_data=csv_content)):
        result = parse_csv_to_dicts('dummy.csv')

    assert result[0]['hourly_rate'] == 50.0


def test_parse_csv_to_dicts_malformed_row():
    """Test handling malformed rows"""
    csv_content = "id,name,department,hours_worked,hourly_rate\n1,John Doe,IT,160\n2,Jane Smith,HR,150,60"

    with patch('builtins.open', mock_open(read_data=csv_content)):
        result = parse_csv_to_dicts('dummy.csv')

    assert len(result) == 1
    assert result[0]['name'] == 'Jane Smith'


def test_generate_payout_report():
    """Test generating payout report"""
    employees_data = [
        {'name': 'John Doe', 'department': 'IT', 'hours_worked': 160, 'hourly_rate': 50},
        {'name': 'Jane Smith', 'department': 'IT', 'hours_worked': 150, 'hourly_rate': 60},
        {'name': 'Bob Brown', 'department': 'HR', 'hours_worked': 170, 'hourly_rate': 40}
    ]

    report = generate_payout_report(employees_data)

    assert 'IT' in report
    assert 'HR' in report
    assert 'John Doe' in report
    assert 'Jane Smith' in report
    assert 'Bob Brown' in report
    assert '$8000' in report  # John's payout
    assert '$9000' in report  # Jane's payout
    assert '$6800' in report  # Bob's payout
    assert 'Total hours: 480' in report
    assert 'Total payout: $23800' in report


def test_generate_payout_report_empty():
    """Test generating payout report with no data"""
    report = generate_payout_report([])
    assert report == "No data available for report."


def test_get_report_generator_valid():
    """Test getting valid report generator"""
    generator = get_report_generator('payout')
    assert callable(generator)
    assert generator == generate_payout_report


def test_get_report_generator_invalid():
    """Test getting invalid report generator"""
    with pytest.raises(ValueError):
        get_report_generator('invalid_report')


def create_temp_csv_file(content):
    """Create a temporary CSV file with the given content"""
    tmp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False)
    tmp_file.write(content)
    tmp_file.close()
    return tmp_file.name


@pytest.fixture
def sample_csv_files():
    """Create sample CSV files for testing"""
    file1_content = "id,name,department,hours_worked,hourly_rate\n1,John Doe,IT,160,50\n2,Jane Smith,IT,150,60"
    file2_content = "id,name,department,hours_worked,rate\n3,Bob Brown,HR,170,40\n4,Alice Green,HR,140,45"

    file1_path = create_temp_csv_file(file1_content)
    file2_path = create_temp_csv_file(file2_content)

    yield [file1_path, file2_path]

    # Clean up temporary files
    os.unlink(file1_path)
    os.unlink(file2_path)


def test_main_success(sample_csv_files, capfd):
    """Test successful execution of main function"""
    with patch('sys.argv', ['main.py'] + sample_csv_files + ['--report', 'payout']):
        result = main()

        out, _ = capfd.readouterr()

        assert result == 0
        assert 'IT' in out
        assert 'HR' in out
        assert 'John Doe' in out
        assert 'Jane Smith' in out
        assert 'Bob Brown' in out
        assert 'Alice Green' in out


def test_main_file_not_found(capfd):
    """Test main function with non-existent file"""
    with patch('sys.argv', ['main.py', 'non_existent_file.csv', '--report', 'payout']):
        result = main()

        out, _ = capfd.readouterr()

        assert result == 1
        assert 'Error: File not found' in out


def test_main_invalid_report_type(sample_csv_files, capfd):
    """Test main function with invalid report type"""
    with patch('sys.argv', ['main.py'] + sample_csv_files + ['--report', 'invalid']):
        result = main()

        out, _ = capfd.readouterr()

        assert result == 1
        assert 'Error: Unknown report type' in out