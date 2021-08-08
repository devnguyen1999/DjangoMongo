import json
import urllib.request
import urllib.parse
import uuid
import hmac
import hashlib
import codecs
from django.conf import settings

def payment_by_MoMo(data):
    #parameters send to MoMo get get payUrl
    endpoint = settings.MOMO_API_ENDPOINT
    partnerCode = settings.MOMO_PARTNER_CODE
    accessKey = settings.MOMO_ACCESS_KEY
    serectkey = settings.MOMO_SECRET_KEY
    orderInfo = data['orderInfo']
    returnUrl = settings.MOMO_RETURN_URL
    notifyurl = "https://dummy.url/notify"
    amount = str(data['amount'])
    orderId = str(data['orderId'])
    requestId = str(uuid.uuid4())
    requestType = "captureMoMoWallet"
    extraData = "merchantName=;merchantId=" #pass empty value if your merchant does not have stores else merchantName=[storeName]; merchantId=[storeId] to identify a transaction map with a physical store

    #before sign HMAC SHA256 with format
    #partnerCode=$partnerCode&accessKey=$accessKey&requestId=$requestId&amount=$amount&orderId=$oderId&orderInfo=$orderInfo&returnUrl=$returnUrl&notifyUrl=$notifyUrl&extraData=$extraData
    rawSignature = "partnerCode="+partnerCode+"&accessKey="+accessKey+"&requestId="+requestId+"&amount="+amount+"&orderId="+orderId+"&orderInfo="+orderInfo+"&returnUrl="+returnUrl+"&notifyUrl="+notifyurl+"&extraData="+extraData


    #puts raw signature
    # print("--------------------RAW SIGNATURE----------------")
    # print(rawSignature)
    #signature
    h = hmac.new( codecs.encode(serectkey), codecs.encode(rawSignature), hashlib.sha256 )
    signature = h.hexdigest()
    # print("--------------------SIGNATURE----------------")
    # print(signature)

    #json object send to MoMo endpoint

    data = {
            'partnerCode' : partnerCode,
            'accessKey' : accessKey,
            'requestId' : requestId,
            'amount' : amount,
            'orderId' : orderId,
            'orderInfo' : orderInfo,
            'returnUrl' : returnUrl,
            'notifyUrl' : notifyurl,
            'extraData' : extraData,
            'requestType' : requestType,
            'signature' : signature
    }
    # print("--------------------JSON REQUEST----------------\n")
    data = json.dumps(data)
    # print(data)

    clen = len(data)
    headers = {'Content-Type': 'application/json', 'Content-Length': clen}
    b_data = data.encode()
    request = urllib.request.Request(endpoint, b_data, headers)
    f = urllib.request.urlopen(request)

    response = f.read()
    f.close()
    response_str = response.decode()
    # print("--------------------JSON response----------------\n")
    # print(response_str+"\n")

    # print("payUrl\n")
    # print(json.loads(response_str)['payUrl']+"\n")
    return json.loads(response_str)['payUrl']
