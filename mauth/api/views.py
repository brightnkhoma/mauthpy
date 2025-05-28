from api.models import User,PhoneNumber, Transactions,Tower
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json
from .otp import OTP


def withDraw(amount : str, phoneNumber : str,isSuspicious : bool = True):
    try:
        phone = PhoneNumber.objects.get(number = phoneNumber)
        user = User.objects.get(phoneNumber = phone)
        if user:          
            oldTransactions = Transactions.objects.filter(user = user,type = "withdraw")
            if oldTransactions.exists():
                averageTransaction =  (sum(list(map( lambda x:float(x.amount),oldTransactions))))/len(oldTransactions)
                if((float(amount)/averageTransaction) > 2.5 and len(oldTransactions) > 8 and isSuspicious):
                    return "exceeds normal"
                else:
                    user.average_transaction = averageTransaction
            balance = float(user.balance)
            amount = float(amount)
            newBalance = (balance - amount) if amount <= balance else balance
            user.balance = newBalance
            newTransaction = Transactions(user = user, amount = str(amount),type = "withdraw")
            newTransaction.save()
            user.save()                
            return newBalance if newBalance != balance else False
    except Exception as e:
        print(e)
        return False

def deposit(amount : str,phoneNumber : str, _from : str)->bool:
    try:
        user = User.objects.get(number = phoneNumber)
        newTransaction = Transactions(amount = amount,user = user, type = "deposit",_from = _from)
        oldBalance = user.balance
        newBalance = float(oldBalance) + float(amount)
        user.balance = newBalance
        user.save()
        newTransaction.save()
        return True
        # return toJsonResponse({"status" : True,"message" : f"You have received Mk {amount} from {_from}"})



    except Exception as e:
        print(e)
        return False
        # return toJsonResponse({"status" : False,"message" : "Failed, something went wrong"})

@csrf_exempt 
def makeWithdraw(request):
    if request.method == "POST": 
        try:
            data = json.loads(request.body.decode())
            phoneNumber = data.get("phoneNumber")
            amount = data.get("amount")
            isSuspicious = data.get("isSuspicious",True)
            print(isSuspicious)
            print(amount)
            if phoneNumber and amount:
                result = withDraw(amount=amount,phoneNumber=phoneNumber,isSuspicious=isSuspicious)
                if result == "exceeds normal":
                    return toJsonResponse({"status" : False,"message" : "Transaction Failed, unusual transaction detected"})
                if result:
                    return toJsonResponse({"status" : True,"message" : f"{result}"})
                else:
                    return toJsonResponse({"status" : False,"message" : "Something went wrong, please try again"})
        except Exception as e:
            print(e)
            return toJsonResponse({"status" : False,"message" : "Something went wrong, it is not you, it's us"})


@csrf_exempt
def logout(request):
       if request.method == "POST":       
        try:
            data = json.loads(request.body.decode())
            phoneNumber = data.get("phoneNumber")
            print(phoneNumber)
            myPhone = PhoneNumber.objects.get(number = phoneNumber)
            if myPhone:
                user = User.objects.get(phoneNumber = myPhone)
                if user:
                    user.currentDevice = ""
                    user.save()
                    return toJsonResponse({"status" : True,"message" : "Logout Success"})
            return toJsonResponse({"status" : False,"message" : "Something went wrong,please try again"})

        except Exception as e:
            print(e)
            return toJsonResponse({"status" : False,"message" : "Something went wrong, it is not you, it's us"})



@csrf_exempt
def register(request):
       if request.method == "POST":       
        try:
            data = json.loads(request.body.decode()) 
            phoneNumber = data.get("phoneNumber",None)
            nationalId = data.get("nationalId",None)
            password = data.get("password",None)
            email = data.get("email","None")
            secondaryNumber = data.get("secondaryNumber","None")
            avatar = data.get("avatar","None")
            phone = getPhoneDetails(phoneNumber,nationalId)
            print("passing",phone)
            if not phone:
                return toJsonResponse({"success" : False})


            if phoneNumber and password and nationalId and phoneNumber:
                user = User(phoneNumber=phone,password=password,email=email,secondaryPhoneNumber=secondaryNumber,avatar=avatar,iccid=phone.iccid)
                user.save()
                json_data = json.dumps({"success" : True})
                response = HttpResponse(json_data, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="data.json"'
                return response
            else:               
                json_data = json.dumps({"success" : False})
                response = HttpResponse(json_data, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="data.json"'
                return response
        except Exception as e:
            print(e)
            json_data = json.dumps({"success" : False})
            response = HttpResponse(json_data, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="data.json"'
            return response

@csrf_exempt
def login(request):
    try:
        if request.method == "POST":
            loginData = json.loads(request.body.decode())
            phoneNumber = loginData.get("phoneNumber")
            password = loginData.get("password")
            nationalId = loginData.get("nationalId")
            deviceName = loginData.get("deviceName")
            phone = PhoneNumber.objects.get(number = phoneNumber,nationalId=nationalId)
            user = User.objects.get(phoneNumber = phone,password=password)
            if phone.iccid != user.iccid:
                print("sim swap")
                return toJsonResponse({"id" : "", "status" : False,"simSwap" : True})
            if user.currentDevice and user.currentDevice != deviceName:
                print(deviceName)
                print(user.currentDevice)
                return toJsonResponse({"id" : user.currentDevice, "status" : False,"simSwap" : False,"deviceError" : True})
            if not user.currentDevice:
                user.currentDevice = deviceName
                user.save()
            result = {"id" : user.id, "status" : True,"simSwap" : False}
            otp_server = OTP()
            otp_server.send_otp(user.id,user.email)

            return toJsonResponse(result)
        else:
            print("INCORRECT REQUEST")
            result = {"id" : "NONE", "status" : False,"simSwap" : False}
    except Exception as e:
        result = {"id" : "NONE", "status" : False,"simSwap" : False}
        print(e)
        return toJsonResponse(result)

    
        

def toJsonResponse(data)->HttpResponse:
    json_data = json.dumps(data)   
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="data.json"'
    return response

@csrf_exempt
def verifyOTP(request):
    try:
        if request.method == "POST":
            userData = json.loads(request.body.decode()) 
            id = userData.get("id")   
            otp = userData.get("otp") 
            otp_server = OTP()       
            user = otp_server.verifyOTP(id=id,otp=otp)
            print(user)
            if user:
                phone = model_to_dict(user.phoneNumber) 
                fistName = phone.get("firstName")
                lastName  = phone.get("lastName")
                phoneNumber = phone.get("number")
                print()
                person = {
                        "firstName" : fistName,
                        "lastName" : lastName,
                        "phoneNumber" : phoneNumber,  
                        "email" :user.email,
                        "secondaryPhoneNumber" : user.secondaryPhoneNumber,
                        "avatar" : user.avatar,
                        "balance" : user.balance
                }
                return toJsonResponse({"content" : person, "status": True})
            else:
                 data = {"content" : "", "status" : False}
                 return toJsonResponse(data)
           
    except Exception as e:
        print(e)
        data = {"content" : "", "status" : False}
        return toJsonResponse(data)
    
def getPhoneDetails(phoneNumber:str,nationalId:str):
    try:
        number = PhoneNumber.objects.get(number=phoneNumber,nationalId=nationalId)
        return number
    except Exception as e:
        print(e)
        return False

@csrf_exempt
def registerPhoneNumber(request):
    try:
        if(request.method == "POST"):
            data = json.loads(request.body.decode())
            phoneNumber = data.get("phoneNumber")
            firstName = data.get("firstName")
            lastName = data.get("lastName")
            nationalId = data.get("nationalId")
            ICCID = data.get("ICCID")
            statement = data.get("statement")
            answer = data.get("answer")
            phone = PhoneNumber(number = phoneNumber,iccid=ICCID,firstName=firstName,lastName=lastName,nationalId=nationalId,statement=statement,answer=answer)
            phone.save()
            return toJsonResponse({"status" : True,"message" : "Sim reqistration success"})
    except Exception as e:
        print(e)
        return toJsonResponse({"status" : False,"message" : "failed to add number, maybe it is already registered"})

@csrf_exempt
def getStatementAnswer(request):
    try:
        if (request.method == "POST"):
            data = json.loads(request.body.decode())
            phoneNumber = data.get("phoneNumber")
            firstName = data.get("firstName")
            lastName = data.get("lastName")
            nationalId = data.get("nationalId")
           
            if phoneNumber and firstName and lastName and nationalId:
                phoneDetails = PhoneNumber.objects.get(number = phoneNumber,firstName = firstName,lastName = lastName,nationalId=nationalId)
                answer = phoneDetails.answer
                statement = phoneDetails.statement
                return toJsonResponse({"status": True,"answer" : answer,"statement" : statement})
            else:
                return toJsonResponse({"status": False,"statement" : "invalid details","answer" : ""})
    except Exception as e:
        print(e)
        return toJsonResponse({"status":False,"statement" : "invalid details, maybe the phone number is not registered","answer" : ""})

@csrf_exempt
def reregister(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode())
            phoneNumber = data.get("phoneNumber")
            firstName = data.get("firstName")
            lastName = data.get("lastName")
            nationalId = data.get("nationalId")
            ICCID = data.get("ICCID")
            answer = data.get("answer")
            if phoneNumber and firstName and lastName and nationalId and ICCID and answer:
                phoneDetails = PhoneNumber.objects.get(number = phoneNumber,firstName = firstName,lastName = lastName,nationalId=nationalId, answer=answer)
                phoneDetails.iccid = ICCID 
                phoneDetails.save()
                return toJsonResponse({"status" : True,"message" : "Sim card re-registered successifully"})
            else:
                return toJsonResponse({"status" : False,"message" : "Sim card re-registration failed"})
    except Exception as e:
        print(e)
        return toJsonResponse({"status" : False,"message" : "Sim card re-registration failed"})
    

@csrf_exempt
def verifyUser(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode())
            phoneNumber = data.get("phoneNumber")
            nationalId = data.get("nationalId")
            answer = data.get("answer")
            phone = PhoneNumber.objects.get(number = phoneNumber, nationalId = nationalId)
            if answer == phone.answer:
                user = User.objects.get(phoneNumber=phone)
                user.iccid = phone.iccid
                user.save()
                return toJsonResponse({"status" : True,"message" : "User verified"})
            else:
                return toJsonResponse({"status" : False,"message" : "user unrecognized"})
    except Exception as e:
        print(e)
        return toJsonResponse({"status" : False,"message" : "user unrecognized"})

@csrf_exempt
def otp(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode())
            otp = data.get("otp")
            email = data.get("email")
            newOtp = OTP()
            newOtp.simpleOTP(to=email,otp=otp)
            return toJsonResponse({"status" : True,"message" : "otp sent"})
    except Exception as e:
        print(e)
        return toJsonResponse({"status" : False,"message" : "Failed to send otp"})



@csrf_exempt
def simpleVerify(request):
    try:
         data = json.loads(request.body.decode())
         phoneNumber = data.get("phoneNumber")
         password = data.get("password")
         print(data)
         phone = PhoneNumber.objects.get(number = phoneNumber)
         if phone:
                 user = User.objects.get(phoneNumber = phone)
                 if user.password == password:
                     user.incorrectPasswordTrials = "4"
                     user.save()
                     return toJsonResponse({"status" : True,"message" : "verified"})
                 trials = int(user.incorrectPasswordTrials) - 1
                 user.incorrectPasswordTrials = str(trials) if trials > 0 else "0"
                 return toJsonResponse({"status" : False, "message" : f"verification failed, you will be loged out after {trials} incorrect trials"})
         return toJsonResponse({"status" : False, "message" : f"verification failed"})
    except Exception as e:
        print(e)
        return toJsonResponse({"status" : False, "message" : f"something went wrong, it's not you, it's us, we will fix this problem soon"})

