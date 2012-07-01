#!/usr/bin/python
# -*- coding: utf8 -*-

import imapclient
import getpass
import datetime
from email.header import decode_header


def main():
    '''
        1. login
        2. select folder (AllMail)
        3. find already `read mails' with 'Inbox' label
        4. filter mails with labels more than 1
        5. remove 'Inbox' label for that mails
    '''
    WEEK_AGO = datetime.datetime.now() - datetime.timedelta(days=7)

    # login
    username = raw_input('Username: ')
    username = username + '@gmail.com' if '@' not in username else ''
    password = getpass.getpass('Password: ' )
    server = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    server.login(username, password)
    del password

    # list
    folders = server.xlist_folders() 
    allmail_name = [folderinfo for folderinfo in folders if r"\AllMail" in folderinfo[0]][0][-1]
    server.select_folder(allmail_name)
    msgids = server.search(['SEEN', 'BEFORE %s' % WEEK_AGO.strftime("%d-%b-%Y"), r'X-GM-LABELS "\\Inbox"'])
    print len(msgids), 'read messages', 'since', WEEK_AGO.strftime("%d-%b-%Y")

    # filter
    msgs_with_labels = server.get_gmail_labels(msgids)
    #labled_msgs = [msgid for (msgid, labels) in msgs_with_labels.iteritems() if len(labels) > 1]
    labled_msgs = [msgid for (msgid, labels) in msgs_with_labels.items()[:3]]
    print len(labled_msgs), 'labled messages'

    # print
    def print_mail_info(_id, header):
        import re
        ecre = re.compile(r'''
          =\?                   # literal =?
          (?P<charset>[^?]*?)   # non-greedy up to the next ? is the charset
          \?                    # literal ?
          (?P<encoding>[qb])    # either a "q" or a "b", case insensitive
          \?                    # literal ?
          (?P<encoded>.*?)      # non-greedy up to the next ?= is the encoded string
          \?=                   # literal ?=
        ''', re.VERBOSE | re.IGNORECASE | re.MULTILINE)
        import email
        email.header.ecre = ecre
        def decode(header_line):
            #decoded = [s.decode(encoding if encoding else 'utf8') for (s,encoding) in decode_header(header_line.strip())]
            decoded = []
            for s, encoding in decode_header(header_line):
                if not encoding:
                    encoding = 'utf8'
                decoded.append(s.decode(encoding))
            return ''.join(decoded)
        #subject = mail['BODY[HEADER.FIELDS (SUBJECT)]'].replace("\r", "").replace("\n", "")[len('Subject: ')-1:]
        #subject = [(s,encoding) for (s,encoding) in decode_header(subject)]
        #subject = [s.decode(encoding if encoding else 'utf8') for (s,encoding) in decode_header(subject)][0]
        #print _id, data['SUBJECT'], data['FROM'], data['DATE']
        #
        #data = {}
        #for field_name in ['SUBJECT', 'FROM', 'DATE']:
        #    data[field_name] = mail['BODY[HEADER.FIELDS (%s)]' % field_name]
        #    data[field_name] = data[field_name].replace('\r', '').replace('\n', '')
        #    # strip prefix (ex: leading 'Subject: ')
        #    data[field_name] = data[field_name][len(field_name)+2:]
        #    # decode
        #    data[field_name] = decode(data[field_name])
        #print "[%(DATE)s] %(FROM)s: %(SUBJECT)s" % data
        #
        print " / ".join([decode(line) for line in header.strip().splitlines()])
            

    if len(labled_msgs) <= 30:
        #result = server.fetch(labled_msgs, ['BODY[HEADER.FIELDS (SUBJECT)]', 'BODY[HEADER.FIELDS (FROM)]', 'BODY[HEADER.FIELDS (DATE)]'])
        result = server.fetch(labled_msgs, ['BODY[HEADER.FIELDS (SUBJECT FROM DATE)]'])
        for _id, mail in result.iteritems():
            print_mail_info(_id, mail['BODY[HEADER.FIELDS (SUBJECT FROM DATE)]'])

    ## archive
    #server.remove_gmail_labels(labled_msgs, r"\Inbox")


if __name__ == '__main__':
    #import imaplib; imaplib.Debug = 4
    main()

