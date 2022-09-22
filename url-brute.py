#! /bin/env python3
import sys
import urllib.request
import os
import threading
import queue
import time
import multiprocessing
import argparse
from colorama import Fore, Style
import random 
import subprocess


# Colors
if sys.platform != "win32":
    red = Fore.RED
    yellow = Fore.YELLOW
    blue = Fore.BLUE
    norm = Style.RESET_ALL
    green = Fore.GREEN
    box = (red + "[" + yellow + "+" + red + "] " + norm)
    error_box = (red + "[" + yellow + "!" + red + "] " + norm)
else:
    red = ""
    yellow = ""
    blue = ""
    norm = ""
    green = ""
    box = "[+] "
    error_box = "[!] "


# Lists to be filled at runtime
found_urls = []
wordlist_line = []
tryed_words = []

q = queue.Queue()

# Spinning cursor for when script is running
def spinning_cursor():
    colors = [red, yellow, blue, green, norm]
    try:
        while True:
            for cursor in '\\|/-':
                rand_color = random.choice(colors)
                time.sleep(0.1)
                sys.stdout.write(f'\r{rand_color}{cursor}{norm}')
                sys.stdout.flush()
    except KeyboardInterrupt:
        exit(0)

# Take Url and append a word from the wordlist and checks the response code
def get_statusCode(word):
    if len(tryed_words) == len(wordlist_line):
        return

    URL_test = URL + word
    if word not in tryed_words:
        try:
            tryed_words.append(word)
            FOUND_url = urllib.request.urlopen(URL_test).getcode()

            if FOUND_url == 200:
                print(f"{green}[+] {norm}{URL_test}        Status: ({yellow}{FOUND_url}{norm})")
                found_urls.append(URL_test)
            elif FOUND_url in range(300, 399):
                print(f"{blue}[+] {norm}{URL_test}        Status: ({yellow}{FOUND_url}{norm})")
            elif FOUND_url in range(100, 199):
                print(f"[+] {URL_test}        Status: ({yellow}{FOUND_url}{norm})")
        except KeyboardInterrupt:
            exit()
        except:
            pass

# Grabs a word from the queue and runs the get_statusCode function
def thread():
    while True:
        word = q.get()
        if word != "":
            word = "/" + word
            get_statusCode(word)
        q.task_done()


def main(URL, wordlist, num_of_threads):
    if not os.path.exists(wordlist) and not os.path.isfile(wordlist):
        print(f"{error_box}Invalid wordlist file: {wordlist}")
        exit(1)


    try:
        URL_Validate = urllib.request.urlopen(URL).getcode()
        if not URL_Validate == 200:
            print(f"{error_box}{URL} Is not reachable.")
            exit(1)

    except ValueError:
        print(f"{error_box}{URL} Is not a valid URL.")
        exit(1)


    with open(wordlist, "r") as f:
        for line in f:
            if line != "" and not line.startswith("#") and line != "/":
                wordlist_line.append(line.strip())
                q.put(line.strip())



    if sys.platform == "win32":
        os.system("cls")
        wordlist_split = wordlist.split("\\")
    else:
        os.system("clear")
        wordlist_split = wordlist.split("/")



    wordlist_name = wordlist_split[-1]
    print(blue + "=" * 60 + norm)
    print(f"""{box} Url     :                 {URL}
{box} Threads :                 {num_of_threads}
{box} Wordlist:                 {wordlist_name}
 """)
    print(blue + "=" * 18 + yellow + " Starting Enumeration " + blue + "=" * 19 + norm)

    p1 = multiprocessing.Process(target=spinning_cursor)
    p1.start()

    for i in range(num_of_threads):
        t = threading.Thread(target=thread)
        t.daemon = True
        t.start()

    try:
        q.join()
    except KeyboardInterrupt:
        exit()

    print(f"\n\n{box}Finished wordlist\n{box}Starting stage 2.")
    # Stage 2
    for _ in found_urls:
        tryed_words.clear()

        for line in (wordlist_line):
            q.put(line)

        for _ in range(num_of_threads):
            t = threading.Thread(target=thread,)
            t.daemon = True
            t.start()

        try:
            q.join()
        except KeyboardInterrupt:
            exit()

    p1.kill()
    print(blue + "=" * 24 + yellow + " Finished " + blue + "=" * 25 + norm)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="url-brute: Takes in a URl and wordlist. Then appends a word to the end of the Url and checks the response code.")
    parser.add_argument("-u", type=str, required=True,help="Url to enumerate", dest="url")
    parser.add_argument("-w", type=str, required=True,help="Path to the wordlist.", dest="wordlist")
    parser.add_argument("-t", type=int, help="Number of threads to use. Default 200", default=200, dest="threads")
    parsed_args = parser.parse_args()
    URL = str(parsed_args.url)
    main(URL, parsed_args.wordlist, parsed_args.threads)
