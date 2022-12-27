from aioping import ping
import asyncio
from itertools import product
from miner_monitor.config import log


# TODO: redo with base IP
def ip_ranges_to_list(f_range: range, s_range: range) -> list:
    ip_range = []
    for i, j in product(f_range, s_range):
        ip_range.append("192.168.{}.{}".format(i, j))
    return ip_range


async def ping_ip(ip: str) -> str | None:
    try:
        if await ping(ip):
            return ip
        log.warning(f"Can't ping address: {ip}")
    except Exception as ex:
        log.exception(f"Can't ping address: {ip}. Exception: {ex}")
    return None


async def ping_ip_range(ip_list: list[str]) -> list[str]:
    tasks = [asyncio.create_task(ping_ip(ip)) for ip in ip_list]
    full_ip_list = await asyncio.gather(*tasks)
    return [item for item in full_ip_list if item]


def find_dveices_ip() -> list[str]:
    ip_list  = ip_ranges_to_list(range(80, 90), range(2, 256))
    found_ip = asyncio.run(ping_ip_range(ip_list))   
    return found_ip
