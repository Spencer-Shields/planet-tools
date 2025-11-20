"""
This script is for mass-acquiring PlanetScope scene imagery.

It works in two phases. In the first phase, Planet's Data API is queried to get the IDs of scenes which meet certain criteria.
In the second phase, these IDs are passed to Planet's Orders API, they are ordered, and then they are downloaded.
Multiple orders are automatically created and placed if you want more than 500 scenes.

Users must edit this script to make it usable.
Search for the tag TO_EDIT to find places to make modifications. Some are mandatory (e.g. inputing your API key), others are optional (e.g., filtering scene IDs or selecting pr-processing tools).
"""
#%% import libraries, setup API and session
import json
import os
import pathlib
import time
import pandas as pd
import requests

#TO_EDIT: input your API key if it is not set an an environment variable
# if your Planet API Key is not set as an environment variable, you can paste it below
if os.environ.get('PL_API_KEY', ''):
    API_KEY = os.environ.get('PL_API_KEY', '')
else:
    API_KEY = 'INSERT API KEY HERE'

#setup session
session = requests.Session()

#Authenticate
session.auth = (API_KEY, '')


#%% use Data API to get list of scene IDs for download
"""
This cell queries the Planet Data API to return scenes which meet provided criteria. The output is a dataframe of scenes and metadata.
At the very least, you'll want to provide your area of interest as well as the date range to search for images. You may also want to filter out cloud-covered scenes.

Reference https://docs.planet.com/develop/apis/data/item-search/#andfilter
"""
#URL for querying Data API
data_url = 'https://api.planet.com/data/v1'

#URL for returning search results from data API query
quick_search_url = '{}/quick-search'.format(data_url)

#define function to print formatted json
def p(data):
    print(json.dumps(data, indent=2))

#TO_EDIT: the range of dates you want imagery for
#date filter
start_date = '2013-01-01'
end_date = '2024-12-31'

date_filter = {
    'type': 'DateRangeFilter',
    'field_name': 'acquired',
    'config': {
        'gte': f'{start_date}T00:00:00.000Z', #start date
        'lte': f'{end_date}T23:59:59.999Z' #end date
    }
}

#TO_EDIT: provide the coordinates defining your area of interest. Polygons or points are acceptable.
#Geometry filter
aoi_geojson = {'type': 'Polygon',
 'coordinates': [[[-122.78314758004296, 53.33052904360998],
   [-122.70020261459693, 53.3282536221804],
   [-122.69657565349696, 53.37451376544108],
   [-122.779611532762, 53.37679163403286],
   [-122.78314758004296, 53.33052904360998]]]}

geometry_filter = {
    'type': 'GeometryFilter',
    'field_name': 'geometry',
    'relation': 'intersects', #look for scenes which intersect the area of interest
    'config': aoi_geojson
}

# Use instrument filter to specify what generations of satellite you want imagery from
# instrument_filter = {
#     'type': 'StringInFilter',
#     'field_name': 'instrument',
#     'config': [
#         'PS2',  #dove classic (4 band)
#         'PS2.SD', #dove-r (4 band)
#         'PSB.SD' #super dove (4 band or 8 band)
#     ]
# }

#cloud filter
max_cloud_cover = 0.99 #max proportion cloud cover (1 = 100%)

cloud_filter = {
    'type': 'RangeFilter',
    'field_name': 'cloud_cover',
    'config': {
        'lte': 0.99 #less than or equal to 99% cloud cover
        ,'gte': 0 #greater than or equal to 0% cloud cover
    }
}

#quality filter
quality_filter = {
    'type': 'StringInFilter',
    'field_name': 'quality_category',
    'config': ['standard'] #only standard quality
}

#asset filter (to only get scenes where surface reflectance and udm2 assets are available)

asset_filter = {
  "type": "AndFilter",
  "config": [
    {
      "type": "AssetFilter",
      "config": ["analytic_sr"]      # analytic SR asset
    }
  ]
}

#permission filter (only get scenes that can be downloaded)
permission_filter ={
      "type": "PermissionFilter",
      "config": [
        #   "assets:download"
        "assets.ortho_analytic_4b_sr:download",
        "assets.ortho_udm2:download"
          ]
    }
  

#TO_EDIT: double check filters before searching for Planet scenes
#combine filters
combined_filter = {
    'type': 'AndFilter',
    'config': [
        date_filter,
        geometry_filter,
        cloud_filter,
        quality_filter,
        # asset_filter,
        permission_filter
        # instrument_filter
    ]
}

#set up request
item_types = ['PSScene'] #look for planetscope scenes (as opposed to RapidEye, SkySat, etc)

data_request = {
    'item_types': item_types,
    'filter': combined_filter
}

#send request to data API quick search endpoint
data_response = session.post(quick_search_url, json=data_request)

#assign response to a variable
data_response_geojson = data_response.json()

#paginate through response to aggregate all results (since results get returned in chunks of 250 per page)
links = data_response_geojson['_links']
feats = data_response_geojson['features']

all_features = feats
next_link = data_response_geojson['_links']['_next']

while next_link:
    next_response = session.get(next_link)
    next_response_geojson = next_response.json()
    next_feats = next_response_geojson['features']
    all_features.extend(next_feats)
    next_link = next_response_geojson['_links'].get('_next', None)

#TO_EDIT: do additional filtering using dataframe if desired (just make sure that the final dataframe to be passed on is called all_features_df)
#put all results in a dataframe
all_features_df = pd.DataFrame([feat['properties'] for feat in all_features])
all_features_df['id'] = [feat['id'] for feat in all_features]


# %% Set up to place order
"""
This step takes the scene ids from the last phase and orders them. The maximum number of scenes that can be ordered for local delivery at one time is
500. This script will automatically break the list of ids into groups of 500 and place separate orders for each group.
You will want to specify your order name, output directory for downloading imagery, and "product bundle" (i.e., do you want 4band or 8band imagery, 
and do you also want the udm2 assets?). You may also want to add pre-processing to the imagery, such as clipping to the AOI, harmonization with Sentinel-2, or coregistration.
"""
#extract ids of scenes to order from features dataframe
desired_feat_ids = all_features_df['id'].tolist()

#remove duplicate ids
desired_feat_ids = list(set(desired_feat_ids))

#set url for interacting with orders API
orders_url = 'https://api.planet.com/compute/ops/orders/v2'

#reorder the strings so that similar dates are grouped together
desired_feat_ids.sort()

#organize ids into chunks due to order size limits
chunk_size = 500
desired_feat_chunks = [
    desired_feat_ids[i:i+chunk_size] 
    for i in range(0, len(desired_feat_ids), chunk_size)
    ]

#check authentication (want response code 200)
order_response = requests.get(orders_url, auth=session.auth)
order_response

#set content type 
headers = {'content-type': 'application/json'}

#make poll for success function to monitor order status
def poll_for_success(order_url, auth, num_loops=30, wait_sec = 30):
    count = 0
    while(count < num_loops):
        count += 1
        r = requests.get(order_url, auth=auth)
        response = r.json()
        state = response['state']
        print(state)
        end_states = ['success', 'failed', 'partial']
        if state in end_states:
            break
        time.sleep(wait_sec)

#make function for downloading results
def download_results(results, download_dir='data', overwrite=False):
    results_urls = [r['location'] for r in results]
    results_names = [r['name'] for r in results]
    print('{} items to download'.format(len(results_urls)))
    
    for url, name in zip(results_urls, results_names):
        path = pathlib.Path(os.path.join(download_dir, name))
        
        if overwrite or not path.exists():
            print('Downloading {} to {}'.format(name, path))
            r = requests.get(url, allow_redirects=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(r.content)
        else:
            print('{} already exists, skipping {}'.format(path, name)) 

#define a timer function (to help prevent throwing a 405 error when placing orders too quickly)
def countdown_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        time_format = f'Wait to order next chunk: {mins:02}:{secs:02}'
        print(time_format, end='\r')
        time.sleep(1)
        seconds -= 1
    print("00:00\nTime's up!")

#TO_EDIT: check product bundle selection (analytic_sr_udm2 is 4band, use analytic_8b_sr_udm2 for 8band)
#define product bundle to order
product_bundle = 'analytic_sr_udm2' #4band surface reflectance with UDM2

#TO_EDIT: make basename for the order (chunk number will be added automatically)
#make base name for ordering all the chunks
order_basename = f'Quesnel_Clipped_Product={product_bundle}_Time={start_date}to{end_date}_MaxCloudProp={max_cloud_cover}_MaxChunkSize={chunk_size}'

#%%place orders for each chunk or get urls if orders have already been placed

#get names and ids of previous orders, place in dataframe
orders_response = requests.get(orders_url, auth=session.auth)
previous_orders = order_response.json()['orders']
previous_order_names = [r['name'] for r in previous_orders]
previous_order_ids = [r['id'] for r in previous_orders]
previous_orders_df = pd.DataFrame({
    'name': previous_order_names,
    'id': previous_order_ids})
previous_orders_df = previous_orders_df.assign(url = lambda x: orders_url + '/' + x['id'])

#initiate list to store order urls
order_urls_list = []

#loop over chunks of ids, place order if not already placed, otherwise get order url
for i in range(len(desired_feat_chunks)):

    #make order name
    order_name = order_basename + f'_chunk_{i+1}_of_{len(desired_feat_chunks)}'

    #proceed if order name is not in previous orders
    if order_name not in previous_orders_df['name'].tolist():
        print('Placing order for chunk' + str(i + 1) + ' of ' + str(len(desired_feat_chunks)))

        #get current chunk of scene ids
        chunk = desired_feat_chunks[i]

        #set up order request
        order_request = {
            "name": order_name,
            'order_type': 'partial', #ignore scene ids that cannot be downloaded
            "products": [
                {
                    "item_ids": chunk,
                    "item_type": "PSScene",
                    "product_bundle": product_bundle #get 4band imagery
                }
            ],
            "delivery": {
                "archive_type": "zip",
                "single_archive": True
            },
            "tools": [ #TO_EDIT: add preprocessing tools such as clipping, harmonization, coregistration, band math, etc
        {
            "clip": {
                "aoi": Quesnel_bbox  # must be valid Polygon or MultiPolygon GeoJSON
            }
        }
    ]
}

        #place order
        order_response = requests.post(
            orders_url,
            auth =session.auth,
            data=json.dumps(order_request),
            headers=headers
        )
        print(order_response.json())
        order_id = order_response.json()['id']
        print(order_id)
        order_url = orders_url + '/' + order_id

        order_urls_list.append(order_url)
        countdown_timer(1) #wait 1 second between orders to avoid rate limit errors

    else:
        print('Order exists for chunk' + str(i + 1) + ' of ' + str(len(desired_feat_chunks)))
        order_url = previous_orders_df.loc[previous_orders_df['name'] == order_name, 'url'].values[0]
        order_urls_list.append(order_url)

#%% Download orders using order urls

#TO_EDIT: set ouptut directory for downloading results
#define output directory to download results to
download_dir = pathlib.Path(rf'D:\Quesnel\data\planet_scenes\raw_additional\{order_basename}')
if not download_dir.exists(): #create directory if it doesn't exist
    download_dir.mkdir(parents=True, exist_ok=True)

#loop over order urls, download to download directory
for order_url in order_urls_list:

    print('Processing order: ' + order_url)

    #poll for success
    poll_for_success(order_url, session.auth, num_loops=300, wait_sec=60)

    #get order results
    r = requests.get(order_url, auth=session.auth)
    response = r.json()
    results = response['_links']['results']

    #download results
    download_results(results, download_dir=download_dir)



