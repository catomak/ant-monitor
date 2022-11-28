from requests.auth import HTTPDigestAuth
from config import log
from src.modules import telegram_bot
import requests
import json
import time
import config


class Miner:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Miner, cls).__new__(cls)
        return cls.instance

    # TODO: учесть зависимость от наличия инфо на каждой стадии
    def __init__(self, ip: str, session: requests.Session) -> None:
        self.ip = ip
        self.session = session
        self.system_info = self.get_system_info(self.session, self.ip)                                                                                       

    @classmethod
    def get_system_info(cls, session, ip) -> json:
        if not isinstance(session, requests.Session):
            log.info(f'{ip}: Устройство не Bitmain Antminer')
            return None

        system_info = session.get('http://' + ip + config.API_URLS.get('system_info'))

        if system_info.status_code != 200 or 'DOCTYPE HTML' in system_info.text.upper():
            log.info(f'{ip}: Не удалось получить доступ к данным устройства')
            return None

        if not (system_info := system_info.json()):
            log.info(f'{ip}: Устройство еще не запустилось')
            return None 

        return system_info

    # TODO: переделать
    @classmethod
    def get_miner_api(cls, miner_type: str) -> dict:
        for api_type, data in config.API.items():
            for model in data.get('models'):
                if model in miner_type:
                    return data

    @classmethod
    def get_device_status(cls, ip: str, session: requests.Session, api: dict) -> json:
        # TODO: remake
        if not (ip or session or api):
            return None

        device_status = session.get('http://' + ip + api.get('status_url'))

        if device_status.status_code != 200:
            log.info(f'{ip} не отвечает')
            return None

        return device_status.json()

    @classmethod
    def parse_device_data(cls, ip: str, session: requests.Session, system_info: dict) -> dict | None:
        # МБ стоит добавить детализацию по хэш рейту каждой платы в статистику
        # TODO: Определенно стоит объединить функционал вне зависимости от API

        # TODO: переделать
        if not (ip or session or system_info):
            return None

        miner_type = system_info.get('minertype')
        macaddr = system_info.get('macaddr')

        if not (api := cls.get_miner_api(miner_type)):
            log.info(f'{ip}: Не удалось определить API майнера')
            return None

        device_status = cls.get_device_status(ip, session, api)
        # Dict with data for saving
        parsed_data = {
            'ip': ip,
            'macaddr': macaddr,
            'miner_type': miner_type,
            'ghs5s': None,
            'ghsav': None,
            'fan_speed': [],
            'pcb_temp': [],
            'chip_temp': [],
            'chain_rate': [],
            'elapsed': None
        }

        if api.get('api_version') == 'api_v1':

            if not (devs := device_status.get('devs')):
                log.info(f'{ip}: Не обнаружено плат. Вероятно майнер был недавно перезапущен')
                # TODO: переделать на завершение работы с майнером, т.к. дальше падают ошибки.
                #       Аналогично везде где получается криритически важная инфа для работы других функций
                return None

            summary = device_status.get('summary')
            parsed_data['ghs5s'] = int(float(summary.get('ghs5s')))
            # For fuccking 'ghsav': '55460.43,GHS 30m=55726.86',
            parsed_data['ghsav'] = int(float(summary.get('ghsav')[:summary.get('ghsav').find(',')]))
            parsed_data['elapsed'] = time.strftime("%H:%M:%S", time.gmtime(int(summary.get('elapsed'))))

            # all freq info
            def get_freq_info(freq_str: str) -> dict:
                for f in freq_str.split(','):
                    if (sep := f.find('=')) < 0:
                        continue
                    # TODO: переделать под шаблон float
                    freq[f[:sep]] = f[sep + 1:].replace('|', '')
                return freq

            freq = {} # all freq data and maybe too match
            # PCB list
            for d in devs:
                parsed_data['pcb_temp'].append(int(d.get('temp')))
                # self.fan_speed.append(int(d.get('fan')[:d.get('fan').find(',')]))
                if not freq:
                    freq = get_freq_info(d.get('freq'))

            # TODO: подумать на переделать в установление параметров в инициализации
            for r in range(4):
                if fan := freq.get(f'fan{r}'):
                    parsed_data['fan_speed'].append(int(fan))
                # chip temp S17
                if chip_temp := freq.get(f'temp_chip{r}'):
                    parsed_data['chip_temp'].append(max(map(int, chip_temp.split('-'))))
                # chip temp L3
                if chip_temp_2 := freq.get(f'temp2_{r}'):
                    parsed_data['chip_temp'].append(int(float(chip_temp_2)))

                if chain_rate := freq.get(f'chain_rate{r}'):
                    parsed_data['chain_rate'].append(int(float(chain_rate)))

        elif api.get('api_version') == 'api_v2':

            summary = device_status.get('STATS')[0]
            parsed_data['ghs5s'] = max(int(summary.get('rate_5s')), 0)
            parsed_data['ghsav'] = max(int(summary.get('rate_avg')), 0)
            parsed_data['fan_speed'] = summary.get('fan')
            parsed_data['elapsed'] = time.strftime('%H:%M:%S', time.gmtime(float(summary.get('elapsed'))))

            if not (devs := device_status.get('STATS')[0].get('chain')):
                log.info(f'{ip}: Не обнаружено плат. Вероятно майнер был недавно перезапущен')
                return None
            
            for d in devs:
                parsed_data['pcb_temp'].append(max(map(int, d.get('temp_pcb'))))
                parsed_data['chip_temp'].append(max(map(int, d.get('temp_chip'))))
                parsed_data['chain_rate'].append(max(int(d.get('rate_real')), 0))

        else:
            log.info(f'{ip}: API не поддерживается, проверьте наличие модели. в конфигурации программы')

        return parsed_data

    @classmethod
    def set_miner_data(cls, key: str, miner_data: dict, save_dict: dict) -> None:
        if not miner_data:
            return

        if not save_dict.get(key):
            save_dict[key] = {}

        for index, data in miner_data.items():
            save_dict[key][index] = data

    @classmethod
    # TODO: change method type to connection type DB/pic
    def get_saved_miner_data(cls, ip: str, method: str) -> dict:
        return {}

    @property
    def get_miner_system_info(self):
        return self.system_info

    @classmethod
    def reboot_device(cls, ip: str) -> bool:
        try:
            requests.get('http://' + ip + '/cgi-bin/reboot.cgi')
            log.info(f'{ip} Перезагружается...')
            return True
        except Exception as e:
            log.info(f'{ip}: Не получилось перезагрузить. Ошибка: {e}')
            return False


class MinerConnector:

    def __init__(self, ip: str, auth_data: str = None) -> None:
        self.ip = ip
        self.auth_data = auth_data
        self.session = self.start_session(ip, auth_data)

    def __enter__(self) -> requests.Session:
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not hasattr(self, 'session') and isinstance(self.session, requests.Session):
            self.session.close()

    def start_session(self, ip, auth_data: dict = None) -> requests.Session | None:
        session = requests.Session()
        if auth_data:
            return self.get_access(session, auth_data)
        for auth_item in config.AUTH:
            if access := self.get_access(session, auth_item):
                return access
        return None

    def get_access(self, session: requests.Session, auth: dict) -> requests.Session | None:
        # TODO: записывать данные авторизации в инфо о майнерах
        session.auth = HTTPDigestAuth(auth.get('username'), auth.get('password'))
        try:
            response = session.get(f'http://{self.ip}')
            if response.status_code == 200:
                config.SESSION_DEVICES_IP.append(self.ip)
                return session
        except Exception as e:
            log.error(f'{self.ip}: Не удалось подключитьcя к устройству. Ошибка: {e}')
        return None 


# TODO: redo with anywhere calling, but with a complex diagnostic in main
class MinerErrorDiag:

    ERRS = {
        'max_temp': '{ip}:{type} - превышение MAX температура PCB: {pcb_temp}!',
        'min_temp': '{ip}:{type} - похоже отвалилась плата. MIN температура PCB: {pcb_temp}!',
        'fan_speed': '{ip}:{type} - низкие обороты вентилятора: {fan_speed}',
        'hash_rate': '{ip}:{type} - критично снизился хеш-рейт.\nТекущий: {cur_rate}\nСредний хеш-рейт: {avg_rate}'
    }

    @classmethod
    def send_session_errors(cls, errors: list) -> None:
        errors_str = '\n\n'.join(errors)
        telegram_bot.send_message(config.TG_RECIPIENTS, errors_str)

    @classmethod
    def check_session_devices(cls, devices: dict):
        session_errors = []
        for d in devices.values():
            if d_errors := cls.full_check_device(d):
                session_errors += d_errors

        if session_errors:
            cls.send_session_errors(session_errors)

    @classmethod
    def full_check_device(cls, device: dict) -> list:
        checks = (cls.check_pcb_temp, cls.check_fan_speed, cls.check_hash_rate)
        errors = [c(device) for c in checks if c(device)]
        return errors

    @classmethod
    def check_pcb_temp(cls, device: dict) -> str:
        if not (pcb_temp := device.get('pcb_temp')):
            log.warning(f"{device.get('ip')}:{device.get('miner_type')} - не удалось определить температуру плат")
        temp_errs = ''

        if max(pcb_temp) >= config.TEMP_PCB_MAX:
            temp_errs += cls.ERRS['max_temp'].format(device.get('ip'), device.get('miner_type'), device.get('pcb_temp'))

        if min(pcb_temp) >= config.TEMP_PCB_MIN:
            temp_errs += cls.ERRS['min_temp'].format(device.get('ip'), device.get('miner_type'), device.get('pcb_temp'))

        return temp_errs

    @classmethod
    def check_fan_speed(cls, device: dict) -> str:
        if not (fan_speed := device.get('fan_speed')):
            log.warning(f"{device.get('ip')}:{device.get('miner_type')} - не удалось определить скорость вентиляторов")

        if min(fan_speed) <= config.FAN_SPEED_MIN:
            return cls.ERRS['min_temp'].format(device.get('ip'), device.get('miner_type'), device.get('fan_speed'))

    @classmethod
    def check_hash_rate(cls, device: dict) -> str:
        if not device.get('ghs5s') or not device.get('ghsav'):
            log.warning(f"{device.get('ip')}:{device.get('miner_type')} - не удалось определить hash rate")

        if device.get('elapsed') > 30.0 and (1 - device.get('ghs5s') / device.get('ghsav')) >= 0.2:
            return cls.ERRS['min_temp'].format(device.get('ip'), device.get('miner_type'), device.get('ghs5s'), device.get('ghsav'))

