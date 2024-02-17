import tls_client
import concurrent.futures
import random
import yaml
import os
import datetime
import ctypes
from httpx import get
from base64 import b64encode
from json import dumps
from colorama import Fore

v = 0
i = 0
l = 0
r = 0
e = 0

config = yaml.safe_load(open('config.yml', 'r'))
def title():
    global v, i, l , r, e
    ctypes.windll.kernel32.SetConsoleTitleW(f'Free Tokens Checker | Valid: {v} | Invalid: {i} | Locked: {l} | Ratelimit: {r} | Error: {e}')

nows = datetime.datetime.now()
folder = f'Output/{nows.strftime("%d-%m-%Y %H-%M")}'
os.makedirs(f'{folder}', exist_ok=True)

login_response = get('https://discord.com/login')
good_file = login_response.text.split('<script src="/assets/')
good_file = good_file[-10].split('"')[0]
file = 'https://discord.com/assets/' + good_file
file_response = get(file)
build_number = file_response.text.split('build number ".concat("')[1].split('"')[0]
xprops = {
            "os":"Windows",
            "browser":"Chrome",
            "device":"",
            "system_locale":"fr-FR",
            "browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "browser_version":"119.0.0.0",
            "os_version":"10",
            "referrer":"",
            "referring_domain":"",
            "referrer_current":"",
            "referring_domain_current":"",
            "release_channel":"stable",
            "client_build_number":build_number,
            "client_event_source":None,
            "design_id":0
            }
xsuperprops = b64encode(dumps(xprops).encode()).decode()

def getProxy():
    proxy_list = random.choice(open('Data/proxies.txt', 'r').read().splitlines())
    return {"http": f"http://{proxy_list}", "https": f"http://{proxy_list}"}
        
def getTokens():
    all_tokens = []
    for i in open('Data/tokens.txt', 'r').read().splitlines():
        if ':' in i:
            i = i.split(':')[2]
            all_tokens.append(i)
        elif '|' in i:
            i = i.split('|')[2]
            all_tokens.append(i)
        else:
            all_tokens.append(i)
    return all_tokens


def check(token):
    global v, i, l, r, e
    client = tls_client.Session(client_identifier="chrome112", random_tls_extension_order=True)
    client.proxies = getProxy() if config['proxies'] == True else None
    headers = {
                "Accept": "*/*",
                "Accept-language": "fr-FR,fr;q=0.8",
                "Authorization": token,
                "Content-type": "application/json",
                "Origin": "https://discord.com",
                "Referer": "https://discord.com/channels/@me",
                "Sec-Ch-Ua": '"Not.A/Brand";v="24", "Chromium";v="119", "Google Chrome";v="119"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "Windows",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "X-Debug-Options": "bugReporterEnabled",
                "X-Discord-Locale": "fr",
                "X-Super-Properties": xsuperprops
    }
    title()
    response = client.get('https://discord.com/api/v9/users/@me', headers=headers)
    if response.status_code == 200:
        print(Fore.LIGHTGREEN_EX, "Valid", token, Fore.RESET)
        v += 1
        open(f"{folder}/valid.txt", "a+").write(f"{token}\n")
    elif response.status_code == 401:
        print(Fore.RED, "Invalid", token, Fore.RESET)
        i += 1
        open(f"{folder}/invalid.txt", "a+").write(f"{token}\n")
    elif "You are being rate limited." in response.text:
        retry_time = response.json()['retry_after']
        print(Fore.YELLOW, "Ratlimit retry in", retry_time, "s", Fore.RESET)
        r += 1
    elif "verifiy" in response.text:
        print(Fore.YELLOW, "Locked", token, Fore.RESET)
        l += 1
        open(f"{folder}/locked.txt", "a+").write(f"{token}\n")
    else:
        print(Fore.LIGHTBLUE_EX, response.json(), Fore.RESET)
        e += 1

def start():
    tokens = getTokens()
    t = config['thread']
    with concurrent.futures.ThreadPoolExecutor(max_workers=t) as executor:
        for token in tokens:
            executor.submit(check, token)

if __name__ == "__main__":
    start()
    print(Fore.BLUE, 'Sucessfully checked', len(open('Data/tokens.txt', 'r').read().splitlines()), 'token(s).', Fore.RESET)
    input(f' {Fore.BLUE}Press enter to exit.')