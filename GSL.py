import requests
import hashlib,json

class GuangSuLian:

    def __init__(self):
        self.loginInfo = {}     #账号密码
        self.userInfo = {}      #用户信息
        self.orderInfo = {}     #购买信息
        self.speedInfo = {}     #提速的项目信息
        self.speedResult = {}   #提速结果信息
        self.stateCode = 'true' # 该网站提速状态码是字符串,不是布朗值
        # self.login_code=0
        # self.Authorization=''
        self.login_url = 'https://www.fangyb.com:2039/biz/user/login.do'
        self.exitLogin_url = 'https://www.fangyb.com:2039/biz/user/exitLogin.action'
        # self.state_url = 'https://www.fangyb.com:2039/biz/common/stateSvc.do'
        self.myOrder_url = 'https://www.fangyb.com:2039/biz/common/myOrder.action'
        self.openSpeed_url = 'https://www.fangyb.com:2039/biz/common/openSpeed.action'
        self.closeSpeed_url = 'https://www.fangyb.com:2039/biz/common/closeSpeed.action'
        self.speedQuery_url = 'https://www.fangyb.com:2039/biz/common/speedQuery.do'
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'DNT': '1',
            'Host': 'www.fangyb.com:2039',
            'Origin': 'http://www.fangyb.com',
            'Referer': 'http://www.fangyb.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64'
        }

    def set_info(self):
        username = input('请输入用户名：')
        password = input('请输入密码：')
        self.loginInfo ['userName'] = username
        self.loginInfo['userPassword'] = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
        self.userInfo['userName'] = username
        self.speedInfo['userName'] = username

    def login(self):
        login_response = requests.post(url=self.login_url, headers=self.headers, json=self.loginInfo)
        login_code = login_response.json()['code']
        Authorization = login_response.json()['data']
        return login_code, Authorization

    def exitLogin(self):
        requests.post(url=self.exitLogin_url, headers=self.headers, json=self.userInfo)

    def getOrderInfo(self):
        myOrderInfo = requests.post(url=self.myOrder_url, headers=self.headers, json=self.userInfo)
        self.orderInfo = myOrderInfo.json()
        self.stateCode = self.orderInfo['data']['statusCode']
        self.speedInfo['className'] = self.orderInfo['data']['orderDetail']['list'][0]['className']
        self.speedInfo['orderId'] = self.orderInfo['data']['orderDetail']['list'][0]['orderId']
    def openSpeed(self):
        requests.post(url=self.openSpeed_url, headers=self.headers, json=self.speedInfo)

    def closeSpeed(self):
        requests.post(url=self.closeSpeed_url, headers=self.headers, json=self.speedInfo)

    def getSpeedQuery(self):
        #请求两次原因：有时候需要用浏览器登录，比如续费,账户未正常退出等，这样第一次请求可能返回“您的账号已在其它地方登陆”，不会出现提速结果
        #为了方便，就不做判断，直接请求两次
        requests.post(url=self.speedQuery_url, headers=self.headers, json=self.userInfo)
        speedQueryResponse = requests.post(url=self.speedQuery_url, headers=self.headers, json=self.userInfo)
        self.speedResult = speedQueryResponse.json()

if __name__=="__main__":
    gsl = GuangSuLian()
    while True:
        gsl.set_info()
        login_code, Authorization = gsl.login()
        if 0 == login_code:
            print('登录成功')
            gsl.headers['Authorization'] = Authorization
            break
        elif 12 == login_code:
            print('用户名或密码不正确,请重试')
            continue
        elif 11 == login_code:
            print('未注册，请检查手机号是否正确或前往注册后再运行程序')
            a = input('是否重新输入(y/Y)，键入其他则退出程序：')
            if 'y' == a or 'Y' == a:
                continue
            else:
                exit(0)
        else:
            print('登录失败，请重试')
            continue
        
    gsl.getOrderInfo()
    print('购买日期：' + gsl.orderInfo['data']['orderDetail']['list'][0]['orderDateStr'])
    print('失效日期：' + gsl.orderInfo['data']['orderDetail']['list'][0]['validDateStr'])
    if 'true' == gsl.stateCode:
        print('提速状态：提速中')
        gsl.getSpeedQuery()
        print('结束时间：' + gsl.speedResult['data']['endTime'])
        a = input('是否重新提速(y/Y)，键入其他则退出登录并结束程序：')
        if 'y' == a or 'Y' == a:
            gsl.closeSpeed()
            print('提速已关闭，正在重新开始提速')
            gsl.openSpeed()
            gsl.getSpeedQuery()
            speedResultCode = gsl.speedResult['data']['statusCode']
            if 'true' == speedResultCode:
                print('提速状态：提速成功')
                print('开始时间： ' + gsl.speedResult['data']['beginTime'] + '\n' + '结束时间： ' +
                      gsl.speedResult['data']['endTime'])
                print('用户省份： ' + gsl.speedResult['data']['province'])
                print('运营商  ： 中国' + gsl.speedResult['data']['operator'])
                print('IP地址  ： ' + gsl.speedResult['data']['ip'])
                print('提速说明： ' + gsl.speedResult['data']['speedDesc'])
            else:
                print('提速失败，请检查账户是否到期，账号即将登出并退出程序')
                gsl.exitLogin()
                exit(-1)
        else:
            gsl.exitLogin()
            exit(0)

    else:
        print('提速状态：未提速\n正在开始提速')
        gsl.openSpeed()
        gsl.getSpeedQuery()
        speedResultCode = gsl.speedResult['data']['statusCode']
        if 'true' == speedResultCode:
            print('提速状态：提速成功')
            print('开始时间： ' + gsl.speedResult['data']['beginTime'] + '\n' + '结束时间： ' +
                  gsl.speedResult['data']['endTime'])
            print('用户省份： ' + gsl.speedResult['data']['province'])
            print('运营商：  中国' + gsl.speedResult['data']['operator'])
            print('IP地址：  ' + gsl.speedResult['data']['ip'])
            print('提速说明：' + gsl.speedResult['data']['speedDesc'])
        else:
            print('提速失败，请检查账户是否到期，账号即将登出并结束程序')
            gsl.exitLogin()
            exit(-1)

    print('账号即将登出并结束程序')
    gsl.exitLogin()
    exit(0)

