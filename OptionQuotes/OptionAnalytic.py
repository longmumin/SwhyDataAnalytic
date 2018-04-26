from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
import json, re, logging, datetime
import numpy as np
from . import TYApi

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import loadDataModel
from .serializers import optionSerializer, optionAnalyicDataSerializer
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
期货历史数据及预测
传递参数:
    1. FuturesType 标的合约名称
    2. duration 期限
    3. startTime 开始时间
    4. endTime 结束时间
    5. containerName 容器名称
    6. arrayData价格序列数组
返回参数：
    1. quoteData 行情序列
    2. lastPrice 前一交易日收盘价
    3. premium 组合权利金
    3. containerName 容器名称
'''

# def loadData(request):
#     #抽取request中数据
#     if(request.method == 'POST'):
#         try:
#             futuresType = request.POST['futuresType']
#             startTime = request.POST['startTime']
#             endTime = request.POST['endTime']
#             containerName = request.POST['containerName']
#             optionData = request.POST.getlist('optionStr[]')
#         except Exception as e:
#             logger.error("get request error, ret = %s" % e.args[0])

class loadData(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = optionSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            futuresType = request.POST['futuresType']
            startTime = request.POST['startTime']
            endTime = request.POST['endTime']
            containerName = request.POST['containerName']
            optionData = request.POST.getlist('optionStr[]')
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        quoteData = {}

        '''
            获取各种数据指标
        '''

        #获取期货合约数据
        optionStructure = generatePackage(optionData)
        quoteData['quoteData'] = getFuturesData(futuresType, startTime, endTime)
        #存储期货合约名称
        quoteData['futuresType'] = futuresType
        #存储container的名字
        quoteData['containerName'] = containerName

        #存储类型转换
        arrayData = quoteData['quoteData']
        arrayData = sorted(zip(arrayData.keys(), arrayData.values()))
        # 最新收盘价
        lastPrice = float(arrayData[-1][1]['close'])

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



        '''
        参数含义
        1. Price 行权价
        2. option 看涨/看跌期权类型
        3. pricing 单个期权价格
        4. premium 期权组合期权费
        '''
        contractData = {}
        for k in optionStructure.keys():
            SData={}
            predictPrice = float(optionStructure[k]['price']) * lastPrice
            optionType = str.lower(optionStructure[k]['optionType'])
            tradeDirect = str.lower(optionStructure[k]['trade'])
            #float(tyApi.TYPricing(forward, forward, vol - 0.03, tau, r, 'call'))
            pricing = tyApi.TYPricing(lastPrice, predictPrice, vol - 0.03, tau, r, optionType)
            SData['price'] = predictPrice
            SData['option'] = optionType
            SData['pricing'] = str(round(pricing, 2))
            SData['trade'] = tradeDirect
            contractData[predictPrice] = SData

        #quoteData['contractData'] = contractData
        quoteData['lastPrice'] = str(lastPrice)

        # 计算期权组合期权费，并对行权价排序
        contractData = [(k, contractData[k]) for k in sorted(contractData.keys())]
        premium = getPackagePrice(contractData)
        quoteData['optionPremium'] = str(round(premium, 2))


        if (containerName == 'YTM_tab1_container'):
            logger.info(quoteData)
            # return JsonResponse(json.dumps(quoteData, ensure_ascii=False, sort_keys=True), safe=False)

            serializer = optionSerializer(data=quoteData)
            a = serializer.is_valid()
            if serializer.is_valid():
                serializer.save()
                b = serializer.data
                # json_dumps_params为json.dumps的参数
                return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},
                                    safe=False, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:

            # 存储价格区间
            forwardList = getForwardList(contractData)
            scenaData = {}

            # 获取组合收益曲线
            forwardData = {}
            for forward in forwardList:
                TQuoteData = {}
                revenue = getRevenue(lastPrice, forward, contractData)
                TQuoteData['revenue'] = str(round(revenue, 2))
                TQuoteData['forward'] = str(round(forward))
                forwardData[str(forward)] = TQuoteData

            '''
            组装数据，收益曲线、期权组合结构
            '''
            scenaData['revenueList'] = forwardData
            # scenaData['contractData'] = contractData
            # scenaData['strikePrice'] = sorted([str(k[0]) for k in contractData])
            scenaData['futuresType'] = futuresType
            scenaData['containerName'] = containerName

            # return JsonResponse(json.dumps(scenaData, ensure_ascii=False, sort_keys=True), safe=False)

            serializer = optionAnalyicDataSerializer(data=scenaData)
            c = serializer.is_valid()
            if serializer.is_valid():
                serializer.save()
                # json_dumps_params为json.dumps的参数
                return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},
                                    safe=False, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



'''
解析期权组合结构
1. futuresType 期货标的合约
2. duration    到期期限
3. price       期权行权价，现价百分比标价
4. optionType  看涨看跌期权
5. trade       多or空（ASK/BID)
'''
def generatePackage(optionStructure):
            optionData = {}
            for option in optionStructure:
                option = option.split(",")
                optionStr={}
                price = option[3][0:4]
                future = option[0].strip()
                optionStr['futuresType'] = future[4:]
                optionStr['duration'] = option[2]
                optionStr['price'] = str(price)
                optionStr['optionType'] = option[1]
                optionStr['trade'] = (option[0].lstrip())[0:3]
                optionData[price] = optionStr
            logger.info(optionData)
            return optionData

'''
情景分析
返回参数：
    1. revenueList 损益曲线
    2. contractData 期权组合结构
    3. futuresType 标的期货合约
'''

def getPackagePrice(contractData):

    premium = 0
    #期权组合费用叠加
    for (i,item) in contractData:
        if (item['trade'] == 'ask'):
            premium += float(item['pricing'])
        else:
            premium -= float(item['pricing'])
    return premium


def getForwardList(contractData):
    forwardList = []
    predictPrice = [k[0] for k in contractData]
    step = (max(predictPrice) - min(predictPrice)) / 10

    '''
    x<500 变动范围5, 500<x<2000 变动范围10, 2000<x<6000 变动范围50, 6000<x 变动范围100
    '''
    for i in range(-3, 15):
        # if (i < 0):
            forwardList.append(round(min(predictPrice)+step*i,2))
        # elif (i >= 0 and i < 10 ):
        #     forwardList.append(round(min(predictPrice)+step*1.5*i,2))
        # elif (i >=10 ):
        #     forwardList.append(round(max(predictPrice)+step*(i-15),2))
    logger.info(forwardList)

    return forwardList



def getRevenue(lastPrice, forward, contractData):
    # 获取期权结构组合收益

    revenue = 0

    for (i, item) in contractData:
            #获取键值
            pricing = float(item['pricing'])
            strikePrice = item['price']

            if (strikePrice > lastPrice):
                if (item['trade'] == 'ask'):
                    if (forward < strikePrice ):
                        revenue += (- pricing)
                    else:
                        revenue += (forward - strikePrice - pricing)
                else:
                    if (forward < strikePrice ):
                        revenue += (pricing)
                    else:
                        revenue += (pricing - forward + strikePrice)
            else:
                if (item['trade'] == 'ask'):
                    revenue += ((bool(forward < strikePrice))*(strikePrice - forward) - pricing)
                else:
                    revenue += (pricing - (bool(forward < strikePrice)) * (strikePrice - forward))
    return revenue



def getFuturesData(futuresType, startTime, endTime):
    #建立数据库连接
    futuresType = futuresType[0:futuresType.find('.')]
    cursor = connection.cursor()

    '''
    此处需要对传入的时间做判断，根据时间是否为空细化检索条件
    '''
    if(startTime == '' and endTime == ''):
        try:

            cursor.execute("SELECT fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                           " FROM fut_mkt_quot_day WHERE fut_mkt_quot_day.contractid LIKE '%s%%'"
                           " ORDER BY fut_mkt_quot_day.timestamp DESC" %(futuresType))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif(startTime != '' and endTime == ''):
        try:
            cursor.execute("select fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                           " from fut_mkt_quot_day where fut_mkt_quot_day.contractid LIKE '%s%%' "
                           "and fut_mkt_quot_day.timestamp >= %s ORDER BY fut_mkt_quot_day.timestamp DESC" % (futuresType, startTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    elif (startTime == '' and endTime != ''):
        try:
            cursor.execute("select fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                           " from fut_mkt_quot_day where fut_mkt_quot_day.contractid LIKE '%s%%' "
                           "and fut_mkt_quot_day.timestamp <= %s ORDER BY fut_mkt_quot_day.timestamp DESC" % (futuresType, endTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()
    else:
        try:
            cursor.execute("select fut_mkt_quot_day.close, fut_mkt_quot_day.timestamp"
                           " from fut_mkt_quot_day where fut_mkt_quot_day.contractid LIKE '%s%%' "
                           "and bondytm.timestamp >= %s "
                           "and bondytm.timestamp <= %s ORDER BY bondytm.timestamp DESC" % (futuresType, startTime, endTime))
        except Exception as e:
            logger.error("select table failed, ret = %s" % e.args[0])
            cursor.close()


    listData = cursor.fetchall()
    cursor.close()
    #类型转换
    keys = ['close', 'timestamp']
    dictData = list2dict(keys, listData)
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