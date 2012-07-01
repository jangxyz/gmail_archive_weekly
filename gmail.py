#!/usr/bin/python
import imaplib
import re
import shlex

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
        self.IMAP_SERVER = 'imap.gmail.com'
        self.IMAP_PORT = 993
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

    #
    def labels(self, single_mailid):
        rc, self.response = self.M.fetch(single_mailid, 'X-GM-LABELS')
        strip_label_str = self.response[0].split('X-GM-LABELS (', 1)[1].rsplit(')')[0]
        return [x.decode('imap4-utf-7') for x in shlex.split(strip_label_str)]


def do_login(username=None):
    import getpass
    if username is None:
        username = raw_input('Username: ')
    password = getpass.getpass('Password: ' )

    #imaplib_Debug = imaplib.Debug
    #if imaplib.Debug >= 4: # don't show password
    #    imaplib.Debug = 3
    #
    g = Gmail()
    g.login(username, password)
    del password
    #imaplib.Debug = imaplib_Debug

    return g

def squeeze_sequence_set(sequence_set):
    '''
    >>> squeeze_sequence_set([1,2,3])
    ['1:3']
    >>> squeeze_sequence_set([1,2, 4,5])
    ['1:2', '4:5']
    '''
    sequence_set = map(int, sequence_set)
    sequence_set.sort()

    result = []
    if sequence_set == []:
        return result

    group_start_number, group_last_number = sequence_set[0], None
    for i,number in enumerate(sequence_set[1:]):
        if number == sequence_set[i]+1:
            group_last_number = number
        else:
            result.append( '%d:%d' % (group_start_number, group_last_number) )
            group_start_number, group_last_number = number, None
    result.append( '%d:%d' % (group_start_number, group_last_number) )

    return result


def search(msgid, **options):
    '''
    default_options = {
        all       : None,
        answered  : None,
        bcc       : ''
        before    : <DATE>
        body      : ''
        cc        : ''
        deleted   : None,
        draft     : None,
        flagged   : None,
        from      : ''
        header    : <FIELD-NAME> ''
        keyword   : <FLAG>
        new       : None,
        not       : <SEARCH-KEY>
        old       : None,
        or        : (<SEARCH-KEY1>, <SEARCH-KEY2>)
        recent    : None,
        seen      : None,

        on        : <DATE>
        sentbefore: <DATE>
        senton    : <DATE>
        sentsince : <DATE>
        since     : <DATE>

        smaller   : <N>
        larger    : <N>
        subject   : ''
        text      : ''
        to        : ''
        uid       : <SEQUENCE SET>
        unanswered: None,
        undeleted : None,
        undraft   : None,
        unflagged : None,
        unkeyword : <FLAG>
        unseen    : None,
    }
    
    This implements SEARCH command in IMAP(RFC 3501)

        http://tools.ietf.org/html/rfc3501#section-6.4.4

      ALL
         All messages in the mailbox; the default initial key for ANDing.

      ANSWERED
         Messages with the \Answered flag set.

      BCC <string>
         Messages that contain the specified string in the envelope structure's BCC field.

      BEFORE <date>
         Messages whose internal date (disregarding time and timezone) is earlier than the specified date.

      BODY <string>
         Messages that contain the specified string in the body of the message.

      CC <string>
         Messages that contain the specified string in the envelope structure's CC field.

      DELETED
         Messages with the \Deleted flag set.

      DRAFT
         Messages with the \Draft flag set.

      FLAGGED
         Messages with the \Flagged flag set.

      FROM <string>
         Messages that contain the specified string in the envelope structure's FROM field.

      HEADER <field-name> <string>
         Messages that have a header with the specified field-name (as defined in [RFC-2822]) and that contains the specified string in the text of the header (what comes after the colon).  If the string to search is zero-length, this matches all messages that have a header line with the specified field-name regardless of the contents.

      KEYWORD <flag>
         Messages with the specified keyword flag set.

      LARGER <n>
         Messages with an [RFC-2822] size larger than the specified number of octets.

      NEW
         Messages that have the \Recent flag set but not the \Seen flag.  This is functionally equivalent to "(RECENT UNSEEN)".


      NOT <search-key>
         Messages that do not match the specified search key.

      OLD
         Messages that do not have the \Recent flag set.  This is functionally equivalent to "NOT RECENT" (as opposed to "NOT NEW").

      ON <date>
         Messages whose internal date (disregarding time and timezone) is within the specified date.

      OR <search-key1> <search-key2>
         Messages that match either search key.

      RECENT
         Messages that have the \Recent flag set.

      SEEN
         Messages that have the \Seen flag set.

      SENTBEFORE <date>
         Messages whose [RFC-2822] Date: header (disregarding time and timezone) is earlier than the specified date.

      SENTON <date>
         Messages whose [RFC-2822] Date: header (disregarding time and timezone) is within the specified date.

      SENTSINCE <date>
         Messages whose [RFC-2822] Date: header (disregarding time and timezone) is within or later than the specified date.

      SINCE <date>
         Messages whose internal date (disregarding time and timezone) is within or later than the specified date.

      SMALLER <n>
         Messages with an [RFC-2822] size smaller than the specified number of octets.

      SUBJECT <string>
         Messages that contain the specified string in the envelope structure's SUBJECT field.

      TEXT <string>
         Messages that contain the specified string in the header or body of the message.

      TO <string>
         Messages that contain the specified string in the envelope structure's TO field.

      UID <sequence set>
         Messages with unique identifiers corresponding to the specified unique identifier set.  Sequence set ranges are permitted.

      UNANSWERED
         Messages that do not have the \Answered flag set.

      UNDELETED
         Messages that do not have the \Deleted flag set.

      UNDRAFT
         Messages that do not have the \Draft flag set.

      UNFLAGGED: Messages that do not have the \Flagged flag set.

      UNKEYWORD <flag>: Messages that do not have the specified keyword flag set.

      UNSEEN: Messages that do not have the \Seen flag set.
    '''


def test():
    g = do_login()
    g.M.select('inbox')
    # search read articles with label
    import datetime
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    #typ, data = g.M.search('', 'SEEN', 'BEFORE', week_ago.strftime("%d-%b-%Y"))
    typ, data = g.M.search('', 'SEEN', 'SINCE', week_ago.strftime("%d-%b-%Y"))
    messages = data[0].split()

    print 'read', len(messages), 'mails from', week_ago
    labeled_messages = [msg for msg in messages if len(g.labels(msg)) > 1]
    print len(labeled_messages), 'mails labled'
    for msg in labeled_messages:
        typ, data = g.M.fetch(msg, '(BODY[HEADER.FIELDS (SUBJECT)])')
        print data[0][1].strip()


if __name__ == '__main__':
    test()


