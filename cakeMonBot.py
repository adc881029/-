from ast import NotIn
import sqlite3
import os
import pygsheets
from datetime import datetime, timedelta
import json
import socket
import random
import requests 
import re
import json
import urllib.request
import chardet 
from plurk_oauth import PlurkAPI
import time



#plurkAPI
plurk = PlurkAPI('', '')
plurk.authorize('', '')

#getPlurks
now = (datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%S")
print(now)
lastTime=""

#userdata
gc = pygsheets.authorize(service_file='./creds.json')
survey_url = ''
sh = gc.open_by_url(survey_url)
userData=sh.worksheet('title','UserData')

#behavior
behaviorData=sh.worksheet('title','Behavior2')
behaviorList=behaviorData.get_col(1,include_tailing_empty=False)

#frendList
friend={}
friend_id_list=[]
friend_nickname_list=[]

#cakemonData
cakemonData=sh.worksheet('title','CakemonData')
n=cakemonData.get_col(1,include_tailing_empty=False)#蛋糕獸名字
del n[0]
w=cakemonData.get_col(2,include_tailing_empty=False)#蛋糕獸權重
del w[0]
weight=[]
#權重轉為數字
for i in w:
    weight.append(float(i))
c=cakemonData.get_col(3,include_tailing_empty=False)#蛋糕獸表符代碼
del c[0]

def printswitch(pid,string):
    try:
        #mod 0 
        mod=1
        if mod==0:
            print(string)
        else:
            plurkResponse(pid,str(string))
    except Exception as e:
        print("[err]printswitch:")
        print(e)
def setFriendList():
    try:
        data = plurk.callAPI('/APP/FriendsFans/getCompletion')
        #data=plurk.callAPI('/APP/FriendsFans/getFriendsByOffset',{'user_id':'','limit':99999})
        time.sleep(0.1)
        friend.clear()
        friend_id_list.clear()#清空好友id
        friend_nickname_list.clear()#清空好友暱稱
        friend_number = int(plurk.callAPI('/APP/Profile/getOwnProfile').get('friends_count'))
        nowFriendNum=len(friend_id_list)
        while(nowFriendNum<friend_number):
            nowFriendNum=len(friend_id_list)
            friend_number = int(plurk.callAPI('/APP/Profile/getOwnProfile').get('friends_count'))
            data=plurk.callAPI('/APP/FriendsFans/getFriendsByOffset',{'user_id':,'limit': 100,'offset':(nowFriendNum)})
            if len(data)==0:
                break
            for user in data:
                friend_id_list.append(user['id'])
                friend_nickname_list.append(user['nick_name'])
                friend[str(user['id'])]=user['nick_name']
        gc = pygsheets.authorize(service_file='./creds.json')
        survey_url = 'https://docs.google.com/spreadsheets/d/1QwnPezCF8T_TJgY9C0vTa_lykLgXF2Y-WEYPISwRZkA/'
        sh = gc.open_by_url(survey_url)
        userData=sh.worksheet('title','UserDataTest')
        userID=userData.get_col(1,include_tailing_empty=False)

        user_nickname_list=[]
        print(len(userID))
        for ID in userID:
            try:
                #print(str(ID)+" : "+str(friend[str(ID)]))
                user_nickname_list.append(friend[str(ID)])
            except:
                print("can't find user:"+str(ID))
                user_nickname_list.append('nickname')
        userData.update_col(2, values=[user_nickname_list], row_offset=0)#紀錄好友
    except Exception as e:
        print("[err]setFriendList:")
        print(e)
    

def plurkResponse(pid,content):
    plurk.callAPI('/APP/Responses/responseAdd', {'plurk_id': pid,'content': content, 'qualifier': ':'})        

def getCakemon(pid,times,user_id,user_nickname):
    userNameList=userData.get_col(1,include_tailing_empty=False)#已知使用者名字
    try:
        userPlace=userNameList.index(str(user_id))#回傳位置
        print('find user')
    except:
        #新使用者
        try:
            userPlace= len(userNameList)#回傳最新一列
            userData.add_rows(0)
            namelist=[str(user_id),'',str(0)]
            userData.update_row(userPlace+1, values=[namelist], col_offset=0)        
        except:
            print("新使用者"+str(user_id)+"無法加入")
            printswitch(pid, "無法登錄新使用者，若持續收到此訊息請再通知管理員處理")

                
    '''以上是找到userPlace'''
    now=datetime.now()
    today=now.strftime("%d/%m/%Y")
    have=userData.get_row(userPlace+1,include_tailing_empty=False)
    if(have[2]==today and user_id!=14722035):
        print('今天'+have[0]+'已經抽過')
        printswitch(pid, "您今天已經抓過蛋糕獸囉！請等到明天早上8點再回來吧~")
        return
    
    
    get=''
    text='您今天抓到了 '
    getlist=[]
    getID=range(len(n))
    for i in range(times):
        new=random.choices(getID, weight)
        get=get+c[new[0]]+' '
        text=text+n[new[0]]+' '
        getlist.append(str(new[0]))
    get=get+'\n'+text
    get = user_nickname +get
    printswitch(pid, get)

    
    print(have)
    del have[0]#去掉ID
    del have[0]#去掉nickname
    if(len(have)>=1):
        del have[0]#去掉時間
    for new in getlist:
        have.append(new)
    have=list(set(have))
    have.sort()
    have.insert(0,today)
    userData.update_row(userPlace+1, values=have, col_offset=2)#紀錄蛋糕獸

def showCakemon(pid,user_id,user_nickname):
    try:
        userNameList=userData.get_col(1,include_tailing_empty=False)#已知使用者名字
        '''以上是使用者表單'''
        try:
            userPlace=userNameList.index(str(user_id))#回傳位置
            print('find user')
        except:
            printswitch(pid, "您還沒有任何蛋糕獸哦，使用抓蛋糕獸指令來獲得蛋糕獸吧！")
            return
        have=userData.get_row(userPlace+1,include_tailing_empty=False)
        del have[0]#去掉ID
        del have[0]#去掉nickname
        if(len(have)>=1):
            del have[0]#去掉時間
        random.shuffle(behaviorList)
        behavior=behaviorList[0]
        while(behavior.find("@")!=-1):
            Cakemon = (random.choice(have))
            Cakemon=c[int(Cakemon)] + n[int(Cakemon)]
            behavior=behavior.replace("@",Cakemon,1)
        behavior = user_nickname + behavior  
        printswitch(pid, behavior)
    except Exception as e:
        print("[err]showCakemon:")
        print(e)

def showCollect(pid,user_id,user_nickname):
    userNameList=userData.get_col(1,include_tailing_empty=False)#已知使用者名字
    try:
        userPlace=userNameList.index(str(user_id))#回傳位置
        print('find user')
    except:
        printswitch(pid, "您還沒有任何蛋糕獸哦，使用抓蛋糕獸指令來獲得蛋糕獸吧！")
        return
    have=userData.get_row(userPlace+1,include_tailing_empty=False)
    del have[0]#去掉ID
    del have[0]#去掉nickname
    if(len(have)>=1):
        del have[0]#去掉時間
    get_number = len(have)
    cakemon_number=len(c)
    content = ''
    for cakemon_id in have:
        cakemon = c[int(cakemon_id)]
        content = content + cakemon
    content = user_nickname + '蒐集進度：'+ str(get_number) +'/'+ str(cakemon_number) + content
    printswitch(pid, content)
def dealcontent(pid,user_id,content,user_nickname):
    #print("deal content start")
    '''
    if user_id not in testers :
        return
    '''
    if content.find("stoptest") != -1:
        os._exit(0) 
        print("stop")
    if content.find("抓蛋糕獸") != -1:
        getCakemon(pid,getTimes,user_id,user_nickname) 
        print("收到"+user_nickname+"的抓蛋糕獸要求")       
    if content.find("蛋糕獸出來玩") != -1:
        showCakemon(pid,user_id,user_nickname)
        print("收到"+user_nickname+"的蛋糕獸出來玩要求")
    if content.find("蛋糕獸圖鑑") != -1:
        showCollect(pid,user_id,user_nickname)
        print("收到"+user_nickname+"的蛋糕獸圖鑑要求")    
    #print("deal content end")    
def findTargetResponse(res_list, res_id):
    print("find Target response start")
    for res in res_list:
        if res['id'] == res_id:
            return res['content_raw']
    print("find target response end")
    return "not found"
def getPlurks():
    global lastTime
    global now
    #print("offset now : ",now)
    data = plurk.callAPI('/APP/Polling/getPlurks',{'offset':now,'limit':100})
    if not data:
        return
    if not data['plurks']:
        return
    lastTime=data['plurks'][0]['posted']
    for p in data['plurks']:
        #print(p['content_raw'])
        print(p['posted'])
        dealcontent(p['plurk_id'],p['owner_id'],p['content_raw'],"")
    if lastTime!="":
        print("lastTTime : ",lastTime)
        now=(datetime.strptime(lastTime, "%a, %d %b %Y %H:%M:%S %Z")+timedelta(seconds = 1)).strftime("%Y-%m-%dT%H:%M:%S")
        print("now : ",now)
        lastTime=""
def responseMentioned():
    try:
        plurks = plurk.callAPI('/APP/Alerts/getActive')
        if plurks is not None:
            for pu in plurks:
                if pu is not None:
                    if pu['type'] == "mentioned":
                        #print(pu)
                        user_id=pu['from_user']['id']
                        user_nickname=pu['from_user']['nick_name']
                        user_nickname = '@'+str(user_nickname)+':'
                        res_id = pu['response_id']
                        pid = pu['plurk_id']
                        res_json = plurk.callAPI('/APP/Responses/get', {'plurk_id': pid})
                        if res_json is None:
                            pass
                        else:
                            res_list = res_json['responses']
                            content = findTargetResponse(res_list, res_id)
                            print(str(pid)+" "+str(user_id)+" "+str(content))
                            dealcontent(pid,user_id,content, user_nickname)
    
    except Exception as e:
        print("[err]responseMetioned:")
        print(e)

def dateCheck():
    #日期測試
    global getTimes
    present = datetime.now()
    print(present)
    if (datetime(2022,7,15) <= present):
        getTimes =4
        print('get times =' + str(getTimes))
    else:
        getTimes =3


#setFriendList()

print('bot start')
getTimes =3


while True:
    #plurk.callAPI('/APP/Alerts/addAllAsFriends')
    plurk.callAPI('/APP/Alerts/addAllAsFriends')
    getPlurks()
    responseMentioned()
    time.sleep(3)

#print(owns)