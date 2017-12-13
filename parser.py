# -*- coding: utf-8 -*-
"""
@author: edipdemirbilek
"""
import codecs
import copy
import sys
import os
import re
from bs4 import BeautifulSoup
import urllib3
import requests


def findSubstring(s1, s2):
    """
    Finds the longest sequence common between two strings where the common
    string is at the end of first string and at the beginning of second
    string.
    """
    len_s1 = len(s1)
    len_s2 = len(s2)

    if len_s1 > 1 and len_s2 > 1:
        len_min = min(len_s1, len_s2)

        for i in range(len_min, 1, -1):
            sub_s1 = s1[len(s1)-i:]
            sub_s2 = s2[:i]
            if sub_s1 == sub_s2:
                return i
    return 0


def download(show_episode_url):
    """
    Download *.vtt subtitle file from the given URL.
    """
    print("Downloading Episode HTML File From: " + show_episode_url)
    urllib3.PoolManager()
    r = requests.get(show_episode_url)

    print("Processing HTML File for VTT information.")
    soup = BeautifulSoup(r.text, 'html.parser')

    lists = soup.find_all('meta')
    file_name = re.search('2016.*jpg', str(lists[-1])).group(0)[:-7] + '.vtt'
    full_url = "http://static.tou.tv/medias/webvtt/" + file_name

    print("Downloading Episode VTT File From: " + full_url)
    f = open(file_name, 'wb')
    f.write(requests.get(full_url).content)
    f.close()

    return file_name


def preprocess(vtt_file, pre_file):
    """
    Merges multiple lines into single line.
    """
    fi = codecs.open(vtt_file, "r", "utf-8")
    fo = codecs.open(pre_file, "w", "utf-8")

    longLine = ""
    print("Merging multiple lines into one line.")
    for line in fi:
        if len(line) > 1:
            longLine += line.rstrip('\n')+" "

        else:
            longLine.rstrip(' ')
            fo.write(longLine)
            fo.write("\n")
            longLine = ""

    fo.close()
    fi.close()


def extract_text(pre_file, extract_file):
    """
    Remove duplicates in the text.
    """
    fi = codecs.open(pre_file, "r", "utf-8")
    fo = codecs.open(extract_file, "w", "utf-8")
    i = 0
    last_line = ""
    fi.readline()

    print("Removing duplicates in text.")
    for line in fi:
        new_line = copy.copy(line[30:].rstrip('\n'))
        maxStrInd = findSubstring(last_line, new_line)
        if maxStrInd > 0:
            last_line += copy.copy(new_line[maxStrInd:])
        else:
            last_line += " "+copy.copy(new_line)
        i += 1

    fo.write(last_line.replace("- ", "\n- "))
    fo.close()
    fi.close()


def add_time_stamps(extract_file, pre_file, txt_file, vtt_file):
    """
    Adds proper timestamps to the text.
    """
    fi_extract = codecs.open(extract_file, "r", "utf-8")
    fi_pre = codecs.open(pre_file, "r", "utf-8")
    fo = codecs.open(txt_file, "w", "utf-8")

    pre_lines = fi_pre.readlines()
    index = 0

    print("Adding time_stamps.")
    for line in fi_extract:
        if line[:2] == "- " and len(line) > 3:
            token = "- "+line[2:].split()[0]

            while index < len(pre_lines):
                if pre_lines[index].find(token) != -1:
                    time_stamp = pre_lines[index][:8]
                    line = line.replace(token, time_stamp+" "+token)
                    fo.write(line)
                    break
                index += 1

    fo.close()
    fi_extract.close()
    fi_pre.close()

    os.remove(vtt_file) if os.path.exists(extract_file) else None
    os.remove(extract_file) if os.path.exists(extract_file) else None
    os.remove(pre_file) if os.path.exists(pre_file) else None

    print("Done!")
    print("Content at: " + txt_file)


def main():
    """
    Download, process and writes subtitle info to txt file.

    Arguments:
        None

    Returns:
        None

    Raises:
        None
    """
    if len(sys.argv) < 2:
        print("Please provide episode URL as argument.")
        raise SystemExit

    show_episode_url = sys.argv[1]

    vtt_file = download(show_episode_url)

    pre_file = os.path.splitext(vtt_file)[0] + ".pre"
    preprocess(vtt_file, pre_file)

    extract_file = os.path.splitext(vtt_file)[0] + ".extract"
    extract_text(pre_file, extract_file)

    txt_file = os.path.splitext(vtt_file)[0] + ".txt"
    add_time_stamps(extract_file, pre_file, txt_file, vtt_file)


if __name__ == '__main__':
    main()
