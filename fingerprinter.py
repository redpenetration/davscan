import subprocess
import requests
from urllib.parse import urlparse
#####################################################
#
# Color class for text output
# Making shit pretty since 1982!
#
#########################################################
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
######################################################
# Fingerprinter function:
#       Uses a head request to fingerprint
#       server usingarch_define the Server and X headers
#       uses the () and xfind() functions
#
# Requires "u" as the url
#
# Returns "d" as dict listing server
#       powered by and/or ASP version information
#
#
######################################################
def fingerprint(sess, url, msf, dos):
    d = {}
    u = url.scheme + '://' + url.netloc + '/'
    r = sess.options(u)
    print(("options response status: " + str(r.status_code)))
    if r.status_code == 200:
        print("response headers: ")
        for h in r.headers:
            print(("- " + h + " ==> " + r.headers[h]))
            #print(bcolors.HEADER + "[*] looking at header %s " % h + bcolors.ENDC)
            if "Server" in h:
                d.update({'Server': r.headers[h]})
                o = exploit_finder(r.headers[h], msf, dos)
                if o is not None:
                    for k,v in o.items():
                        d.update({k:v})
            if "Allow" in h:
                print("[*] Searching for enabled WebDAV...")
                if "PROPFIND" in r.headers[h]:
                    print((bcolors.OKGREEN + "[+] WebDAV enabled!" + bcolors.ENDC))
                    d.update({'WebDAV': 'Enabled'})
                else:
                    d.update({'WebDAV': 'Disabled'})
            if "X-Powered-By" in h:
                x = xfind(r.headers[h], msf, dos)
                if x is not None:
                    for k,v in x.items():
                        d.update({k:v})
    return d
#######################################################
# exploit_find function:
#       Uses the server header to identify IIS or Apache or nginx
#       web server arch and then returns y as a list of possible
#       exploits in addition to DAV scanning.
#
#       Requires "m" as server header value
#
#       Returns "y" a list of exploits for the server.
#
#######################################################
def exploit_finder(m, msf, dos):
    y = {}
    if "/" in m:
        n = m.split('/')
        print((bcolors.HEADER + "[*] Server identified itself as %s with version %s. Finding exploits for server"% (n[0], n[1]) + bcolors.ENDC))
        if n[0] == "Microsoft-IIS":
            if n[1] == "5.0":
                from sploits import IIS5
                y = IIS5(msf, dos).sploits
                return y
            if n[1] == "6.0":
                from sploits import IIS6
                y = IIS6(msf, dos).sploits
                return y
            if n[1] == "7.5":
                from sploits import IIS75
                y = IIS75(msf, dos).sploits
                return y
            print((bcolors.WARNING + "[-] No public exploits found for IIS version %s" % n[1] + bcolors.ENDC))
            return None
        if n[0] == "Apache":
            if "1.3" in n[1]:
                from sploits import Apache13
                y = Apache13(msf, dos).sploits
                return y
            if "2.0" in n[1]:
                from sploits import Apache20
                y = Apache20(msf, dos).sploits
                return y
            if "2.2" in n[1]:
                from sploits import Apache22
                y = Apache22(msf, dos).sploits
                return y
            if "2.4" in n[1]:
                from sploits import Apache24
                y = Apache24(msf, dos).sploits
                return y
            print((bcolors.WARNING + "[-] No public exploits found for Apache version %s" % n[1] + bcolors.ENDC))
            return None
        if n[0] == "nginx":
            if "0.6" in n[1]:
                from sploits import nginx06
                y = nginx06(msf, dos).sploits
                return y
            if "0.7" in n[1] or "0.8" in n[1]:
                #0.7 and 0.8 have the same vulnerabilities.  We'll lump them together
                from sploits import nginx078
                y = nginx078(msf, dos).sploits
                return y
            if "1.1.17" in n[1]:
                from sploits import nginx11
                y = nginx11(msf, dos).sploits
                return y
                #same as with 0.7 and 0.8 similar vulnerabilities so we combine them.
            if "1.3.9" in n[1] or "1.4" in n[1]:
                from sploits import nginx134
                y = nginx134(msf, dos).sploits
                return y
            print((bcolors.WARNING + "[-] No public exploits found for nginx version %s" %  n[1] + bcolors.ENDC))
            return None
    else:
        print((bcolors.HEADER + "[*] no sploit collection has been provided for %s.  Checking local exploit-db..." % m + bcolors.ENDC))
        from sploits import Other
        y = Other(m, msf, dos).sploits
        return y
#########################################################
# xfind function:
#       Uses the x-powered-by header to find technologies
#       that are in use on the server
#
#       Requires "m" as x-powered-by header value
#
#       Returns "l" as list of technologies or m if only one
#       technology
#
##########################################################
def xfind(m, msf, dos):
    ploit = {}
    if "," in m:
        l = m.split(',')
        k = len(l)
        for a in l:
            print(("[*] Searching for exploits for %s" % a))
            if "/" in a:
                b = a.split('/')
                if b[0] == "PHP":
                    from sploits import PHP
                    if PHP(b[1],msf,dos).sploits is not None:
                        for k,v in p.sploits.items():
                            ploit[k] = v
                    else:
                        print(("[-] Unable to find public exploits for %s" % a))
                if b[0] == "ASP.NET":
                    from sploits import ASP
                    if ASP(b[1],msf,dos).sploits is not None:
                        for k,v in p.sploits.items():
                            ploit[k] = v
                    else:
                        print(("[-] Unable to find public exploits for %s" % a))
    else:
        if "ASP.NET" in m:
            if "/" in m:
                n = m.split('/')
                print("[*] Server uses %s and is at version %s" % (n[0], n[1]))
                from sploits import ASP
                if ASP(n[1],msf,dos).sploits is not None:
                    for k,v in ASP(n[1],msf,dos).sploits.items():
                        ploit[k] = v
        if "PHP" in m:
            if "/" in m:
                n = m.split('/')
                print("[*] Server uses %s and is at version %s" % (n[0], n[1]))
                from sploits import PHP
                if PHP(n[1],msf,dos).sploits is not None:
                    for k,v in PHP(n[1],msf,dos).sploits.items():
                        ploit[k] = v
    return ploit
