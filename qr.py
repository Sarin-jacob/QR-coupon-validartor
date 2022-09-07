import cv2  
from pandas import read_csv
import pymsgbox
import numpy as np
import ctypes
cap = cv2.VideoCapture(0)
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
        print(a) 
    cv2.waitKey(10)

    cs=read_csv(r"\\PERSEUS\QR-Cop\qr.csv")
    mask=cs["code"].values==a
    pos = np.flatnonzero(mask)
    if a:
        if len(pos)!=0 :
            if cs["no"][pos[0]]>0:
                if cs["no"][pos[0]]>1:
                    no=pymsgbox.prompt("How many Coupons to be used NOW","Number of Coupons","1")
                    try:
                        int(no)
                    except:
                        ctypes.windll.user32.MessageBoxW(0, "Enter a proper number! ","Wrong Data Given", 16)
                        continue
                    if no==0 :
                        ctypes.windll.user32.MessageBoxW(0, "Enter a proper number! ","Wrong Data Given", 16)
                        continue
                    if cs["no"][pos[0]]-int(no)>-1:
                        cs["no"][pos[0]]=cs["no"][pos[0]]-int(no)
                        # pymsgbox.alert("Validation Succesful", "Valid")
                        ctypes.windll.user32.MessageBoxW(0, "Validation Succesful", "Valid", 64)
                    else:
                        # pymsgbox.alert("Not enough Coupons ","Not Valid")
                        ctypes.windll.user32.MessageBoxW(0, "Not enough Coupons ","Not Valid", 16)
                else:
                    # pymsgbox.alert("Validation Succesful", "Valid")
                    ctypes.windll.user32.MessageBoxW(0, "Validation Succesful", "Valid", 64)
                    cs["no"][pos[0]]=0
            else:
                # pymsgbox.alert("Coupon Expired","Not Valid")
                ctypes.windll.user32.MessageBoxW(0, "Coupon Expired","Not Valid", 16)
        else:
            # pymsgbox.alert("QR not Valid","COUNTERFEIT")
            ctypes.windll.user32.MessageBoxW(0, "QR not Valid","COUNTERFEIT", 16)
        # print(cs)
        
    cs.to_csv(r"\\PERSEUS\QR-Cop\qr.csv",index=False)
    a=None
