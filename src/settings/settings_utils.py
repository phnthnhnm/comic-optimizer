import os

import toml

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'user_settings.toml')

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
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            toml.dump(settings, f)
    except Exception:
        pass
