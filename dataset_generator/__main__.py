import sys

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

from .cli import app

if __name__ == "__main__":
    if load_dotenv is not None:
        load_dotenv()
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1].startswith("-")):
        sys.argv.insert(1, "generate")
    app()
