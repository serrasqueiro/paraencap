# aresolver.py  (c)2021  Henrique Moreira
#
# dns.resolver, yet another resolver!

"""
Wraps dns.resolver
"""

# pylint: disable=missing-function-docstring, no-self-use, invalid-name

import dns.resolver


def basic_test():
    assert Singleton().validate_ipaddr("1.2.3.4")
    res = Resolved()
    res.query("serrasqueiro.com", "MX")
    for key in sorted(res.basics()):
        there = res.basics()[key]
        print(f"{key}\t{there}")
    domain = input("Please enter a www domain... ")
    if not domain or domain == ".":
        domain = "www.yahoo.com"
    full_list = res.query(domain, "CNAME")
    full_list = res.results()
    if full_list:
        _, data = full_list[0]
        show = data
    else:
        show = f"None! Message: {res.message()}"
    print(domain, "; CNAME:", show)
    assert len(full_list) <= 1


class Singleton():
    """ Main aresolver singleton! """
    _resolver = None

    def __init__(self):
        resolver = dns.resolver.Resolver()
        self._resolver = resolver

    def Resolver(self):
        """ Returns the object 'Resolver' """
        return self._resolver

    def NameServers(self) -> list:
        """ Returns the list of nameservers """
        names = self._resolver.nameservers
        assert isinstance(names, list)
        return names

    @staticmethod
    def validate_ipaddr(ipaddr:str, only_ipv4=True) -> bool:
        """ Basic validation of an IPv4 addess """
        assert isinstance(ipaddr, str)
        assert ipaddr.strip() == ipaddr, f"Uops: '{ipaddr}'"
        octals = ipaddr.split(".")
        if len(octals) != 4:
            return False
        for astr in octals:
            value = int(astr)
            if 0 <= value < 256:
                continue
            return False
        assert only_ipv4, "Only prepared with IPv4 so far!"
        return True

class Utils():
    """ Abstract generic string utils. """
    _msg = ""

    def message(self) -> str:
        return self._msg

    def _simpler_MX_list(self, mxs:list) -> list:
        if not mxs:
            return []
        res = []
        for elem in sorted(mxs):
            text = elem.split(" ", maxsplit=1)[1]
            if text not in res:
                res.append(text)
        return res

class Resolved(Utils):
    """ Wrapper for 'resolve()' results """

    _result = None

    def __init__(self):
        """ Just initialize """
        self._msg = ""
        self._result = None

    def results(self) -> list:
        """ Returns the list of results
        """
        if self._result is None:
            return list()
        return [self._is_valid(elem) for elem in self._result]

    def basics(self) -> dict:
        """ Returns results as a dictionary """
        dct = {
            "A": [],
            "MX": [],
            "CNAME": [],
            "@other": [],
        }
        datas = self.results()
        for kind, rdata in datas:
            there = kind
            if kind in dct:
                if kind == "MX":
                    text = rdata.to_text().split(" ", maxsplit=1)[1]
                    what = f"{rdata.preference:03} {text}"
                else:
                    what = rdata.to_text()
                dct[there].append(what)
            else:
                there = "@other"
                dct[there].append((kind, rdata.to_text()))
        dct["MX"] = self._simpler_MX_list(dct["MX"])
        return dct

    def query(self, name:str, what:str=""):
        self._msg = ""
        resolver = Singleton().Resolver()
        if what:
            try:
                data = resolver.resolve(name, what)
            except dns.resolver.NXDOMAIN:
                data = None
                self._msg = f"No domain: '{name}'"
            except dns.resolver.NoAnswer:
                self._msg = f"No answer: '{name}'"
                data = None
        else:
            try:
                data = resolver.resolve(name)
            except dns.resolver.NXDOMAIN:
                data = None
        self._result = data
        return data

    def _is_valid(self, elem):
        assert elem
        return (elem.rdtype.name, elem)

# Main script
if __name__ == "__main__":
    print("Please import me!")
    basic_test()
