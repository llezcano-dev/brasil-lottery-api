import pyexcel as pe

def xlsx_to_csv(input_file, output_file):
    # Load the spreadsheet data
    sheet = pe.get_sheet(file_name=input_file)
    # Save it as CSV
    sheet.save_as(output_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python xlsx_to_csv.py input.xlsx output.csv")
        sys.exit(1)
    xlsx_to_csv(sys.argv[1], sys.argv[2])
    print(f"CSV file '{sys.argv[2]}' generated successfully.")

