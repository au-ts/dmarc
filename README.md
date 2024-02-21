# DMARC handling


By adding a `_dmarc` record to your DNS you can
receive deliverability reports on your email
Outlook.com and Google, and possibly other email providers, email a
daily report to the address in the `rua` field of the `_dmarc` record.

The `capture_dmarc` script is designed to be the recipient of such reports.
It takes them on standard input, decodes the MIMEtext in the email, extracts
the actual report (some providers just provide a gzipped XML file, others
encapsulate it in a ZIP file), and dumps it in a file.

Use by adding an alias in `/etc/aliases` like:
```
dmarc: |/usr/bin/python3 /usr/local/sbin/capture_dmarc.py
```
or similar; or you can use a `procmail` recipe.

The `serve_dmarc` script sets up a simple webserver on port 5002 using
Flask, and serves the reports.  It has no security; but provides a
simple visualisation of the reports so far.

You probably need a `cron` job to clean up old reports too.
Suggest something like:

```
10 12 * * * root find /var/cache/dmarc -name '*xml' -mtime +60 -print0 | xargs -0 rm -f
```
in `/etc/cron.d/dmarc` to remove all reports over 60 days old.