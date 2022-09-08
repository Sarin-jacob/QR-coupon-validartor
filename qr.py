
from playsound import playsound
import cv2  
import logging
from pandas import read_csv
import pymsgbox
import numpy as np
import ctypes
cap = cv2.VideoCapture(0)
logger=logging.getLogger()
logging.basicConfig(level=logging.INFO,filename=r"\\PERSEUS\QR-Cop\Coupon.log",format="%(asctime)s -> %(message)s")
logger.warning(f'Script Initiated')

detector = cv2.QRCodeDetector()
a=None
while 1:
    _,img = cap.read()
    data, bbox, _ = detector.detectAndDecode(img)
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
            for i in range(len(pose)):
                if cs["Count"][pose[i]]>0:
                    a=cs['Secret'][pose[i]]
                    break
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
                    playsound(r"\\PERSEUS\QR-Cop\retro.wav")
                    no=pymsgbox.prompt(f"Hello {cs['Name'][pos[0]]}, Your itinary conatins {cs['Count'][pos[0]]} food coupon(s). \n How many coupons would you like to redeem currently?","Happy Onam 😃","1")
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
                        logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have used {no} coupon/s, {cs["Count"][pos[0]]} left! >PASS')
                        ctypes.windll.user32.MessageBoxW(0, f" {no} food coupon(s) have been redeemed.✅ \n Have a happy meal 😃", "Welcome", 64)
                    else:
                        # pymsgbox.alert("Not enough Coupons ","Not Valid")
                        logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have wanted {no} coupon/s, but thers only {cs["Count"][pos[0]]} left! >FAIL')
                        ctypes.windll.user32.MessageBoxW(0, f"😕 You only have {cs['Count'][pos[0]]} coupon(s) left.","Insufficient Balance", 16)
                        continue
                else:
                    # pymsgbox.alert("Validation Succesful", "Valid")
                    ctypes.windll.user32.MessageBoxW(0, "Your food coupon has been redeemed.✅ \n Have a happy meal 😃", "Welcome", 64)
                    logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have used their coupon >PASS')
                    cs["Count"][pos[0]]=0
            else:
                # pymsgbox.alert("Coupon Expired","Not Valid")
                logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have tried to use expired coupon >FAIL')
                ctypes.windll.user32.MessageBoxW(0, "All food coupons have been already redeemed ☠️. This QR Code is no more valid.","Ticket Exhausted", 16)
        else:
            # pymsgbox.alert("QR not Valid","COUNTERFEIT")
            ctypes.windll.user32.MessageBoxW(0, "Oops! Something went wrong ❌","Invalid QR Code", 16)
            logger.warning(f'Invalid QR Code')

        # print(cs)
        
        cs.to_csv(r"\\PERSEUS\QR-Cop\qr.csv",index=False)
    a=None
