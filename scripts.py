import subprocess


def fmt():
    subprocess.run(["ruff", "format"], check=True)


def check():
    subprocess.run(["ruff", "check", "--fix"], check=True)
