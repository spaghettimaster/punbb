#!/usr/bin/python
"""Set PunBB admin password, email and domain to serve

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively

"""

import sys
import getopt
import inithooks_cache

import hashlib
import random
import string

from dialog_wrapper import Dialog
from mysqlconf import MySQL
from executil import system

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError, e:
        usage(e)

    email = ""
    password = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "PunBB Password",
            "Enter new password for the PunBB 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "PunBB Email",
            "Enter email address for the PunBB 'admin' account.",
            "admin@example.com")

    inithooks_cache.write('APP_EMAIL', email)

    def sha1(s):
        return hashlib.sha1(s).hexdigest()
    
    salt = ''.join((random.choice(string.letters+string.digits) for x in range(12)))
    hash = sha1(salt + sha1(password))

    m = MySQL()
    m.execute('UPDATE punbb.users SET password=\"%s\", salt=\"%s\", email=\"%s\" WHERE username=\"admin\";' % (hash, salt, email))

    m.execute('UPDATE punbb.config SET conf_value=\"%s\" WHERE conf_name=\"o_mailing_list\";' % email)
    m.execute('UPDATE punbb.config SET conf_value=\"%s\" WHERE conf_name=\"o_admin_email\";' % email)
    m.execute('UPDATE punbb.config SET conf_value=\"%s\" WHERE conf_name=\"o_webmaster_email\";' % email)


if __name__ == "__main__":
    main()

