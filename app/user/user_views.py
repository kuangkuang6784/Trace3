from __future__ import unicode_literals
from django.shortcuts import HttpResponse, render, redirect
from app import models
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.template import Context
# from django.utils import simplejson
from django.core import serializers
import json
import datetime
from OpenSSL.crypto import PKey
from OpenSSL.crypto import TYPE_RSA, FILETYPE_PEM
from OpenSSL.crypto import dump_privatekey, dump_publickey
# Create your views here.


'''
加入新功能




'''

'''
def register(request):
    characterflag = request.GET.get("characterFlag")
    print(characterflag)
    def producer():
        models.ProducerRegistry(**json.loads(request.body)).save()  # 可以直接存，没传进来的表项数据里默认为空
    def trans():
        models.TransporterRegistry(**json.loads(request.body)).save()  # 可以直接存，没传进来的表项数据里默认为空
    def quaratine():
        models.QuarantineRegistry(**json.loads(request.body)).save()
    def processor():
        models.ProcessorRegistry(**json.loads(request.body)).save()
    def seller():
        models.SellerRegistry(**json.loads(request.body)).save()
    def company():
        models.CompanyRegistry(**json.loads(request.body)).save()
    def consumer():
        models.ConsumerRegistry(**json.loads(request.body)).save()
    switcher={
        "0":producer(),
        "1":trans(),
        "2":quaratine(),
        "3":producer(),
        "4":seller(),
        "5":consumer(),
        "6":company()
    }
    switcher.get(characterflag,"error")()#替代switch/case,Expression is not callable

    return {
        "0":producer(),
        "1":trans(),
        "2":quaratine(),
        "3":producer(),
        "4":seller(),
        "5":consumer(),
        "6":company()
        }.get(characterflag, 'error')  # 'error'为默认返回值，可自设置

    return HttpResponse("注册成功！")
'''


def DateEncoder(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.strftime('%Y-%m-%d')


idcountper = 0  # 反正所有人ID都是从这里来，干脆定义一个全局变量，个人用户的自增id
idcountcom = 0  # 企业的自增id


def register(request):  # 少一个企业的注册
    ContactNo = json.loads(request.body.decode())["ContactNo"]  # 通过电话号码注册
    temp = models.ConsumerRegistry.objects.filter(ContactNo=ContactNo)
    if temp.exists():
        return HttpResponse("该手机号已被注册！")
    characterflag = request.GET.get("CharacterFlag")  # 表明注册的人是个人还是企业,1为个人，0为企业
    import random
    province = str(random.randint(1, 34)).zfill(2)
    if characterflag == "1":
        global idcountper
        ID = province + str(idcountper).zfill(8)
        idcountper += 1
        models.ConsumerRegistry(**json.loads(request.body), ConsumerId=ID).save()
        print(request.body)
        dict_ = {
            "ConsumerId": ID,
        }
        return HttpResponse(json.dumps(dict_, ensure_ascii=False),
                            content_type="application/json")

    else:
        global idcountcom
        ID = province + str(idcountcom).zfill(5)
        idcountcom += 1
        models.CompanyRegistry(**json.loads(request.body), CompanyId=ID).save()
        dict_ = {
            "CompanyId": ID,
        }
        return HttpResponse(json.dumps(dict_, ensure_ascii=False),
                            content_type="application/json")


def login(request):  ##登陆注册之后返回企业名称，经营地址，还有个人全部信息！！！！！！！！！！包括角色属性
    characterflag = request.GET.get("CharacterFlag")  # 表明登陆的人是个人还是企业
    if characterflag == "1":  # 个人
        ContactNo = json.loads(request.body.decode())["ContactNo"]  # 通过电话号码登录
        Password = json.loads(request.body.decode())["Password"]
        aaa = models.ConsumerRegistry.objects.filter(ContactNo=ContactNo)
        if (aaa.count() == 0):
            return HttpResponse("该用户不存在！")
        else:
            temp = aaa.first()
            if Password != temp.Password:
                return HttpResponse("密码不正确！")
            else:
                temp.__dict__.pop("_state")
                temp.__dict__.pop("Password")
                dict_ = {
                    "ConsumerId": temp.ConsumerId,
                    "CharacterFlag": temp.CharacterFlag,
                }
                temp.__dict__.update(dict_)
                return HttpResponse(json.dumps(temp.__dict__, ensure_ascii=False, default=DateEncoder),
                                    content_type="application/json")
    else:  # 跟上面一样的，企业
        CorporateContactNo = json.loads(request.body.decode())["CorporateContactNo"]
        Password = json.loads(request.body.decode())["Password"]
        aaa = models.ConsumerRegistry.objects.filter(CorporateContactNo=CorporateContactNo)
        if (aaa.count() == 0):
            return HttpResponse("该用户不存在！")
        else:
            temp = aaa.first()
            if Password != temp.Password:
                return HttpResponse("密码不正确！")
            else:
                temp.__dict__.pop("_state")
                temp.__dict__.pop("Password")
                dict_ = {
                    "CompanyId": temp.CompanyId,
                }
                temp.__dict__.update(dict_)
                return HttpResponse(json.dumps(temp.__dict__, ensure_ascii=False, default=DateEncoder),
                                    content_type="application/json")


def fulfil(request):  # 个人信息完善函数,这个函数也要返回完善过后的所有信息的！！
    # characterflag = request.POST.get("CharacterFlag")#表明要完善哪个角色
    # ConsumerId = request.POST.get("ConsumerId")
    # imgID=request.FILES.get("imgID")
    # imgwork = request.FILES.get("imgwork")
    characterflag = request.GET.get("CharacterFlag")  # 表明要完善哪个角色
    # 0为生产者；1为检疫员；2为加工员；3为运输员；4为销售员；5为普通用户
    # 这个时候这个json里是有个人的ID的,因为登陆进去之后我是传了这个人的ID给前端的
    dicttemp = json.loads(request.body.decode())
    print(dicttemp)
    ConsumerId = dicttemp["ConsumerId"]
    dicttemp.pop("ConsumerId")  # 把ConsumerId这个键值对删掉，免得后面重复
    temp = models.ConsumerRegistry.objects.get(ConsumerId=ConsumerId)  # 在消费者表里找到该表项，该人
    #print(temp.__dict__)


    CompanyName = dicttemp["CompanyName"]
    dicttemp.pop("CompanyName")  # 后面注册的时候公司名称是要去掉的

    dic = temp.__dict__
    dic.pop("_state")
    #dic.pop("id")
    dicttemp.update(dic)
    # for key, value in dicttemp.items():
    #     print(key, value)
    # for key,value in temp.__dict__.items():
    #     print(key,value)

    def producer():
        aaa = models.ProducerRegistry.inherit.update(models.ProducerRegistry,CompanyName,**dicttemp)
        if aaa == 0:
            return 0
        else:
            aaa.CharacterFlag |= 0b100000  # 把第一位置1
            aaa.save()


    def quarantine():
        aaa = models.QuarantineRegistry.inherit.update(models.ProducerRegistry, CompanyName, **dicttemp)
        if aaa == 0:
            return 0
        else:
            aaa.CharacterFlag |= 0b010000  # 把第二位置1
            aaa.save()


    def processor():
        aaa = models.ProcessorRegistry.inherit.update(models.ProducerRegistry, CompanyName, **dicttemp)
        if aaa == 0:
            return 0
        else:
            aaa.CharacterFlag |= 0b001000  # 把第三位置1
            aaa.save()


    def trans():
        aaa = models.TransporterRegistry.inherit.update(models.ProducerRegistry, CompanyName, **dicttemp)
        if aaa == 0:
            return 0
        else:
            aaa.CharacterFlag |= 0b000100  # 把第四位置1
            aaa.save()


    def seller():
        aaa = models.SellerRegistry.inherit.update(models.ProducerRegistry, CompanyName, **dicttemp)
        if aaa == 0:
            return 0
        else:
            aaa.CharacterFlag |= 0b000010  # 把第五位置1
            aaa.save()


    if characterflag == "0":
        if producer()==0:
            return HttpResponse("该农场不存在！")
    elif characterflag == "1":
        if quarantine()==0:
            return HttpResponse("该检疫局不存在！")
    elif characterflag == "2":
        if processor()==0:
            return HttpResponse("该加工厂不存在！")
    elif characterflag == "3":
        if trans()==0:
            return HttpResponse("该物流公司不存在！")
    elif characterflag == "4":
        if seller()==0:
            return HttpResponse("该销售点不存在！")
    dict_ = {"ConsumerId": ConsumerId}

    return HttpResponse(json.dumps(dict_, ensure_ascii=False), content_type="application/json")  # 返回ID



def fulfil_img(request):
    #http://127.0.0.1:8000/user/media/images/1.png
    ConsumerId = request.POST.get("ConsumerId")
    characterflag = request.POST.get("CharacterFlag")  # 表明要完善哪个角色
    print(ConsumerId, characterflag)
    imgID = request.FILES.get("imgID")
    imgwork = request.FILES.get("imgwork")

    def producer():
        temp = models.ProducerRegistry.objects.get(ConsumerId=ConsumerId)
        temp.imgID = imgID
        temp.imgwork = imgwork
        temp.save()

    def quarantine():
        imgquality1 = request.FILES.get("imgquality1")
        imgquality2 = request.FILES.get("imgquality2")
        temp = models.QuarantineRegistry.objects.get(ConsumerId=ConsumerId)
        temp.imgID = imgID
        temp.imgwork = imgwork
        temp.imgquality1 = imgquality1
        temp.imgquality2 = imgquality2
        temp.save()

    def processor():
        imgquality = request.FILES.get("imgquality")
        temp = models.ProcessorRegistry.objects.get(ConsumerId=ConsumerId)
        temp.imgID = imgID
        temp.imgwork = imgwork
        temp.imgquality = imgquality
        temp.save()

    def trans():
        imgquality = request.FILES.get("imgquality")
        temp = models.TransporterRegistry.objects.get(ConsumerId=ConsumerId)
        temp.imgID = imgID
        temp.imgwork = imgwork
        temp.imgquality = imgquality
        temp.save()

    def seller():
        temp = models.SellerRegistry.objects.get(ConsumerId=ConsumerId)
        temp.imgID = imgID
        temp.imgwork = imgwork
        temp.save()

    # switcher = {
    #     "0": producer(),
    #     "1": quarantine(),
    #     "2": processor(),
    #     "3": trans(),
    #     "4": seller(),
    # }
    # switcher.get(characterflag, "error")  # 替代switch/case,Expression is not callable
    if characterflag=="0":
        producer()
    elif characterflag=="1":
        quarantine()
    elif characterflag=="2":
        processor()
    elif characterflag=="3":
        trans()
    elif characterflag=="4":
        seller()
    dict_ = {"ConsumerId": ConsumerId}
    return HttpResponse(json.dumps(dict_, ensure_ascii=False), content_type="application/json")  # 返回ID
#消费者-更改
def update(request):
    if request.method=="POST":
        try:
            co = json.loads(request.body)  #获得json
            co_id = co.get("ConsumerId")  #获得id
            temp2 = models.ConsumerRegistry.objects.get(ConsumerId=co_id) #获得对象
            temp2.Password = co.get("Password")
            temp2.ContactNo = co.get("ContactNo")
            temp2.save()
            print("密码修改成功")
            return HttpResponse("密码更改成功")
        except ObjectDoesNotExist:
            return HttpResponse("修改不成功")

#消费者-溯源
def origin(request):
    if request.method == "GET":
        production_id = request.GET.get("ProductionID")  # 获得加工人员的processor_idTrace2@223.3.79.211
#        print("production_id is %s" % (production_id))

        #预处理
        sheep_id_0 = production_id[0:8]
#        print("前8位是 %s" % (sheep_id_0))
        id = ['00000000', '000000', '0000', '00']
#        print(id[0])
#        print(id[1])
#        print(id[2])
#        print(id[3])

        sheep_id = sheep_id_0+''+id[0]
#        print("sheep_id is %s" % (sheep_id))

        isheep_id = production_id[8:17]
#        print(isheep_id)

        print("数据查询开始")

        try:
            ret = []
            #生产表的查询

            # 运输表的查询
            temp2 = models.TransportData.objects.filter(ProductionID=sheep_id, Transport_Flag=30)
            if (temp2):
                for sample2 in temp2:
                    temp_person = models.TransporterRegistry.objects.get(IDNo=sample2.TransactionPersonID)
#                    print("id %s" % (temp_person.ConsumerName))
#                    print(temp_person.ConsumerName)
                    i = model_to_dict(sample2)
                    i.pop("id")
                    i.update({'TransactionPersonID': temp_person.ConsumerName}) #修改
#                    i.update({'b': 2}) #更改
                    ret.append(json.dumps(i, cls=models.DateEncoder, ensure_ascii=False))
                    print("运输表1 有数据")
            else:
                print("运输表1没有数据")


            # 检疫表的查询
            temp3 = models.QuarantineData.objects.filter(ProductionId=sheep_id)
            if (temp3):
                for sample3 in temp3:
                    i = model_to_dict(sample3)
                    i.pop("id")
                    ret.append(json.dumps(i, cls=models.DateEncoder, ensure_ascii=False))
                print("检疫表 有数据")
            else:
                print("检疫表没有数据")

            #检疫到加工
            temp4 = models.TransportData.objects.filter(ProductionID=sheep_id, Transport_Flag=31)
            if (temp4):
                for sample4 in temp4:
                    temp_person = models.TransporterRegistry.objects.get(IDNo=sample4.TransactionPersonID)
                    i = model_to_dict(sample4)
                    i.pop("id")
                    i.update({'TransactionPersonID': temp_person.ConsumerName})  # 修改
                    ret.append(json.dumps(i, cls=models.DateEncoder, ensure_ascii=False))
                    print("运输表2 有数据")
            else:
                print("运输表2没有数据")

            #加工表数据查询
            temp5 = models.ProcessData.objects.get(ReproductionID=production_id)
            if(temp5):
                n = temp5.Step #最大值
                t = n
                stack =[] #创建一个栈
                while t >0:
                    stack.append(t)  #添加元素
                    t = t - 1
#                    print("t: %s" %(t))
#                print("lenth is %s " % (len(stack)))
#                print(stack)
                for j in range(len(stack)):
                    k = stack.pop()
                    if(k < 4):
                        i = 8 + 2 * k
                        #print("k: %s" %(k))
                        #print("j: %s" %(j))
                        #print("i: %s" %(i))
                        serch_id = production_id[0:i] + '' + id[k]
                        print(serch_id)
                        tempp1 = models.ProcessData.objects.get(ReproductionID=serch_id)
                        #print("ProcessID is %s" % (tempp1.ProcessID))
                        #print("ConsumerID is %s" % (tempp1.ConsumerId))
                        temp_person1 = models.ProcessorRegistry.objects.get(id=tempp1.ConsumerId)
                        #print("ConsumerID is %s" % (temp_person1.id))
                        #print(temp_person1.ConsumerName)
                        print("...........")
                        i = model_to_dict(tempp1)
                        i.pop("id")
                        i.update({'ConsumerId': temp_person1.ConsumerName})  # 修改
                        ret.append(json.dumps(i, cls=models.DateEncoder, ensure_ascii=False))
                    j=j+1
                    if(k==4):
                        print(production_id)
                        tempp = models.ProcessData.objects.get(ReproductionID=production_id)
#                       print("ProcessID is %s"%(tempp.ProcessID))
#                       print("ConsumerID is %s"%(tempp.ConsumerId))
                        temp_person = models.ProcessorRegistry.objects.get(id=tempp.ConsumerId)
#                       print(temp_person.ConsumerName)
                        print("...........")
                        i = model_to_dict(tempp)
                        i.pop("id")
                        i.update({'ConsumerId': temp_person.ConsumerName})  # 修改
                        ret.append(json.dumps(i, cls=models.DateEncoder, ensure_ascii=False))
                print("加工表 有数据")
            else:
                print("加工表没有数据")

            #运输表 加工到销售
            temp6 = models.TransportData.objects.filter(ProductionID=production_id, Transport_Flag=32)
            if (temp6):
                for sample6 in temp6:
                    temp_person = models.TransporterRegistry.objects.get(IDNo=sample6.TransactionPersonID)
                    i = model_to_dict(sample6)
                    i.pop("id")
                    i.update({'TransactionPersonID': temp_person.ConsumerName})  # 修改
                    ret.append(json.dumps(i, cls=models.DateEncoder, ensure_ascii=False))
                print("运输表3 有数据")
            else:
                print("运输表3没有数据")

            #销售表溯源
            temp7 = models.SellData.objects.filter(ProductionID=production_id)
            if (temp7):
                for sample7 in temp7:
                    i = model_to_dict(sample7)
                    i.pop("id")
                    ret.append(json.dumps(i, cls=models.DateEncoder, ensure_ascii=False))
                print("销售表有 数据")
            else:
                print("销售表没有数据")

            return HttpResponse(ret, content_type="application/json", charset="utf-8")
        except ObjectDoesNotExist:
            return HttpResponse("数据查询失败")
    else:
        return HttpResponse("method 应该为GET")


def qrcode(request):
    import qrcode
    img = qrcode.make('{name:123}')
    img.save('test.png')


def key(request):
    pk = PKey()

    pk.generate_key(TYPE_RSA, 512)

    pri_key = dump_privatekey(FILETYPE_PEM, pk)  # 生成私钥

    pub_key = dump_publickey(FILETYPE_PEM, pk)  # 生成公钥

    dic = {}
    dic["pri_key"] = pri_key.decode()
    dic["pub_key"] = pub_key.decode()
    print(type(pri_key))
    print(dic)
    return HttpResponse(json.dumps(dic, ensure_ascii=False), content_type="application/json")  # 返回公私钥

def test(request):
    pk = PKey()

    pk.generate_key(TYPE_RSA, 512)

    pri_key = dump_privatekey(FILETYPE_PEM, pk)  # 生成私钥

    pub_key = dump_publickey(FILETYPE_PEM, pk)  # 生成公钥

    dic = {}
    dic["pri_key"] = pri_key.decode()
    dic["pub_key"] = pub_key.decode()
    print(type(pri_key))
    print(dic)
    return HttpResponse(json.dumps(dic, ensure_ascii=False), content_type="application/json")  # 返回公私钥
    # return HttpResponse("测试ing")




























