#!/bin/python3
#waypoint1
from argparse import ArgumentParser
from datetime import datetime
from os import getcwd


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
    with open(log_file_pathname, 'rb') as sever:
        data = sever.read()
    return data


def parse_log_start_time(log_data, timezone=None):
    content = log_data.splitlines()[0][15:].decode()
    start_time = datetime.strptime(content, '%A, %B %m, %Y %H:%M:%S')
    return start_time


def installization(log_data):
    initialization = {}
    content = log_data.splitlines()
    for line in content:
        line = line.decode()
        if 'Lua cvar' in line:
            data = line[19:-1].split(',')
            initialization.setdefault(data[0], data[1])
    return initialization



def log_start_time(numberic_status):
    return datetime(numberic_status.split(' '))


def main():
    path = handle_parser().path
    content = read_log_file(path)
    initialization = installization(content)
    start_tinme = parse_log_start_time(content, initialization['g_timezone'])

if __name__ == '__main__':
    main()