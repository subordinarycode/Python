#! /bin/env python3

import sys
import os
import threading
import queue
import time
import multiprocessing
import argparse
from colorama import Fore
import random
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Colors
red = Fore.RED
yellow = Fore.YELLOW
blue = Fore.BLUE
norm = Fore.RESET
green = Fore.GREEN
box = (red + "[" + yellow + "+" + red + "] " + norm)
error_box = (red + "[" + yellow + "!" + red + "] " + norm)



# Lists to be filled at runtime
found_urls = []
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


# Take Url and append a word from the wordlist and checks the response code
def get_statusCode(url):
    try:
        r = requests.get(url, verify=False)
        if r.status_code == 200:
            print(f"{green}[+] {norm}{url}        Status: ({yellow}{status_code}{norm})")
            found_urls.append(url)

        elif r.status_code in range(300, 399):
            print(f"{blue}[+] {norm}{url}        Status: ({yellow}{status_code}{norm})")

        elif r.status_code in range(100, 199):
            print(f"[+] {url}        Status: ({yellow}{status_code}{norm})")

    except KeyboardInterrupt:
        p1.kill()
        exit()
    except:
        pass


# Grabs a word from the queue and runs the get_statusCode function
def thread(url):
    while q.qsize() > 0:
        word = q.get()
        if not url.endswith("/"):
            new_url = f"{url}/{word}"
        else:
            new_url = url + word

        get_statusCode(new_url)
        q.task_done()
    return


# Menu for when enumeration has started
def print_menu():
    if sys.platform == "win32":
        os.system("cls")
        wordlist_name = args.wordlist.split("\\")[-1]
    else:
        os.system("clear")
        wordlist_name = args.wordlist.split("/")[-1]

    print(blue + "=" * 60 + norm)
    print(f"""{box} Url     :                 {args.url}
{box} Threads :                 {args.threads}
{box} Wordlist:                 {wordlist_name}
 """)
    print(blue + "=" * 18 + yellow + " Starting Enumeration " + blue + "=" * 19 + norm)



def main():
    wordlist = []

    if not os.path.isfile(args.wordlist):
        print(f"{error_box}Invalid wordlist file: {args.wordlist}")
        exit(1)

    try:
        r = requests.get(args.url, verify=False)
        if not r.ok:
            print(f"{error_box}{args.url} Is not reachable.")
            exit(1)
    except:
        print(f"{error_box}{args.url} Is not reachable.")
        exit(1)


    with open(args.wordlist, "r") as f:
        content = f.read().split("\n")

    for line in content:
        if line and line != "/":
            if not line.startswith("#"):
                wordlist.append(line.strip())
                q.put(line.strip())

    print_menu()
    p1.start()


    for i in range(args.threads):
        t = threading.Thread(target=thread, args=[args.url])
        t.daemon = True
        t.start()
        worker_threads.append(t)


    try:
        for Thread in worker_threads:
            Thread.join()

    except KeyboardInterrupt:
        p1.kill()
        exit()

    print(f"\n\n{box}Finished wordlist\n{box}Starting stage 2.")


    # Stage 2
    for url in found_urls:
        for line in wordlist:
            q.put(line)

        for i in range(args.threads):
            t = threading.Thread(target=thread, args=[url])
            t.daemon = True
            worker_threads.append(t)
            t.start()

        try:
            for Thread in worker_threads:
                Thread.join()

        except KeyboardInterrupt:
            p1.kill()
            exit()

    p1.kill()
    print(blue + "=" * 24 + yellow + " Finished " + blue + "=" * 25 + norm)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="url-brute: Takes in a URl and wordlist. Then appends a word to the end of the Url and checks the response code.")
    parser.add_argument("-u", type=str, required=True,help="Url to enumerate", dest="url")
    parser.add_argument("-w", type=str, required=True,help="Path to the wordlist.", dest="wordlist")
    parser.add_argument("-t", type=int, help="Number of threads to use. Default 20", default=20, dest="threads")
    args = parser.parse_args()

    p1 = multiprocessing.Process(target=spinning_cursor)

    main()
