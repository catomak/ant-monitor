from miner import Miner, MinerConnector, MinerErrorDiag
from src.modules import ip_searcher
from config import log
import config
import time
 

def get_session_devices(ip_addresses: list) -> dict | None:
    if not ip_addresses:
        log.info('Устройств в локальной сети не найдено')
        return None

    session_devices = {}

    for ip in ip_addresses:
        with MinerConnector(ip, None) as connection:
            miner = Miner(ip, connection)
            if miner.system_info:
                miner_data = miner.parse_device_data(ip, miner.session, miner.system_info)
                miner.set_miner_data(ip, miner_data, session_devices)
        time.sleep(0.1)
    return session_devices


def look_device(devices: dict) -> None:

    if not devices:
        log.info('Устройств в локальной сети не найдено')
        return None

    col_lens = {
        'ip': 20,
        'macaddr': 22,
        'miner_type': 20,
        'ghs5s': 11,
        'ghsav': 11,
        'fan_speed': 28,
        'pcb_temp': 21,
        'chip_temp': 21,
        'chain_rate': 26,
        'elapsed': 13
    }

    items = ''
    indexes = ''
    for device, column in devices.values(), col_lens:
        items += device.get(column).ljust(col_lens.get(column))
        items += '\n'
        if not indexes:
            indexes += column.ljust(col_lens.get(column))

    print(indexes, items, sep='\n')


def monitor():
    log.info("Searching for devices on the network...")
    devices = ip_searcher.find_devices_ip()
    log.info(f'Finded {devices} devices:')
    print('\n'.join(devices))
    # session_devices = get_session_devices(devices)
    # session_devices = {}
    # look_device(session_devices)
    # # TODO: добавить поле ошибки в майнере и диагностировать при работе с конкретным устройством, потом отображать
    # MinerErrorDiag.check_session_devices(session_devices)


def main():
    log.info('START MONITORING')
    while True:
        monitor()
        time.sleep(config.CHECK_PAUSE)
        log.info(f'SLEEPING {config.CHECK_PAUSE}')


if __name__ == '__main__':
    main()
