from aioping import ping
import asyncio
from itertools import product
from time import time

def get_ip_from_list():
    pass

# TODO: obtaiting base IP
def get_ip_family():
    pass

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
    except Exception as ex:
        # print(f"{ip}: error ({ex})")
        return None
    
async def ping_ip_range() -> list[str]:
    ip_list = ip_ranges_to_list(range(88, 90), range(2, 256))
    
    tasks = []
    for ip in ip_list:
        tasks.append(asyncio.create_task(ping_ip(ip)))
    
    full_ip_list = await asyncio.gather(*tasks)

    working_ip_list = [item for item in full_ip_list if item]

    return working_ip_list

def find_dveices_ip():
    found_ip = asyncio.run(ping_ip_range())   
    return found_ip