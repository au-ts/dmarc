#!/bin/env python3
import email
import os
import sys
from shlex import quote
from email.mime.text import MIMEText

DMARCDIR = "/var/cache/dmarc"

def save_report(content, filename):
    os.chdir(DMARCDIR)
    pathname = os.path.join(DMARCDIR, filename)
    with open(pathname, "wb") as f:
        f.write(content)
    safefilename = quote(filename)
    if filename.endswith(".zip"):
        os.system("unzip %s" % safefilename)
        os.remove(pathname)
    elif filename.endswith(".gz"):
        os.system("gunzip %s" % safefilename)
    
def decode_email(msg):
    if msg.is_multipart():
        parts = msg.get_payload()
        m = parts.pop(0)
        ct = m.get_content_type()
        while "application/zip" not in ct and "application/gzip" not in ct:
            m = parts.pop(0)
            ct = m.get_content_type()
        report = m.get_payload(decode=True)
        name = m.get_filename()
    else:
        report = msg.get_payload(decode=True)
        name = msg.get_filename()
    save_report(report, name)
               
if __name__ == "__main__":
    # Get the email from STDIN
    mail = email.message_from_file(sys.stdin)
    decode_email(mail)
               
