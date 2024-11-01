import time
import json
import random
from urllib.parse import urlparse, parse_qs
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import requests


def get_public_key(pwd):
    public_key = '0725@pwdorgopenp'
    pwd_val = pwd  # You may replace this with your input mechanism
    # PKCS7 Padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(pwd_val.encode('utf-8')) + padder.finalize()

    cipher = Cipher(
        algorithms.AES(public_key.encode('utf-8')),
        modes.ECB(),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    encrypted_pwd = encryptor.update(padded_data) + encryptor.finalize()
    encrypted_pwd_base64 = base64.b64encode(encrypted_pwd).decode('utf-8')
    return encrypted_pwd_base64


def get_tokenKey(userName, pwd):
    # 请求头信息
    headers = {
        'Host': 'org.xjtu.edu.cn',
        'Proxy-Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'http://org.xjtu.edu.cn',
        'Referer': 'http://org.xjtu.edu.cn/openplatform/login.html',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': 'cur_appId_=kUO8wVrniFw=;',
    }

    # 请求数据
    data = {
        'loginType': 1,
        'username': userName,
        'pwd': get_public_key(pwd),
        'jcaptchaCode': ''
    }

    # 发送 POST 请求
    url = 'http://org.xjtu.edu.cn/openplatform/g/admin/login'
    response = requests.post(url, json=data, headers=headers, verify=False)

    # 使用loads函数将字符串转换为JSON对象
    result = json.loads(response.text)
    return result['data']['tokenKey']


def getOriginUrl(userName, pwd):
    tokenKey = get_tokenKey(userName, pwd)
    # 获取当前时间戳（秒级别）
    current_timestamp_seconds = time.time()
    # 将秒级别时间戳转换为毫秒级别
    current_timestamp_milliseconds = int(current_timestamp_seconds * 1000)

    # 尾部拼接了一个毫秒时间戳
    url = 'http://org.xjtu.edu.cn/openplatform/oauth/auth/getRedirectUrl?userType=1&personNo='+ userName +'&_=' + str(
        current_timestamp_milliseconds)
    headers = {
        'Host': 'org.xjtu.edu.cn',
        'Proxy-Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.36',
        'Content-Type': 'application/json;charset=utf-8',
        'Referer': 'http://org.xjtu.edu.cn/openplatform/login.html',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': 'state=xjdCas; memberId=879790; usertypekey=1; employeenokey=' + userName +'; cur_appId_=N43pA2kWCxo=; open_Platform_User=' + tokenKey,
    }

    # 发送 GET 请求
    response = requests.get(url, headers=headers, verify=False)

    # 使用loads函数将字符串转换为JSON对象
    result = json.loads(response.text)
    return result['data']


def getToken(userName, pwd):
    originUrl = getOriginUrl(userName, pwd)
    # 使用 urlparse 获取 URL 中的查询参数部分
    parsed_url = urlparse(originUrl)
    query_params = parse_qs(parsed_url.query)

    # 提取需要的参数
    user_type = query_params.get('userType', [None])[0]
    code = query_params.get('code', [None])[0]
    employee_no = query_params.get('employeeNo', [None])[0]

    url = 'https://ipahw.xjtu.edu.cn/szjy-boot/sso/codeLogin'
    params = {
        'userType': user_type,
        'code': code,
        'employeeNo': employee_no
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.36',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'content-type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://ipahw.xjtu.edu.cn/sso/callback?code=' + code + '&state=1234&' + 'userType=' + user_type + '&employeeNo=' + employee_no,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }

    response = requests.get(url, params=params, headers=headers, verify=False)
    # 使用loads函数将字符串转换为JSON对象
    result = json.loads(response.text)
    return result['data']['token']


# 随机经纬度
def changeLongitudeLatitude(original_longitude, original_latitude):
    # 生成随机数，范围为[-0.5, 0.5]
    random_adjustment_longitude = random.uniform(-0.0005, 0.0005)
    random_adjustment_latitude = random.uniform(-0.0005, 0.0005)

    # 调整后的经纬度值
    adjusted_longitude = original_longitude + random_adjustment_longitude
    adjusted_latitude = original_latitude + random_adjustment_latitude

    return adjusted_longitude, adjusted_latitude
