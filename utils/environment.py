import os


def are_we_at_home():
    import socket
    return socket.gethostname().startswith('cafeezy')


def are_we_at_monash():
    import socket
    return (socket.gethostname() == 'bioinformaticslab') or (socket.gethostname() == 'tsonika-lab')
#    return socket.gethostname() == 'bioinformaticslab'


def setup_settings():
    if are_we_at_home():
        settings_filename = "cidmirnaweb.settingslocal"
    elif are_we_at_monash():
        settings_filename = "cidmirnaweb.settingslivemonash"
    else:
        settings_filename = "cidmirnaweb.settingslive"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_filename)
