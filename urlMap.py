#! /bin/env python3.10
import re
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

worker_threads = []

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


# If responce code is not over 400 print responce to screen
def print_responce(status_code, url):
    if status_code == 200:
        print(f"{green}[+] {norm}{url}        Status: ({yellow}{status_code}{norm})")
        found_urls.append(url)

    elif status_code in range(300, 399):
        print(f"{blue}[+] {norm}{url}        Status: ({yellow}{status_code}{norm})")

    elif status_code in range(100, 199):
        print(f"[+] {url}        Status: ({yellow}{status_code}{norm})")


# Take Url and append a word from the wordlist and checks the response code
def get_statusCode(word, new_url=""):
    if new_url == "":
        url = base_url + word
    else:
        url = new_url + word

    
    try:
        FOUND_url = urllib.request.urlopen(url).getcode()
        print_responce(FOUND_url, url)
    except KeyboardInterrupt:
        exit()
    except:
        pass

    



# Grabs a word from the queue and runs the get_statusCode function
def thread(url=""):
    while q.qsize() > 0:
        word = q.get()
        if word != "":
            word = "/" + word

            get_statusCode(word, url)
        q.task_done()


# Menu for when enumeration has started
def print_menu(wordlist, num_of_threads, URL):
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



    print_menu(wordlist, num_of_threads, URL)

    p1 = multiprocessing.Process(target=spinning_cursor)
    p1.start()

    for i in range(num_of_threads):
        t = threading.Thread(target=thread)
        t.daemon = True
        t.start()
        worker_threads.append(t)


    try:
        for Thread in worker_threads:
            Thread.join()

    except KeyboardInterrupt:
        exit()



    print(f"\n\n{box}Finished wordlist\n{box}Starting stage 2.")
   
   
    # Stage 2
    for URL in found_urls:
        for line in (wordlist_line):
            q.put(line)


        for i in range(num_of_threads):
            t = threading.Thread(target=thread, args=(URL,))
            t.daemon = True
            worker_threads.append(t)
            t.start()

        try:
            for Thread in worker_threads:
                Thread.join()

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
    base_url = parsed_args.url
    main(parsed_args.url, parsed_args.wordlist, parsed_args.threads)