from dotenv import load_dotenv; load_dotenv()
import os
from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient(os.getenv('MONGO_URI'))
db = client['customer_management']

# Clean up the rogue Ph nested field first
db['customer'].update_many(
    {"Ph": {"$exists": True}},
    {"$unset": {"Ph": ""}}
)
print("Cleaned Ph field")

# Now simulate exactly what app.py does after our fix
doc = db['customer'].find_one({"Id": "002"})
print("\nBEFORE:")
print("  Ph.no:", doc.get("Ph.no"))
print("  Name:", doc.get("Name"))

# Mutate and replace
doc["Name"] = "VEL UPDATED"
doc["Ph.no"] = "1234567890"
doc["Address"] = "TEST ADDRESS 123"
doc["Model"] = "TEST MODEL"
doc["updated_at"] = datetime.now(timezone.utc)
doc["updated_by"] = "admin"

result = db['customer'].replace_one({"Id": "002"}, doc)
print("\nreplace_one matched:", result.matched_count, "| modified:", result.modified_count)

doc2 = db['customer'].find_one({"Id": "002"})
print("\nAFTER:")
print("  Ph.no:", doc2.get("Ph.no"))
print("  Name:", doc2.get("Name"))
print("  Address:", doc2.get("Address"))
print("  Keys:", list(doc2.keys()))
