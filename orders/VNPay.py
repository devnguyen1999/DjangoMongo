import hashlib
import urllib
from django.utils.http import urlquote
from django.conf import settings
import urllib.request
import urllib.parse
from datetime import datetime

def payment_by_VNPay(data):
    order_type = data['order_type']
    order_id = data['order_id']
    amount = data['amount']
    order_desc = data['order_desc']
    bank_code = data['bank_code']
    language = data['language']
    # ipaddr = get_client_ip(request)

    # Build URL Payment
    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.0.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
    vnp.requestData['vnp_Amount'] = amount * 100
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = order_id
    vnp.requestData['vnp_OrderInfo'] = order_desc
    vnp.requestData['vnp_OrderType'] = order_type
    # Check language, default: vn
    if language and language != '':
        vnp.requestData['vnp_Locale'] = language
    else:
        vnp.requestData['vnp_Locale'] = 'vn'
        # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
    if bank_code and bank_code != "":
        vnp.requestData['vnp_BankCode'] = bank_code

    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
    # vnp.requestData['vnp_IpAddr'] = ipaddr
    vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
    # print(vnpay_payment_url)
    return vnpay_payment_url


class vnpay:
    requestData = {}
    responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        inputData = sorted(self.requestData.items())
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urlquote(str(val))
                hasData = hasData + "&" + str(key) + '=' + str(val)
            else:
                seq = 1
                queryString = key + '=' + urlquote(str(val))
                hasData = str(key) + '=' + str(val)

        hashValue = self.__sha256(secret_key + hasData)
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHashType=SHA256&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key):
        vnp_SecureHash = self.responseData['vnp_SecureHash']
        # Remove hash params
        if 'vnp_SecureHash' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHashType')

        inputData = sorted(self.responseData.items())
        hasData = ''
        seq = 0

        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + str(val)
                else:
                    seq = 1
                    hasData = str(key) + '=' + str(val)
        hashValue = self.__sha256(secret_key + hasData)

        # print(
        #     'Validate debug, HashData:' + secret_key + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)

        return vnp_SecureHash == hashValue

    def __sha256(self, input):
        byteInput = input.encode('utf-8')
        return hashlib.sha256(byteInput).hexdigest()
