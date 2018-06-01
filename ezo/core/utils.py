import json, asyncio
from eth_account import Account
from xkcdpass import xkcd_password as xp


def create_ethereum_account():
    ac = Account.create()
    wf = xp.locate_wordfile()
    words= xp.generate_wordlist(wordfile=wf, min_length=5, max_length=8)

    password_str = xp.generate_xkcdpassword(words)
    print("password string to decrypt private key -- please store in safe location:")
    print()
    print(password_str)
    print()
    print("address:")
    print(ac.address)

    ks = json.dumps(Account.encrypt(ac.privateKey, password_str), indent=2)
    print(ks)


async def event_loop(event_filter, interval=1):
    while True:
        for event in event_filter.get_new_entries():
            print("got an event: {}".format(event))
            handle_event(event)
        print("in event loop")
        await asyncio.sleep(interval)


def handle_event(event):
    print("event: {}".format(event))