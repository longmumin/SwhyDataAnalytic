# import pandas as pd
# from datetime import datetime
#
# # from WindPy import *
#
# from django.shortcuts import render
# import json
#
# # 从wind取数有时间限制，15分钟只能取到最近3年的数据，所以取数的开始期限可以写在2014.06.02
# def GetDatafromWind(request):
#
#     #定义期货合约列表
#     contractList = ["CU1805.SHF","CU1803.SHF"]
#
#     #启动wind API
#     # w.start()
#
#     # #获得当前时间
#     # now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     # #开盘时间
#     # start = datetime.now().strftime("%Y-%m-%d") + " 09:00:00"
#     # startTime = datetime.strptime('2017-12-25 09:00:00', '%Y-%m-%d %H:%M:%S')
#     # endTime = datetime.strptime('2017-12-25 15:00:00', '%Y-%m-%d %H:%M:%S')
#     # print(startTime)
#     startTime = "2017-12-25 09:00:00"
#     endTime = "2017-12-25 15:00:00"
#
#     # 定义panel
#     panel = {}
#     for contract in contractList:
#
#         #从wind取数
#         quoteData = w.wsi(contract, "open,high,low,close", startTime, endTime, "BarSize=5")
#
#         #时间序列格式调整
#         timeList = quoteData.Times
#         for i in range(len(timeList)):
#             timeList[i] = timeList[i].strftime('%Y-%m-%d %H:%M:%S')
#
#         #包装成DataFrame
#         df = pd.DataFrame([quoteData.Data[0], quoteData.Data[1], quoteData.Data[2], quoteData.Data[3]],
#                       columns = timeList,
#                       index = ['open','high','low','close'])
#         panel[contract] = df
#
#     #计算价差
#     panel['priceDiff'] = panel[contractList[0]] / panel[contractList[1]]
#
#     #压缩为JsonData
#     json_data = panel['priceDiff'].to_json()
#     print(json_data)
#
#     return render(request, 'index.html', {  # 这里会指定到index.html下,把data1传输过去，对应变量名为series
#         'series': json_data})
#
