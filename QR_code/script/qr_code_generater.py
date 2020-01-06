import qrcode
import ntplib
from time import ctime
import datetime
import pytz
import os

class qr_code_generate:
	def __init__(self,qr_size,time_zone,time_flag,encode_flag):
		self.formatted_date_with_corrections =""
		if time_flag == True:
			try:
				LOCALTIMEZONE = pytz.timezone("Asia/Shanghai")
				time_client = ntplib.NTPClient()
				response = time_client.request('cn.pool.ntp.org', version=3)
				response.offset
				formatted_date_with_micro_seconds = datetime.datetime.strptime(str(datetime.datetime.utcfromtimestamp(response.tx_time)),"%Y-%m-%d %H:%M:%S.%f")
				local_dt = formatted_date_with_micro_seconds.replace(tzinfo=pytz.utc).astimezone(LOCALTIMEZONE)
				self.formatted_date_with_corrections = str(local_dt).split(".")[0]
			except: 
				self.formatted_date_with_corrections = "please check the internet connect"
		if encode_flag == True:
			self.encode = True
		else:
			self.encode = False
		self.qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=qr_size,
		border=4,
		)	

	def save_qrcode(self,data,name):
		if self.encode :
			encode_data = data + " " +self.formatted_date_with_corrections
			self.qr.add_data(encode_data.encode('base64', 'strict'))
		else:
			self.qr.add_data(data + " " +self.formatted_date_with_corrections )
		self.qr.make(fit=True)
		img = self.qr.make_image(fill_color="black", back_color="white")
		if not os.path.exists('qr_code'):
			os.mkdir('qr_code')
		img.save("qr_code/"+name+".png")

if __name__== "__main__":
	print("start") 
	time_zone = "Asia/Shanghai"
	qr = qr_code_generate(10,time_zone,False,False)
	name = "Sky worker"
	product = "light sword"
	place = "earth"
	data = name + " " + product + " " + place
	qr.save_qrcode(data,name) 





