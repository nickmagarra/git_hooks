#!/usr/bin/python3

import re
import sys
from subprocess import check_output

RELEASE = UPDATE = FIX = DRAFT = 0
REPLACE_VER = ""


def get_version(message: str):
    matches = re.findall(r"(?:\d+\.)+\d+", message)

    if len(matches) > 0:
        # DEBUG
        print(f"Found Version in Commit: {matches}")

        global RELEASE
        global UPDATE
        global FIX
        global DRAFT
        global REPLACE_VER

        version = matches[0].split('.')
        RELEASE = int(version[0]) if len(version) >= 1 else 0
        UPDATE = int(version[1]) if len(version) >= 2 else 0
        FIX = int(version[2]) if len(version) >= 3 else 0
        DRAFT = int(version[3]) if len(version) >= 4 else 0
        REPLACE_VER = matches[0]


if __name__ == "__main__":
    try:
        commit_msg_filepath = sys.argv[1]
    except Exception as e:
        print(f"Read commit message failed. Error: {repr(e)}")
        sys.exit(1)

    branch = check_output(["git", "symbolic-ref", "--short", "HEAD"]).decode("utf-8").strip()
    last_commit = check_output(["git", "log", "-1", f"origin/{branch}", "--pretty='%s'"]).decode("utf-8").strip().replace("'", "")
    # DEBUG
    print(f"LAST Commit Message: {last_commit}")

    # Try to get version from last commit
    get_version(last_commit)

    # DEBUG
    print(f"RELEASE: {str(RELEASE)}")
    print(f"UPDATE: {str(UPDATE)}")
    print(f"FIX: {str(FIX)}")
    print(f"DRAFT: {str(DRAFT)}")

    with open(commit_msg_filepath, "r+") as f:
        commit_msg = f.read()
        # DEBUG
        print(f"NEW Commit MESSAGE: {commit_msg}")

        # Try to get version from new commit
        get_version(commit_msg)

        if commit_msg.startswith("rr", 0):
            new_version = f'{str(RELEASE + 1)}.0.0'
            new_message = (f'[{branch}](Release) {new_version} {commit_msg.replace("rr", "", 1).replace(REPLACE_VER, "", 1).strip()}')
        elif commit_msg.startswith("uu", 0):
            new_version = f'{str(RELEASE)}.{str(UPDATE + 1)}.0'
            new_message = (f'[{branch}](Update) {new_version} {commit_msg.replace("uu", "", 1).replace(REPLACE_VER, "", 1).strip()}')
        elif commit_msg.startswith("ff", 0):
            new_version = f'{str(RELEASE)}.{str(UPDATE)}.{str(FIX + 1)}'
            new_message = (f'[{branch}](Fix) {new_version} {commit_msg.replace("ff", "", 1).replace(REPLACE_VER, "", 1).strip()}')
        elif commit_msg.startswith("init", 0):
            new_version = '0.0.0.1'
            new_message = (f'(Initial) {new_version}')
        else:
            new_version = f'{str(RELEASE)}.{str(UPDATE)}.{str(FIX)}.{str(DRAFT + 1)}'
            new_message = (f'(Draft) {new_version} {commit_msg.replace("dd", "", 1).replace(REPLACE_VER, "", 1).strip()}')

        if len(new_message) > 0:
            f.truncate(0)
            f.seek(0)
            f.write(new_message.strip())
