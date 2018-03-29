from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
import json, re, logging, datetime
import numpy as np
from . import TYApi

# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView

from .models import loadDataModel
from .serializers import loadDataSerializer, bondYTMAnalyicDataSerializer
'''
日志模块加载
'''
logger = logging.getLogger('SwhyDataAnalytic.Debug')

'''
加载主页面
'''
def loadPage(request):
    return render(request, 'QuoteAnalysis.html')


'''
价差分析
传递参数:
    1. bondType 债券名称
    2. duration 债券久期
    3. startTime 开始时间
    4. endTime 结束时间
    5. containerName 容器名称
    6. method 是否是价差函数方法名
    7. arrayData价格序列数组
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
            futuresType = request.POST['futuresType']
            duration = request.POST['duration']
            startTime = request.POST['startTime']
            endTime = request.POST['endTime']
            containerName = request.POST['containerName']
            arrayData = request.POST.getlist['arrayData[]']
            optionStructure = request.POST['optionStr']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

    '''
        获取各种数据指标
    '''
    #获取期货合约数据
    quoteData['quoteData'] = getFuturesData(futuresType, duration, startTime, endTime)
    #存储期货合约名称
    quoteData['futuresType'] = futuresType
    #存储container的名字
    quoteData['containerName'] = containerName
    quoteData['futuresPredict'] = '收益--' + futuresType

    #存储类型转换
    arrayData = np.array(arrayData)
    arrayData = arrayData.astype(np.float)
    arrayData = [data for data in arrayData if str(data) != 'nan']

    # 初始化同余API
    tyApi = TYApi.TYApi()

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    time_zone = 'Asia/Shanghai'
    tau = 1/12  # 期限
    r = 0.015  # 无风险利率
    forward = tyApi.TYMktQuoteGet(today, futuresType, time_zone)

    # 获取波动率曲线
    volSpread = tyApi.TYMdload('VOL_BLACK_ATM_' + re.sub(r'([\d]+)', '', futuresType))
    # 获得波动率
    vol = tyApi.TYVolSurfaceImpliedVolGet(forward, forward, today, volSpread)

    # 最新收盘价
    lastPrice = arrayData[-1]
    contractData = {}
    for i in range(0, len(optionStructure)):
        SData={}
        predictPrice = str(optionStructure[i].price * lastPrice)
        SData['price'] = predictPrice
        SData['option'] = optionStructure[i].option
        pricing = tyApi.TYPricing(forward, optionStructure[i].price, vol - 0.03, tau, r, str.lower(optionStructure[i].option))
        SData['pricing'] = str(round(pricing, 2))
        contractData[predictPrice] = SData


    # 计算期权组合期权费，并对行权价排序
    contractData = [(k, contractData[k]) for k in sorted(contractData.keys())]
    quoteData['contractData'] = contractData
    quoteData['lastPrice'] = str(lastPrice)
    premium = getPackagePrice(contractData)
    quoteData['premium'] =  str(round(premium, 2))

    if (containerName == 'YTM_tab1_container'):
        logger.info(quoteData)
        return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)
    else:

        # 存储价格区间
        forwardList = getForwardList(contractData)
        logger.info(forwardList)
        scenaData = {}

        # 获取组合收益曲线
        forwardData = {}
        for forward in forwardList:
            TQuoteData = {}
            revenue = getRevenue(lastPrice, forward, premium, contractData)
            TQuoteData['revenue'] = str(round(revenue, 4))
            TQuoteData['forward'] = str(round(forward, 2))
            forwardData[forward] = TQuoteData

        '''
        组装数据，收益曲线、期权组合结构
        '''
        scenaData['revenueList'] = forwardData
        scenaData['contractData'] = contractData
        scenaData['futuresType'] = futuresType

        return scenaData


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

def getRevenue(lastPrice, forward, premium, contractData):
    # 获取期权收益结构

    for (i, item) in contractData:
            if (item[1].price > lastPrice):
                if (item[1].option == 'ASK'):
                    if (forward < item[1].price ):
                        revenue = - premium
                    else:
                        revenue = forward - item[1].price - premium
                else:
                    if (forward < item[1].price ):
                        revenue = premium
                    else:
                        revenue = premium - forward + item[1].price
            else:
                if (item[1].option == 'ASK'):
                    revenue = (bool(forward < item[1].price))*(item[1].price - forward) - premium
                else:
                    revenue = premium - (bool(forward < item[1].price)) * (item[1].price - forward)
    return revenue



def getPackagePrice(contractData):

    premium = 0
    #期权组合费用叠加
    for (i,item) in contractData:
        if (item.trade == 'ask'):
            premium += item.pricing
        else:
            premium -= item.pricing
    return premium



def getFuturesData(futuresType, duration, startTime, endTime):
    #建立数据库连接
    cursor = connection.cursor()

    '''
    此处需要对传入的时间做判断，根据时间是否为空细化检索条件
    '''
    if(startTime == '' and endTime == ''):
        try:
            cursor.execute("select fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                       " from fut_mkt_quot_day where fut_mkt_quot_day.contractid = % "
                       "ORDER BY fut_mkt_quot_day.timestamp DESC", (futuresType))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif(startTime != '' and endTime == ''):
        try:
            cursor.execute("select fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                       " from fut_mkt_quot_day where fut_mkt_quot_day.contractid = %s "
                       "and fut_mkt_quot_day.timestamp >= %s "
                       "ORDER BY fut_mkt_quot_day.timestamp DESC", (futuresType, startTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif (startTime == '' and endTime != ''):
        try:
            cursor.execute("select fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                           " from fut_mkt_quot_day where fut_mkt_quot_day.contractid = %s "
                           "and fut_mkt_quot_day.timestamp <= %s "
                            "ORDER BY fut_mkt_quot_day.timestamp DESC", (futuresType, endTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    else:
        try:
            cursor.execute("select fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                           " from fut_mkt_quot_day where fut_mkt_quot_day.contractid = %s "
                           "and bondytm.timestamp >= %s "
                           "and bondytm.timestamp <= %s ORDER BY bondytm.timestamp DESC", (futuresType, startTime, endTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()


    listData = cursor.fetchall()
    cursor.close()
    #类型转换
    keys = ['close', 'timestamp']
    dictData = list2dict(keys, listData)
    # dictData = [(k, dictData[k]) for k in sorted(dictData.keys())]
    return dictData



def getForwardList(predictPrice):
    forwardList = []
    step = (np.max(predictPrice)-np.min(predictPrice))/20

    '''
    x<500 变动范围5, 500<x<2000 变动范围10, 2000<x<6000 变动范围50, 6000<x 变动范围100
    '''
    for i in range(-3, 25):
        if (i < 0):
            forwardList.append(np.min(predictPrice)-step*2*i)
        elif (i >= 0 and i < 10 ):
            forwardList.append(np.min(predictPrice)+step*1.5*i)
        elif (i >=10 ):
            forwardList.append(np.max(predictPrice)+step*(i-15))

    return forwardList


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