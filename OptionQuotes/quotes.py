from django.shortcuts import render

import re, datetime, os, json, math, logging
import pandas as pd
from django.http import JsonResponse
# from WindPy import w

from . import TYApi

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import loadDataModel
from .serializers import loadDataSerializer

'''
日志模块加载
'''
logger = logging.getLogger('SwhyDataAnalytic.Debug')


#读取期货合约
baseDir = os.path.dirname(os.path.abspath(__name__))
contractListFileDir = baseDir + '/files/BasicInfo/contractList.xlsx'
logger.info(baseDir)
contractList = list(pd.read_excel(contractListFileDir)['contract'])
contractName = list(pd.read_excel(contractListFileDir)['name'])
contractList = dict(zip(contractList, contractName))


'''
加载主页面
'''


def loadPage(request):
    return render(request, 'quotes.html')


class loadData(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = loadDataSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            qixian = int(request.data['qixian'])
#            selected_date = request.data['dateselect']

        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        quoteData = {}
        quoteData['quoteData'] = GetQuotesDataFromTY(qixian)
        quoteData['qixian'] = str(qixian)
        logger.info(quoteData)

        serializer = loadDataSerializer(data=quoteData)
        if serializer.is_valid():
            serializer.save()
        #  json_dumps_params为json.dumps的参数
            return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},
                                safe=False, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''

def loadData(request):
    #获取同余数据
    if(request.method=='POST'):
        try:
            qixian = int(request.POST['qixian'])
 #           selected_date = request.POST['dateselect']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

    quoteData = {}
    quoteData['quoteData'] = GetQuotesDataFromTY(qixian)
    quoteData['qixian'] = str(qixian)

    logger.info(quoteData)
    return JsonResponse(quoteData, safe=False)
'''

'''
期货及平值期权价格
传递参数:
    1. qixian 期权期限
返回参数：
    1. quoteData 价格序列
'''


def GetQuotesDataFromTY(qixian) -> object:

    quoteData = {}

    #获得当前时间
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    time_zone = 'Asia/Shanghai'

    #定价参数
    tau = 1/12 #期限
    r = 0.015     #无风险利率

    if (qixian != 1):
        try:
            tau = qixian/12
#            if(selected_date != '当日'and selected_date != ''):
#                if(datetime.date(*map(int, selected_date.split('-'))) <= datetime.date(*map(int, today))):#当选择日期超过当前日期时不跳转
#                    today = selected_date
#                    yesterday = (datetime.date(*map(int, selected_date.split('-'))) + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

    #初始化同余API
    tyApi = TYApi.TYApi()

    #开启wind接口
    # w.start()

    #获取报价
    for contract in contractList.keys():

        contractData = {}

        #获取期货现价
        forward = tyApi.TYMktQuoteGet(today, contract, time_zone)
        lastPrice = tyApi.TYMktQuoteGet(yesterday, contract, time_zone, 'close', 'settle')
        # forward = w.wsq(contract, "rt_last").Data[0][0]

        #获取波动率曲线
        volSpread = tyApi.TYMdload('VOL_BLACK_ATM_' + re.sub(r'([\d]+)', '', contract))
        #获得波动率
        vol = tyApi.TYVolSurfaceImpliedVolGet(forward, forward, today, volSpread)

        # 获取spread曲线
        volSpreadCurve = tyApi.TYMdload(yesterday, model_name=('VOL_BLACK_ATM_SPREAD_' + re.sub(r'([\d]+)', '', contract)))
        # 获得sprea
        spread = tyApi.TYVolSurfaceImpliedVolGet(forward, forward, today, volSpreadCurve)
        # print(contract, volCurve, volSpreadCurve, vol, float(spread/2))

        pricingAsk = float(tyApi.TYPricing(forward, forward, vol + float(spread / 2), tau, r, 'call'))
        # print(pricingAsk)
        # 出错处理
        if (math.isnan(pricingAsk)):
            pricingAsk = float(0)
        pricingBid = float(tyApi.TYPricing (forward, forward, vol - 0.03, tau, r, 'call'))
        # 出错处理
        if (math.isnan(pricingBid)):
            pricingBid = float(0)

        contractData['forward'] = str(round(forward, 2))
        contractData['pricingAsk'] = str(round(pricingAsk, 2))
        contractData['pricingBid'] = str(round(pricingBid, 2))
        contractData['name'] = contractList[contract]
        contractData['lastPrice'] = str(round(lastPrice, 2))

        #组成dict
        quoteData[contract] = contractData

    #关闭wind接口
    # w.stop()
    #quoteData = [(k, quoteData[k]) for k in sorted(quoteData.keys())]

    logger.info(quoteData)

    return quoteData

'''
def GetQuotesDataFromTY(request):

    quoteData = {}

    #获得当前时间
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    time_zone = 'Asia/Shanghai'

    #定价参数
    tau = 1/12 #期限
    r = 0.015     #无风险利率

    if (request.method == 'POST'):
        try:
            tau = int(request.POST['qixian'])/12
            # selected_date = request.POST['dateselect']
            # if(selected_date!='当日'and selected_date!=''):
            #     if(datetime.date(*map(int, selected_date.split('-'))) <= datetime.datetime.now().strftime('%Y-%m-%d')):#当选择日期超过当前日期时不跳转
            #         today = selected_date
            #         yesterday = (datetime.date(*map(int, selected_date.split('-'))) + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

    #初始化同余API
    tyApi = TYApi.TYApi()

    #开启wind接口
    # w.start()

    #获取报价
    for contract in contractList.keys():

        contractData = {}

        #获取期货现价
        forward = tyApi.TYMktQuoteGet(today, contract, time_zone)
        lastPrice = tyApi.TYMktQuoteGet(yesterday, contract, time_zone, 'close', 'settle')
        # forward = w.wsq(contract, "rt_last").Data[0][0]

        #获取波动率曲线
        volCurve = tyApi.TYMdload(yesterday, model_name = ('VOL_BLACK_ATM_' + re.sub(r'([\d]+)', '', contract)))
        #获得波动率
        vol = tyApi.TYVolSurfaceImpliedVolGet(forward, forward, today, volCurve)

        #获取spread曲线
        volSpreadCurve = tyApi.TYMdload(yesterday, model_name = ('VOL_BLACK_ATM_SPREAD_' + re.sub(r'([\d]+)', '', contract)))
        # 获得sprea
        spread = tyApi.TYVolSurfaceImpliedVolGet(forward, forward, today, volSpreadCurve)
        #print(contract, volCurve, volSpreadCurve, vol, float(spread/2))

        pricingAsk = float(tyApi.TYPricing(forward, forward, vol + float(spread/2), tau, r, 'call'))
        # print(pricingAsk)
        #出错处理
        if(math.isnan(pricingAsk)):
            pricingAsk = float(0)
        pricingBid = float(tyApi.TYPricing(forward, forward, vol - 0.03, tau, r, 'call'))
        # 出错处理
        if (math.isnan(pricingBid)):
            pricingBid = float(0)

        contractData['forward'] = round(forward, 2)
        contractData['pricingAsk'] = round(pricingAsk, 2)
        contractData['pricingBid'] = round(pricingBid, 2)
        contractData['name'] = contractList[contract]
        contractData['lastPrice'] = round(lastPrice, 2)

        #组成dict
        quoteData[contract] = contractData

    #关闭wind接口
    # w.stop()
    quoteData = [(k, quoteData[k]) for k in sorted(quoteData.keys())]
    logger.info(quoteData)

    return quoteData
'''