import datetime
import random
import time
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import config
from tqdm import tqdm
from other import *
import warnings
import urllib3

# 忽略InsecureRequestWarning
warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)
credentials = {
    "3123108013": "20010628.jyh",
    "3123108043": "Tsg521189",
    "3122303038": "xp615719",
    "3123108112": "Ghgh5656@",
    "3123354008": "asd1231236666",
    "4124197010": "WSS9408051.",
    "3124108068": "910159zheng",
    # 可以继续添加其他学号和密码
}


def sign_in(userName, pwd, token):
    # 请求头信息
    headers = {
        'Host': 'ipahw.xjtu.edu.cn',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; 23116PN5BC Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 toon/2122313098 toonType/150 toonVersion/6.3.0 toongine/1.0.12 toongineBuild/12 platform/android language/zh skin/white fontIndex/0',
        # 必须存在
        'token': token,
        'Accept': '*/*',
        'Origin': 'https://ipahw.xjtu.edu.cn',
        'X-Requested-With': 'synjones.commerce.xjtu',
        'Referer': 'https://ipahw.xjtu.edu.cn/pages/index/hdgl/hdgl_run?courseType=7&signType=1&activityAddress=&courseInfoId=1828599707263381506',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    # POST请求的数据
    post_data = {
        "sportType": 2,
        "longitude": str(config.original_longitude),
        "latitude": str(config.original_latitude),
        "courseInfoId": "1828599707263381506"
    }

    # 目标URL
    url = 'https://ipahw.xjtu.edu.cn/szjy-boot/api/v1/sportActa/signRun'

    # 发送POST请求
    response = requests.post(url, json=post_data, headers=headers, verify=False)

    # 使用loads函数将字符串转换为JSON对象
    result = json.loads(response.text)
    while result['msg'] == "距离最近的指定运动地点超过100m，无法打卡":
        config.original_longitude, config.original_latitude = changeLongitudeLatitude(config.original_longitude, config.original_latitude)
        # POST请求的数据
        post_data = {
            "sportType": 2,
            "longitude": str(config.original_longitude),
            "latitude": str(config.original_latitude),
            "courseInfoId": "1828599707263381506"
        }
        # 发送POST请求
        response = requests.post(url, json=post_data, headers=headers, verify=False)
        # 使用loads函数将字符串转换为JSON对象
        result = json.loads(response.text)

    # 打印响应内容
    print(response.text)
    return result['msg']


def sign_out(userName, pwd, token):
    # 请求头信息
    headers = {
        'Host': 'ipahw.xjtu.edu.cn',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; 23116PN5BC Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 toon/2122313098 toonType/150 toonVersion/6.3.0 toongine/1.0.12 toongineBuild/12 platform/android language/zh skin/white fontIndex/0',
        'token': token,
        'Accept': '*/*',
        'Origin': 'https://ipahw.xjtu.edu.cn',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://ipahw.xjtu.edu.cn/pages/index/hdgl/hdgl_run?courseType=7&signType=1&activityAddress=&courseInfoId=1828599707263381506',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }

    # POST请求的数据
    post_data = {
        "longitude": str(config.original_longitude),
        "latitude": str(config.original_latitude),
    }

    # 目标URL
    url = 'https://ipahw.xjtu.edu.cn/szjy-boot/api/v1/sportActa/signOutTrain'

    # 发送POST请求
    response = requests.post(url, json=post_data, headers=headers, verify=False)

    # 打印响应内容
    print(response.text)
    return json.loads(response.text)['msg']


def print_now_time():
    # 获取当前时间
    current_time = datetime.datetime.now()

    # 格式化并打印当前时间
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print("当前时间:", formatted_time)


def send_success_email(subject, message):
    sender_email = '1905955545@qq.com'  # 发件人邮箱
    sender_password = 'aikyancbnkmmbdec'  # 发件人邮箱授权码
    recipient_email = 'yuhaoji2001@163.com'  # 收件人邮箱

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()


if __name__ == "__main__":
    while True:
        try:
            # 所有的学生账号
            userNameli = list(credentials.keys())
            random.shuffle(userNameli)  # 随机打乱顺序

            successful_sign_in_users = []
            successful_sign_out_users = []

            # 先签退排除故障
            for userName in userNameli:
                pwd = credentials[userName]
                token = getToken(userName, pwd)
                sign_out(userName, pwd, token)

            time.sleep(random.randint(1, 3))  # 随机等待1到3秒

            # 签到
            for userName in userNameli:
                pwd = credentials[userName]
                token = getToken(userName, pwd)
                sign_in_msg = sign_in(userName, pwd, token)
                # 获取当前脚本所在目录，并设置文件路径
                current_directory = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_directory, 'successful_sign_in.txt')
                if "成功" in sign_in_msg:
                    successful_sign_in_users.append(userName + ": " + sign_in_msg)
                    with open(file_path, 'a') as file:  # 'a'模式表示追加到文件末尾
                        file.write(userName + "-" + str(datetime.datetime.now()) + '-signin\n')
                time.sleep(random.randint(1, 3))  # 随机等待1到3秒
            with open(file_path, 'a') as file:  # 'a'模式表示追加到文件末尾
                        file.write('\n')
            # 生成一个的随机休眠时间（以秒为单位） 锻炼
            random_sleep_time = random.randint(1805, 2189)
            # random_sleep_time = random.randint(1, 3)
            # 发送签到成功邮件
            if successful_sign_in_users:
                successful_sign_in_users.append('此次打卡时间最少有' + str(random_sleep_time) + '秒')
                subject = "打卡签到成功信息"
                message = "\n".join(map(str, successful_sign_in_users))
                send_success_email(subject, message)
                # print(message)
            print("-----------------------锻炼中-----------------------")
            # 进度条
            for _ in tqdm(range(random_sleep_time), desc="锻炼中", unit="秒"):
                time.sleep(1)
            print("-----------------------签退-----------------------")

            # 签退
            random.shuffle(userNameli)  # 随机打乱顺序
            for userName in userNameli:
                pwd = credentials[userName]
                token = getToken(userName, pwd)
                sign_out_msg = sign_out(userName, pwd, token)
                # 存储在这个文件夹下
                # 获取当前脚本所在目录，并设置文件路径
                current_directory = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_directory, 'successful_sign_out.txt')
                if "成功" in sign_out_msg and '请勿重复签退' not in sign_out_msg:
                    successful_sign_out_users.append(userName + ": " + sign_out_msg)
                    with open(file_path, 'a') as file:  # 'a'模式表示追加到文件末尾
                        file.write(userName + "-" + str(datetime.datetime.now()) + '-signout\n')
                time.sleep(random.randint(1, 3))  # 随机等待1到3秒
            with open(file_path, 'a') as file:  # 'a'模式表示追加到文件末尾
                        file.write('\n')

            # 发送签退成功邮件
            if successful_sign_out_users:
                successful_sign_out_users.append('此次打卡时间最少有' + str(random_sleep_time) + '秒')
                subject = "打卡签退成功信息"
                message = "\n".join(map(str, successful_sign_out_users))
                send_success_email(subject, message)
                # print(message)
            
            # 程序成功执行完毕，退出循环
            break

        except requests.exceptions.RequestException as e:
            print("网络连接出错: ", e)


        except Exception as e:
            # 捕获其他未预料的错误，打印错误信息以便调试
            print("发生未知错误: ", e)

        # 等待一段时间后重试，以避免频繁的请求失败
        time.sleep(10)
