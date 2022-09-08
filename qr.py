from asyncio.log import logger
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
    cv2.waitKey(10)
    
    if a:
        cs=read_csv(r"\\PERSEUS\QR-Cop\qr.csv")
        mask=cs["Secret"].values==int(a)
        pos = np.flatnonzero(mask)
        if len(pos)!=0 :
            if cs["Count"][pos[0]]=='One':
                ctypes.windll.user32.MessageBoxW(0, "Validation Succesful", "Valid", 64)
                logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have used their coupon')
                cs["Count"][pos[0]]=0
                a=None
                continue
            if cs["Count"][pos[0]]>0:
                if cs["Count"][pos[0]]>1:
                    no=pymsgbox.prompt(f"How many Coupons to be used NOW, there's {cs['Count'][pos[0]]} entries left","Number of Coupons","1")
                    try:
                        int(no)
                    except:
                        ctypes.windll.user32.MessageBoxW(0, "Enter a proper number! ","Wrong Data Given", 16)
                        continue
                    if no==0 :
                        ctypes.windll.user32.MessageBoxW(0, "Enter a proper number! ","Wrong Data Given", 16)
                        continue
                    if cs["Count"][pos[0]]-int(no)>-1:
                        cs["Count"][pos[0]]=cs["Count"][pos[0]]-int(no)
                        # pymsgbox.alert("Validation Succesful", "Valid")
                        logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have used {no} coupon/s, {cs["Count"][pos[0]]} left!')
                        ctypes.windll.user32.MessageBoxW(0, "Validation Succesful", "Valid", 64)
                    else:
                        # pymsgbox.alert("Not enough Coupons ","Not Valid")
                        logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have wanted {no} coupon/s, but thers only {cs["Count"][pos[0]]} left!')
                        ctypes.windll.user32.MessageBoxW(0, "Not enough Coupons ","Not Valid", 16)
                else:
                    # pymsgbox.alert("Validation Succesful", "Valid")
                    ctypes.windll.user32.MessageBoxW(0, "Validation Succesful", "Valid", 64)
                    logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have used their coupon')
                    cs["Count"][pos[0]]=0
            else:
                # pymsgbox.alert("Coupon Expired","Not Valid")
                logger.warning(f'{cs["Name"][pos[0]]} ({cs["Email"][pos[0]]}) have tried to use expired coupon')
                ctypes.windll.user32.MessageBoxW(0, "Coupon Expired","Not Valid", 16)
        else:
            # pymsgbox.alert("QR not Valid","COUNTERFEIT")
            ctypes.windll.user32.MessageBoxW(0, "QR not Valid","COUNTERFEIT", 16)
            logger.warning(f'Counterfeit detected!!')

        # print(cs)
        
        cs.to_csv(r"\\PERSEUS\QR-Cop\qr.csv",index=False)
    a=None
