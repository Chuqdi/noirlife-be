import threading
from referals.models import Referal
from users.models import User
from utils.SMSHelper import send_message
from utils.EmailSender import actionNotificationEmail




def onDepositForAReferedUser(user:User, amount:int):
    referalCode = user.referalCode
    refered_by = User.objects.get(phone_number = referalCode)
    referal = Referal.objects.get(refered_by = refered_by)
    if not referal.is_deposited:
        amount = amount/5
        referal.amount = amount
        referal.is_deposited = True
        referal.save()


        body =f"""
        Congrats, you have recieved {amount} as referal commission from {user.phone_number}.
        """

        thread = threading.Thread(target=send_message, kwargs={"body":body, "to_number":referal.refered_by.phone_number})
        thread.start()


        if referal.refered_by.email_verified:
            thread = threading.Thread(target=actionNotificationEmail, kwargs={"message":body, "to":referal.refered_by.email, "title":"Referal Notification"})
            thread.start()
            




def onUserCreateReferalAction(referal_code:str, refered_phone_number):
    refering = User.objects.get(phone_number=refered_phone_number)
    refered_by = User.objects.get(phone_number=referal_code)


    r = Referal.objects.create(
        refered_by =refered_by,
        refering=refering
    )
    refered_by.wallet_balance = int(refered_by.wallet_balance) + 50
    refered_by.save()

    body =f"""
        Congrats, {refering.phone_number} used your referal code during sign up.
        Your account has been credited with NGN500.
        """

    thread = threading.Thread(target=send_message, kwargs={"body":body, "to_number":refered_by.phone_number})
    thread.start()


    if refered_by.email_verified:
        thread = threading.Thread(target=actionNotificationEmail, kwargs={"message":body, "to":refered_by.email, "title":"Referal Notification"})
        thread.start()


