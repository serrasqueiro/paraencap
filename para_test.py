""" Test para.py
"""

# pylint: disable=missing-function-docstring, unused-argument

import sys
import paramiko
import miko.para
from miko.netrc import NetRC

def main():
    host, username, password = get_credentials(sys.argv[1:])
    is_ok = True
    if host.startswith("@"):
        print(host)
    elif host:
        is_ok = connect_host(host, username, password)
    else:
        print("Wrong usage")
    assert is_ok

def get_credentials(args):
    if len(args) > 1:
        return "", "", ""
    param = args if args else ["127.0.0.1"]
    host = param[0]
    nrc = NetRC()
    if nrc.message():
        print(nrc.message())
        return "", "", ""
    nrc.plain()
    what = nrc.machines().get(host)
    if what is None:
        print("Invalid host:", host)
        return "@invalid", "", ""
    username, password = what["login"], what["pass"]
    return host, username, password

def connect_host(host, username, password):
    ccc = miko.para.Connector(host)
    cred = (username, password)
    try:
        ccc.connect_user(cred)
    except paramiko.ssh_exception.AuthenticationException:
        print("Failed to connect to:", host)
        return False
    print(f"Connected, ccc.get_name(): {ccc.get_name()}, user: {username}")
    ccc.new_session()
    tup = ccc.dribble("ls -la ~")
    dump_result(tup)
    while True:
        cmd = input("Enter command ... ")
        if cmd == ".":
            return True
        tup = ccc.dribble(cmd)
        print(tup)
        dump_result(tup)

def dump_result(tup, to_out=None):
    one, two, three = tup
    print("tup:", len(one), len(two), len(three))
    if not two and not three:
        print("No session?")
        return False
    out = sys.stdout if to_out is None else to_out
    if not out:
        return False
    alist = two
    for idx, line in enumerate(alist, 1):
        print(f"Idx #{idx}")
        #astr = b'ca\xe7o'.decode("ISO-8859-1")
        try:
            astr = line.decode("ascii")
        except UnicodeDecodeError:
            astr = line.decode("ISO-8859-1")
        out.write(astr + "\n")
    print()
    return True

# Main script
if __name__ == "__main__":
    main()
    # Short examples follow:
    #
    # abc = Connector("pena")
    # abc.connect("guest", mypass); abc.new_session(); abc.dribble("ls -la /")
