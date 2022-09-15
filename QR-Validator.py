from time import sleep
from tkinter import Tk, filedialog 
from datetime import datetime
from socket import gethostname
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from playsound import playsound
import cv2  
import logging
from pandas import read_csv
import pymsgbox
from numpy import flatnonzero
from os import remove,system
from ctypes import windll
import concurrent.futures
import pickle 
executor = concurrent.futures.ThreadPoolExecutor() 
global etru
system("")

def saver(obj,filename):
    with open(filename,"wb")as f:
        pickle.dump(obj,f)
def loader(filename):
    with open(filename,"rb")as f:
        obj =pickle.load(f)
    return obj

def effify(non_f_str: str):
    return eval(f'f"""{non_f_str}"""')

try:
    config=loader("Validator.conf")
except:

    config=dict()
    print('\nThe csv file should contain these Headers: \nName Email Count Secret Purchased\nWhere Count and Purchased is the number of coupons purchasd, Secret is the alpha-numeral text of the QR code.\n You will be prmopted to select the csv file in few seconds.')
    import dance
    root=Tk()
    root.withdraw()
    csvfil=filedialog.askopenfilename(parent=root,title="Select CSV File",filetypes=(("CSV Files","*.csv"),("CSV Files","*.CSV")))
    config["csv_path"]=csvfil
    root.destroy()
    emd=input('\n Enter 1 if email sending feature is to be enabled, esle enter 0.\n')
    config["send_email"]=int(emd)
    if emd=="1":
        print("\n\nFor sending mails one should generate app password and enable two-step verification turned on from google account.\n Use Institute email id if possible since mails comming from external source may get identified as spam!\n you can reffer this link to know how to generate app password:\nhttps://www.febooti.com/products/automation-workshop/tutorials/enable-google-app-passwords-for-smtp.html")
        input("\n\nPress enter once u have made sure u have copied the generated app password!\n")
        config["mailid"]=input("\n\nEnter the mail id from which messages to be send\n")
        config["pass"]=input('\n\nEnter app password for the previously entered email\n')
        msg=input("\n\n Input the message to be sent in mail for those who have bought more than one coupon\nNote: can use {name} for name of user, {cop} for number of coupon that got redeemed on last scan, {purchased} for total coupons purchased, {timedate} for date and time.\n press Enter twice to submit!!\n\n")
        lines = [msg]
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                break
        config["email-message1"] = '\n'.join(lines)

        msg=input("\n Input the message to be sent in mail for those who have exhausted their coupon\nleave blank for using same email message as before.\nNote: can use {name} for name of user, {cop} for number of coupon that got redeemed on last scan, {purchased} for total coupons purchased, {timedate} for date and time.\n \n")
        config["mail-sub"]=input("\nEnter subject line for mail\n")
        if not msg:
            config["email-message2"]=config["email-message1"]
        else:
            lines = [msg]
            while True:
                line = input()
                if line:
                    lines.append(line)
                else:
                    break
            config["email-message2"] = '\n'.join(lines)
    config["number-cop-t"]=input("\n\nEnter the title of message box that asks number of coupon to be redeemed\n\n")
    config["number-cop-mesg"]=input("\n\nEnter the message that asks number of coupon to be redeemed\n\n")
    config["multi-cop-t"]=input("\n\nEnter the title of message box to be shown when one qr have more than one coupon is reedemed(partialy or fully).\n\n ")
    config["multi-cop-mesg"]=input("\n\nEnter the message to be shown when one qr have more than one coupon is reedemed(partialy or fully).\nNote: you can use the variables {name},{email},{count}(coupons left before last usage)\n\n")
    config["multi-cop-error-t"]=input("\n\nEnter the title of message box to be shown when one qr have more than one coupon enters more than the qr holds(after earlier uses too).\n\n ")
    config["multi-cop-error-mesg"]=input("\n\nEnter the message to be shown when one qr have more than one coupon enters more than the qr holds(after earlier uses too).\n\n ")
    config["cop-t"]=input("\n\nEnter the title of message box to be shown when one coupon is redeemed.\n\n ")
    config["cop-mesg"]=input("\n\nEnter the message to be shown when  one coupon is redeemed.\nNote: you can use the variables {name},{email},{count}(coupons left before last usage)\n\n")
    config["invalid-t"]=input("\n\nEnter the title of message box shown when invalid(not registered) qr code is scanned\n\n")
    config["invalid-mesg"]=input("\n\nEnter the message when invalid(not registered) qr code is scanned\n\n")
    config["exhausted-t"]=input("\n\nEnter the title of message box when an fully redeemed qr is shown\n\n")
    config["exhausted-mesg"]=input("\n\nEnter the message when an fully redeemed qr is shown\n\n")

    saver(config,"validator.conf")
etru=config["send_email"]





def mail_send(name,ide,cop=1,purchased=1):
    if etru==1:
        now = datetime.now()
        timedate = now.strftime("%d/%m/%Y %H:%M:%S")
        if cop!=1:
            mail_content = effify(config["email-message1"])
        else:
            mail_content=effify(config["email-message2"])
        try:
            #The mail addresses and password
            sender_address = config["mailid"]
            sender_pass = config["pass"]
            receiver_address = ide
            # receiver_address = 'sarin.jacob@niser.ac.in'
            #Setup the MIME
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = config["mail-sub"]   #The subject line
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


cap = cv2.VideoCapture(0)
ho=gethostname()
logger=logging.getLogger()
logging.basicConfig(level=logging.INFO,filename=r"Coupon.log",format="  %(asctime)s -> %(message)s")

logger.warning(f'{ho}: Script Initiated')


# messagebox=ctypes.windll.user32.MessageBoxW
messagebox=windll.user32.MessageBoxW
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
        em=pymsgbox.prompt("Enter Email",'Email',"")
        if em==None :
            a=None
            continue
        elif em=="reconfig":
            remove("validator.conf")
            cap.release()
            cv2.destroyAllWindows()
            logger.warning(f'{ho}: Validator reconfigured')
            print("\n\n Run the executable file once again to reconfigure.")
            import dance
            break
        elif em=="entryleft":
            cs=read_csv(config["csv_path"])
            sumi=0
            for i in cs['Count']:
                sumi+=i
            messagebox(0, f"{sumi} entries left ","Entries Left!!", 64)
            continue
        elif em=="scansdone":
            cs=read_csv(config["csv_path"])
            sumi=0
            for i in cs['Entered']:
                sumi+=i
            messagebox(0, f"{sumi} entered ","Entries Done!!", 64)
            continue
        elif em=="savecsv":
            now = datetime.now()
            timedate = now.strftime("%d-%m_%H.%M")
            cs=read_csv(config["csv_path"])
            cs.to_csv(rf"qrsave_{timedate}.csv",index=False)
        elif em=="exit":
            cap.release()
            cv2.destroyAllWindows()
            logger.warning(f'{ho}: Script Terminated')
            sleep(0.1)
            import dance
            print("Terminated")
            break

        cs=read_csv(config["csv_path"])
        maske=cs["Email"].values==em
        pose = flatnonzero(maske)
        if len(pose)>0:
            k=0
            for i in range(len(pose)):
                if cs["Count"][pose[i]]>0:
                    a=cs['Secret'][pose[i]]
                    k=1
                    break
            if k==0:    
                messagebox(0, "All Coupons exhausted! ","Coupons Ranout.", 16)
        else:
            messagebox(0, "Please enter a valid Email! ","Not a Registered Email.", 16)

    if a:
        cs=read_csv(config["csv_path"]) 
        mask=cs["Secret"].values==a
        pos = flatnonzero(mask)
        if len(pos)!=0 :
            name=cs['Name'][pos[0]]
            count=cs['Count'][pos[0]]
            email=cs['Email'][pos[0]]
            entered=cs["Entered"][pos[0]]
            if count>0:
                if count>1:
                    executor.submit(playsound,"retro.wav")
                    no=pymsgbox.prompt(effify(config["number-cop-mesg"]),effify(config["number-cop-t"]),f"{count}")
                    if no==None :
                        a=None
                        continue
                    try:
                        int(no)
                    except:
                        messagebox(0, "Please enter a valid number! ","Not a valid number.", 16)
                        continue
                    
                    if no=="0" :
                        messagebox(0, "You entered 0 coupons for redemption. Please enter a valid number of coupons to be redeemed.","Invalid Request.", 16)
                        continue

                    if count-int(no)>-1:
                        count=count-int(no)
                        if entered==None:
                            entered=0
                            entered=entered+int(no)
                        else:
                            entered=entered+int(no)
                        # pymsgbox.alert("Validation Succesful", "Valid")
                        logger.warning(f'{ho}: {name} ({email}) have used {no} coupon/s, {count} left! >PASS')
                        messagebox(0, effify(config["multi-cop-mesg"]), effify(config["multi-cop-t"]), 64)
                        executor.submit(mail_send,name,email,no,cs["Purchased"][pos[0]])
                    else:
                        # pymsgbox.alert("Not enough Coupons ","Not Valid")
                        logger.warning(f'{ho}: {name} ({email}) have wanted {no} coupon/s, but thers only {count} left! >FAIL')
                        messagebox(0, effify(config["multi-cop-error-mesg"]),effify(config["multi-cop-error-t"]), 16)
                        continue
                else:
                    # pymsgbox.alert("Validation Succesful", "Valid")
                    messagebox(0, effify(config["cop-mesg"]), effify(config["cop-t"]), 64)
                    logger.warning(f'{ho}: {name} ({email}) have used their coupon >PASS')
                    count=0
                    if entered==None:
                        entered=0
                        entered=entered+1
                    else:
                        entered=entered+1
                    executor.submit(mail_send,name,email)
            else:
                # pymsgbox.alert("Coupon Expired","Not Valid")
                logger.warning(f'{ho}: {name} ({email}) have tried to use expired coupon >FAIL')
                messagebox(0, effify(config["exhausted-mesg"]),effify(config["exhausted-t"]), 16)
        else:
            # pymsgbox.alert("QR not Valid","COUNTERFEIT")
            messagebox(0, effify(config["invalid-mesg"]),effify(config["invalid-t"]), 16)
            logger.warning(f'{ho}: Invalid QR Code')

        # print(cs)
        
        cs.to_csv(config["csv_path"],index=False)
    a=None




