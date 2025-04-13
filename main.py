import pandas as pd
import numpy as np
import yfinance as yf
import os
import time

from yfoptions import get_DF_optionchain, daysleft

from dotenv import load_dotenv
from datetime import datetime

from utils import upload_to_hf_dataset, download_from_hf_dataset, load_hf_dataset

# Get current date and time
# current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
current_datetime = datetime.now().strftime("%Y-%m-%d")

#Output folder for option chains
outputfolder = 'optionchains'

# Create the gurufocus folder if it doesn't exist
if not os.path.exists(outputfolder):
    os.makedirs(outputfolder)



# Load environment variables from .env file
load_dotenv()

# Get the name of the HuggingFace dataset for TradingView to read from
dataset_name_TradingView_input = os.getenv('dataset_name_TradingView_input')

# Get the name of the HuggingFace dataset for YfOptions to export
dataset_name_YfOptions_output = os.getenv('dataset_name_YfOptions_output')

# Get the Hugging Face API token from the environment; either set in .env file or in the environment directly in GitHub
HF_TOKEN_YfOptions = os.getenv('HF_TOKEN_YfOptions')

#Load lastest TradingView DataSet from HuggingFace Dataset which is always america.csv
# download_from_hf_dataset("america.csv", "AmirTrader/TradingViewData", HF_TOKEN_YfOptions)
DF = load_hf_dataset("america.csv", HF_TOKEN_YfOptions, dataset_name_TradingView_input)

# get ticker list by filtering only above 1 billion dollar company
# DF = pd.read_csv(f'america_2024-03-01.csv')
tickerlst  = list(DF.query('`Market Capitalization`>100e9').Ticker)
# tickerlist = ['INDO', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NFLX', 'META', 'NVDA', 'AMD', 'INTC', 'IBM', 'CSCO', 'ORCL', 'QCOM', 'TXN', 'AVGO', 'ADBE', 'CRM', 'NFLX', 'PYPL', 'SNAP']

#measure runtime
start_time = time.time()

option_chain_data_lst = []
for ticker in tickerlst:

    try:
        # Get the option chain data
        option_chain_data = get_DF_optionchain(ticker)
        # Get the option chain data
        option_chain_data_lst.append(option_chain_data)

    except ValueError as e:
        print(f"Error retrieving data for {ticker}: {e}")
        continue

# Combine all option chain data into a single DataFrame
option_chain_data_combined = pd.concat(option_chain_data_lst, ignore_index=True)

# Print the combined option chain data
print(option_chain_data_combined.head())

end_time = time.time()
print(f"Execution time: {end_time - start_time} seconds")
# Save the combined option chain data to a CSV file
option_chain_data_combined.to_csv(os.path.join(outputfolder,'optionchain.csv'), index=False)

file_path = fr'{outputfolder}/optionchain_{current_datetime}.csv'
latest_file_path = fr'{outputfolder}/optionchain.csv'

option_chain_data_combined.to_csv(file_path,index=False)
option_chain_data_combined.to_csv(latest_file_path,index=False)

# Upload each file to the dataset
upload_to_hf_dataset(file_path, dataset_name_YfOptions_output, HF_TOKEN_YfOptions, repo_type="dataset")
upload_to_hf_dataset(latest_file_path, dataset_name_YfOptions_output, HF_TOKEN_YfOptions, repo_type="dataset")



