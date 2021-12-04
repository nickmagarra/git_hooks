import re
import sys
from subprocess import check_output

commit_msg_filepath = sys.argv[1]

branch = check_output(["git", "symbolic-ref", "--short", "HEAD"]).decode("utf-8").strip()
last_commit = check_output(["git", "log", "-1", f"origin/{branch}","--pretty='%s'"]).decode("utf-8").strip().replace("'","")

matches = re.findall(r"\d{1,9}", last_commit)

if len(matches) > 0:
    release = int(matches[0]) if len(matches) >= 1 else 0
    update = int(matches[1]) if len(matches) >= 2 else 0
    fix = int(matches[2]) if len(matches) >= 3 else 0
    draft = int(matches[3]) if len(matches) >= 4 else 0
else:
    release =  0
    update =  0
    fix = 0
    draft = 0

with open(commit_msg_filepath, "r+") as f:
    commit_msg = f.read()

    if commit_msg.startswith("rr", 0):
        new_version = f'{str(release + 1)}.0.0'
        new_message = (f'[{branch}][Release] {new_version} {commit_msg.replace("rr", "", 1).strip()}')
    elif commit_msg.startswith("uu", 0):
        new_version = f'{str(release)}.{str(update + 1)}.0'
        new_message = (f'[{branch}][Update] {new_version} {commit_msg.replace("uu", "", 1).strip()}')
    elif commit_msg.startswith("ff", 0):
        new_version = f'{str(release)}.{str(update)}.{str(fix + 1)}'
        new_message = (f'[{branch}][Fix] {new_version} {commit_msg.replace("ff", "", 1).strip()}')
    else:
        new_version = f'{str(release)}.{str(update)}.{str(fix)}.{(str(draft + 1))}'
        new_message = (f'[Draft] {new_version} {commit_msg.strip()} ')

    if len(new_message) > 0:
        f.truncate(0)
        f.seek(0)
        f.write(new_message.strip())
