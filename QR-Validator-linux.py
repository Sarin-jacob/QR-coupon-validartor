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
from os import remove
# from ctypes import windll
import concurrent.futures
import pickle 
executor = concurrent.futures.ThreadPoolExecutor() 
global etru


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
    print('\nThe csv file should contain these Headers: \nName Email Count Secret\nWhere Count is the number of coupons purchasd, Secret is the alpha-numeral text of the QR code.\n You will be prmopted to select the csv file in few seconds.')
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
    config["number-cop-mesg"]=input("\n\nEnter the message that asks number of coupon to be redeemed.\nNote: you can use the variables {name},{email},{count}(coupons left before last usage)\n\n")
    config["multi-cop-t"]=input("\n\nEnter the title of message box to be shown when one qr have more than one coupon is reedemed(partialy or fully).\n\n ")
    config["multi-cop-mesg"]=input("\n\nEnter the message to be shown when one qr have more than one coupon is reedemed(partialy or fully).\nNote: you can use the variables {name},{email},{count}(coupons left before last usage)\n\n")
    config["multi-cop-error-t"]=input("\n\nEnter the title of message box to be shown when one qr have more than one coupon enters more than the qr holds(after earlier uses too).\n\n ")
    config["multi-cop-error-mesg"]=input("\n\nEnter the message to be shown when one qr have more than one coupon enters more than the qr holds(after earlier uses too).\nNote: you can use the variables {name},{email},{count}(coupons left before last usage)\n\n ")
    config["cop-t"]=input("\n\nEnter the title of message box to be shown when one coupon is redeemed.\n\n ")
    config["cop-mesg"]=input("\n\nEnter the message to be shown when  one coupon is redeemed.\nNote: you can use the variables {name},{email},{count}(coupons left before last usage)\n\n")
    config["invalid-t"]=input("\n\nEnter the title of message box shown when invalid(not registered) qr code is scanned\n\n")
    config["invalid-mesg"]=input("\n\nEnter the message when invalid(not registered) qr code is scanned\n\n")
    config["exhausted-t"]=input("\n\nEnter the title of message box when an fully redeemed qr is shown\n\n")
    config["exhausted-mesg"]=input("\n\nEnter the message when an fully redeemed qr is shown\n\n")

    config["cop-mesg"]=config["cop-mesg"].replace("{count}","{cs['Count'][pos[0]]}")
    config["multi-cop-mesg"]=config["multi-cop-mesg"].replace("{count}","{cs['Count'][pos[0]]}")
    config["multi-cop-error-mesg"]=config["multi-cop-error-mesg"].replace("{count}","{cs['Count'][pos[0]]}")
    config["number-cop-mesg"]=config["number-cop-mesg"].replace("{count}","{cs['Count'][pos[0]]}")

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

try:
    cs=read_csv(config["csv_path"])
    test=cs["Entered"]
except:
    cs=read_csv(config["csv_path"])
    cs["Entered"]=0
    cs.to_csv(config["csv_path"],index=False)

try:
    cs=read_csv(config["csv_path"])
    test=cs["Purchased"]
except:
    cs=read_csv(config["csv_path"])
    cs["Purchased"]=cs["Count"]
    cs.to_csv(config["csv_path"],index=False)

cap = cv2.VideoCapture(0)
ho=gethostname()
logger=logging.getLogger()
logging.basicConfig(level=logging.INFO,filename=r"Coupon.log",format="  %(asctime)s -> %(message)s")

logger.warning(f'{ho}: Script Initiated')


# messagebox=ctypes.windll.user32.MessageBoxW
# messagebox=windll.user32.MessageBoxW
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
            executor.submit(playsound,"info.wav")
            pymsgbox.alert(  "Run the executable file once again to reconfigure.")
            print("\n\n Run the executable file once again to reconfigure.")
            import dance
            break
        elif em=="saveconfig":
            saver(config,"validator.conf.save")
            executor.submit(playsound,"info.wav")
            pymsgbox.alert( "Configuration file saved as 'validator.conf.save' ")
            continue
        elif em=="entryleft":
            cs=read_csv(config["csv_path"])
            sumi=0
            for i in cs['Count']:
                sumi+=i
            executor.submit(playsound,"info.wav")
            pymsgbox.alert( f"{sumi} entries left ","Entries Left!!")
            continue
        elif em=="scansdone":
            cs=read_csv(config["csv_path"])
            sumi=0
            for i in cs['Entered']:
                sumi+=i
            executor.submit(playsound,"info.wav")
            pymsgbox.alert( f"{sumi} entered ","Entries Done!!")
            continue
        elif em=="savecsv":
            now = datetime.now()
            timedate = now.strftime("%d-%m_%H.%M")
            cs=read_csv(config["csv_path"])
            cs.to_csv(rf"qrsave_{timedate}.csv",index=False)
            executor.submit(playsound,"info.wav")
            pymsgbox.alert( "CSV saved!")
            continue
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
                executor.submit(playsound,"fail.wav")
                pymsgbox.alert( "All Coupons exhausted! ","Coupons Ranout.")
        else:
            executor.submit(playsound,"fail.wav")
            pymsgbox.alert( "Please enter a valid Email! ","Not a Registered Email.")

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
                    executor.submit(playsound,"info.wav")
                    no=pymsgbox.prompt(effify(config["number-cop-mesg"]),effify(config["number-cop-t"]),f"{count}")
                    if no==None :
                        a=None
                        continue
                    try:
                        int(no)
                    except:
                        executor.submit(playsound,"fail.wav")
                        pymsgbox.alert( "Please enter a valid number! ","Not a valid number.")
                        continue
                    
                    if no.strip()=="0" :
                        executor.submit(playsound,"fail.wav")
                        pymsgbox.alert( "You entered 0 coupons for redemption. Please enter a valid number of coupons to be redeemed.","Invalid Request.")
                        continue

                    if count-int(no)>-1:
                        cs['Count'][pos[0]]=count-int(no)
                        cs["Entered"][pos[0]]=entered+int(no)
                        # pymsgbox.alert("Validation Succesful", "Valid")
                        logger.warning(f'{ho}: {name} ({email}) have used {no} coupon/s, {cs["Count"][pos[0]]} left! >PASS')
                        executor.submit(playsound,"pass.wav")
                        pymsgbox.alert( effify(config["multi-cop-mesg"]), effify(config["multi-cop-t"]))
                        executor.submit(mail_send,name,email,no,cs["Purchased"][pos[0]])
                    else:
                        # pymsgbox.alert("Not enough Coupons ","Not Valid")
                        logger.warning(f'{ho}: {name} ({email}) have wanted {no} coupon/s, but thers only {cs["Count"][pos[0]]} left! >FAIL')
                        executor.submit(playsound,"fail.wav")
                        pymsgbox.alert( effify(config["multi-cop-error-mesg"]),effify(config["multi-cop-error-t"]))
                        continue
                else:
                    # pymsgbox.alert("Validation Succesful", "Valid")
                    executor.submit(playsound,"pass.wav")
                    pymsgbox.alert( effify(config["cop-mesg"]), effify(config["cop-t"]))
                    logger.warning(f'{ho}: {name} ({email}) have used their coupon >PASS')
                    cs['Count'][pos[0]]=0
                    cs["Entered"][pos[0]]=entered+1
                    executor.submit(mail_send,name,email)
            else:
                # pymsgbox.alert("Coupon Expired","Not Valid")
                logger.warning(f'{ho}: {name} ({email}) have tried to use expired coupon >FAIL')
                executor.submit(playsound,"fail.wav")
                pymsgbox.alert( effify(config["exhausted-mesg"]),effify(config["exhausted-t"]))
        else:
            # pymsgbox.alert("QR not Valid","COUNTERFEIT")
            executor.submit(playsound,"fail.wav")
            pymsgbox.alert( effify(config["invalid-mesg"]),effify(config["invalid-t"]))
            logger.warning(f'{ho}: Invalid QR Code')

        # print(cs)
        
        cs.to_csv(config["csv_path"],index=False)
    a=None




