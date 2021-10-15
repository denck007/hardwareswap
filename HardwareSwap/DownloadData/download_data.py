
import datetime
import json
import glob
import os
import pandas as pd
import requests
import time


def timestamp_to_iso(ts):
    return datetime.datetime.isoformat(datetime.datetime.fromtimestamp(ts))

def get_data_in_timestamp_range(start_time, end_time, data_dir, sleep_time_on_ratelimit=3):
    print(f"Start date: {timestamp_to_iso(start_time)} End Date: {timestamp_to_iso(end_time)}")
    #print(f"Start_time: {start_time} End_time: {end_time} Duration: {end_time - start_time}")
    retry_count = 0
    iter_start_timestamp = start_time
    while iter_start_timestamp < end_time:
        print(f"\rCurrent start date: {timestamp_to_iso(iter_start_timestamp)}", end="")
        if retry_count > 10:
            print(f"\n\n\tHit limit of {retry_count}, exiting!")
            break
        
        # 0.5 causes no rate limiting
        time.sleep(0.3)
        url = f"https://api.pushshift.io/reddit/search/submission/?subreddit=hardwareswap&sort=asc&sort_type=created_utc&after={iter_start_timestamp}&before={end_time}&size=100"
        response = requests.get(url)
        
        if response.status_code == 429: #if rate limited, then sleep for a little bit
            print(f"Rate limited, sleeping for {sleep_time_on_ratelimit:.1f} seconds")
            retry_count += 1
            time.sleep(sleep_time_on_ratelimit)
            continue
        elif response.status_code == 521: # cloudflare says server is down
            print(f"\nGot 521 status code, sleeping {sleep_time_on_ratelimit:.1f} seconds and trying again")
            retry_count += 1
            time.sleep(sleep_time_on_ratelimit)
            continue
        elif response.status_code>500:
            print(f"\nUnknown Status Code: {response.status_code}. Sleeping for {sleep_time_on_ratelimit:.1f} seconds and trying again\nContent: {response.content}\nurl: {url}")
            retry_count += 1
            time.sleep(sleep_time_on_ratelimit)
            continue
        elif response.status_code > 201:
            raise ValueError(f"\nbad response from server for: Status Code: {response.status_code}\nContent: {response.content}\nurl: {url}")
        
        retry_count  = 0 # made it this far so not retrying
        data = response.json()['data']
        if len(data) == 0:
            print(f"\n\tDone! len(data) == 0")
            break

        time_file_start = data[0]['created_utc']
        time_file_end = data[-1]['created_utc']

        if iter_start_timestamp == time_file_end:
            print(f"\n\tDone! iter_start_timestamp == time_file_end")
            break

        fname =  f"data_{time_file_start}-{time_file_end}.json"
        with open(os.path.join(data_dir, fname), 'w') as fp:
            json.dump(data, fp)
        iter_start_timestamp = time_file_end

def find_existing_time_range_on_disk(data_dir):
    """
    Return the start and end time for all data on disk
    """
    start_time = int(time.time())
    end_time = 0
    file_count = 0
    for fname in glob.glob(os.path.join(data_dir, "data_*-*.json")):
        file_count += 1
        start, end = os.path.splitext(os.path.basename(fname))[0].split("_")[1].split("-")
        start_time = min(start_time, int(start))
        end_time = max(end_time, int(end))
    return start_time, end_time

def load_dataframe_from_disk(data_glob_pattern, limit=None):
    all_data = []
    fnames = glob.glob(data_glob_pattern)
    if limit is not None:
        fnames = fnames[:limit]

    for fname in fnames:
        with open(fname, 'r') as fp:
            data = json.load(fp)
        all_data.extend(data)
    df = pd.DataFrame(all_data)
    df.sort_values("created_utc", inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df


def remove_duplicate_rows(df, column, additional=[]):
    """
    Remove any rows that have duplicate values in column
    Also remove any keys that are in 'additional
    """
    counts = df[column].value_counts()
    to_remove = counts[counts>1].index.to_list()
    to_remove +=  additional
    df = df[~df[column].isin(to_remove)].copy()
    df.reset_index(inplace=True, drop=True)
    return df
