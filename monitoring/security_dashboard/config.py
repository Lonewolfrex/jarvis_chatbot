import os

# ----------------------------------
# GitHub Configuration
# ----------------------------------

GITHUB_OWNER = "Lonewolfrex"
GITHUB_REPO = "jarvis_chatbot"

GITHUB_TOKEN = os.environ.get("GH_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError(
        "GITHUB_TOKEN environment variable not set"
    )

# ----------------------------------
# Directories
# ----------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ARTIFACT_DIR = os.path.join(
    BASE_DIR,
    "artifacts"
)

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "security.db"
)

os.makedirs(
    ARTIFACT_DIR,
    exist_ok=True
)

os.makedirs(
    os.path.join(BASE_DIR, "data"),
    exist_ok=True
)

os.makedirs(
    os.path.join(BASE_DIR, "logs"),
    exist_ok=True
)