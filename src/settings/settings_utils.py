import logging
import os
import sys

import toml

logger = logging.getLogger(__name__)


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
    'font_size': 10,
    'last_root_dir': '',
    'presets': {
        'lossy': ["pingo", "-s4", "-webp", "-process=4"],
        'lossless': ["pingo", "-s4", "-lossless", "-webp", "-process=4", "-no-jpeg"]
    }
}


def load_user_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_user_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        data = toml.load(SETTINGS_FILE)
        settings = DEFAULT_SETTINGS.copy()
        # Merge presets dict if present, else use default
        settings['presets'] = data.get('presets', DEFAULT_SETTINGS['presets'])
        # Merge other settings
        for k, v in DEFAULT_SETTINGS.items():
            if k != 'presets':
                settings[k] = data.get(k, v)
        return settings
    except Exception as e:
        logger.warning(f"Failed to load user settings: {e}")
        save_user_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def save_user_settings(settings):
    try:
        os.makedirs(USER_CONFIG_DIR, exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            toml.dump(settings, f)
    except Exception as e:
        logger.warning(f"Failed to save user settings: {e}")
