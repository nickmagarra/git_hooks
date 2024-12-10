# Usefull hooks for Git

![Nice and clear commits!](media/commit_example.png)

## prepare-commit-msg

This hook is a Python script. Libraries used: **re**, **sys**, **subprocess**

What hook do:

- Detect current branch name and last commit message from remote
- Lookup version number in last commit message
- Lookups keywords triggers in new commit message (**rr** - release, **uu** - update, **ff** - fix, **dd** - draft)
- Generates incremented version number based on detected triggers (version based on template: **W.X.Y.Z** where **W** for release, **X** for update, **Y** for fix, **Z** for draft).
- If trigger detected, hook generates brand new commit message with template:

`[Branch name][Type of commit by trigger] [New version number of commit] [User commit message]`

- If no trigger detected, hook adds (Draft) prefix and version numder in front of user's text
- If parent numbers incremented, all other will be reset to "0", draft will be removed from commit

## How to use

- Copy file to **.git/hooks/** folder inside local cloned repo
- Don't forget to make it executable `chmod +x prepare-commit-msg.py`
- Use triggers in your commit message:

- **For release:** `git commit -m "rr Some release notes"`
- **For update:** `git commit -m "uu Some update notes"`
- **For fix:** `git commit -m "ff Some fix notes"`
- **For draft:** `git commit -m "dd Some fix notes"`

- **Tip**: you just can print trigger (exampe - ff) and commit - it will looks like: [Branch name] [Type of commit by trigger] [new version number of commit]

## Set Git Config to  use hook

To use hook in **current repo**, place it to **.git/hooks** directory inside your local cloned repo. Hook will be accessible for current project only.  
To use hook **globally** place it to common folder and set up Git:

```bash
mkdir ~/.git_hooks
cp prepare-commit-msg.py ~/.git_hooks
git config --global core.hooksPath ~/.git_hooks
```

## On Windows

On Windows systems some trick must be used, because Git couldn't run Python interpreter correctly: create Shell script to run Python script.  
In "windows" repo folder you can find prepared files.

Do next steps:

1. Copy files `prepare-commit-msg.py` and `windows/prepare-commit-msg` repo folder somewhere you like (example: `C:\Users\your_user_name\.git_hooks\`)
2. Make files executable (fore example using Linux-like syntax in GitBash):

    ```bash
    chmod +x prepare-commit-msg.py && chmod +x prepare-commit-msg.py
    ```

3. Set up Git global hook folder where you've put hook files (for example c:\\users\\your_user_name\\.git_hooks\\):

    ```bash
    git config --global core.hooksPath C:\\Users\\your_user_name\\.git_hooks\\
    ```

### Tip

On Windows you can receive an error: ***fatal: cannot run /home/nick/.git_hooks/prepare-commit-msg: No such file or directory***

- Verify extension (must be `.py` )
- Verify shebang (must be `which python3` )
- Verify permission flags ( `chmod +x` )
