# -*- coding:utf-8 -*-
"""
GMail notificator module
"""
import smtplib

from decorators import retry


GMAIL_SMTP_SERVER = 'smtp.gmail.com:587'

_MAIL_TEMPLATE = """From: {user}
To: {dest}
Content-Type: text/plain
Subject: {subject}

{content}
"""

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


    @retry
    def notify(self, message, subject=None):
        """
        Send a plain text email to all emails contained at "destinations_addresses" list.

        :param str message: should contain message content to be send
        :param str subject: email subject (optional)
        :return dict: a dictionary containing the result of the attempt to send the email.
        """

        if subject is None:
            subject = str()

        _MAIL_TEMPLATE.format(user=self.username, dest=self.destination_addresses, subject=subject, content=message)

        smtp_handler = smtplib.SMTP(GMAIL_SMTP_SERVER, timeout=self.timeout)
        smtp_handler.starttls()
        smtp_handler.login(self.username, self.password)
        result = smtp_handler.sendmail(self.username, self.destination_addresses, message)
        smtp_handler.quit()

        return result
