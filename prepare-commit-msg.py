#!/usr/bin/python3

import re
import sys
from subprocess import check_output

try:
    commit_msg_filepath = sys.argv[1]
except Exception as e:
    print(f"Read commit message failed. Error: {e}")
    sys.exit(1)


def head_subject():
    try:
        return check_output(["git", "log", "-1", "HEAD", "--pretty=%s"]).decode("utf-8").strip()
    except Exception:
        return ""


raw_msg = open(commit_msg_filepath, encoding="utf8").read()

# Детектор amend: сообщение совпало с subject HEAD. Тогда база - родитель, и номер не растёт.
is_amend = raw_msg.strip() == head_subject() != ""
tip = "HEAD~1" if is_amend else "HEAD"

try:
    branch = check_output(["git", "symbolic-ref", "--short", "HEAD"]).decode("utf-8").strip()
except Exception:
    branch = "HEAD"

try:
    last_commit = check_output(["git", "log", "-1", f"origin/{branch}", "--pretty=%s"]).decode("utf-8").strip()
    if int(check_output(["git", "rev-list", "--count", f"origin/{branch}..{tip}"])) > 0:
        last_commit = check_output(["git", "log", "-1", tip, "--pretty=%s"]).decode("utf-8").strip()
except Exception:
    # Ветка без origin или без коммитов: берётся вершина локального дерева, а при неудаче - ноль.
    try:
        last_commit = "" if branch == "HEAD" else check_output(["git", "log", "-1", tip, "--pretty=%s"]).decode("utf-8").strip()
    except Exception:
        last_commit = ""

matches = re.findall(r"(?:\d+\.)+\d+", last_commit)
parts = matches[0].split('.') if matches else []
release, update, fix, draft = [int(n) for n in parts] + [0] * (4 - len(parts))

print(f"branch: {str(branch)}")
print(f"release: {str(release)}")
print(f"update: {str(update)}")
print(f"fix: {str(fix)}")
print(f"draft: {str(draft)}")

with open(commit_msg_filepath, "r+", encoding="utf8") as f:
    commit_msg = f.read()

    if len(sys.argv) > 2 and sys.argv[2] in ("merge", "squash"):
        # merge любого вида: источник сообщения merge -> не трогать сообщение.
        new_message = commit_msg.strip()
    elif commit_msg.startswith("init", 0):
        new_message = (f'[{branch}] Initial 0.0.0.1')
    elif is_amend:
        # amend: старый префикс снимается, тело и тип остаются; номер берётся из старого префикса.
        old = re.match(r"^\[[^\]]*\]\s+(\w+)\s+([\d.]+):", commit_msg.strip())
        kind = {"Release": "rr", "Update": "uu", "Fix": "ff"}.get(old.group(1), "dd") if old else commit_msg.strip()[:2]
        body = commit_msg.strip()[old.end():] if old else commit_msg
        if kind not in ("rr", "uu", "ff", "dd"):
            kind, body = "dd", "dd" + body
        elif not old:
            # Префикса не было: тело начинается с триггера, снимается он, как у нового коммита.
            body = body.lstrip()[2:] if body.lstrip()[:2] == kind else body

        prefix = {"rr": "Release", "uu": "Update", "ff": "Fix", "dd": "Draft"}[kind]
        new_version = old.group(2) if old else {
            "rr": f'{release + 1}.0.0', "uu": f'{release}.{update + 1}.0',
            "ff": f'{release}.{update}.{fix + 1}'}.get(kind, f'{release}.{update}.{fix}.{draft + 1}')

        # Прежний текст - всё после старого префикса; он же и есть тело нового коммита.
        new_message = (f'[{branch}] {prefix} {new_version}:{body}' if body.strip() else
                       f'[{branch}] {prefix} {new_version}')
    elif commit_msg.startswith("[", 0):
        # Чужое готовое сообщение (cherry-pick, revert) несёт номер своего коммита - номер растёт.
        new_message = re.sub(r"(?<=\] )(\w+ )?[\d.]+\b",
                             lambda m: (m.group(1) or "Fix ") + f'{release}.{update}.{fix + 1}',
                             commit_msg.strip(), count=1)
    else:
        # Источник пуст = пишет редактор: в файле блок инструкций git.
        # Он приклеивался к тексту сообщения.
        edited = len(sys.argv) <= 2
        lines = commit_msg.splitlines()
        if edited:
            lines = [l for l in lines if not l.lstrip().startswith("#")]
        text = "\n".join(lines).strip()

        # Триггер - отдельное слово: у ddns-настройки первые две буквы -
        # не триггер, а начало текста.
        trigger = re.match(r"(rr|uu|ff|dd)(?=\s|$)", text)
        forms = {"rr": ("Release", f'{release + 1}.0.0'), "uu": ("Update", f'{release}.{update + 1}.0'),
                 "ff": ("Fix", f'{release}.{update}.{fix + 1}'), "dd": ("Draft", f'{release}.{update}.{fix}.{draft + 1}')}
        prefix, new_version = forms[trigger.group(1)] if trigger else forms["dd"]
        rest = text[trigger.end():].strip() if trigger else text
        # Текста нет: редактор допишет его в строку, двоеточие - сепаратор.
        separator = f": {rest}" if rest else (":" if edited else "")
        new_message = f'[{branch}] {prefix} {new_version}{separator}'

    if len(new_message) > 0:
        f.truncate(0)
        f.seek(0)
        f.write(new_message.strip())
