from datetime import datetime, timedelta
import os
import pandas as pd


def print_and_save_account(account_dict):
    folder_path = './reports/accounts_info'

    # Print account details
    for key, value in account_dict.items():
        print(f"{key}: {value}")

    # Ensure the folder exists
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)

    existing_files = os.listdir(folder_path)
    file_numbers = []
    existing_file = None

    for filename in existing_files:
        if filename.startswith(f"{account_dict['login']}") and filename.endswith(".txt"):
            existing_file = filename
            break

    if existing_file:
        next_filename = existing_file
    else:
        for filename in existing_files:
            if filename.startswith(f"{account_dict['login']}") and filename.endswith(".txt"):
                try:
                    file_number = int(
                        filename[len(f"{account_dict['login']}_accountNo_"):-len(".txt")])
                    file_numbers.append(file_number)
                except ValueError:
                    continue

        next_file_number = max(file_numbers, default=0) + 1
        next_filename = f"{account_dict['login']
                           }_accountNo_{next_file_number}.txt"

    # Save account details to the new file or overwrite the existing one
    with open(os.path.join(folder_path, next_filename), "w") as file:
        for key, value in account_dict.items():
            file.write(f"{key}: {value}\n")


def make_report(pred_truth_report_df: pd.DataFrame):
    folder_path = './reports/predictions'

    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)

    existing_files = os.listdir(folder_path)
    file_numbers = []

    for filename in existing_files:
        if filename.startswith("predictionNo_") and filename.endswith(".csv"):
            try:
                number = int(filename[len("predictionNo_"):-len(".csv")])
                file_numbers.append(number)
            except ValueError:
                continue

    next_file_number = max(file_numbers, default=0) + 1
    next_filename = f"predictionNo_{next_file_number}.csv"

    try:
        pred_truth_report_df.to_csv(os.path.join(
            folder_path, next_filename), index=False)
        print(f'Saved {next_filename}!')
    except Exception as e:
        print(f"Error occurred when trying to save CSV file: {e}")


def round_down_to_nearest_15_minutes(dt):

    minutes = (dt.minute // 15) * 15

    rounded_dt = dt.replace(minute=minutes, second=0, microsecond=0)
    return rounded_dt
