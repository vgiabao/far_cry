# !/bin/python3
#waypoint1
import csv
import re
from argparse import ArgumentParser
from datetime import datetime, timezone, timedelta
from os import getcwd
import sqlite3

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


def find_time_zone(content):
    for line in content:
        if 'g_timezone' in line:
            return find_character(line, '(', ')').split(',')[1]




def parse_log_start_time(log_data):

    '''
    find start time, timezone in log data
    :param log_data: content file
    :return: datetime
    '''

    #take string containing time
    content = log_data[0][15:]
    start_time = datetime.strptime(content, '%A, %B %m, %Y %H:%M:%S')
    # find timezone line
    timezones = int(find_time_zone(log_data))
    start_time = start_time.replace(tzinfo=timezone(timedelta(hours=timezones)))
    return start_time


def installization(content):
    '''
    make a dictionary contains key and value for loading game
    :param content: content of given file
    :return: dictionary includes loading objects and its details
    '''
    initialization = {}
    for line in content:
        if 'Lua cvar' in line:
            data = line[19:-1].split(',')
            initialization.setdefault(data[0], data[1])
    return initialization


def find_character(line, start, end):
    '''
    function used to replace regex
    :param line: string contain needed information
    :param start: the string in front of needed information
    :param end: the string after needed information
    :return: keywords
    '''
    start_point = line.find(start) + len(start)
    end_point = line.rfind(end)
    return line[start_point:end_point]


def parse_session_mode_and_map(content):
    '''
    take string comprising detail of map and mode
    :param content:
    :return:
    '''
    mode_and_map = ''
    for item in content:
        if '---------------------- Loading' in item:
            mode_and_map = item
    map = find_character(mode_and_map, 'level Levels/', ',')
    mode = find_character(mode_and_map, 'mission ', ' ----')
    return (map, mode)


def character_time(content, char_time):
    '''
    using for changing the format of given time
    :param content: the content of given file
    :param char_time: time of each player in match
    :return:
    '''
    initial_time = parse_log_start_time(content)
    try:
        c_minute = int(find_character(char_time, '<', ':'))
        c_second = int(find_character(char_time, ':', '>'))
    except ValueError:
        pass
    if c_minute != 59 and c_second != 59:
        initial_time = initial_time.replace(minute=c_minute, second=c_second)
    else:
        initial_time = initial_time.replace(hour=initial_time.hour + 1,
                                            second=00, minute=00)
    # initial_time.replace(tzinfo=timezone(timedelta(hours=int_)))
    return initial_time.isoformat()


def parse_frags(content):
    '''
    make a list comprising time, killer, victim, weapon of each match event
    :param content: content of file
    :return: detailed information of each event
    '''
    frags = []
    bin = ['killed', '<Lua>', 'with', 'itself']
    victim_name = ''
    for item in content:
        # find line comprising 'killed' and take keyword
        if 'killed' in item:
            if 'itself' not in item:
                victim_name = find_character(item, 'killed ', ' with')
                killer_name = find_character(item, '<Lua> ', ' killed')
            else:
                killer_name = find_character(item, '<Lua> ', ' killed')
            for trash in bin:
                # delete unnecessary string
                item = item.replace(trash, '')
            # a handicraft method to make a wanted list
            item = re.sub(killer_name, '', item)
            item = re.sub(victim_name, '', item)
            frags_information = item.split()
            if len(frags_information) == 2:
                weapon = frags_information[1]
                frags_information[1] = killer_name
                if victim_name:
                    frags_information.append(victim_name)
                frags_information.append(weapon)
            elif len(frags_information) == 1:
                frags_information.append(killer_name)
            frags_information[0] = character_time(content,
                                                  frags_information[0])
            frags.append(frags_information)

    return frags


def prettify_frags(frags):
    '''
    add emoji to each frags
    :param frags: list of frag
    :return: frags with pretty emojy
    '''
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
    '''
    calculate start time and end time of the match
    :param content: content of given file
    :return: start time and end time
    '''
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


def insert_frags_to_sqlite(connection, match_id, frags):
    '''
    fill the math_frag table in sql
    :param connection: connected database file
    :param match_id: id of match
    :param frags: list of frags
    '''
    cr = connection.cursor()
    for item in frags:
        if len(item) > 3:
            cr.execute('INSERT INTO match_frag\
                            (match_id , frag_time, killer_name, victim_name, weapon_code)\
                            VALUES\
                            (?, ?, ?, ?, ?)', (match_id, item[0], item[1], item[2], item[3]))
        else:
            cr.execute('INSERT INTO match_frag\
                                        (match_id , frag_time, killer_name)\
                                        VALUES\
                                        (?, ?, ?)', (match_id, item[0], item[1]))
    return


def analyse_game_statistics(frags):
    '''
    handle the information, count kill, death, suicide, and efficiency
    :param frags: list of frags
    '''
    distinct_players = []
    dic = {}
    for item in frags:
        if item[1] not in distinct_players:
            distinct_players.append(item[1])
    for player in distinct_players:
        dic[player] = [0, 0, 0]
    for item in frags:
        for player in dic:
            if item[1] == player and len(item) > 3:
                dic[player][0] += 1
            if len(item) > 3 and  item[2] == player:
                dic[player][1] += 1
            if len(item) <= 3:
                dic[player][1] += 1
    for statistic in dic:
        dic[statistic][2] = ("%.2f" % (dic[statistic][0]/(dic[statistic][0] + dic[statistic][1])*100)) + '%'
    return dic


def insert_frags_to_match_statistics(connection, match_id, frags):
    '''
    fill the math_statistics table in sql
    :param connection: connected database file
    :param match_id: id of match
    :param frags: list of frags
    '''

    information = analyse_game_statistics(frags)
    cr = connection.cursor()
    for item in information:
        cr.execute('INSERT INTO match_statistics\
                        (match_id , player_name, kill_count, death_count, efficiency)\
                        VALUES\
                        (?, ?, ?, ?, ?)', (match_id, item, information[item][0], information[item][1],
                                           information[item][2]))
    return


def insert_match_to_sqlite(file_pathname, start_time1, end_time1, game_mode1, map_name1, frags):
    '''
    insert information to sqlite
    :param file_pathname: file database
    :param start_time1: start time of the match
    :param end_time1: the end moment of the match
    :param game_mode1: type of match
    :param map_name1: category of map
    :param frags: list of frags
    '''
    con = sqlite3.connect(file_pathname)
    cr = con.cursor()
    cr.execute('INSERT INTO match\
                (start_time, end_time, game_mode, map_game)\
                VALUES\
                (?, ?, ?, ?)', (start_time1, end_time1, game_mode1, map_name1))
    match_id = cr.lastrowid
    insert_frags_to_sqlite(con, match_id, frags)
    insert_frags_to_match_statistics(con, match_id, frags)
    con.commit()
    con.close()
    return


def main():
    path = handle_parser().path
    content = read_log_file(path)
    log_start_time = parse_log_start_time(content)
    frags = parse_frags(content)
    game_mode, map_name = parse_session_mode_and_map(content)
    start_time , end_time = parse_game_session_start_and_end_times(content)
    insert_match_to_sqlite('far_cry.db', start_time, end_time, game_mode, map_name, frags)

if __name__ == '__main__':
    main()
