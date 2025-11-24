#!/c/Program Files/Python39/python

import re
import sys
from subprocess import check_output

try:
    commit_msg_filepath = sys.argv[1]
except Exception as e:
    print(f"Read commit message failed. Error: {e}")
    sys.exit(1)

branch = check_output(["git", "symbolic-ref", "--short", "HEAD"]).decode("utf-8").strip()

try:
    last_commit = check_output(["git", "log", "-1", f"origin/{branch}", "--pretty='%s'"]).decode("utf-8").strip().replace("'", "")
except:
    last_commit = ""

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

print(f"branch: {str(branch)}")
print(f"release: {str(release)}")
print(f"update: {str(update)}")
print(f"fix: {str(fix)}")
print(f"draft: {str(draft)}")

with open(commit_msg_filepath, "r+", encoding="utf8") as f:
    commit_msg = f.read()
    
    
    if commit_msg.startswith("init", 0):
        prefix = "Initial"
        new_version = '0.0.0.1'
        new_message = (f'[{branch}] {prefix} {new_version}')
    else:
        if commit_msg.startswith("rr", 0):
            prefix = "Release"
            new_version = f'{str(release + 1)}.0.0'
        elif commit_msg.startswith("uu", 0):
            prefix = "Update"
            new_version = f'{str(release)}.{str(update + 1)}.0'
        elif commit_msg.startswith("ff", 0):
            prefix = "Fix"
            new_version = f'{str(release)}.{str(update)}.{str(fix + 1)}'
        elif commit_msg.startswith("dd", 0):
            prefix = "Draft"
            new_version = f'{str(release)}.{str(update)}.{str(fix)}.{str(draft + 1)}'
        else:
            commit_msg = "dd " + commit_msg
            prefix = "Draft"
            new_version = f'{str(release)}.{str(update)}.{str(fix)}.{str(draft + 1)}'
    
        commit_msg_parsed = "" if len(commit_msg.strip()) == 2 else ": " + commit_msg.strip()[2:]
        new_message = (f'[{branch}] {prefix} {new_version}{commit_msg_parsed}')

    if len(new_message) > 0:
        f.truncate(0)
        f.seek(0)
        f.write(new_message.strip())
