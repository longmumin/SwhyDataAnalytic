from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
import json
import numpy as np
import pandas as pd

def loadPage(request):
    return render(request, 'YTMAnalytic.html')


'''
价差分析
传递参数:
    1. bondType 债券名称
    2. duration 债券久期
    3. startTime 开始时间
    4. endTime 结束时间
    5. containerName 容器名称
    6. method 是否是价差函数方法名
返回参数：
    1. quoteData 行情序列
    2. bondType 价差title
    3. containerName 容器名称
    4. method 是否是价差函数方法名
'''
def loadData(request):
    quoteData = {}
    #抽取request中数据
    if(request.method == 'POST'):
        try:
            bondType = request.POST['bondType']
            duration = request.POST['duration']
            startTime = request.POST['startTime']
            endTime = request.POST['endTime']
            containerName = request.POST['containerName']
            method = request.POST['method']
        except Exception as e:
            print("get request error, ret = %s" % e.args[0])
    #获取YTM数据
    quoteData['quoteData'] = getBondYTMData(bondType, duration, startTime, endTime)
    #存储债券名称
    quoteData['bondType'] = bondType
    #存储container的名字
    quoteData['containerName'] = containerName
    #存储方法名
    quoteData['method'] = method
    print(quoteData)
    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)

'''
价差分析
传递参数:
    1. bondType[] 债券名称数组
    2. duration[] 债券久期数组
    3. startTime 开始时间
    4. endTime 结束时间
    5. containerName 容器名称
    6. method 是否是价差函数方法名
返回参数：
    1. quoteData 价差序列
    2. bondType 价差title
    3. containerName 容器名称
    4. method 是否是价差函数方法名
'''
def getBondYTMDiffCacl(request):
    quoteData = {}
    #抽取request中数据
    if (request.method == 'POST'):
        try:
            bondType = request.POST.getlist('bondType[]')
            duration = request.POST.getlist('duration[]')
            startTime = request.POST['startTime']
            endTime = request.POST['endTime']
            containerName = request.POST['containerName']
            method = request.POST['method']
        except Exception as e:
            print("get request error, ret = %s" % e.args[0])

    #获取价差数据，价差可以换为除法。--------此处如果有多条数据可以用循环
    YTMData1 = getBondYTMData(bondType[0], duration[0], startTime, endTime)
    YTMData2 = getBondYTMData(bondType[1], duration[1], startTime, endTime)
    diffData = dictMinus(YTMData1, YTMData2)
    # 获取YTM数据
    quoteData['quoteData'] = diffData
    # 存储债券名称
    quoteData['bondType'] = '价差--'+ bondType[0] + '和' + bondType[1]
    # 存储container的名字
    quoteData['containerName'] = containerName
    # 存储方法名
    quoteData['method'] = method
    print(quoteData)
    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)

'''
价差分析
传递参数:
    1. bondType[] 债券名称数组
    2. duration[] 债券久期数组
    3. startTime 开始时间
    4. endTime 结束时间
    5. containerName 容器名称
返回参数：
    1. quoteData 价差序列
'''
def getBondYTMMatrix(request):
    quoteData = {}
    YTMData = {}
    #抽取request中数据
    if (request.method == 'POST'):
        try:
            bondType = request.POST.getlist('bondType[]')
            duration = request.POST.getlist('duration[]')
            startTime = request.POST['startTime']
            endTime = request.POST['endTime']
            containerName = request.POST['containerName']
        except Exception as e:
            print("get request error, ret = %s" % e.args[0])

    for bond in bondType:
        data = {}
        for dur in duration:
            data[dur] = getBondYTMData(bond, dur, startTime, endTime)
        YTMData[bond] = data
    #YTMData = pd.DataFrame(YTMData)
    for k1, v1 in YTMData.items():
        ytmData = {}
        for k2, v2 in YTMData.items():
            #去除相同债券和久期的YTM
            if(len(dictMinus(v1, v2).values()) != 0):
                ytmData[k2] = round((next(iter(dictMinus(v1, v2).values())))['bondytm'],4)
                #quoteData[k1+'--'+k2] = round((next(iter(dictMinus(v1, v2).values())))['bondytm'],4)
            else:
                ytmData[k2] = '--'
                #quoteData[k1+'--'+k2] = '--'
        quoteData[k1] = ytmData
    print(quoteData)
    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)


'''
价差分析
传递参数:
    1. arrayData价格序列数组
返回参数：
    1. 
'''
def getBondYTMAnalyicData(request):
    quoteData = {}
    #抽取request中数据
    if (request.method == 'POST'):
        try:
            arrayData = request.POST.getlist('arrayData[]')
        except Exception as e:
            print("get request error, ret = %s" % e.args[0])

    #存储类型转换
    arrayData = np.array(arrayData)
    arrayData = arrayData.astype(np.float)
    arrayData = [data for data in arrayData if str(data) != 'nan']

    '''
    获取各种数据指标
    '''
    #最新价差
    latestDiff = arrayData[-1]
    #昨结价差
    lastDiff = arrayData[-2]
    #最新价差分析变化量，幅度
    latestDiffDiff = latestDiff - lastDiff
    if(latestDiffDiff > 0):
        latestDiffPercent = abs(latestDiffDiff/lastDiff)
    else:
        latestDiffPercent = (latestDiffDiff/lastDiff) if lastDiff>0 else (0-latestDiffDiff/lastDiff)
    #平均值
    mean = np.mean(arrayData)
    #中位数
    median = np.median(arrayData)
    #偏离均值
    deviateMean = arrayData[-1] - mean
    #百分位数

    #标准差
    standardDeviation = np.std(arrayData)
    #偏离标准差

    #最大值

    #最小值

    '''
    组装数据，保留4位小数
    '''
    quoteData['latestDiff'] = round(latestDiff,4)
    quoteData['latestDiffDiff'] = round(latestDiffDiff,4)
    quoteData['latestDiffPercent'] = round(latestDiffPercent,4)
    quoteData['lastDiff'] = round(lastDiff,4)
    quoteData['mean'] = round(mean,4)
    quoteData['median'] = round(median,4)
    quoteData['deviateMean'] = round(deviateMean,4)
    quoteData['standardDeviation'] = round(standardDeviation,4)

    print(quoteData)

    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)


def getBondYTMData(bondType, duration, startTime, endTime):
    #建立数据库连接
    cursor = connection.cursor()

    '''
    此处需要对传入的时间做判断，根据时间是否为空细化检索条件
    '''
    if(startTime == '' and endTime == ''):
        try:
            cursor.execute("select bondytm.bondytm, bondytm.timestamp"
                       " from bondytm, sys_code where sys_code.codetype = 'bondytmtype' "
                       "and bondytm.bondytmtype = sys_code.code and sys_code.codename = %s "
                       "and bondytm.bondduration = %s ORDER BY bondytm.timestamp DESC", (bondType, duration))
        except Exception as e:
            print("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif(startTime != '' and endTime == ''):
        try:
            cursor.execute("select bondytm.bondytm, bondytm.timestamp"
                       " from bondytm, sys_code where sys_code.codetype = 'bondytmtype' "
                       "and bondytm.bondytmtype = sys_code.code and sys_code.codename = %s "
                       "and bondytm.bondduration = %s and bondytm.timestamp >= %s "
                       "ORDER BY bondytm.timestamp DESC", (bondType, duration, startTime))
        except Exception as e:
            print("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif (startTime == '' and endTime != ''):
        try:
            cursor.execute("select bondytm.bondytm, bondytm.timestamp"
                           " from bondytm, sys_code where sys_code.codetype = 'bondytmtype' "
                           "and bondytm.bondytmtype = sys_code.code and sys_code.codename = %s "
                           "and bondytm.bondduration = %s and bondytm.timestamp <= %s "
                            "ORDER BY bondytm.timestamp DESC", (bondType, duration, endTime))
        except Exception as e:
            print("select table failed, ret = %s" % e.args[0])
            cursor.close()
    else:
        try:
            cursor.execute("select bondytm.bondytm, bondytm.timestamp"
                           " from bondytm, sys_code where sys_code.codetype = 'bondytmtype' "
                           "and bondytm.bondytmtype = sys_code.code and sys_code.codename = %s "
                           "and bondytm.bondduration = %s and bondytm.timestamp >= %s and "
                           "bondytm.timestamp <= %s ORDER BY bondytm.timestamp DESC", (bondType, duration, startTime, endTime))
        except Exception as e:
            print("select table failed, ret = %s" % e.args[0])
            cursor.close()


    listData = cursor.fetchall()
    cursor.close()
    #类型转换
    keys = ['bondytm', 'timestamp']
    dictData = list2dict(keys, listData)
    # dictData = [(k, dictData[k]) for k in sorted(dictData.keys())]
    return dictData


def list2dict(keys, values):
    dictData = {}
    for value in values:
        row = {}
        value = list(value)
        for i in range(0, len(keys)):
            row[keys[i]] = str(value[i])
        #时间戳作为keys
        dictData[str(value[1])] = row
    return dictData

def dictMinus(dict1, dict2):
    diffDict = {}
    for k, v in dict2.items():
        if k in dict1.keys():
            data = {}
            data['bondytm'] = (float(dict1[k]['bondytm']) - float(v['bondytm']))
            data['timestamp'] = k
            diffDict[k] = data

    return diffDict