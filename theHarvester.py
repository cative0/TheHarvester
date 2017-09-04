#!/usr/bin/env python
import json
import string
import httplib
import sys
import os
from socket import *
import re
import getopt

try:
    import requests
except:
    print "Request library not found, please install it before proceeding\n"
    sys.exit()

from discovery import *
from lib import htmlExport
from lib import hostchecker

print "\n*******************************************************************"
print "*                                                                 *"
print "* | |_| |__   ___    /\  /\__ _ _ ____   _____  ___| |_ ___ _ __  *"
print "* | __| '_ \ / _ \  / /_/ / _` | '__\ \ / / _ \/ __| __/ _ \ '__| *"
print "* | |_| | | |  __/ / __  / (_| | |   \ V /  __/\__ \ ||  __/ |    *"
print "*  \__|_| |_|\___| \/ /_/ \__,_|_|    \_/ \___||___/\__\___|_|    *"
print "*                                                                 *"
print "* TheHarvester Ver. 2.7                                           *"
print "* Coded by Christian Martorella                                   *"
print "* Edge-Security Research                                          *"
print "* cmartorella@edge-security.com                                   *"
print "*******************************************************************\n\n"


def usage():

    comm = os.path.basename(sys.argv[0])

    if os.path.dirname(sys.argv[0]) == os.getcwd():
        comm = "./" + comm

    print "Usage: theharvester options \n"
    print "       -d: Domain to search or company name"
    print """       -b: data source: baidu, bing, bingapi, dogpile,google, googleCSE,
                        googleplus, google-profiles, linkedin, pgp, twitter, vhost, 
                        yahoo, all\n"""
    print "       -s: Start in result number X (default: 0)"
    print "       -v: Verify host name via dns resolution and search for virtual hosts"
    print "       -f: Save the results into an HTML and XML file (both)"
    print "       -n: Perform a DNS reverse query on all ranges discovered"
    print "       -c: Perform a DNS brute force for the domain name"
    print "       -t: Perform a DNS TLD expansion discovery"
    print "       -e: Use this DNS server"
    print "       -l: Limit the number of results to work with(bing goes from 50 to 50 results,"
    print "            google 100 to 100, and pgp doesn't use this option)"
    print "       -h: use SHODAN database to query discovered hosts"
    print "\nExamples:"
    print "        " + comm + " -d microsoft.com -l 500 -b google -f myresults.html"
    print "        " + comm + " -d microsoft.com -b pgp"
    print "        " + comm + " -d microsoft -l 200 -b linkedin"
    print "        " + comm + " -d apple.com -b googleCSE -l 500 -s 300\n"
    print "        " + comm + " -d input/target.txt -l 500 -b google -f myresults.html"


def start(opts):
    # if len(sys.argv) < 4:
    #     usage()
    #     sys.exit()
    # try:
    #     opts, args = getopt.getopt(argv, "l:d:b:s:vf:nhcte:")
    # except getopt.GetoptError:
    #     usage()
    #     sys.exit()
    start = 0
    host_ip = []
    filename = ""
    bingapi = "yes"
    dnslookup = False
    dnsbrute = False
    dnstld = False
    shodan = False
    vhost = []
    virtual = False
    limit = 100
    dnsserver = ""
    for opt, arg in opts:
        if opt == '-l':
            limit = int(arg)
        elif opt == '-d':
            word = arg
        elif opt == '-s':
            start = int(arg)
        elif opt == '-v':
            virtual = "basic"
        elif opt == '-f':
            filename = arg
        elif opt == '-n':
            dnslookup = True
        elif opt == '-c':
            dnsbrute = True
        elif opt == '-h':
            shodan = True
        elif opt == '-e':
            dnsserver = arg
        elif opt == '-t':
            dnstld = True
        elif opt == '-b':
            engine = arg
            if engine not in ("baidu", "bing", "bingapi","dogpile", "google", "googleCSE", "googleplus", "google-profiles","linkedin", "pgp", "twitter", "vhost", "yahoo", "all"):
                usage()
                print "Invalid search engine, try with: baidu, bing, bingapi, dogpile, google, googleCSE, googleplus, google-profiles, linkedin, pgp, twitter, vhost, yahoo, all"
                sys.exit()
            else:
                pass
    if engine == "google":
        print "[-] Searching in Google:"
        search = googlesearch.search_google(word, limit, start)
        search.process()
        all_emails = search.get_emails()
        all_hosts = search.get_hostnames()

    if engine == "googleCSE":
        print "[-] Searching in Google Custom Search:"
        search = googleCSE.search_googleCSE(word, limit, start)
        search.process()
        search.store_results()
        all_emails = search.get_emails()
        all_hosts = search.get_hostnames()

    elif engine == "bing" or engine == "bingapi":
        print "[-] Searching in Bing:"
        search = bingsearch.search_bing(word, limit, start)
        if engine == "bingapi":
            bingapi = "yes"
        else:
            bingapi = "no"
        search.process(bingapi)
        all_emails = search.get_emails()

    elif engine == "dogpile":
        print "[-] Searching in Dogpilesearch.."
        search = dogpilesearch.search_dogpile(word, limit)
        search.process()
        all_emails = search.get_emails()
        all_hosts = search.get_hostnames()

    elif engine == "pgp":
        print "[-] Searching in PGP key server.."
        search = pgpsearch.search_pgp(word)
        search.process()
        all_emails = search.get_emails()
        all_hosts = search.get_hostnames()

    elif engine == "yahoo":
        print "[-] Searching in Yahoo.."
        search = yahoosearch.search_yahoo(word, limit)
        search.process()
        all_emails = search.get_emails()
        all_hosts = search.get_hostnames()

    elif engine == "baidu":
        print "[-] Searching in Baidu.."
        search = baidusearch.search_baidu(word, limit)
        search.process()
        all_emails = search.get_emails()

    elif engine == "googleplus":
        print "[-] Searching in Google+ .."
        search = googleplussearch.search_googleplus(word, limit)
        search.process()
        people = search.get_people()
        print "Users from Google+:"
       	print "===================="
       	for user in people:
            print user
        sys.exit()

    elif engine == "twitter":
        print "[-] Searching in Twitter .."
        search = twittersearch.search_twitter(word, limit)
        search.process()
        people = search.get_people()
        print "Users from Twitter:"
       	print "===================="
       	for user in people:
            print user
        sys.exit()

    elif engine == "linkedin":
        print "[-] Searching in Linkedin.."
        search = linkedinsearch.search_linkedin(word, limit)
        search.process()
        people = search.get_people()
        print "Users from Linkedin:"
       	print "===================="
       	for user in people:
            print user
        sys.exit()
    elif engine == "google-profiles":
        print "[-] Searching in Google profiles.."
        search = googlesearch.search_google(word, limit, start)
        search.process_profiles()
        people = search.get_profiles()
        print "Users from Google profiles:"
        print "---------------------------"
        for users in people:
            print users
        sys.exit()
    elif engine == "all":
        print "Full harvest.."
        all_emails = []
        virtual = "basic"
        print "[-] Searching in Google.."
        search = googlesearch.search_google(word, limit, start)
        search.process()
        emails = search.get_emails()
        all_emails.extend(emails)
        print "[-] Searching in PGP Key server.."
        search = pgpsearch.search_pgp(word)
        search.process()
        emails = search.get_emails()
        all_emails.extend(emails)
        print "[-] Searching in Bing.."
        bingapi = "no"
        search = bingsearch.search_bing(word, limit, start)
        search.process(bingapi)
        emails = search.get_emails()
        all_emails.extend(emails)
        print "[-] Searching in Exalead.."
        search = exaleadsearch.search_exalead(word, limit, start)
        search.process()
        emails = search.get_emails()
        all_emails.extend(emails)

        #Clean up email list, sort and uniq
        all_emails=sorted(set(all_emails))
    #Results############################################################
    print "\n\n[+] Emails found:"
    print "------------------"
    if all_emails == []:
        print "No emails found"
    else:
        print "\n".join(all_emails)

    #Reporting#######################################################
    if filename != "":
        try:
            # filename = filename.split(".")[0] + ".json"
            # with open(filename, 'w') as f:
            #     json.dump({'email': all_emails}, f)

            filename = r"output\tw.json"
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    json.dump([], f)

            with open(filename, mode='r') as feedsjson:
                feeds = json.load(feedsjson)

            with open(filename, 'w') as feedsjson:
                entry = {'id': len(feeds), 'url': word, 'email': all_emails, 'email_total': len(all_emails)}
                feeds.append(entry)
                json.dump(feeds, feedsjson)


            print "Files saved!"
        except Exception as er:
            print "Error saving XML file: " + er
        # sys.exit()

if __name__ == "__main__":
    try:
        start(sys.argv[1:])
    except KeyboardInterrupt:
        print "Search interrupted by user.."
    except:
        sys.exit()
