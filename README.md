Archive Gmail weekly
====================

Run
---

### Install
fetch program
```
$ git clone git@github.com:jangxyz/gmail_archive_weekly.git
```

requires: 
* `imapclient` python package
```
$ pip install imapclient
```

### Usage

```
$ python archive_weekly.py -h
Usage: archive_weekly.py [options]

    --user USERNAME     login with this username.
    --auth AUTHFILE     login with this oauth file.
    --print             print subjects of target mails.
    --archive           actually archive target mails.
    -h|--help           display this help message and exit.
```

### Simple login

An example login:
```
$ python archive_weekly.py
Username: janghwan
Do you want to login via OAuth and save for later (Y/n)? n
Password: *********
logged in with janghwan@gmail.com
900 read messages before 30-Jun-2012
7 labeled messages
```

You can print each mails with `--print` option, and actually archive the mails with `--archive`

### Login via OAuth
You can save the OAuth token once logged in, and use it for later.
```
$ python archive_weekly.py 
Username: janghwan
Do you want to login via OAuth and save for later (Y/n)? y

To authorize token, visit this url and follow the directions to generate a verification code:
  https://www.google.com/accounts/OAuthAuthorizeToken?oauth_token=********************************
Enter verification code: ************************
saved to .oauth . run `archive_weekly.py --auth .oauth` next time to login by oauth

logged in with janghwan@gmail.com
900 read messages before 30-Jun-2012
7 labeled messages
```
You should click the link printed out above, and manually accept the access. Gmail is asking you (the user) whether to grant access to a consumer service (this program). You only need to do this once, if you save the result token to a file.

Now your OAuth token is saved in file named `.oauth`. Be sure not to let anyone else read the file!


Now login with givne auth file:
```
$ python archive_weekly.py --auth .oauth
logged in with janghwan@gmail.com
900 read messages before 30-Jun-2012
7 labeled messages
```

### Cron
With oauth option, you can set a cron job like this:
```
0   0   *   *   *   /usr/bin/python /home/jangxyz/cron/gmail/archive_weekly.py --auth /home/jangxyz/cron/gmail/.oauth
```
This will archive mails every midnight.



How does it Work?
-----------------

### IMAP, and extending it
Usually email APIs are implemented with the IMAP protocol([RFC3501]:(http://tools.ietf.org/html/rfc3501)). However, gmail has some additional features like **Label**s. Google implemented this feature by [extending the IMAP api](https://developers.google.com/google-apps/gmail/imap_extensions).

### imaplib and imapclient
You can use the python `imaplib` package to interact with gmail's IMAP protocol, and implement the additional protocol yourself,
or, simply use the [`imapclient` package](http://imapclient.readthedocs.org/en/latest/index.html) which does it for your :)

### OAuth
Gmail also supports OAuth, an open standard for authorization. I wouldn't go into detail here, you can read more about it [here](http://en.wikipedia.org/wiki/Oauth).


For More
--------
Try setting `imaplib.Debug = 4` before running the code. It will print all sorts of messages sent and received.

Also checkout these references:
* https://developers.google.com/google-apps/gmail/imap_extensions
* http://tools.ietf.org/html/rfc3501
* http://imapclient.readthedocs.org/en/latest/index.html
* http://oauth.net/

