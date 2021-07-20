# netrc.py  (c)2021  Henrique Moreira
#
# Reader of ~/.netrc file

"""
Basic netrc file reader
"""

# pylint: disable=missing-function-docstring, unused-argument

import os
import re

def test():
    print("""machines() result is a dictionary, keyed by the host strings;
each host entry has a 'list' dictionary, a 'login' string, and a 'pass' string.
""")
    nrc = NetRC()
    code = nrc.plain()
    assert code == 1, f"Invalid nrc.plain(): {code}"
    print("nrc:", nrc.machines())
    key = input("Enter host or IP: ...")
    if len(key) >= 1:
        print(f"Credentials for host '{key}':", nrc.credential(key))

class Reader():
    """ Basic abstract reader. """
    @staticmethod
    def home_path() -> str:
        """ Returns the home path """
        if os.name == "nt":
            astr = os.environ.get("USERPROFILE")
        else:
            astr = os.environ.get("HOME")
        if not astr:
            return "/"
        return astr

    @staticmethod
    def relevant(astr:str) -> str:
        """ Returns a right-stripped string, if it is not a comment (hash, i.e. '#');
        or an empty string otherwise.
        """
        new = astr.rstrip(" \n")
        if not new or new.startswith("#"):
            return ""
        return new

class NetRC(Reader):
    """ Plain-text password reader """
    _data = ""
    _seqs = None
    _mach = None

    def __init__(self, fname=None):
        self._data, self._seqs, self._mach = "", list(), dict()
        if fname == "":
            return;
        suffix = ".netrc" if os.name != "nt" else "_netrc"
        path = fname if fname else os.path.join(Reader.home_path(), suffix)
        self._data = open(path, "r").read()

    def sequence(self) -> list:
        assert self._seqs is not None
        return self._seqs

    def machines(self) -> dict:
        """ Returns the 'machine' dictionary.
        """
        return self._mach['machine']

    def credential(self, machine:str) -> tuple:
        machs = self._mach['machine']
        if machine not in machs:
            return (None, None)
        return machs[machine]['login'], machs[machine]['pass']

    def plain(self) -> bool:
        """ Parse plain-text in _data """
        code = self._parse(self._data)
        return code == 0

    def _parse(self, data:str) -> int:
        # Throw away comments
        lines = [astr for astr in data.splitlines() if Reader.relevant(astr)]
        self._seqs = re.split(r"(machine) ", '\n'.join(lines))
        msg, machs = self._parse_machines(self._seqs)
        if msg:
            return 1
        self._mach = {
            'machine': machs,
        }
        return 0

    def _parse_machines(self, seqs:list) -> dict():

        def flush_this(alist:list, result:dict):
            if not alist:
                return False
            # New-line, or tab, or space...
            spl = re.split("\n|\t|\s", '\n'.join(alist))
            mach, rest = spl[0], spl[1:]
            login, password = "", ""
            idx = 0
            for item in rest:
                if item == "login":
                    login = rest[idx+1]
                elif item == "password":
                    password = rest[idx+1]
                idx += 1
            result[mach] = dict()
            result[mach]['list'] = [item for item in rest if item]
            result[mach]['login'], result[mach]['pass'] = login, password
            alist.clear()
            return True

        adict = dict()
        last = list()
        for item in seqs:
            if not item:
                continue
            if item == "machine":
                flush_this(last, adict)
            else:
                last.append(item)
        return ("", adict)

# Main script
if __name__ == "__main__":
    print("Please import me!")
    test()
