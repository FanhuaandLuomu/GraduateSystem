#coding:utf-8
# 无聊写了一个简易的模拟浏览器登录学校学生管理系统的爬虫
# 实现登录并爬取学生成绩的功能。
# author:yinhao
# date:2017/2/12
# email:1049755192@qq.com
# 运行:python spiderManageSystem.py
import urllib2
import cookielib
import urllib
import re
import getpass
import msvcrt
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 考虑安全性和操作习惯 密码输入
def pwd_input():    
	print 'password:',
	chars=[]
	while True:
		try:
			newChar=msvcrt.getch().decode('utf-8')
		except:
			print u'你可能不是在cmd下运行，密码将不会被隐藏.'
			return raw_input('password:')
		if newChar in '\r\n':
			break
		elif newChar=='\b':
			if chars:
				del chars[-1]
				msvcrt.putch('\b'.encode('utf-8'))  # 光标回退一格
				msvcrt.putch(' '.encode('utf-8'))   # 输出空格覆盖
				msvcrt.putch('\b'.encode('utf-8'))  # 光标回退
		else:
			chars.append(newChar)
			msvcrt.putch('*'.encode('utf-8'))  # 显示星号
	return ''.join(chars)

def login(username,password,opener,postUrl,headers):
	# 根据抓包信息 构造表单  
	postData={
		'__EVENTTARGET':'',
		'__EVENTARGUMENT':'',
		'__VIEWSTATE':'/wEPDwUKMTIzNjIzMDUzNmQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgIFEl9jdGwwOkltYWdlQnV0dG9uMQUSX2N0bDA6SW1hZ2VCdXR0b24y+4I4fY+7OPulH8kpYcREU2J8X+dWlJ4KKu1MLBKEtxQ=',
		'_VIEWSTATEGENERATOR':'D40EB50E',
		'__EVENTVALIDATION':'/wEWCQK5jM69AwLN+daWBQL3o8v7DQL3o7/7DQKFr86aBAKqwYRUAqvBhFQCqMGEVAKpwYRU8kml4VCM2AKVxgikMEDJJHlqh53t3II8SGkrRmLp4wQ=',
		'_ctl0:txtusername':username,
		'_ctl0:ImageButton1.x':'20',
		'_ctl0:ImageButton1.y':'32',
		'_ctl0:txtpassword':password,
		'_ctl0:drplx':'4'
	}
	# 生成post数据 ?key1=value1&key2=value2的形式 
	data=urllib.urlencode(postData)
	# 构造request请求  
	request=urllib2.Request(postUrl,data,headers)

	try:
		response=opener.open(request)
		result=response.read()
		print u'\n---登录成功!---\n'
	except urllib2.HTTPError,e:
		print e.code,e
	except Exception,e:
		print e

def getInfo(xscjUrl,opener,headers):
	# 使用opener打开目标url  成绩页面
	response=opener.open(urllib2.Request(xscjUrl,headers=headers))
	result=response.read()
	# 使用etree解析html
	page=etree.HTML(result.decode('utf-8'))
	sid=page.xpath(u'//*[@id="lblxh"]')   # 学号
	if sid==None or len(sid)==0:
		return
	print u'学号:',sid[0].text
	name=page.xpath(u'//*[@id="lblxm"]')  # 姓名
	if name==None or len(name)==0:
		return
	print u'姓名:',name[0].text

	#成绩列表
	trList=page.xpath(u'//table[@class="GridBackColor"]/tr[not(@class)]')
	scoreList=[]
	for item in trList:
		tdList=item.xpath(u'td')
		if len(tdList)==4:
			scoreList.append([tdList[0].text,tdList[1].text,tdList[2].text,tdList[3].text])
		else:
			print u'成绩列表出错...'
			return
	return scoreList


def main():
	# 将cookies绑定到一个opener cookie由cookielib自动管理 
	cookie=cookielib.CookieJar()
	handler=urllib2.HTTPCookieProcessor(cookie)
	opener=urllib2.build_opener(handler)

	# 模拟浏览器 headers
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36", 
	}
	# 登录 post地址
	postUrl='http://42.244.6.101/gmis/login.aspx'

	# username='20155227031'
	# password='xxxxx'
	username=raw_input('username:')
	# 考虑密码安全性
	# password=getpass.getpass('password:')
	password=pwd_input()

	# 登录系统
	login(username.strip(),password.strip(),opener,postUrl,headers)

	# 成绩页面的地址
	xscjUrl='http://42.244.6.101/pyxx/grgl/xskccjcx.aspx'
	average=0  # 平均分
	try:
		scoreList=getInfo(xscjUrl,opener,headers)
		print u'共有%d门课程，成绩如下(课程 学分 选修学期 成绩):' %len(scoreList)
		for item in scoreList:
			print '%s %s %s %s' %(item[0],item[1],item[2],item[3])
			average+=int(item[3])
		average=float(average)/len(scoreList)
		print u'%d门课程平均分:' %len(scoreList),average
	except Exception,e:
		print e

if __name__ == '__main__':
	main()