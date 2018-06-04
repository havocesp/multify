# -*- coding:utf-8 -*-
"""
GMail notificator module
"""
import email
import imaplib
import smtplib

GMAIL_SMTP_SERVER = 'smtp.gmail.com:587'
GMAIL_IMAP_SERVER = 'imap.gmail.com'

_MAIL_TEMPLATE = """From: {user}
To: {dest}
Content-Type: text/plain
Subject: {subject}

{content}
"""


def decode_mime_words(s):
    """
    Returns header decoded content.

    Header content encoding will be inferred (if possible)

    :param s: header content
    :return: decoded header content
    """
    result = list()
    if s is None:
        return
    for word, encoding in email.header.decode_header(s):
        if isinstance(word, bytes):
            try:
                result.append(word.decode(encoding or 'utf8'))
            except LookupError:
                pass
        else:
            result.append(word)
    return u''.join(result)


class ByGMail:
    """
    Class for handling GMail notifications
    """

    def __init__(self, username, password, destination_addresses=None, timeout=30.0):
        """
        Constructor

        :param str username: Username of the GMail account to use for sending message.
        :param str password: Password of the GMail account to use for sending message.
        :param list destination_addresses: A list of email addresses to notify.
        """
        self.username = username
        self.password = password
        if destination_addresses:
            if isinstance(destination_addresses, str):
                self.destination_addresses = [destination_addresses]
            self.destination_addresses = ','.join([*destination_addresses])
        else:
            self.destination_addresses = [username]
        self.timeout = timeout

    def get_first_text_block(self, email_message_instance):
        """
        Get Body content from an email.

        :param email.message.Message email_message_instance: raw email data
        :return: body content from mail raw data
        """
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
        elif maintype == 'text':
            return email_message_instance.get_payload()

    def notify(self, message, subject=None):
        """
        Send a plain text email to all emails contained at "destinations_addresses" list.

        :param str message: should contain message content to be send
        :param str subject: email subject (optional)
        :return dict: a dictionary containing the result of the attempt to send the email.
        """

        if subject is None:
            subject = str()

        message = _MAIL_TEMPLATE.format(user=self.username, dest=self.destination_addresses, subject=subject,
                                        content=message)

        smtp_handler = smtplib.SMTP(GMAIL_SMTP_SERVER, timeout=self.timeout)
        smtp_handler.starttls()
        smtp_handler.login(self.username, self.password)
        result = smtp_handler.sendmail(self.username, self.destination_addresses, message)
        smtp_handler.quit()
        return result

    def login(self, mail):
        """
        GMail IMAP login routine.

        :param mail: a IMAP4_SSL instance pointed to GMail server.
        :return: login related data
        """
        try:
            rv, data = mail.login(self.username, self.password)
        except imaplib.IMAP4.error as err:
            import sys
            print('[ERROR] Login fail. Details:\n{}'.format(str(err)))
            sys.exit(1)
        return rv, data

    def get_mailboxes(self):
        """
        Get a list with all mailboxes names at GMail user account.

        :return list: list with all mailboxes names
        """
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER)
        self.login(mail)
        rv, mailboxes = mail.list()
        mail.logout()
        return mailboxes

    def read_emails(self, limit=20):
        """
        Read mails from "inbox"  mailbox.

        :param int limit: max emails to read
        :return: list of dicts (one dict per email with keys: subject, from_email, to_emails, body)
        """
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER)
        emails = list()
        try:
            self.login(mail)
            mail.select('inbox')

            data_type, data = mail.search(None, 'ALL')
            mail_ids = data[0]

            id_list = mail_ids.split()
            
            latest_email_id = int(id_list[-1])

            for i in range(latest_email_id, latest_email_id - limit, -1):
                typ, data = mail.fetch(str(i), '(RFC822)')
                email_data = dict(subject=str(), from_email=str(), to_emails=list(), body=str())
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])  # type: email.message.Message
                        email_data['subject'] = decode_mime_words(msg['subject'])
                        email_data['from_email'] = decode_mime_words(msg['from'])
                        email_data['to_emails'] = [decode_mime_words(msg['to'])]
                        if email_data['body'] is not None and msg is not None:
                            text = self.get_first_text_block(msg)
                            email_data['body'] += text if text is not None else str()

                emails.append(email_data)
         return emails


        except TypeError as e:
            raise e
        finally:
            mail.logout()
        return emails
