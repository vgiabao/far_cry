# !/bin/python3
#waypoint1
import csv
import re
from argparse import ArgumentParser
from datetime import datetime, time, tzinfo, timezone, timedelta
from os import getcwd
from re import fullmatch, match


def handle_parser():
    '''
    handle the command line interface
    '''
    default_path = getcwd()
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', help='whatever-directory',
                        metavar='filename', required=True,
                        default=default_path+'/log00.txt')
    return parser.parse_args()


def read_log_file(log_file_pathname):
    with open(log_file_pathname, 'r') as sever:
        data = sever.read()
    return data.splitlines()


def parse_log_start_time(log_data, timezones=None):
    content = log_data[0][15:]
    start_time = datetime.strptime(content, '%A, %B %m, %Y %H:%M:%S')
    if timezones:
        return start_time.replace(tzinfo=timezone(timedelta(hours=
                                                            int(timezones))))
    return start_time

def installization(content):
    initialization = {}
    for line in content:
        if 'Lua cvar' in line:
            data = line[19:-1].split(',')
            initialization.setdefault(data[0], data[1])
    return initialization


def find_character(line, start, end):
    start_point = line.find(start) + len(start)
    end_point = line.rfind(end)
    return line[start_point:end_point]


def parse_session_mode_and_map(content):
    mode_and_map = ''
    for item in content:
        if '---------------------- Loading' in item:
            mode_and_map = item
    map = find_character(mode_and_map, 'level Levels/', ',')
    mode = find_character(mode_and_map, 'mission ', ' ----')
    return (map, mode)


def character_time(content, char_time):
    initial_time = parse_log_start_time(content)
    c_minute = int(find_character(char_time, '<', ':'))
    c_second = int(find_character(char_time, ':', '>'))
    if c_minute != 59 and c_second != 59:
        initial_time = initial_time.replace(minute=c_minute, second=c_second)
    else:
        initial_time = initial_time.replace(hour=initial_time.hour + 1,
                                            second=00, minute=00)
    return initial_time.isoformat()

def parse_frags(content):
    frags = []
    bin = ['killed', '<Lua>', 'with']
    for item in content:
        if 'killed' in item:
            for trash in bin:
                item = item.replace(trash, '')
            frags_information = item.split()
            frags_information[0] = character_time(content,
                                                  frags_information[0])
            frags.append(frags_information)
    return frags


def prettify_frags(frags):
    beautify_list = []
    emoji_dic = {"\U0001F682": ['Buggy, Humvee'],
                 "\U0001F52B": ['Falcon', 'Shotgun', 'P90', 'MP5', 'M4'
                     ,'AG36', 'OICW', 'SniperRifle', 'M249', 'MG',
                               'VehicleMountedAutoMG', 'VehicleMountedMG'],
                 "\U0001F4A3": ['HandGrenade', 'AG36Grenade', 'OICWGrenade',
                                'StickyExplosive'],
                 "\U0001F680": ['Rocket', 'VehicleMountedRocketMG',
                                'VehicleRocket'],
                 "\U0001F52A": ['Machete'],
                 "\U0001F6F6":['Boat']}
    killer_emoji = "\U0001F618"
    victim_emoji = "\U0001F60E"
    suicide_emoji = "\U0001F480"
    for frag in frags:
        for key in emoji_dic:
            for value in emoji_dic[key]:
                if value == frag[-1]:
                    frag[-1] = key
        if len(frag) > 3:
            frag = '[' + frag[0] + '] ' + killer_emoji + ' ' + frag[1] + \
                   frag[-1] + victim_emoji + ' ' + frag[2]
        elif len(frag) == 3:
            frag = '[' + frag[0] + ']' + victim_emoji + ' ' + frag[1] + \
                   ' ' + suicide_emoji
        beautify_list.append(frag)
    return beautify_list


def parse_game_session_start_and_end_times(content):
    start_line = ''
    end_line = ''
    for index, line in enumerate(content):
        if 'killed' in line:
            start_line = (content[index - 1]).split()[0]
            break
    for index, line in enumerate(content):
        if '== Statistics             ' in line:
            end_line = (content[index - 1]).split()[0]
            break
    return (character_time(content, start_line),
            character_time(content, end_line))


def write_frag_csv_file(log_file_pathname, frags):
    with open(log_file_pathname, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows([item for item in frags])
    return




def main():
    path = handle_parser().path
    content = read_log_file(path)
    frags =  parse_frags(content)
    print(frags)
    write_frag_csv_file('bao.csv', frags)

if __name__ == '__main__':
    main()
