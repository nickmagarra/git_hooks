#!/usr/bin/python3

import re
import sys
from subprocess import check_output

try:
    commit_msg_filepath = sys.argv[1]
except Exception as e:
    print(f"Read commit message failed. Error: {e}")
    sys.exit(1)

branch = check_output(["git", "symbolic-ref", "--short", "HEAD"]).decode("utf-8").strip()
last_commit = check_output(["git", "log", "-1", f"origin/{branch}", "--pretty='%s'"]).decode("utf-8").strip().replace("'", "")

matches = re.findall(r"(?:\d+\.)+\d+", last_commit)

if len(matches) > 0:
    version = matches[0].split('.')
    release = int(version[0]) if len(version) >= 1 else 0
    update = int(version[1]) if len(version) >= 2 else 0
    fix = int(version[2]) if len(version) >= 3 else 0
    draft = int(version[3]) if len(version) >= 4 else 0
else:
    release = 0
    update = 0
    fix = 0
    draft = 0

print(f"release: {str(release)}")
print(f"update: {str(update)}")
print(f"fix: {str(fix)}")
print(f"draft: {str(draft)}")

with open(commit_msg_filepath, "r+") as f:
    commit_msg = f.read()

    if commit_msg.startswith("rr", 0):
        new_version = f'{str(release + 1)}.0.0'
        new_message = (f'[{branch}](Release) {new_version} {commit_msg.replace("rr", "", 1).strip()}')
    elif commit_msg.startswith("uu", 0):
        new_version = f'{str(release)}.{str(update + 1)}.0'
        new_message = (f'[{branch}](Update) {new_version} {commit_msg.replace("uu", "", 1).strip()}')
    elif commit_msg.startswith("ff", 0):
        new_version = f'{str(release)}.{str(update)}.{str(fix + 1)}'
        new_message = (f'[{branch}](Fix) {new_version} {commit_msg.replace("ff", "", 1).strip()}')
    elif commit_msg.startswith("init", 0):
        new_version = '0.0.0.1'
        new_message = (f'(Initial) {new_version}')
    else:
        new_version = f'{str(release)}.{str(update)}.{str(fix)}.{str(draft + 1)}'
        new_message = (f'(Draft) {new_version} {commit_msg.replace("dd", "", 1).strip()} ')

    if len(new_message) > 0:
        f.truncate(0)
        f.seek(0)
        f.write(new_message.strip())
