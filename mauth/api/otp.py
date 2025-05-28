import smtplib
from email.message import EmailMessage
from random import randint
from .models import User
class OTP: 
    def __init__(self) -> None:
        self.from_email = 'blownbrian@gmail.com'
        self.password = 'sxbg xjgm jlin acrq'        
        self.server = smtplib.SMTP('smtp.gmail.com',587)
        self.start_server()


    def start_server(self) -> bool:
        try: 
            print("starting otp server")
            self.server.starttls()
            login_status = self.server.login(self.from_email,self.password)
            print("login success" + str(login_status))
            return True
        except Exception as e:
            print(e)
            return False
        
       
    def create_otp(self)->str:
        return ''.join([str(randint(0,9)) for i in range(6)])
    
    def send_otp(self,id : str, to:str)->bool:
        try:
            msg = EmailMessage()
            msg['Subject'] = "mAuth verification code"
            msg['From'] = self.from_email
            otp = self.create_otp()
            msg['To'] = to
            msg.set_content('Your OTP is '+ otp)
            user = User.objects.get(id = id) 
            user.otp = otp
            user.save()
            self.server.send_message(msg)
            return True
        except smtplib.SMTPException as e:
            #self.server.starttls()
            self.server.login(self.from_email,self.password)
            self.send_otp(id=id,to=to)
            print("recused with error : ",e)
        except Exception as e:
            print(e)
            return False
        

    def simpleOTP (self, to : str, otp : str):
        try:
            msg = EmailMessage()
            msg['Subject'] = "mAuth verification code"
            msg['From'] = self.from_email
            msg['To'] = to
            msg.set_content('Your OTP is '+ otp)
            self.server.send_message(msg)
            return True
        except Exception as e:
            print(e)
            return False


    def verifyOTP(self,id : str,otp: str):        
        try:
            user = User.objects.get(id=id)           
            if user:             
             if otp == user.otp:              
                 return user
             else:                 
                 return False
            else:                
                return False
        except Exception as e:            
            print(e)
            return False