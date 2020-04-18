#coding:utf-8
from lcd1602 import *
from datetime import *
import commands
import cv2
import numpy as np
import requests 
import time
import RPi.GPIO as GPIO

lcd = lcd1602()
lcd.clear()
def gpio_init():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23, GPIO.OUT)
	GPIO.output(23, GPIO.LOW)

def get_time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M\n')  # 获取时间信息
	
def face_recognize():
	face_one='./face1.jpg'
	face_two='./face2.png'
	#FACE++  API Key与API Secret
	API_KEY = 'LA6b5U51JCv9x1UIyAWVvW2xh8fY5cTz'
	API_SECRET = 'BsWvLJWkMA29UkhRgE-WaaAKz2MlsZg3'
	# API网址
	BASE_URL = 'https://api-cn.faceplusplus.com/facepp/v3/compare'
	# 使用Requests上传图片
	url = '%s?api_key=%s&api_secret=%s'%(BASE_URL, API_KEY, API_SECRET)
	cv2.namedWindow("test")#命名一个窗口
	cap=cv2.VideoCapture(0)#打开0号摄像头
	success, frame = cap.read()#读取一桢图像，前一个返回值是是否成功，后一个返回值是图像本身
	color = (134,126,255)#设置人脸框的颜色
	classfier=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")#定义分类器  改动的地方在这里  添加分类器的绝对路径
	success,frame = cap.read()
	#print 'frame type:',type(frame)#frame是一个图像灰度数组 
	while(success):
		success, frame = cap.read()
		size=frame.shape[:2]#获得当前桢彩色图像的大小
	#    print frame.shape
		image=np.zeros(size,dtype=np.float16)#定义一个与当前桢图像大小相同的的灰度图像矩阵
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#将当前桢图像转换成灰度图像
		cv2.equalizeHist(image, image)#灰度图像进行直方图等距化 
		#如下三行是设定最小图像的大小
		divisor=8
		h, w = size
		minSize=(w/divisor, h/divisor)
		faceRects = classfier.detectMultiScale(image, 1.2, 2, cv2.CASCADE_SCALE_IMAGE,minSize)#人脸检测
		if len(faceRects)>0:#如果人脸数组长度大于0
		   for faceRect in faceRects: #对每一个人脸画矩形框
					x, y, w, h = faceRect
					cv2.rectangle(frame, (x, y), (x+w, y+h), color)
					cv2.circle(image,(x+w/2,y+h/2),2,color,2,8,0)
		   cv2.imwrite('face2.png',frame)  #保存每次截取到的人脸
		   flag=True
		else:
			flag=False  
		cv2.imshow("test", frame)#显示图像
		if(flag):#有人脸的时候进行匹配比对
	#        print 'compare action'
			files = {'image_file1': open(face_one,'rb'),#图片，二进制文件，需要用post multipart/form-data的方式上传。
					'image_file2': open(face_two,'rb') }
			r = requests.post(url, files = files)
	#        print r #http状态码信息
			confidence =  r.json().get('confidence') #比对结果置信度，范围 [0,100]，小数点后3位有效数字，数字越大表示两个人脸越可能是同一个人。		
			if(confidence>70):
				print 'Open!'
				lcd.clear()
				lcd.message( get_time_now() )
				lcd.message( '      OPEN!' )
				flag_open = True
				GPIO.output(23,GPIO.HIGH)
			else:
				print 'Cannot Open!' 
				#print confidence
				lcd.clear()
				lcd.message( get_time_now() )
				lcd.message( '   Cannot OPEN!' )
#				flag_open = False
				GPIO.output(23,GPIO.LOW)		
		key=cv2.waitKey(10)
		c = chr(key & 255)
		if c in ['q', 'Q', chr(27)]:
				break	
if __name__ == '__main__':
		gpio_init()
		face_recognize()
		GPIO.cleanup()
		cv2.destroyWindow("test")
		
