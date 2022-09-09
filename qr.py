from datetime import datetime
import socket
ho=socket.gethostname()
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from playsound import playsound
import cv2  
import logging
from pandas import read_csv
import pymsgbox
import numpy as np
import ctypes
import concurrent.futures 
executor = concurrent.futures.ThreadPoolExecutor() 
cap = cv2.VideoCapture(0)
logger=logging.getLogger()
logging.basicConfig(level=logging.INFO,filename=r"\\PERSEUS\QR-Cop\Coupon.log",format="  %(asctime)s -> %(message)s")

def mail_send(name,ide,cop=1,purchased=1):
    now = datetime.now()
    timedate = now.strftime("%d/%m/%Y %H:%M:%S")
    if cop!=1:
        mail_content = f'''
Hello {name}, 
        This mail is to notify you that {cop} out of {purchased} coupons from your QR code based ticket have been reedemed (Time: {timedate}). In case the coupon was not redeemed by you, please reply back to tis email.
        We hope you enjoyed your meal. Wish you and your loved ones a happy onam. 
Thank You,
System: Sarin C Jacob 
        '''
    else:
        mail_content=f'''
Hello {name},
        This Mail is to notify you that your food coupon has been redeemed and is no more valid (Time:{timedate}). In case it was not redeemed by you, please reply back to this email.
        We hope you enjoyed your meal. Wish you and your loved ones a happy onam. 
Thank You
System: Sarin C Jacob
        '''
    try:
        sender_address = 'xxxxxx'
        sender_pass = 'xxxxxxxxx'
        receiver_address = ide
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Onam Food Coupon Usage Confirmation'   #The subject line
        #The body and the attachments for the mail m m
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable securityx
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        # print('Mail Sent')
        logger.warning(f'{ho}: send mail to {name} ({ide})- used {cop} coupon >DONE')
    except:
        logger.warning(f'{ho}: failed to send mail to {name} ({ide})- used {cop} coupon >ERROR')



logger.warning(f'{ho}: Script Initiated')

detector = cv2.QRCodeDetector()
a=None
while 1:
    _,img = cap.read()
    try:
        data, bbox, _ = detector.detectAndDecode(img)
    except:
        continue
    cv2.namedWindow('preview', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('preview',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("preview",img)
    if data:
        a=data
    wk=cv2.waitKey(10)
    if wk==32:
        em=pymsgbox.prompt("Enter Email",'Email',"@niser.ac.in")
        if em==None :
            a=None
            continue
        cs=read_csv(r"\\PERSEUS\QR-Cop\qr.csv")
        maske=cs["Email"].values==em
        pose = np.flatnonzero(maske)
        if len(pose)>0:
            k=0
            for i in range(len(pose)):
                if cs["Count"][pose[i]]>0:
                    a=cs['Secret'][pose[i]]
                    k=1
                    break
            if k==0:    
                ctypes.windll.user32.MessageBoxW(0, "All Coupons exhausted! ","Coupons Ranout.", 16)
        else:
            ctypes.windll.user32.MessageBoxW(0, "Please enter a valid Email! ","Not a Registered Email.", 16)

    if a:
        cs=read_csv(r"\\PERSEUS\QR-Cop\qr.csv") 
        mask=cs["Secret"].values==a
        pos = np.flatnonzero(mask)
        if len(pos)!=0 :
            if cs["Count"][pos[0]]>0:
                if cs["Count"][pos[0]]>1:
                    executor.submit(playsound,r"\\PERSEUS\QR-Cop\retro.wav")
                    no=pymsgbox.prompt(f"Hello {cs['Name'][pos[0]]}, Your itinary conatins {cs['Count'][pos[0]]} food coupon(s). \n How many coupons would you like to redeem currently?","Happy Onam 😃",f"{cs['Count'][pos[0]]}")
                    if no==None :
                        a=None
                        continue
                    try:
                        int(no)
                    except:
                        ctypes.windll.user32.MessageBoxW(0, "Please enter a valid number! ","Not a valid number.", 16)
                        continue
                    
                    if no=="0" :
                        ctypes.windll.user32.MessageBoxW(0, "You entered 0 coupons for redemption. Please enter a valid number of coupons to be redeemed.","Invalid Request.", 16)
                        continue

                    if cs["Count"][pos[0]]-int(no)>-1:
                        cs["Count"][pos[0]]=cs["Count"][pos[0]]-int(no)
                        # pymsgbox.alert("Validation Succesful", "Valid")
                        logger.warning(f'{ho}: {cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have used {no} coupon/s, {cs["Count"][pos[0]]} left! >PASS')
                        ctypes.windll.user32.MessageBoxW(0, f" {no} food coupon(s) have been redeemed.✅ \n Have a happy meal 😃", "Welcome", 64)
                        executor.submit(mail_send,cs["Name"][pos[0]],cs["Email"][pos[0]],no,cs["Purchased"][pos[0]])
                    else:
                        # pymsgbox.alert("Not enough Coupons ","Not Valid")
                        logger.warning(f'{ho}: {cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have wanted {no} coupon/s, but thers only {cs["Count"][pos[0]]} left! >FAIL')
                        ctypes.windll.user32.MessageBoxW(0, f"😕 You only have {cs['Count'][pos[0]]} coupon(s) left.","Insufficient Balance", 16)
                        continue
                else:
                    # pymsgbox.alert("Validation Succesful", "Valid")
                    ctypes.windll.user32.MessageBoxW(0, "Your food coupon has been redeemed.✅ \n Have a happy meal 😃", "Welcome", 64)
                    logger.warning(f'{ho}: {cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have used their coupon >PASS')
                    cs["Count"][pos[0]]=0
                    executor.submit(mail_send,cs["Name"][pos[0]],cs["Email"][pos[0]])
            else:
                # pymsgbox.alert("Coupon Expired","Not Valid")
                logger.warning(f'{ho}: {cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have tried to use expired coupon >FAIL')
                ctypes.windll.user32.MessageBoxW(0, "All food coupons have been already redeemed ☠️. This QR Code is no more valid.","Ticket Exhausted", 16)
        else:
            # pymsgbox.alert("QR not Valid","COUNTERFEIT")
            ctypes.windll.user32.MessageBoxW(0, "Oops! Something went wrong ❌","Invalid QR Code", 16)
            logger.warning(f'{ho}: Invalid QR Code')

        # print(cs)
        
        cs.to_csv(r"\\PERSEUS\QR-Cop\qr.csv",index=False)
    a=None




