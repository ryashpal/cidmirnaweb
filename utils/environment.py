import os

def are_we_at_home():
    import socket
    return socket.gethostname().startswith('ale')


def setup_settings():
    if are_we_at_home():
        settings_filename = "cidmirnaweb.settingslocal"
    else:
        settings_filename = "cidmirnaweb.settingslive"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_filename)

    