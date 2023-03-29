import email.message
import smtplib

def send_email_with_data(mailTo, subject, body):
    #Set up Sender
    gmailaddress = 'email'
    gmailpassword = 'password'

    #Set up lib
    mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
    mailServer.starttls()
    mailServer.login(gmailaddress , gmailpassword)

    #Format email message
    message = email.message.Message()
    message['From'] = gmailaddress
    message['To'] = mailTo
    message['Subject'] = subject
    message.set_payload(body)

    #Send it
    mailServer.sendmail(gmailaddress, mailTo , message.as_string())
    mailServer.quit()
