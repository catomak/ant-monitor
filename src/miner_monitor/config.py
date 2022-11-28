import logging


# OLD
# project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# path_logs = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs/'))


# LOGGING
def get_logger() -> logging.getLogger():
    formatting = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(level="NOTSET", format=formatting, datefmt='%d/%m/%Y %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging.getLogger('app.log')
    return logger


log = get_logger()


TG_RECIPIENTS = [
    # '284754687',
    # '370180455', # Олег
    # '558338567', # Серега
    # '911755144', # Лука
    # '5411996165', # Дато
    # '1230776012', # Гио
    '294773056'  # Саша
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
    },
    {
        'username': 'root',
        'password': 'root'
    },
    {
        'username': 'root',
        'password': '2wsx'
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

