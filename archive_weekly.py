#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import getpass
import datetime
from email.header import decode_header
import urllib

import imapclient

def print_mail_info(_id, header):
    import email
    import re
    email.header.ecre = re.compile(r'''
      =\?                   # literal =?
      (?P<charset>[^?]*?)   # non-greedy up to the next ? is the charset
      \?                    # literal ?
      (?P<encoding>[qb])    # either a "q" or a "b", case insensitive
      \?                    # literal ?
      (?P<encoded>.*?)      # non-greedy up to the next ?= is the encoded string
      \?=                   # literal ?=
    ''', re.VERBOSE | re.IGNORECASE | re.MULTILINE) # easier parsing
    def decode(header_line):
        decoded = []
        for s, encoding in decode_header(header_line):
            if not encoding:
                encoding = 'utf8'
            decoded.append(s.decode(encoding))
        return ''.join(decoded)
    header_dict = dict(map(lambda x: x.strip(), decode(line).split(':', 1)) for line in header.strip().splitlines())
    print '[%(Date)s] %(From)s  =>  "%(Subject)s"' % header_dict


def login(server, email, auth_file=None):
    if auth_file:
        try:
            return login_by_oauth(server, email, auth_file)
        except Exception as e:
            print 'failed loggin in by oauth:'
            print e

    # no oauth.
    yn = raw_input('Do you want to login via OAuth and save for later (Y/n)? ')
    if yn.upper() == 'N':
        return login_by_password(server, email)
    else:
        filename = '.oauth'
        save_oauth(email, filename)
        prog_name = sys.argv[0]
        print 'saved to %(filename)s . run `%(prog_name)s %(filename)s` next time to login by oauth' % locals()
        print
        return login_by_oauth(server, email, filename)


def login_by_password(server, email):
    password = getpass.getpass('Password: ' )
    server.login(email, password)
    del password

def login_by_oauth(server, email, filename):
    url = 'https://mail.google.com/mail/b/%s/imap/' % email
    token, secret = open(filename).read().split()
    server.oauth_login(url, token, secret)

def save_oauth(email, filename):
    # shamelessly copied from http://google-mail-xoauth-tools.googlecode.com/svn/trunk/python/xoauth.py
    import xoauth
    import time
    import random
    escape = lambda text: urllib.quote(text, safe='~-._')

    # Get Request Token
    #request_token = GenerateRequestToken(consumer, scope, nonce, timestamp, google_accounts_url_generator)
    REQUEST_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
    SCOPE       = 'https://mail.google.com/'
    CONSUMER    = ('anonymous', 'anonymous')
    params = {
        'oauth_consumer_key'    : CONSUMER[0],
        'oauth_nonce'           : str(random.randrange(2**64 - 1)),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version'         : '1.0',
        'oauth_timestamp'       : str(int(time.time())),
        'oauth_callback'        : 'oob',
        'scope'                 : SCOPE,
    }
    base_string = '&'.join([escape(x) for x in ['GET', REQUEST_URL, urllib.urlencode(sorted(params.items()))]])
    params['oauth_signature'] = xoauth.GenerateOauthSignature(base_string, CONSUMER[1], '')

    url = '%s?%s' % (REQUEST_URL, urllib.urlencode(params))
    response = urllib.urlopen(url).read()
    response_params = xoauth.ParseUrlParamString(response)
    #for param in response_params.items():
    #    print '%s: %s' % param
    REQUEST_TOKEN = (response_params['oauth_token'], response_params['oauth_token_secret'])
    print
    print 'To authorize token, visit this url and follow the directions to generate a verification code:'
    print '  https://www.google.com/accounts/OAuthAuthorizeToken?oauth_token=%s' % (escape(REQUEST_TOKEN[0]))

    # Get Access Token
    #access_token = GetAccessToken(consumer, request_token, oauth_verifier, google_accounts_url_generator)
    REQUEST_URL =  'https://www.google.com/accounts/OAuthGetAccessToken'
    oauth_verifier = raw_input('Enter verification code: ').strip()

    params = {
        'oauth_consumer_key'    : CONSUMER[0],
        'oauth_nonce'           : str(random.randrange(2**64 - 1)),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version'         : '1.0',
        'oauth_timestamp'       : str(int(time.time())),
        'oauth_token'           : REQUEST_TOKEN[0],
        'oauth_verifier'        : oauth_verifier,
    }
    base_string = '&'.join([escape(x) for x in ['GET', REQUEST_URL, urllib.urlencode(sorted(params.items()))]])
    params['oauth_signature'] = xoauth.GenerateOauthSignature(base_string, CONSUMER[1], REQUEST_TOKEN[1])

    url = '%s?%s' % (REQUEST_URL, urllib.urlencode(sorted(params.items())))
    response = urllib.urlopen(url).read()
    response_params = xoauth.ParseUrlParamString(response)
    #for param in ('oauth_token', 'oauth_token_secret'):
    #    print '%s: %s' % (param, response_params[param])
    access_token = (response_params['oauth_token'], response_params['oauth_token_secret'])

    # save to file
    if hasattr(filename, 'write') and hasattr(filename, 'close'):
        f = filename
    else:
        f = open(filename, 'w')

    f.write(access_token[0] + "\n")
    f.write(access_token[1])
    f.close()
    return filename


def main():
    '''
        1. login
        2. select folder (AllMail)
        3. find `read mails' with 'Inbox' label
        4. filter mails with labels more than 1
        5. remove 'Inbox' label for that mails
    '''
    WEEK_AGO = datetime.datetime.now() - datetime.timedelta(days=7)

    # args
    filename = sys.argv[sys.argv.index('--auth')+1] if len(sys.argv) > 2 and '--auth' in sys.argv else None
    username = sys.argv[sys.argv.index('--user')+1] if len(sys.argv) > 2 and '--user' in sys.argv else None

    # login
    username = username or raw_input('Username: ')
    username = username + '@gmail.com' if '@' not in username else username
    server = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    #server.login(email, getpass.getpass('Password: ' )) # deprecated.
    login(server, username, filename)
    print 'logged in with', username

    # list
    folders = server.xlist_folders() 
    allmail_name = [folderinfo for folderinfo in folders if r"\AllMail" in folderinfo[0]][0][-1]
    server.select_folder(allmail_name)
    msgids = server.search(['SEEN', 'BEFORE %s' % WEEK_AGO.strftime("%d-%b-%Y"), r'X-GM-LABELS "\\Inbox"'])
    print len(msgids), 'read messages', 'since', WEEK_AGO.strftime("%d-%b-%Y")

    # filter
    msgs_with_labels = server.get_gmail_labels(msgids)
    labled_msgs = [msgid for (msgid, labels) in msgs_with_labels.iteritems() if len(labels) > 1]
    #labled_msgs = [msgid for (msgid, labels) in msgs_with_labels.items()[:3]]
    print len(labled_msgs), 'labeled messages'

    # print
    if len(labled_msgs) <= 30:
        #result = server.fetch(labled_msgs, ['BODY[HEADER.FIELDS (SUBJECT FROM DATE)]'])
        fields = ['BODY[HEADER.FIELDS (SUBJECT)]', 'BODY[HEADER.FIELDS (FROM)]', 'BODY[HEADER.FIELDS (DATE)]']
        result = server.fetch(labled_msgs, fields)
        for _id, mail in result.iteritems():
            #print_mail_info(_id, mail['BODY[HEADER.FIELDS (SUBJECT FROM DATE)]'])
            header = '\n'.join(mail[f].strip().replace('\n', '').replace('\r', '') for f in fields)
            print_mail_info(_id, header)

    ## archive
    #server.remove_gmail_labels(labled_msgs, r"\Inbox")


if __name__ == '__main__':
    #import imaplib; imaplib.Debug = 4
    main()

