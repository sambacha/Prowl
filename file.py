#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import re
import argparse
import string
import time
import urllib2
import json
import os

parser = argparse.ArgumentParser(description="Scrape LinkedIn for company staff members")
parser.add_argument("-c", "--company", help="Company to search for")
parser.add_argument("-e", "--emailformat", help='Format of house email address style. Use: <fn>,<ln>,<fi>,<li> as placeholders for first/last name/initial. e.g "<fi><ln>@company.com"')
parser.add_argument("-nj", "--nojobs", help="Exclude available jobs in result", action='store_true')
parser.add_argument("-d", "--depth", help="How many pages of Yahoo to search through", default='10')
args = parser.parse_args()

found = []
emails=[]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CUSTOM = '\033[37m'

def formatout(companyname,emailformat):
	domain = emailformat.split("@")[1]
	if emailformat:
		print "Output file name: "+companyname+".csv"
	if not os.path.exists("Output"):
		os.makedirs("Output")
	print "_"*50
	print " "
	target = open("Output/"+companyname+".csv", 'w')
	target.write("First Name, Last Name, Email, Title, Profile, Breach"+"\r\n")

def search(comp,emailformat):
	depth = int(args.depth)
	print "\n"
	print bcolors.UNDERLINE + bcolors.WARNING + "S" + bcolors.OKBLUE + "T" + bcolors.OKGREEN + "A" + bcolors.ENDC + bcolors.UNDERLINE + "F" + bcolors.FAIL + "F" + bcolors.ENDC
	print "\n"
	for i in range(1,depth):
		i = str(i)
		r = requests.get('https://uk.search.yahoo.com/search;_ylt=A9mSs3IiEdVYsUMAY6ZLBQx.;_ylu=X3oDMTEzdm1nNDAwBGNvbG8DaXIyBHBvcwMxBHZ0aWQDBHNlYwNwYWdpbmF0aW9u?p="at+{0}"+site%3Alinkedin.com&pz=10&ei=UTF-8&fr=yfp-t-UK317&b={1}0&pz=10&xargs=0'.format(comp,i))
		soup = BeautifulSoup(r.text, "lxml")
        	for tag in soup.findAll("div", {"class" : "dd algo algo-sr Sr"}):
			if re.search("linkedin.com/in/", str(tag)):
				if re.search("Top", tag.getText()):
					pass
				else:
					if tag.getText() not in found:
						title = tag.find("h3", {"class" : "title"});
						div = " "
						cut = title.getText().split(div,2)[:2]
						name = cut[0]+" "+cut[1]
						jobtext = tag.find("p", {"class" : "lh-16"});
						job = jobtext.getText()
						href = tag.find("a");
						linkpof = ""
						linkpof = href['href']
						found.append(tag.getText())
						if "View " in job:
							fulljob = ""
							mangle_emails(name, comp, emailformat, fulljob, linkpof)
						else:
							first = job.split(".",1)[1]
							fulljob = first.split(" at ",1)[0]
							mangle_emails(name, comp, emailformat, fulljob, linkpof)

def mangle_emails(name, company, emailformat, fulljob, linkpof):
	target = open("Output/"+company+".csv", 'a')
        fn = string.split(name)[0]
        fi = fn[0]
        ln = string.split(name)[1]
        li = ln[0]
        email = emailformat.replace('<fn>',fn).replace('<ln>',ln).replace('<fi>',fi).replace('<li>',li).lower()
        email2 = filter(lambda x: x in string.printable, email)
	headers = {
	'User-Agent': 'Prowl'
	}

	if email2 not in emails:
       		try:
			time.sleep(1.5)
			emails.append(email2)
			req = requests.get("https://haveibeenpwned.com/api/breachedaccount/"+email2+"?truncateResponse=true", headers=headers)
			try:
				breach = str(req.content)
				print "{0:30} {1:40} {3:40} {2}".format(name, email2, req.content, fulljob)
				target.write(fn+","+ln+","+email2+","+fulljob+","+linkpof+","+breach+"\r\n")
			except:
                        	pass
        	except:
			emails.append(email2)
			print "{0:20} {1}".format(name,email2)
			print "fail"
	else:
		pass

def jobs(comp):
	print bcolors.UNDERLINE + bcolors.WARNING + "J" + bcolors.OKBLUE + "O" + bcolors.OKGREEN + "B" + bcolors.ENDC + bcolors.UNDERLINE + "S"  + bcolors.ENDC
	print " "
	r = requests.get("https://www.indeed.co.uk/jobs?as_and='at+{0}'&as_phr=&as_any=&as_not=&as_ttl=&as_cmp=&jt=all&st=&salary=&radius=25&l=&fromage=any&limit=30&sort=&psf=advsrch".format(comp))
	soup = BeautifulSoup(r.text, "lxml")
	for tag in soup.findAll("h2", {"class" : "jobtitle"}):
		print str(tag.getText().encode('utf-8')).strip()
		pass
if args.company:
	if args.emailformat:
		formatout(args.company, args.emailformat)

if args.nojobs is True:
	pass
else:
	jobs(args.company)

if args.company:
	if args.emailformat:
			search(args.company, args.emailformat)
else:
        parser.print_usage()
