from django.shortcuts import render

import re, datetime, os, json, math, time
import pandas as pd
from django.http import JsonResponse
# from WindPy import w

from . import TYApi

#读取期货合约
baseDir = os.path.dirname(os.path.abspath(__name__))
contractListFileDir = baseDir + '/files/BasicInfo/contractList.xlsx'
print(baseDir)
contractList = list(pd.read_excel(contractListFileDir)['contract'])
contractName = list(pd.read_excel(contractListFileDir)['name'])
contractList = dict(zip(contractList, contractName))


def loadPage(request):
    return render(request, 'quotes.html')

def loadData(request):
    #获取同余数据
    quoteData = GetQuotesDataFromTY(request)
    return JsonResponse(quoteData, safe=False)


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
            selected_date = request.POST['dateselect']
            if(selected_date!='当日'and selected_date!=''):
                #selected_date = time.strptime('%Y-%m-%d', request.POST['dateselect'])
                today = selected_date
                yesterday = (selected_date + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        except Exception as e:
            print("get request error, ret = %s" % e.args[0])

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

        pricingAsk = float(tyApi.TYPricing(forward, forward, vol - 0.03, tau, r, 'call'))
        # print(pricingAsk)
        #出错处理
        if(math.isnan(pricingAsk)):
            pricingAsk = float(0)
        pricingBid = float(tyApi.TYPricing(forward, forward, vol + 0.03, tau, r, 'call'))
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
    quoteData = [(k,quoteData[k]) for k in sorted(quoteData.keys())]
    print(quoteData)

    return quoteData
