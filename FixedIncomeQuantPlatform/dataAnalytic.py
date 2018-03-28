# -*- coding:utf-8 -*-
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
import logging, tushare, datetime
import numpy as np
from scipy import stats

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import loadDataModel
from .serializers import loadDataSerializer, bondYTMAnalyicDataSerializer, bondYTMMatrixSerializer
from SwhyDataAnalytic.publicMethod import getLastTradeDate, list2dict
from django.contrib.auth.decorators import permission_required

'''
日志模块加载
'''
logger = logging.getLogger('SwhyDataAnalytic.Debug')


'''
加载主页面
'''
def loadPage(request):
    return render(request, 'YTMAnalytic.html')


'''
数据加载
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
#@permission_required('car.drive_car')，在这里定义所需要的权限后就可以限制，但是必须对request进行显示
class loadData(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = loadDataSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            bondType = request.data['bondType']
            duration = request.data['duration']
            startTime = request.data['startTime']
            endTime = request.data['endTime']
            containerName = request.data['containerName']
            method = request.data['method']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])
        quoteData = {}

        # 获取YTM数据
        quoteData['quoteData'] = getBondYTMData(bondType, duration, startTime, endTime)
        # 存储债券名称
        quoteData['bondType'] = bondType
        # 存储container的名字
        quoteData['containerName'] = containerName
        # 存储方法名
        quoteData['method'] = method
        logger.info(quoteData)

        serializer = loadDataSerializer(data=quoteData)
        if serializer.is_valid():
            serializer.save()
            #json_dumps_params为json.dumps的参数
            return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii":False, "sort_keys":True}, safe=False, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            logger.error("get request error, ret = %s" % e.args[0])
    #获取YTM数据
    quoteData['quoteData'] = getBondYTMData(bondType, duration, startTime, endTime)
    #存储债券名称
    quoteData['bondType'] = bondType
    #存储container的名字
    quoteData['containerName'] = containerName
    #存储方法名
    quoteData['method'] = method
    logger.info(quoteData)
    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)
'''


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
class getBondYTMDiffCacl(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = loadDataSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        quoteData = {}
        # 抽取request中数据
        try:
            bondType = request.data.getlist('bondType[]')
            duration = request.data.getlist('duration[]')
            startTime = request.data['startTime']
            endTime = request.data['endTime']
            containerName = request.data['containerName']
            method = request.data['method']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        # 获取价差数据，价差可以换为除法。--------此处如果有多条数据可以用循环
        YTMData1 = getBondYTMData(bondType[0], duration[0], startTime, endTime)
        YTMData2 = getBondYTMData(bondType[1], duration[1], startTime, endTime)
        diffData = dictVolMinusCacl(YTMData1, YTMData2)
        # 获取YTM数据
        quoteData['quoteData'] = diffData
        # 存储债券名称
        quoteData['bondType'] = '价差--' + bondType[0] + '和' + bondType[1]
        # 存储container的名字
        quoteData['containerName'] = containerName
        # 存储方法名
        quoteData['method'] = method
        logger.info(quoteData)

        serializer = loadDataSerializer(data=quoteData)
        # serializedData = {'data': serializer.data}
        if serializer.is_valid():
            serializer.save()
            #json_dumps_params为json.dumps的参数
            return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},safe=False, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            logger.error("get request error, ret = %s" % e.args[0])


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
    logger.info(quoteData)
    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)
'''

class getBondYTMVolDiffCacl(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = loadDataSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        quoteData = {}
        # 抽取request中数据
        try:
            bondType = request.data.getlist('bondType[]')
            duration = request.data.getlist('duration[]')
            startTime = request.data['startTime']
            endTime = request.data['endTime']
            containerName = request.data['containerName']
            method = request.data['method']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        # 获取价差数据，价差可以换为除法。--------此处如果有多条数据可以用循环
        YTMData1 = getBondYTMData(bondType[0], duration[0], startTime, endTime)
        YTMData2 = getBondYTMData(bondType[1], duration[1], startTime, endTime)
        diffData = dictMinusCacl(YTMData1, YTMData2)
        # 获取YTM数据
        quoteData['quoteData'] = diffData
        # 存储债券名称
        quoteData['bondType'] = '价差--' + bondType[0] + '和' + bondType[1]
        # 存储container的名字
        quoteData['containerName'] = containerName
        # 存储方法名
        quoteData['method'] = method
        logger.info(quoteData)

        serializer = loadDataSerializer(data=quoteData)
        # serializedData = {'data': serializer.data}
        if serializer.is_valid():
            serializer.save()
            #json_dumps_params为json.dumps的参数
            return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},safe=False, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
class getBondYTMMatrix(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = loadDataSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        quoteData = {}
        YTMData = {}
        try:
            bondType = request.data.getlist('bondType[]')
            duration = request.data.getlist('duration[]')
            startTime = request.data['startTime']
            endTime = request.data['endTime']
            containerName = request.data['containerName']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        #获取上一个交易日
        startTime = getLastTradeDate(startTime)
        endTime = datetime.datetime.strptime(startTime,'%Y-%m-%d') + datetime.timedelta(days = 1)
        endTime = endTime.strftime('%Y-%m-%d')

        '''
        债券名称做主键，两个期限做内部主键
        通过containerName选择债券类型（bondType）和期限（duration）的矩阵形成方式
        债券类型：bondYTMMatrix
        期限：durationMatrix
        '''
        # 生成债券期限矩阵
        if (containerName == 'durationMatrix'):
            for bond in bondType:
                data = {}
                for dur in duration:
                    data[dur] = getBondYTMData(bond, dur, startTime, endTime)
                YTMData[bond] = data
            # YTMData = pd.DataFrame(YTMData)
            # 生成债券期限矩阵
        elif (containerName == 'bondYTMMatrix'):
            for dur in duration:
                data = {}
                for bond in bondType:
                    data[bond] = getBondYTMData(bond, dur, startTime, endTime)
                YTMData[dur] = data
            # YTMData = pd.DataFrame(YTMData)

        bondYTMData = {}
        for k1, v1 in YTMData.items():
            ytmData1 = {}
            for k2, v2 in v1.items():
                ytmData2 = {}
                for k3, v3 in v1.items():
                    # 去除相同债券和久期的YTM
                    if (len(dictMinusMatrix(v2, v3).values()) != 0):
                        ytmData2[k3] = round(((next(iter(dictMinusMatrix(v2, v3).values())))['bondytm'])*100, 2)
                        # quoteData[k1+'--'+k2] = round((next(iter(dictMinus(v1, v2).values())))['bondytm'],4)
                    else:
                        ytmData2[k3] = '--'
                        # quoteData[k1+'--'+k2] = '--'
                ytmData1[k2] = ytmData2
            bondYTMData[k1] = ytmData1

        quoteData['quoteData'] = bondYTMData
        quoteData['containerName'] = containerName
        logger.info(quoteData)

        serializer = bondYTMMatrixSerializer(data=quoteData)
        # serializedData = {'data': serializer.data}
        if serializer.is_valid():
            serializer.save()
            #json_dumps_params为json.dumps的参数
            return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},safe=False, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            logger.error("get request error, ret = %s" % e.args[0])

    债券名称做主键，两个期限做内部主键
    通过containerName选择 债券类型（bondType）和期限（duration）的矩阵形成方式
    债券类型：bondYTMMatrix
    期限：durationMatrix

    # 生成债券期限矩阵
    if (containerName == 'bondYTMMatrix'):
        for bond in bondType:
            data = {}
            for dur in duration:
                data[dur] = getBondYTMData(bond, dur, startTime, endTime)
            YTMData[bond] = data
        #YTMData = pd.DataFrame(YTMData)
    # 生成债券期限矩阵
    elif (containerName == 'durationMatrix'):
        for dur in duration:
            data = {}
            for bond in bondType:
                data[bond] = getBondYTMData(bond, dur, startTime, endTime)
            YTMData[dur] = data
        #YTMData = pd.DataFrame(YTMData)

    bondYTMData = {}
    for k1, v1 in YTMData.items():
        ytmData1 = {}
        for k2, v2 in v1.items():
            ytmData2 = {}
            for k3, v3 in v1.items():
                #去除相同债券和久期的YTM
                if(len(dictMinus(v2, v3).values()) != 0):
                    ytmData2[k3] = round((next(iter(dictMinus(v2, v3).values())))['bondytm'],4)
                    #quoteData[k1+'--'+k2] = round((next(iter(dictMinus(v1, v2).values())))['bondytm'],4)
                else:
                    ytmData2[k3] = '--'
                    #quoteData[k1+'--'+k2] = '--'
            ytmData1[k2] = ytmData2
        bondYTMData[k1] = ytmData1

    quoteData['bondYTMData'] = bondYTMData
    quoteData['containerName'] = containerName

    logger.info(quoteData)

    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)
'''



'''
价差分析
传递参数:
    1. arrayData价格序列数组
返回参数：
    1. 
'''
class getBondYTMAnalyicData(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = loadDataSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        analysisData = {}
        quoteData = {}
        try:
            arrayData = request.data.getlist('arrayData[]')
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        # 存储类型转换
        arrayData = np.array(arrayData)
        arrayData = arrayData.astype(np.float)
        arrayData = [data for data in arrayData if str(data) != 'nan']

        '''
        获取各种数据指标
       '''
        # 最新价差
        latestDiff = arrayData[-1]
        # 昨结价差
        lastDiff = arrayData[-2]
        # 最新价差分析变化量，幅度
        latestDiffDiff = latestDiff - lastDiff
        if (latestDiffDiff > 0):
            latestDiffPercent = abs(latestDiffDiff / lastDiff)
        else:
            latestDiffPercent = (latestDiffDiff / lastDiff) if lastDiff > 0 else (0 - latestDiffDiff / lastDiff)
        # 平均值
        mean = np.mean(arrayData)
        # 中位数
        median = np.median(arrayData)
        # 偏离均值
        deviateMean = arrayData[-1] - mean
        # 百分位数
        percentile = stats.percentileofscore(arrayData, arrayData[-1])

        # 标准差
        standardDeviation = np.std(arrayData)
        # 偏离标准差
        deviateStandardDeviation = arrayData[-1] - standardDeviation

        # 最大值
        max = np.max(arrayData)
        # 最小值
        min = np.min(arrayData)

        '''
        组装数据，保留4位小数
        '''
        analysisData['latestDiff'] = round(latestDiff, 4)
        analysisData['latestDiffDiff'] = round(latestDiffDiff, 4)
        analysisData['latestDiffPercent'] = round(latestDiffPercent, 4)
        analysisData['lastDiff'] = round(lastDiff, 4)
        analysisData['mean'] = round(mean, 4)
        analysisData['median'] = round(median, 4)
        analysisData['deviateMean'] = round(deviateMean, 4)
        analysisData['standardDeviation'] = round(standardDeviation, 4)
        analysisData['percentile'] = round(percentile, 2)
        analysisData['deviateStandardDeviation'] = round(deviateStandardDeviation, 4)
        analysisData['max'] = round(max, 4)
        analysisData['min'] = round(min, 4)
        #获取最新波动率
        analysisData['vol'] = round((getVolDay(arrayData))[-1], 4)
        #获取资金成本，FR007 1年期，上一个交易日的数据
        startTime = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
        startTime = getLastTradeDate(startTime)
        fr007YTM = getBondYTMData('FR007', '1Y', startTime, startTime)
        for (key, value) in fr007YTM.items():
            analysisData['capitalCost'] = value['bondytm']


        quoteData['quoteData'] = analysisData
        logger.info(quoteData)

        serializer = bondYTMAnalyicDataSerializer(data=quoteData)
        # serializedData = {'data': serializer.data}
        if serializer.is_valid():
            serializer.save()
            #json_dumps_params为json.dumps的参数
            return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},safe=False, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
def getBondYTMAnalyicData(request):
    quoteData = {}
    #抽取request中数据
    if (request.method == 'POST'):
        try:
            arrayData = request.POST.getlist('arrayData[]')
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

    #存储类型转换
    arrayData = np.array(arrayData)
    arrayData = arrayData.astype(np.float)
    arrayData = [data for data in arrayData if str(data) != 'nan']

    
    获取各种数据指标
    
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
    percentile = stats.percentileofscore(arrayData, arrayData[-1])

    #标准差
    standardDeviation = np.std(arrayData)
    #偏离标准差
    deviateStandardDeviation = arrayData[-1] - standardDeviation

    #最大值
    max = np.max(arrayData)
    #最小值
    min = np.min(arrayData)

    组装数据，保留4位小数
    
    quoteData['latestDiff'] = round(latestDiff,4)
    quoteData['latestDiffDiff'] = round(latestDiffDiff,4)
    quoteData['latestDiffPercent'] = round(latestDiffPercent,4)
    quoteData['lastDiff'] = round(lastDiff,4)
    quoteData['mean'] = round(mean,4)
    quoteData['median'] = round(median,4)
    quoteData['deviateMean'] = round(deviateMean,4)
    quoteData['standardDeviation'] = round(standardDeviation,4)
    quoteData['percentile'] = round(percentile, 2)
    quoteData['deviateStandardDeviation'] = round(deviateStandardDeviation, 4)
    quoteData['max'] = round(max, 4)
    quoteData['min'] = round(min, 4)

    logger.info(quoteData)

    return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)
'''

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
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif(startTime != '' and endTime == ''):
        try:
            cursor.execute("select bondytm.bondytm, bondytm.timestamp"
                       " from bondytm, sys_code where sys_code.codetype = 'bondytmtype' "
                       "and bondytm.bondytmtype = sys_code.code and sys_code.codename = %s "
                       "and bondytm.bondduration = %s and bondytm.timestamp >= %s "
                       "ORDER BY bondytm.timestamp DESC", (bondType, duration, startTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif (startTime == '' and endTime != ''):
        try:
            cursor.execute("select bondytm.bondytm, bondytm.timestamp"
                           " from bondytm, sys_code where sys_code.codetype = 'bondytmtype' "
                           "and bondytm.bondytmtype = sys_code.code and sys_code.codename = %s "
                           "and bondytm.bondduration = %s and bondytm.timestamp <= %s "
                            "ORDER BY bondytm.timestamp DESC", (bondType, duration, endTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    else:
        try:
            cursor.execute("select bondytm.bondytm, bondytm.timestamp"
                           " from bondytm, sys_code where sys_code.codetype = 'bondytmtype' "
                           "and bondytm.bondytmtype = sys_code.code and sys_code.codename = %s "
                           "and bondytm.bondduration = %s and bondytm.timestamp >= %s and "
                           "bondytm.timestamp <= %s ORDER BY bondytm.timestamp DESC", (bondType, duration, startTime, endTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()


    listData = cursor.fetchall()
    cursor.close()
    #类型转换
    keys = ['bondytm', 'timestamp']
    dictData = list2dict(keys, listData)
    return dictData


def dictMinusCacl(dict1, dict2):
    diffDict = {}
    for k, v in dict2.items():
        if k in dict1.keys():
            data = {}
            data['bondytm'] = str((float(dict1[k]['bondytm']) - float(v['bondytm'])))
            data['timestamp'] = k
            diffDict[k] = data
    return diffDict

def dictMinusMatrix(dict1, dict2):
    diffDict = {}
    for k, v in dict2.items():
        if k in dict1.keys():
            data = {}
            data['bondytm'] = float(dict1[k]['bondytm']) - float(v['bondytm'])
            data['timestamp'] = k
            diffDict[k] = data
    return diffDict

#实际上就是求除法
def getVolDay(arrayData):
    volData = []
    for i in range(0, len(arrayData)-2):
        volData.append(arrayData[i+1]/arrayData[i])
    return volData

#根据dict的键值排序
def dictVolMinusCacl(dict1, dict2):
    volDiffDict = {}
    sortedDict1 = [(k, dict1[k]) for k in sorted(dict1.keys())]
    sortedDict2 = [(k, dict2[k]) for k in sorted(dict2.keys())]

    #求波动率
    for i in range(1, len(sortedDict1)-1):
        sortedDict1[i][1]['bondytm'] = (float(sortedDict1[i][1]['bondytm']) - float(sortedDict1[i-1][1]['bondytm']))/float(sortedDict1[i-1][1]['bondytm'])
    del sortedDict1[0]
    for i in range(1, len(sortedDict2)-1):
        sortedDict2[i][1]['bondytm'] = (float(sortedDict2[i][1]['bondytm']) - float(sortedDict2[i-1][1]['bondytm']))/float(sortedDict2[i-1][1]['bondytm'])
    del sortedDict2[0]

    for i in range(0, min(len(sortedDict1), len(sortedDict2))):
        data = {}
        data['bondytm'] = float(sortedDict1[i][1]['bondytm']) - float(sortedDict2[i][1]['bondytm'])
        data['timestamp'] = sortedDict1[i][0]
        volDiffDict[sortedDict1[i][0]] = data
    return volDiffDict