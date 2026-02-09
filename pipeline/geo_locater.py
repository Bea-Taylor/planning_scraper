# from database.comments import Comments
import time
import random
import requests
import concurrent.futures
import multiprocessing
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm.notebook import tqdm  # Use tqdm.notebook for Jupyter progress bars
import urllib3
from geopy.geocoders import Nominatim

# Create a Nominatim geocoder
geolocator = Nominatim(user_agent="ai4ci-sc4")

# from database.comments import Comments

# from database.comments import Comments

# c = Comments(env="dev")
# df = c.read_all(output_format="dataframe")
# df = df[
#     (df["address"].notnull()) &
#     (df["address"] != "") &
#     (df["lat"].isna()) &
#     (df["lon"].isna())
#     ]

# df

# Determine number of available CPUs and set a reasonable limit
MAX_WORKERS = max(1, min(8, multiprocessing.cpu_count() - 1))  # Limit to max 4 workers to avoid API overload
print(f"Using {MAX_WORKERS} workers for parallel processing")

# Nominatim usage policy requires a 1 second delay between requests
# https://operations.osmfoundation.org/policies/nominatim/
MIN_DELAY = 2.0  # Minimum delay in seconds between requests to same worker
MAX_DELAY = 3.0  # Maximum delay for randomization
# Format: [min_lat, min_lon, max_lat, max_lon]
greater_london_bbox = [51.2867602, -0.5103751, 51.6918741, 0.3340155]
def is_in_greater_london(lat, lon):
    bbox = [51.2867602, -0.5103751, 51.6918741, 0.3340155]
    return bbox[0] <= lat <= bbox[2] and bbox[1] <= lon <= bbox[3]

def setup_session():
    """Create and return a requests session with retry configuration and increased timeout"""
    session = requests.Session()
    # Increase timeout from default 1s to 10s
    retry = Retry(
        total=3,  # Maximum number of retries
        backoff_factor=2,  # Exponential backoff
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods=["GET", "POST"]  # Methods to retry
    )
    # Set longer timeout (10 seconds) to handle slow connections
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def get_coords(address, geolocator, session=None, start=1):
    """Get coordinates for an address by incrementally building it from the end."""
    if session is None:
        session = setup_session()

    if not address or address.strip().lower() == "none":
        return address, None, None

    address_parts = address.split()
    if start > len(address_parts):
        return address, None, None

    # Start building address from the end
    new_address = " ".join(address_parts[-start:])
    print(f"Trying address: '{new_address}' (start={start})")

    try:
        coords = geolocator.geocode(new_address, timeout=10)
        if coords is None:
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            return get_coords(address, geolocator, session, start + 1)
        else:
            print(f"Success: '{new_address}' → Lat: {coords.latitude}, Lon: {coords.longitude}")
            return new_address, coords.latitude, coords.longitude

    except (urllib3.exceptions.ConnectTimeoutError,
            urllib3.exceptions.MaxRetryError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout):
        time.sleep(random.uniform(5.0, 10.0))  # Longer backoff
        return address, None, None
    except Exception as e:
        return address, None, None

def process_comments_parallel(df, geolocator, c):
    """Process all comments in parallel using ThreadPoolExecutor with better rate limiting"""
    # Filter comments with addresses
    comments_to_process = []
    for i, comment in df.iterrows():
        if comment.get("address"):
            comments_to_process.append(comment)

    # Create a progress bar
    pbar = tqdm(total=len(comments_to_process), desc="Geocoding Addresses")
    results = []

    # Process function for each comment
    def process_comment(comment):
        session = setup_session()
        retries = 0
        address = comment["address"]

        while retries < 3:  # Reduced maximum retries to avoid excessive API calls
            try:
                _, lat, lon = get_coords(address, geolocator, session=session)
                if(is_in_greater_london(lat, lon)):
                    # Always respect Nominatim's usage policy with a strict delay
                    # This is critical to avoid being blocked
                    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                    pbar.update(1)
                    return comment["comment_id"], lat, lon
                else:
                    print("Lat and lon are out of bbox")
                    return comment["comment_id"], None, None

            except Exception as e:
                retries += 1
                # print(f"Error processing {address}: {e}. Retry {retries}/3")
                # Exponential backoff between retries
                backoff_time = 2 ** retries + random.uniform(0, 1)
                time.sleep(backoff_time)

        pbar.update(1)
        return comment["comment_id"], None, None

    # Use ThreadPoolExecutor which works better in Jupyter notebooks
    # Save successfully processed results to avoid reprocessing on failure
    processed_results = {}

    # Process in smaller batches to better manage rate limits
    batch_size = min(20, len(comments_to_process))  # Process up to 20 at a time

    for i in range(0, len(comments_to_process), batch_size):
        batch = comments_to_process[i:i+batch_size]
        # print(f"Processing batch {i//batch_size + 1}/{(len(comments_to_process) + batch_size - 1)//batch_size}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_comment = {executor.submit(process_comment, comment): comment
                                 for comment in batch}

            for future in concurrent.futures.as_completed(future_to_comment):
                try:
                    comment_id, lat, lon = future.result()
                    if lat is not None and lon is not None:
                        # Update database
                        try:
                            c.update_lat_lon_by_comment_id(comment_id, lat, lon)
                            processed_results[comment_id] = (lat, lon)
                            results.append((comment_id, lat, lon))
                            print(f"Updated database: comment_id={comment_id}, lat={lat}, lon={lon}")
                        except Exception as e:
                            pass
                            # print(f"Database update error for comment {comment_id}: {e}")
                except Exception as e:
                    print(f"Exception processing comment: {e}")

        # Add a delay between batches to be extra careful with rate limits
        if i + batch_size < len(comments_to_process):
            batch_delay = random.uniform(2.0, 5.0)
            # print(f"Pausing for {batch_delay:.2f} seconds between batches...")
            time.sleep(batch_delay)

    pbar.close()
    print(f"Geocoding complete. Successfully processed {len(processed_results)} out of {len(comments_to_process)} addresses.")
    return results

# Function to resume processing from a specific point (in case notebook crashes)
def resume_processing(df, geolocator, c, start_index=0):
    """Resume processing from a specific index in the dataframe"""
    print(f"Resuming processing from index {start_index}")
    return process_comments_parallel(df.iloc[start_index:], geolocator, c)

# # Example usage:
# results = process_comments_parallel(df, geolocator, c)
# #
# # If your notebook crashes, you can resume from where you left off:
# # results = resume_processing(df, geolocator, c, start_index=50)