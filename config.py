import json
import platform
import os

platform_details = platform.platform()
print(f"Platform Details: {platform_details}")
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
if "macos" in str(platform_details).lower():
    env = "local"
else:
    env = "prod"


with open("config.json") as user_file:
    file_contents = user_file.read()

constant = json.loads(file_contents)
