#!/usr/bin/python
# -*- coding: utf8 -*-

import imapclient
import getpass
import datetime
from email.header import decode_header

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
    print 'logged in with', username

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
    if len(labled_msgs) <= 30:
        result = server.fetch(labled_msgs, ['BODY[HEADER.FIELDS (SUBJECT FROM DATE)]'])
        for _id, mail in result.iteritems():
            print_mail_info(_id, mail['BODY[HEADER.FIELDS (SUBJECT FROM DATE)]'])

    ## archive
    #server.remove_gmail_labels(labled_msgs, r"\Inbox")


if __name__ == '__main__':
    #import imaplib; imaplib.Debug = 4
    main()

