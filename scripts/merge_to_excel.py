import sys
import os
import pandas as pd

def convert_to_excel(csv_file, excel_file=None):
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        return

    # If no excel file provided, derive from csv name
    if not excel_file:
         excel_file = os.path.splitext(csv_file)[0] + ".xlsx"

    print(f"Processing '{csv_file}' -> '{excel_file}'...")

    try:
        # Read new data from CSV
        new_df = pd.read_csv(csv_file)
        
        if new_df.empty:
            print("Warning: CSV file is empty. Nothing to process.")
            return

        mode = 'w' # Default to write (overwrite/create)
        header = True
        
        if os.path.exists(excel_file):
            print(f"Found existing file '{excel_file}'. Appending data...")
            # Read existing data
            try:
                existing_df = pd.read_excel(excel_file)
                # Append new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            except Exception as e:
                print(f"Could not read existing Excel file (might be corrupted or empty): {e}")
                print("Creating new file instead.")
                combined_df = new_df
        else:
            print(f"Creating new file '{excel_file}'...")
            combined_df = new_df
        
        # Reorder columns if possible to make 'name' first
        desired_order = ['name', 'address', 'phone', 'website', 'rating', 'reviews_count']
        # Filter details that are actually in the df
        actual_cols = [col for col in desired_order if col in combined_df.columns]
        # Add any other columns that might be present but not in our list
        remaining_cols = [col for col in combined_df.columns if col not in actual_cols]
        
        final_cols = actual_cols + remaining_cols
        combined_df = combined_df[final_cols]
        
        # Sanitize data: Replace NaN/None with empty string to avoid import errors
        combined_df = combined_df.fillna("")

        # Write to Excel
        combined_df.to_excel(excel_file, index=False)
        print(f"Successfully saved to '{excel_file}' (Total rows: {len(combined_df)})")
        
    except Exception as e:
        print(f"Error processing Excel: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csv_to_excel.py <csv_file> [excel_output_file]")
        sys.exit(1)
        
    csv_filename = sys.argv[1]
    # Optional second argument for output filename
    output_excel = sys.argv[2] if len(sys.argv) > 2 else "master_data.xlsx"
    
    convert_to_excel(csv_filename, output_excel)
