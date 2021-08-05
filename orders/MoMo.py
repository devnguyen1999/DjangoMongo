import json
import urllib
import uuid
import hmac
import hashlib


def payment_by_MoMo(data):
    # parameters send to MoMo get get payUrl
    endpoint = "https://test-payment.momo.vn/gw_payment/transactionProcessor"
    partnerCode = "MOMO"
    accessKey = "F8BBA842ECF85"
    serectkey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    orderInfo = "pay with MoMo"
    returnUrl = "https://momo.vn/return"
    notifyurl = "https://dummy.url/notify"
    amount = str(50000)
    orderId = str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    requestType = "captureMoMoWallet"
    # pass empty value if your merchant does not have stores else merchantName=[storeName]; merchantId=[storeId] to identify a transaction map with a physical store
    extraData = "merchantName=;merchantId="

    # before sign HMAC SHA256 with format
    # partnerCode=$partnerCode&accessKey=$accessKey&requestId=$requestId&amount=$amount&orderId=$oderId&orderInfo=$orderInfo&returnUrl=$returnUrl&notifyUrl=$notifyUrl&extraData=$extraData
    rawSignature = "partnerCode="+partnerCode+"&accessKey="+accessKey+"&requestId="+requestId+"&amount="+amount + \
        "&orderId="+orderId+"&orderInfo="+orderInfo+"&returnUrl=" + \
        returnUrl+"&notifyUrl="+notifyurl+"&extraData="+extraData

    # puts raw signature
    print("--------------------RAW SIGNATURE----------------")
    print(rawSignature)
    # signature
    h = hmac.new(serectkey, rawSignature, hashlib.sha256)
    signature = h.hexdigest()
    print("--------------------SIGNATURE----------------")
    print(signature)

    # json object send to MoMo endpoint

    data = {
        'partnerCode': partnerCode,
        'accessKey': accessKey,
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'returnUrl': returnUrl,
        'notifyUrl': notifyurl,
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature
    }
    print("--------------------JSON REQUEST----------------\n")
    data = json.dumps(data)
    print(data)

    clen = len(data)
    headers = {'Content-Type': 'application/json', 'Content-Length': clen}
    request = urllib.Request(endpoint, data, headers)
    f = urllib.urlopen(request)
    response = f.read()
    f.close()

    print("--------------------JSON response----------------\n")
    print(response+"\n")

    print("payUrl\n")
    print(json.loads(response)['payUrl']+"\n")
    return json.loads(response)['payUrl']
