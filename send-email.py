import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 



def sendEmail():
    # creates SMTP session
    #s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    #s.starttls()
    # Authentication
    #s.login("sender-email", "sender-email-password")
    # message to be sent
    
    # message to be sent
    #message = "Message_you_need_to_send"

    # sending the mail
    #s.sendmail("sender-email", "to-email",message)
    #print(f"Email send to ")
    # terminating the session
    #s.quit()
    
    fromaddr = "sender-email"
    fromaddrPassword = "sender-email-password"
    # list of email_id to send the mail
    li = ["to-01","to-02","to-03"]
 
    for toaddr in li:

        #toaddr = "mithilesh.thakur@hispindia.org"
        
        # instance of MIMEMultipart 
        msg = MIMEMultipart() 
        
        # storing the senders email address   
        msg['From'] = fromaddr 
        
        # storing the receivers email address  
        msg['To'] = toaddr 
        
        # storing the subject  
        msg['Subject'] = "Python Script test of the Mail"
        
        # string to store the body of the mail 
        body = "Python Script test of the Mail"
        
        # attach the body with the msg instance 
        msg.attach(MIMEText(body, 'plain')) 
        
        # open the file to be sent  
        filename = "options.xlsx"
        attachment = open("options.xlsx", "rb") 
        
        # instance of MIMEBase and named as p 
        p = MIMEBase('application', 'octet-stream') 
        
        # To change the payload into encoded form 
        p.set_payload((attachment).read()) 
        
        # encode into base64 
        encoders.encode_base64(p) 
        
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
        
        # attach the instance 'p' to instance 'msg' 
        msg.attach(p) 
        
        # creates SMTP session 
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        
        # start TLS for security 
        s.starttls() 
        
        # Authentication 
        s.login(fromaddr, fromaddrPassword) 
        
        # Converts the Multipart msg into a string 
        text = msg.as_string() 
        
        # sending the mail 
        s.sendmail(fromaddr, toaddr, text) 
        print(f"mail send to: {toaddr}")
        # terminating the session 
        s.quit() 


if __name__ == "__main__":
    print("sending email:")
    try:
        sendEmail()  
    except Exception as e:
        print(f"An error occurred: {e}")