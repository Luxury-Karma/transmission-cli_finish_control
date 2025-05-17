import argparse
from math import trunc
from os import system
import json
from datetime import datetime, timedelta
import re
import subprocess

ACTIVE_FILE:str = "active.json"
SETTING_FILE:str = "setting.json"

def __args() -> dict:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description="Kill PID after a determine amount of time for program who do not want to die ! "
)
    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-t','--time')
    parser.add_argument('-v','--verify', action='store_true')
    parser.add_argument('-d','--directory')
    parser.add_argument('-n','--name')
    parser.add_argument('-dl','--download')
    parser.add_argument('-dd','--download_directory')
    parser.add_argument('-s', '--script')
    return vars(parser.parse_args())

#region json manipulation

def __open_json_file(directory,file:str, enco:str='utf-8' ) -> dict:
    t:dict
    try:
        with open(f'{directory}/{file}','r',encoding=enco) as f:
            t = json.load(f)
            f.close()
    except Exception.args:
        exit(f'ERROR 501: File Could not be read : {directory}/{file}')
    return t

def __write_json_file(directory:str, file:str,file_to_write:dict, enco:str='utf-8'):
    try:
        with open(f'{directory}/{file}', 'w', encoding=enco) as f:
            json.dump(file_to_write, f)
            f.close()
    except Exception.args:
        exit(f'ERROR 502: File Could not be written: {directory}/{file}')

def __open_setting_json(directory:str) -> dict:
    return __open_json_file(directory,SETTING_FILE)

def __write_setting_json(directory: str, t:dict) -> None:
    __write_json_file(directory,SETTING_FILE,t)

def __open_active_json(directory:str) -> dict:
    return __open_json_file(directory,ACTIVE_FILE)

def __write_active_json(directory:str, t:dict) -> None:
    __write_json_file(directory,ACTIVE_FILE,t)

#endregion


#region download

def transmission_download(download_directory:str, magnet_path:str, script_path:str) -> None:
    system(f'transmission-cli -D -f {script_path} -w {download_directory} {magnet_path}')
    return

#endregion

#region Controll the stop of download

def __kill_active_PID(pid:str) -> None:
    system(f'kill {pid}')
    return

def __check_for_new_files(directory:str, name:str,time_to_kill:int = 30):
    try:
        d = subprocess.check_output(['pidof',name]).strip()
        print(f'Process found : {d}')
    except Exception.args:
        print('Error in the command launch')

    pid:list[str] = re.findall(r'\d{4}',f'{d}')
    t:dict = __open_active_json(directory)
    for e in pid:
        if e in t.keys():
            pass
        __add_active_PID(directory, e, time_to_kill)
        print(f'process added {e}')

def __add_active_PID(directory:str,pid:str, time_to_kill:int = 30) -> None:
    t:dict = __open_active_json(directory)

    if pid in t.keys():
        #TODO: logs
        return
    t[f'{pid}'] = {
        'time_to_kill':(datetime.now() + timedelta(seconds=time_to_kill)).isoformat()
    }
    __write_active_json(directory,t)

    return


def __remove_inactive_PID(pid:str,directory:str) -> None:
    t:dict = __open_active_json(directory)
    if pid not in t.keys():
        #TODO: logs
        return
    t.pop(pid)

    __write_active_json(directory,t)

    return


def __new_pids(active_pids: list[str], directory:str) -> None:
    if len(active_pids) == 0:
        return
    t: dict = __open_active_json(directory)

    pids_list = t.keys()

    for e in active_pids:
        if e not in pids_list:
            __add_active_PID(e,directory)

    return


def kill_pids(directory:str) -> None:
    t:dict = __open_active_json(directory)
    pid_to_remove:list[str] = []
    for e in t.keys():
        if datetime.fromisoformat(t[e]['time_to_kill']) <= datetime.now():
            __kill_active_PID(e)
            pid_to_remove.append(e)

    for e in pid_to_remove:
        __remove_inactive_PID(e,directory)

# endregion



def directory_setup(args:dict) -> str:
    t: dict = __open_setting_json('./')

    if args["directory"] and args["directory"] != '':
        with open(f'{args["directory"]}/{SETTING_FILE}', 'r') as f:
            t = json.load(f)
            f.close()



    directory: str = t['active_directory']

    if args['directory'] is not None and args['directory'] != '':
        directory = args['directory']
        t['active_directory'] =directory
        with open(f'{args["directory"]}/{SETTING_FILE}', 'w') as f:
            json.dump(t, f)
            f.close()

    return directory

def download_directory_setup(directory:str, args:dict) -> str:
    t:dict = __open_setting_json(directory)

    d_directory: str = t['download_directory']
    if args['download_directory'] and args['download_directory']!= '':
        d_directory = args['download_directory']
        t['download_directory'] = d_directory
        __write_setting_json(directory,t)
    return d_directory

def script_setup(directory, args:dict) -> str :
    t:dict = __open_setting_json(directory)
    script_path:str = t['transmission_script_path']
    if args['script'] and args['script'] != '':
        script_path = args['script']
        t['transmission_script_path'] = script_path
        __write_setting_json(directory,t)

    return script_path

def main(args:dict) -> None:
    directory:str = directory_setup(args)


    if args['add']:
        try:
            __check_for_new_files(directory,args['name'])
        except Exception.args as e:
            #TODO: logs
            print(f'Err {e}')

    if args['verify']:
        kill_pids(directory)

    if args['download']:
        d_directory: str = download_directory_setup(directory, args)
        script_path: str = script_setup(directory, args)
        transmission_download(d_directory, args['download'], script_path)


if __name__ == "__main__":
    args:dict = __args()
    main(args)