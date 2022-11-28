from miner_utils import Miner, MinerConnector, MinerErrorDiag
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
        # TODO: передавать результат в переменную
        with MinerConnector(ip, None) as connection:
            miner = Miner(ip, connection)
            if miner.system_info:
                miner_data = miner.parse_device_data(ip, miner.session, miner.system_info)
                miner.set_miner_data(ip, miner_data, session_devices)
        time.sleep(0.1)
    return session_devices


def look_device(devices: dict = config.SESSION_DEVICES) -> None:

    if not devices:
        log.info('Устройств в локальной сети не найдено')
        return

    index_lens = {}
    indexes = ''
    miners = ''

    for device in devices.values():
        for index, value in device.items():
            val_len = len(str(value)) + 5
            miners += str(value).rjust(val_len)
            if not index_lens.get(index):
                index_lens[index] = val_len
                indexes += str(index).rjust(val_len)


def monitor():
    log.info('Start monitoring')
    devices = ip_searcher.find_ip()
    log.info('Start sessions')
    session_devices = get_session_devices(devices)
    log.info('Start looking')
    look_device(session_devices)
    MinerErrorDiag.check_session_devices(session_devices)


def main():
    while True:
        monitor()
        time.sleep(60)


if __name__ == '__main__':
    main()
