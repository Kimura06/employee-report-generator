
"""
Script to generate reports from employee data in CSV files.
Supports multiple report types, including payout reports.
"""

import argparse
import os
from typing import List, Dict, Any, Tuple, Callable


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate reports from employee data")
    parser.add_argument(
        "files",
        nargs="+",
        help="CSV files with employee data"
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Type of report to generate"
    )
    return parser.parse_args()


def read_csv(file_path: str) -> Tuple[List[str], List[List[str]]]:
    """
    Read CSV file and return headers and data.

    Args:
        file_path: Path to the CSV file

    Returns:
        Tuple of headers list and data rows list
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip().split('\n')

    if not content:
        return [], []

    headers = content[0].split(',')
    data = [row.split(',') for row in content[1:] if row]

    return headers, data


def parse_csv_to_dicts(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse CSV file into a list of dictionaries.

    Args:
        file_path: Path to the CSV file

    Returns:
        List of dictionaries with employee data
    """
    headers, data = read_csv(file_path)

    if not headers or not data:
        return []


    normalized_headers = []
    for header in headers:
        if header in ['hourly_rate', 'rate', 'salary']:
            normalized_headers.append('hourly_rate')
        else:
            normalized_headers.append(header)

    result = []
    for row in data:
        if len(row) != len(headers):
            continue

        employee = {}
        for i, value in enumerate(row):

            if normalized_headers[i] in ['hours_worked', 'hourly_rate']:
                try:
                    employee[normalized_headers[i]] = float(value)
                except ValueError:
                    employee[normalized_headers[i]] = 0
            else:
                employee[normalized_headers[i]] = value
        result.append(employee)

    return result


def generate_payout_report(employees_data: List[Dict[str, Any]]) -> str:

    if not employees_data:
        return "No data available for report."


    departments = {}
    for employee in employees_data:
        dept = employee.get('department', 'Unknown')
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(employee)


    report_lines = []
    report_lines.append(f"{'name':30} {'hours':>8} {'rate':>8} {'payout':>10}")

    grand_total_hours = 0
    grand_total_payout = 0

    for dept, employees in sorted(departments.items()):
        report_lines.append(f"{dept}")
        dept_total_hours = 0
        dept_total_payout = 0

        for employee in employees:
            name = employee.get('name', 'Unknown')
            hours = employee.get('hours_worked', 0)
            rate = employee.get('hourly_rate', 0)
            payout = hours * rate

            report_lines.append(f"-------------- {name:20} {hours:8.0f} {rate:8.0f} ${payout:9.0f}")

            dept_total_hours += hours
            dept_total_payout += payout

        report_lines.append(f"{' ':45} {dept_total_hours:8.0f} {' ':8} ${dept_total_payout:8.0f}")
        grand_total_hours += dept_total_hours
        grand_total_payout += dept_total_payout

    report_lines.append(f"\nTotal hours: {grand_total_hours:.0f}")
    report_lines.append(f"Total payout: ${grand_total_payout:.0f}")

    return "\n".join(report_lines)


def get_report_generator(report_type: str) -> Callable:

    report_generators = {
        'payout': generate_payout_report,
        # Additional report types can be added here
    }

    if report_type not in report_generators:
        raise ValueError(f"Unknown report type: {report_type}")

    return report_generators[report_type]


def main():

    args = parse_arguments()

    # Check if all files exist
    for file_path in args.files:
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}")
            return 1

    # Read and merge employee data from all files
    all_employees = []
    for file_path in args.files:
        all_employees.extend(parse_csv_to_dicts(file_path))

    try:

        report_generator = get_report_generator(args.report)


        report = report_generator(all_employees)
        print(report)

        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())