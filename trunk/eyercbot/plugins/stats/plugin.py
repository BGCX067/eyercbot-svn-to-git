'''Manages channel stats'''

import logging
log = logging.getLogger("BotLogs.plugins.stats")
import subprocess
import ftplib
import shutil

import eyercbot
import eyercbot.log as log
import datetime

HAS_CONFIG = True
CONFIG_VERSION = 2
config = {'servers': {'serverName': ['#mychannel',]}, 
    'frequency':'0 0 * * *',
    'auto_update': True, 
    'pisg_path': '/usr/bin/pisg',
    'cfg_path': '/path/to/pisg.cfg', 'url': 'http://mystatssite.com/',
    'man_message': 'Channel stats manually updated :: ',
    'auto_message': 'Channel stats automatically updated :: ',
    'use_ftp': True,
    'ftp_server': 'ftp.mystatssite.com',
    'ftp_user': 'username',
    'ftp_pass': 'password',
    'ftp_path': 'public_html/',
    'use_move': False,
    'move_dest': None,}

#midnite = datetime.datetime.combine(datetime.datetime.utcnow()+datetime.timedelta(days=1), datetime.time(0,0))

# Midnight line entry
def midnight(*args):
    for server in eyercbot.config['plugin_config']['stats']['servers']:
        for channel in eyercbot.config['plugin_config']['stats']['servers'][server]:
            update(channel + '.html', server, channel, auto=True)

if 'stats' in eyercbot.config['plugin_config']:
    minute, hour, day, month, day_of_week = eyercbot.config['plugin_config']['stats']['frequency'].split(' ')
    eyercbot.scheduler.add_cron_job(midnight, second='0', month=month, day=day, hour=hour, minute=minute, day_of_week=day_of_week)
    log.info('Added auto stats to scheduler')

def print_url(server, user, target, message):
    url = eyercbot.config['plugin_config']['stats']['url']
    eyercbot.send('sendMsg', server, user, target, 'Channel statistics URL: ' + url + target.lstrip('#') + '.html' )

def generate(server, user, target, message):
    for server in eyercbot.config['plugin_config']['stats']['servers']:
        for channel in eyercbot.config['plugin_config']['stats']['servers'][server]:
            update(channel.lstrip('#') + '.html', server, channel)

def update(file_name, server, channel, auto = False):
    subprocess.call([eyercbot.config['plugin_config']['stats']['pisg_path'], '-co', 
        eyercbot.config['plugin_config']['stats']['cfg_path']])
    if eyercbot.config['plugin_config']['stats']['use_ftp']:
        upload(file_name)
    if eyercbot.config['plugin_config']['stats']['use_move']:
        copy(file_name)
    if auto:
        eyercbot.send('msg', server, channel, eyercbot.config['plugin_config']['stats']['auto_message'] + 
            eyercbot.config['plugin_config']['stats']['url'] + file_name.lstrip('#'))
    else:
        eyercbot.send('msg', server, channel, eyercbot.config['plugin_config']['stats']['man_message'] + 
            eyercbot.config['plugin_config']['stats']['url'] + file_name)

def upload(file_name):
    ftp = ftplib.FTP(eyercbot.config['plugin_config']['stats']['ftp_server'], 
        eyercbot.config['plugin_config']['stats']['ftp_user'],
        eyercbot.config['plugin_config']['stats']['ftp_pass'])
    ftp.set_pasv(False)
    ftp.cwd(eyercbot.config['plugin_config']['stats']['ftp_path'])
    file_upload = open(file_name.lstrip('#'), 'rb')
    cmd = 'STOR ' + file_name.lstrip('#')
    ftp.storbinary(cmd, file_upload)

    file_upload.close()
    ftp.quit()

def copy(file_name):
    shutil.copy(file_name, eyercbot.config['plugin_config']['stats']['move_dest'])

alias_map = {"stats": print_url, "make stats": generate}