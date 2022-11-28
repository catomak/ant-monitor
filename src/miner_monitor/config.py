from rich import pretty
import logging
from rich.logging import RichHandler


# OLD
# project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# path_logs = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs/'))


# LOGGING
def get_logger(file: bool = True, console: bool = True) -> logging.getLogger():
    pretty.install()
    formatting = "%(message)s"
    logging.basicConfig(
        level="NOTSET",
        format=formatting,
        datefmt="[%X]",
        handlers=[RichHandler(),
                  logging.FileHandler('app.log', 'w', 'utf-8')]
    )
    return logging.getLogger("rich")


log = get_logger()

# SESSION
SESSION_DEVICES = {}
SESSION_DEVICES_IP = []

TG_RECIPIENTS = [
]


# TECH
TEMP_PCB_MAX = 85
TEMP_PCB_MIN = 1
FAN_SPEED_MIN = 1000
NET = 'tbs'
AUTH = [
    {
        'username': 'admin',
        'password': 'admin'
    }
]


# API
API_URLS = {
    'system_info': '/cgi-bin/get_system_info.cgi',
    'miner_conf': '/cgi-bin/get_miner_conf.cgi',
    'miner_status': '/cgi-bin/get_miner_status.cgi',
    'miner_status_v2': 'cgi-bin/minerStatus.cgi',
    'network_info': '/cgi-bin/get_network_info.cgi',
    'stats': '/cgi-bin/stats.cgi',
    'pools': '/cgi_bin/pools.cgi',
    'reboot_methods': [
        '/cgi-bin/reboot.cgi',
        '/reboot.cgi',
        '/cgi/reboot.cgi'
    ]
}

API = {
    'api_v1': {
        'models': ['L3', 'S17'],
        'status_url': API_URLS.get('miner_status')
    },
    'api_v2': {
        'models': ['S19'],
        'status_url': API_URLS.get('stats')
    }
}
