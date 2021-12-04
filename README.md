# Usefull hooks for Git

## prepare-commit-msg
This hook is a Python script. Libraries used: re, sys, subprocess

What hook do:
- Detect current branch name and last commit message from remote
- Lookup version number in last commit message
- Lookups keywords triggers in new commit message (**rr** - release, **uu** - update, **ff** - fix)
- Generates incremented version number based on detected triggers (version based on template: **X.Y.Y** where **X** for release, **Y** for update, **Z** for fix)
- If trigger detected, hook generates brand new commit message with template:

<code>{Branch name} {Type of commit by trigger} {new version number of commit} {Commit message by user input}.</code>

- If no trigger detected, hook just adds version numder to user's text

# How to use
- Copy file to **.git/hooks/** folder inside local cloned repo
- Don't forget to make it executable **<code>chmod +x prepare-commit-msg</code>**
- Use triggers in your commit message:

For release: <code>git commit -m "rr Some release notes"</code>

For update: <code>git commit -m "uu Some update notes"</code>

For fix: <code>git commit -m "ff Some update notes"</code>
