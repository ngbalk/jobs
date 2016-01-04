import smtplib
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("redhat.jpmc.pilot", "redhat123")
 
msg = "Black Duck Notification"
server.sendmail("redhat.jpmc.pilot@gmail.com", "nbalkiss@redhat.com", msg)
server.quit()