import os
import sys

import toml


# Determine user config directory cross-platform

def get_user_config_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "comic-optimizer")
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~/Library/Application Support"), "comic-optimizer")
    else:
        # Linux and others
        return os.path.join(os.path.expanduser("~/.config"), "comic-optimizer")


USER_CONFIG_DIR = get_user_config_dir()
SETTINGS_FILE = os.path.join(USER_CONFIG_DIR, 'user_settings.toml')

DEFAULT_SETTINGS = {
    'theme': None,  # None means auto-detect
    'font_family': 'Segoe UI',
    'font_size': 10
}


def load_user_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_user_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        data = toml.load(SETTINGS_FILE)
        settings = DEFAULT_SETTINGS.copy()
        settings.update({k: data.get(k, v) for k, v in DEFAULT_SETTINGS.items()})
        return settings
    except Exception:
        save_user_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def save_user_settings(settings):
    try:
        os.makedirs(USER_CONFIG_DIR, exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            toml.dump(settings, f)
    except Exception:
        pass
