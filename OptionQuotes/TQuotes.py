from django.shortcuts import render
import datetime, re, json, logging
from . import TYApi
from django.http import JsonResponse
# from WindPy import w

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import loadDataModel
from .serializers import loadTDataSerializer


'''
日志模块加载
'''
logger = logging.getLogger('SwhyDataAnalytic.Debug')

'''
加载主页面
'''
def loadPage(request, instrument):
    return render(request, 'TQuotes.html')


'''
传递参数:
    1. instrument 期货品种
    2. qixian 期权到期期限
    3. dateselect 价格日期
返回参数：
    1. quoteData 行情序列
'''


class loadTData(APIView):

    def get(self, request, format=None):
        modelObject = loadDataModel.objects.all()
        serializer = loadTDataSerializer(modelObject, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):

        try:
            qixian = int(request.data['qixian'])
            instrument = request.data['instrument']

        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        # 获取同余数据
        quoteData = GetTQuotesData(qixian, instrument)
        serializer = loadTDataSerializer(data=quoteData)


        if serializer.is_valid():
            # serializer.save()
            # json_dumps_params为json.dumps的参数
            return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False, "sort_keys": True},
                                safe=False, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



'''
def loadTData(request, instrument):
            #获取同余数据
    if (request.method == 'POST'):
        try:
            qixian = request.POST['qixian']
#            selected_date = request.POST['dateselect']
            instrument = request.POST['instrument']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

        quoteData = GetTQuotesData(qixian, instrument)
        logger.info(quoteData)
        return JsonResponse(quoteData, safe=False)
'''

def GetTQuotesData(qixian, instrument):

    # 获得当前时间
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    time_zone = 'Asia/Shanghai'

    # 定价参数
    tau = 1/12  # 量
    r = 0.015  # 无风险利率

    if (qixian != 1):
        try:
            tau = int(qixian) / 12
#            if (selected_date!='当日'and selected_date!=''):
#                today = selected_date
#                yesterday = (datetime.date(*map(int, selected_date.split('-'))) + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

    # 初始化同余API
    tyApi = TYApi.TYApi()

    # 开启wind接口
    # w.start()
    #获取现价
    # forward = w.wsq(instrument, "rt_last").Data[0][0]
    forward = tyApi.TYMktQuoteGet(today, instrument, time_zone)

    # 关闭wind接口
    # w.stop()

    # 获取波动率曲线
    volSpread = tyApi.TYMdload('VOL_BLACK_ATM_' + re.sub(r'([\d]+)', '', instrument))
    # 获得波动率
    vol = tyApi.TYVolSurfaceImpliedVolGet(forward, forward, today, volSpread)

    #返回数据
    TData = {}
    #存储期权数据
    contractData = {}

    forwardList = getForwardList(forward)
    logger.info(forwardList)

    for price in forwardList:
        TQuoteData = {}
        pricingCallAsk = tyApi.TYPricing(forward, price, vol - 0.03, tau, r, 'call')
        pricingCallBid = tyApi.TYPricing(forward, price, vol + 0.03, tau, r, 'call')
        pricingPutAsk = tyApi.TYPricing(forward, price, vol - 0.03, tau, r, 'put')
        pricingPutBid = tyApi.TYPricing(forward, price, vol + 0.03, tau, r, 'put')
        TQuoteData['pricingCallAsk'] = str(round(pricingCallAsk, 2))
        TQuoteData['pricingCallBid'] = str(round(pricingCallBid, 2))
        TQuoteData['pricingPutAsk'] = str(round(pricingPutAsk, 2))
        TQuoteData['pricingPutBid'] = str(round(pricingPutBid, 2))
        price = str(price)
        contractData[price] = TQuoteData

    #对行权价排序
    contractData = [(k, contractData[k]) for k in sorted(contractData.keys())]
    TData['quoteData'] = contractData
    #获取限价和昨收价
    forward = tyApi.TYMktQuoteGet(today, instrument, time_zone)
    lastPrice = tyApi.TYMktQuoteGet(yesterday, instrument, time_zone, 'close', 'settle')
    TData['forward'] = str(round(forward, 2))
    TData['lastPrice'] = str(round(lastPrice, 2))

    return TData


'''
x<500 变动范围5, 500<x<2000 变动范围10, 2000<x<6000 变动范围50, 6000<x 变动范围100
'''


def getForwardList(forward):
    forwardList = []
    for i in range(0, 6):
        if(forward < 500):
            forwardList.append(round(forward, -1) - (i * 5))
        elif(forward < 2000 and forward >= 500):
            forwardList.append(round(forward, -1) - (i * 10))
        elif (forward < 6000 and forward >= 2000):
            forwardList.append(round(forward, -1) - (i * 50))
        elif (forward >= 6000):
            forwardList.append(round(forward, -1) - (i * 100))

    for i in range(1, 6):
        if(forward < 500):
            forwardList.append(round(forward, -1) + (i * 5))
        elif(forward < 2000 and forward >= 500):
            forwardList.append(round(forward, -1) + (i * 10))
        elif (forward < 6000 and forward >= 2000):
            forwardList.append(round(forward, -1) + (i * 50))
        elif (forward >= 6000):
            forwardList.append(round(forward, -1) + (i * 100))

    return forwardList

