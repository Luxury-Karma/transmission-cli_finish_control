import argparse
from os import system
import json
from datetime import datetime, timedelta

ACTIVE_FILE:str = "active.json"

def __args() -> dict:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description="Kill PID after a determine amount of time for program who do not want to die ! "
)
    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-t','--time')
    parser.add_argument('-v','--verify', action='store_true')
    parser.add_argument('-d','--directory',required=True)
    parser.add_argument('-n','--name')
    return vars(parser.parse_args())


def __kill_active_PID(pid:str) -> None:
    system(f'kill {pid}')
    return

def __check_for_new_files(directory:str, name:str,time_to_kill:int = 30):
    print(f'name: {name}')
    pid:list[str] = str(system(f'pidof {name}')).split('\n')
    print(pid)
    t:dict
    with open(f'{directory}/{ACTIVE_FILE}') as f :
        t = json.load(f)
        f.close()
    for e in t.keys():
        if pid in e:
            pass
        print(f'PID added : {e}')
        __add_active_PID(directory, time_to_kill)
    if len(t.keys()) <= 0 and pid != '':
        __add_active_PID(directory, time_to_kill)



def __add_active_PID(directory:str,time_to_kill:int = 30) -> None:
    t:dict
    pid:str = ''
    time_to_kill = int(time_to_kill)
    with open(f'{directory}/{ACTIVE_FILE}', 'r', encoding='utf-8') as f:
        t:dict = json.load(f)
    if pid in t.keys():
        #TODO: logs
        return
    t[f'{pid}'] = {
        'time_to_kill':(datetime.now() + timedelta(seconds=time_to_kill)).isoformat()
    }

    with open(f'{directory}/{ACTIVE_FILE}', 'w', encoding='utf-8') as f:
        json.dump(t, f)
        f.close()
    return


def __remove_inactive_PID(pid:str,directory:str) -> None:
    t:dict
    with open(f'{directory}/{ACTIVE_FILE}','r',encoding='utf-8') as f:
        t:dict = json.load(f)
        f.close()
    if pid not in t.keys():
        #TODO: logs
        return
    t.pop(pid)

    with open(f'{directory}/{ACTIVE_FILE}','w',encoding='utf-8') as f:
        json.dump(t, f)
        f.close()
    return


def __new_pids(active_pids: list[str], directory:str) -> None:
    if len(active_pids) == 0:
        return
    t: dict
    with open(f'{directory}/{ACTIVE_FILE}','r', encoding='utf-8') as f:
        t = json.load(f)
        f.close()

    pids_list = t.keys()

    for e in active_pids:
        if e not in pids_list:
            __add_active_PID(e,directory)

    return


def kill_pids(directory:str) -> None:
    t:dict
    with open(f'{directory}/{ACTIVE_FILE}', 'r', encoding='utf-8') as f:
        t = json.load(f)
        f.close()
    pid_to_remove:list[str] = []
    for e in t.keys():
        if datetime.fromisoformat(t[e]['time_to_kill']) <= datetime.now():
            __kill_active_PID(e)
            pid_to_remove.append(e)

    for e in pid_to_remove:
        __remove_inactive_PID(e,directory)


def main(args:dict) -> None:
    directory:str = args['directory']
    if args['add']:
        try:
            __check_for_new_files(directory,args['name'], args['time'])
        except Exception.args as e:
            #TODO: logs
            print(f'Err {e}')

    if args['verify']:
        kill_pids(directory)


if __name__ == "__main__":
    args:dict = __args()
    main(args)