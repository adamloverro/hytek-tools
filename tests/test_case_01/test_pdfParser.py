import os
import pandas as pd
import pytest
from performance.pdfParser import run_most_improved, write_to_file

def test_pdf_parser():
    # Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "test_input", "most-improved-team-manager-20240717.pdf")
    output_folder = os.path.join(current_dir, "test_output")
    output_prefix = "most_improved"

    # Run the script
    df, improved_df = run_most_improved(input_pdf)
    write_to_file(
        df,
        improved_df,
        output_folder=output_folder,
        output_file_prefix=output_prefix,
        csv=True,
        excel=True
    )

    # Define expected output files
    expected_raw_csv = os.path.join(output_folder, f"{output_prefix}_raw_data.csv")
    expected_improved_csv = os.path.join(output_folder, f"{output_prefix}.csv")
    expected_excel = os.path.join(output_folder, f"{output_prefix}.xlsx")

    # Check if files are created
    assert os.path.exists(expected_raw_csv), "Raw data CSV file was not created."
    assert os.path.exists(expected_improved_csv), "Improved data CSV file was not created."
    assert os.path.exists(expected_excel), "Excel file was not created."

    # Validate CSV content
    expected_raw_df = pd.read_csv(os.path.join(output_folder, "gold_most_improved_raw_data.csv"))
    expected_improved_df = pd.read_csv(os.path.join(output_folder, "gold_most_improved.csv"))

    actual_raw_df = pd.read_csv(expected_raw_csv)
    actual_improved_df = pd.read_csv(expected_improved_csv)

    pd.testing.assert_frame_equal(expected_raw_df, actual_raw_df, check_dtype=False)
    pd.testing.assert_frame_equal(expected_improved_df, actual_improved_df, check_dtype=False)

    # Validate Excel content
    expected_excel_df = pd.read_excel(os.path.join(output_folder, "gold_most_improved.xlsx"), sheet_name=None)
    actual_excel_df = pd.read_excel(expected_excel, sheet_name=None)

    for sheet_name, expected_sheet_df in expected_excel_df.items():
        actual_sheet_df = actual_excel_df[sheet_name]
        pd.testing.assert_frame_equal(expected_sheet_df, actual_sheet_df, check_dtype=False)
