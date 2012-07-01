#!/usr/bin/python
import imaplib
import re

# register 'imap4-utf-7' codec
from imapUTF7 import register_codec
register_codec('imap4-utf-7')

###
imaplib.Commands['XLIST'] = ('AUTH', 'SELECTED')
class GMAIL_IMAP4_SSL(imaplib.IMAP4_SSL):
    pass
###
 
class Gmail:
    def __init__(self):
        self.IMAP_SERVER='imap.gmail.com'
        self.IMAP_PORT=993
        self.M = None
        self.response = None
        self.mailboxes = []
 
    def login(self, username, password):
        self.M = GMAIL_IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
        rc, self.response = self.M.login(username, password)
        return rc
 
    def logout(self):
        self.M.logout()

    def get_mailboxes(self):
        rc, self.response = self.M.list()
        for item in self.response:
            self.mailboxes.append(item.split()[-1])
        return rc

    def rename_mailbox(self, oldmailbox, newmailbox):
        rc, self.response = self.M.rename(oldmailbox, newmailbox)
        return rc
     
    def create_mailbox(self, mailbox):
        rc, self.response = self.M.create(mailbox)
        return rc
     
    def delete_mailbox(self, mailbox):
        rc, self.response = self.M.delete(mailbox)
        return rc

    def get_mail_count(self, folder='Inbox'):
        rc, count = self.M.select(folder)
        return count[0]

    def get_unread_count(self, folder='Inbox'):
        rc, message = self.M.status(folder, "(UNSEEN)")
        unreadCount = re.search("UNSEEN (\d+)", message[0]).group(1)
        return unreadCount



def do_login(username=None):
    import getpass
    if username is None:
        username = raw_input('Username: ')
    password = getpass.getpass('Password: ' )
    g = Gmail()
    g.login(username, password)
    return g



