#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import base64
import os
import socket
import sys
import logging

from xmlrpc.client import ServerProxy, Error

parser = argparse.ArgumentParser()
#parser.add_argument("echo", help="echo the string you use here", type=str)
#parser.add_argument("num", type=int, help="double the number you use here")
parser.add_argument("-d", "--debug",  action="store_true", help="enable debug output")
parser.add_argument("-t", "--timeout", type=int, default=180, help="connection timeout")
parser.add_argument("-u", "--user", default="admin", help="username to login to eXist XML RPC (default: admin)")
parser.add_argument("-p", "--pass", default="", help="password to login to eXist XML RPC (default: \"\")")
parser.add_argument("-H", "--host", default="localhost", help="URL hostname (default: localhost)")
parser.add_argument("-P", "--port", type=int, default=8443, help="URL port (default: 8443)")
parser.add_argument("-T", action="store_true", help="disable TLS connection (default: enabled)")
parser.add_argument("-o", "--owner", default="admin", help="set owner of uploaded file (default: admin)")
parser.add_argument("-g", "--group", default="SYSTEM", help="set group of uploaded file (default: SYSTEM)")
parser.add_argument("-m", "--mode", default="rw-r--r--", help="set mode  of uploaded file (default: rw-r--r--) - NOT 0644 format!")
parser.add_argument("-M", "--mime", default="application/xml", help="set MIME type of uploaded file (default: application/xml)")
parser.add_argument("-Q", action="store_true", help="uploaded file is XQuery, shortcut for \"-M application/xquery\"")
parser.add_argument("-L", action="store_true", help="uploaded file is HTML, shortcut for \"-M text/html\"")
parser.add_argument("-B", action="store_true", help="uploaded file is binary [NOT IMPLEMENTED YET]")
parser.add_argument("file-name", default="", nargs="?", help="name of file to upload")
args = parser.parse_args()

xmlrpcDebug = args.debug
xmlrpcTimeout = args.timeout
xmlrpcUser = args.user
xmlrpcPass = vars(args)['pass']
xmlrpcHost = args.host
xmlrpcPort = args.port
xmlrpcSchema = "https"
if args.T:
    xmlrpcSchema = "http"
xmlrpcOwner = args.owner
xmlrpcGroup = args.group
xmlrpcMode = args.mode
xmlrpcParse = 1
xmlrpcMime = args.mime
if args.Q:
    xmlrpcParse = 0
    xmlrpcMime = "application/xquery"
if args.L:
    xmlrpcParse = 0
    xmlrpcMime = "text/html"
if args.B:
    xmlrpcMime = "application/octet-stream"

scriptName = os.path.basename(sys.argv[0])
fname = sys.argv[-1]

input_data = [line for line in sys.stdin.readlines()]
str_data = "\n".join(input_data)

socket.setdefaulttimeout(xmlrpcTimeout)

logging.info("ServerProxy {xmlrpcSchema}://{xmlrpcUser}:{xmlrpcPass}@{xmlrpcHost}:{xmlrpcPort}/exist/xmlrpc".format(**locals()))
proxy = ServerProxy('{xmlrpcSchema}://{xmlrpcUser}:{xmlrpcPass}@{xmlrpcHost}:{xmlrpcPort}/exist/xmlrpc'.format(**locals()))

if (scriptName == 'execute-xmlrpc.py'):
    xquery = str_data
    limitResultNumberTo = 100 # 0 to disable
    startWithResultNumber = 1
    params = {}
    try:
        logging.info(proxy.query(xquery, limitResultNumberTo, startWithResultNumber, params))
    except Error as v:
        logging.exception("ERROR while running %s script" %scriptName, v)
        sys.exit(-1)
elif (scriptName == 'upload-xmlrpc.py'):
    #print(scriptName)
    #b64 = base64.b64encode(data.encode('utf-8'))
    upres = -1
    pares = -1
    spres = -1
    try:
        upres = proxy.upload(data, len(data))
        logging.info(upres)

        pares = proxy.parseLocalExt(str(upres), fname, 1, xmlrpcMime, xmlrpcParse)
        logging.info(pares)

        spres = proxy.setPermissions(fname, xmlrpcOwner, xmlrpcGroup, xmlrpcMode)
        logging.info(spres)
    except Error as v:
        logging.exception("ERROR while running %s script" %scriptName, v)
        sys.exit(-1) 