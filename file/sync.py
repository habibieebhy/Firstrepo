import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Load mapping ---
with open('config/material_map.json') as f:
    MATERIAL_SHEET_MAP = json.load(f)

# --- Google Sheets Auth ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds/service_account.json", scope)
client = gspread.authorize(creds)

# --- Fetch from Tally (localhost:9000) ---
print("Fetching material data from Tally...")
resp = requests.get("http://localhost:9000")
xml_data = resp.text

# --- Simple XML parsing (brute method) ---
import xml.etree.ElementTree as ET
root = ET.fromstring(xml_data)

entries = []
for item in root.findall(".//Material"):
    name = item.text
    rate = item.find("../Rate").text
    qty = item.find("../Quantity").text
    vendor = item.find("../Vendor").text
    entries.append((name, rate, qty, vendor))

# --- Update sheets ---
for (name, rate, qty, vendor) in entries:
    sheet_id = MATERIAL_SHEET_MAP.get(name)
    if not sheet_id:
        print(f"No sheet found for {name}")
        continue

    sheet = client.open_by_key(sheet_id).sheet1
    sheet.append_row([name, rate, qty, vendor])
    print(f"Updated {name} to sheet.")

print("Sync complete!")