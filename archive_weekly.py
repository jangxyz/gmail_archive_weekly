#!/usr/bin/python
# -*- coding: utf8 -*-

import imapclient
import getpass
import datetime
from email.header import decode_header


def main():
    WEEK_AGO = datetime.datetime.now() - datetime.timedelta(days=7)

    # login
    username = raw_input('Username: ')
    password = getpass.getpass('Password: ' )
    server = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    server.login(username, password)
    del password

    # list
    allmail_name = [folderinfo for folderinfo in server.xlist_folders() if r"\AllMail" in folderinfo[0]][0][-1]
    server.select_folder(allmail_name)
    msgids = server.search(['SEEN', 'BEFORE %s' % WEEK_AGO.strftime("%d-%b-%Y"), r'X-GM-LABELS "\\Inbox"'])
    print len(msgids), 'read messages', 'since', WEEK_AGO

    # filter
    msgs_with_labels = server.get_gmail_labels(msgids)
    labled_msgs = [msgid for (msgid, labels) in msgs_with_labels.iteritems() if len(labels) > 1]
    print len(labled_msgs), 'labled messages'

    # print
    if len(labled_msgs) <= 100:
        for _id, mail in server.fetch(labled_msgs, ['BODY[HEADER.FIELDS (SUBJECT)]']).iteritems():
            subject = mail['BODY[HEADER.FIELDS (SUBJECT)]'].replace("\r", "").replace("\n", "")[len('Subject: ')-1:]
            #subject = [(s,encoding) for (s,encoding) in decode_header(subject)]
            #print subject,
            subject = [s.decode(encoding if encoding else 'utf8') for (s,encoding) in decode_header(subject)][0]
            #print subject
            print _id, subject

    ## archive
    #server.remove_gmail_labels(labled_msgs, r"\Inbox")

if __name__ == '__main__':
    main()

