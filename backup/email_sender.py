import smtplib


class EmailSender:

    def __init__(self, subject, body):
        self.gmail_user = 'unpaidinterns.hypomeals@gmail.com'
        self.gmail_password = ''
        if self.gmail_password == '':
            print("WARNING: GMAIL PASSWORD IS BLANK.")
        self.attempts = 0
        self.attempt_limit = 3
        self.sent_from = self.gmail_user
        self.to = ['marcusoertle@gmail.com', 'nathaniel.e.brooke@gmail.com']
        self.subject = subject
        self.body = body
        self.email_text = """ 
Subject: %s

%s
""" % (subject, body)

    def send_email(self):
        self.attempts += 1
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.gmail_user, self.gmail_password)
            #print(self.email_text)
            server.sendmail(self.sent_from, self.to, self.email_text)
            server.close()
            print('Email sent!')
        except:
            print('Something went wrong...')
            if self.attempts < self.attempt_limit:
                print("Trying again...\n " + "attempt = " + str(self.attempts))
                self.send_email()

