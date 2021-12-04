# Usefull hooks for Git

## prepare-commit-msg
This hook is a Python script. Libraries used: re, sys, subprocess

What hook do:
- Detect current branch name and last commit message from remote
- Lookup version number in last commit message
- Lookups keuwords in new commit message
- If trigger detected, hook generates brand new commit message with template:

<code>{Type of commit (release, update, fix)} {new version number of commit} {Commit message by user input}.</code>

- If no trigger detected, hook just adds version numder to user's text

If **release** or **update** triggered, branch name will be added in front of all 
