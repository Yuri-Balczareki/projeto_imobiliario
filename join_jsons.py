import os
import pandas as pd
import numpy as np
import json
import time


def process_json_file(input_path):
    # Read the original JSON file
    with open(input_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    # Extract the nested part under the key "details"
    nested_part = original_data.get('search', {}).get('result', {}).get('listings', {})
    # Save the nested part as a new JSON file
    with open('intermediare_nested.json', 'w') as file:
        json.dump(nested_part, file, indent=2)
    #TODO: what is that
    nested = 'intermediare_nested.json'
    df = pd.read_json(nested)
    # Read the nested JSON file into a DataFrame
    df_nested = pd.json_normalize(df["listing"])

    return df_nested

def process_all_json_files(input_dir, output_dir):
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize the timer
    start_time = time.time()

    dfs = pd.DataFrame()
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_path = os.path.join(input_dir, filename)
            df_nested = process_json_file(input_path)
            dfs = pd.concat([dfs, df_nested], ignore_index=True)

    # Save the aggregated DataFrame as a JSON file
    final_json_output_filename = 'final_output.json'
    final_json_output_path = os.path.join(output_dir, final_json_output_filename)
    dfs.to_json(final_json_output_path, orient='records', indent=2)

    # Calculate and print the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processing time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    # Give the dir for the JSON files and where to save it. 
    input_directory = 'JSONs/outros/Rent'
    output_directory = 'JSONs/outros/Rent/unified'

    process_all_json_files(input_directory, output_directory)


