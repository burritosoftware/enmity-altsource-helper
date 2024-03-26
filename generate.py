import json
import os
import zipfile
import plistlib
from entitlements import getEntitlements
from dotenv import load_dotenv
import requests
import shutil

api_key = ''
api_key_check = os.getenv('API_KEY')

if api_key_check:
  api_key = api_key_check
  load_dotenv()
else:
  load_dotenv()
  api_key = os.getenv('API_KEY')

BASE_URL = os.getenv("BASE_URL")
APP_KEY = os.getenv("APP_KEY")
BINARY_KEY = os.getenv("BINARY_KEY")
EXTRACT_TO = os.getenv("EXTRACT_TO")
OUTPUT_TO = os.getenv("OUTPUT_TO")
CACHE_TO = os.getenv("CACHE_TO")

# Create EXTRACT_TO folder
if not os.path.exists(EXTRACT_TO):
  os.makedirs(EXTRACT_TO)

# Create OUTPUT_TO folder
if not os.path.exists(OUTPUT_TO):
  os.makedirs(OUTPUT_TO)

# Create CACHE_TO folder
if not os.path.exists(CACHE_TO):
  os.makedirs(CACHE_TO)

headers = {
    'User-Agent': 'Enmity-Worker-Helper/1.0',
    'Authorization': f'token {api_key}'  # Replace YOUR_API_KEY with your actual API key
}

response = requests.get(BASE_URL + '/releases', headers=headers)

# AltStore source construction
source = {}
source['name'] = 'Enmity'
source['subtitle'] = 'The power of addons, all in your hand.'
source['iconURL'] = 'https://github.com/enmity-mod/assets/raw/main/icon-altstore.png'
source['headerURL'] = 'https://github.com/enmity-mod/assets/raw/main/Enmity_Banner%203.png'
source['website'] = 'https://enmity.unbound.rip'
source['tintColor'] = '#6D00FF'
source['apps'] = []
source['news'] = []

app = {
  "name": "Enmity",
  "bundleIdentifier": "com.hammerandchisel.discord",
  "developerName": "Enmity Team",
  "subtitle": "The power of addons, all in your hand.",
  "localizedDescription": f"The power of addons, all in your hand.",
  "iconURL": "https://taidums.are-really.cool/3n8avit.png",
  "tintColor": "#6D00FF",
  "category": "social",
  "screenshots": [
    "https://enmity-mod.github.io/repo/screenshots_iphone/chat.png",
    "https://enmity-mod.github.io/repo/screenshots_iphone/plugins.png",
    "https://enmity-mod.github.io/repo/screenshots_iphone/profile.png",
    "https://enmity-mod.github.io/repo/screenshots_iphone/settings.png"
  ],
}
app['versions'] = []

# Check if request was successful
if response.status_code == 200:
    releases = response.json()
    version_data = {}

    current_release = releases[0]['tag_name']
    # If lastGenerated.json does not exist, or if key "buildVersion" is not the same as the current release tag, then continue
    if not os.path.exists(f'{CACHE_TO}/lastGenerated.json') or json.load(open(f'{CACHE_TO}/lastGenerated.json', 'r'))['buildVersion'] != current_release:
        print(f'Starting to generate source for latest release {current_release}...')
    else:
      # If lastGenerated.json exists and key "buildVersion" is the same as latestPath[:-1], then exit
      print('No new releases found. Exiting.')
      exit()
    
    all_tags = requests.get(BASE_URL + '/tags', headers=headers).json()
    # Iterate over releases
    for release in releases:
        tag_name = release['tag_name']
        assets = release['assets']
        
        # Iterate over assets
        for asset in assets:
            if asset['name'] == APP_KEY:

              # Download the file at BASE_URL/tdAPP_KEY, then extract the Info.plist and binary from the zip in the Payload folder
              downloadURL = asset['browser_download_url']
              response = requests.get(downloadURL)
              
              with open(f'{EXTRACT_TO}/{APP_KEY}', 'wb') as f:
                f.write(response.content)
              
              with zipfile.ZipFile(f'{EXTRACT_TO}/{APP_KEY}', 'r') as zip_ref:
                zip_ref.extract(f'Payload/{BINARY_KEY}.app/Info.plist', path=EXTRACT_TO)
                zip_ref.extract(f'Payload/{BINARY_KEY}.app/{BINARY_KEY}', path=EXTRACT_TO)

              # Declare the plist to get useful info like CFBundleShortVersionString and CFBundleVersion
              plist = plistlib.load(open(f'{EXTRACT_TO}/Payload/Discord.app/Info.plist', 'rb'))

              doesNotExist = True
              # Check if a version with the same version and buildVersion already exists, if so, break the release loop
              for version in app['versions']:
                if version['version'] == plist['CFBundleShortVersionString'] and version['buildVersion'] == plist['CFBundleVersion']:
                  doesNotExist = False
                  break
              
              if doesNotExist:
                # If this is the first asset, we will add the entitlements and privacy to the app object
                if len(app['versions']) == 0:
                  ##
                  # Adding appPermissions including entitlements and privacy
                  ##

                  app['appPermissions'] = {}
                  app['appPermissions']['entitlements'] = []

                  for entitlement in getEntitlements(f'{EXTRACT_TO}/Payload/{BINARY_KEY}.app/{BINARY_KEY}'):
                    # Add entitlement to the entitlements array
                    app['appPermissions']['entitlements'].append(entitlement)

                  app['appPermissions']['privacy'] = {}

                  for key, value in plist.items():
                      # Check if the key starts with "NS" and ends with "UsageDescription"
                      if key.startswith("NS") and key.endswith("UsageDescription"):
                        # Add key-value pairs to the privacy object with the permission name being the key and the value being the value
                        app['appPermissions']['privacy'][key] = value

                # Get the number of bytes of the downloaded file at f'{EXTRACT_TO}/{APP_KEY}'
                appSize = os.path.getsize(f'{EXTRACT_TO}/{APP_KEY}')

                ##
                # Creating and adding the version
                ##

                # Get the last modified date of the latest build
                lastModified = asset['updated_at']

                # Get the version's commit message
                commit_msg = ''
                for tag in all_tags:
                  if tag['name'] == tag_name:
                    commit_msg = requests.get(tag['commit']['url'], headers=headers).json()['commit']['message']
                    break

                version = {
                  "version": plist['CFBundleShortVersionString'],
                  "buildVersion": plist['CFBundleVersion'],
                  "date": lastModified,
                  "localizedDescription": f"{tag_name} - {commit_msg}",
                  "downloadURL": downloadURL,
                  "size": appSize,
                  "minOSVersion": plist['MinimumOSVersion']
                }
                app['versions'].append(version)
                break

# Add app to the source
source['apps'].append(app)

# Output source variable as json to a file named apps.json
with open(f'{OUTPUT_TO}/apps.json', 'w') as f:
  f.write(json.dumps(source, indent=2))
  print('Source generated.')

# Generate lastGenerated.json and save it to CACHE_TO/lastGenerated.json
lastGenerated = {
  "buildVersion": current_release
}

with open(f'{CACHE_TO}/lastGenerated.json', 'w') as f:
  f.write(json.dumps(lastGenerated, indent=2))

# Delete the EXTRACT_TO folder and its contents
shutil.rmtree(EXTRACT_TO)