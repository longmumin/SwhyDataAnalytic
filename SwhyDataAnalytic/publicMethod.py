from django.http import JsonResponse
from django.db import connection
import json, logging, tushare, datetime

'''
日志模块加载
'''
logger = logging.getLogger('SwhyDataAnalytic.Debug')

def getSysCode(request):
    #获取request中的数据
    if (request.method == 'POST'):
        try:
            codeType = request.POST['codeType']
        except Exception as e:
            logger.error("get request error, ret = %s" % e.args[0])

    # 建立数据库连接
    cursor = connection.cursor()
    # 查询数据
    try:
        cursor.execute("select sys_code.code, sys_code.codename, sys_code.sortorder from sys_code where codetype = %s", [codeType])
    except Exception as e:
        logger.error("select table failed, ret = %s" % e.args[0])
        cursor.close()

    codeData = cursor.fetchall()
    cursor.close()
    codeData = sorted(codeData, key=lambda s: s[2])
    keys = ['val', 'text', 'sortorder']
    codeData = list2dict_array(keys, codeData)
    #logger.info(codeData)
    return JsonResponse(json.dumps(codeData, ensure_ascii=False, sort_keys=True), safe=False)


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


def list2dict_array(keys, values):
    dictData = []
    for value in values:
        row = {}
        value = list(value)
        for i in range(0, len(keys)):
            row[keys[i]] = str(value[i])
        dictData.append(row)
    return dictData

def list2array(data):
    dictData = []
    for value in data:
        row = []
        value = list(value)
        for i in range(0, len(value)):
            row.append(value[i])
        #时间戳作为keys
        dictData.append(row)
    return dictData

#输入为string类型
def getLastTradeDate(date):
    # 判断节假日
    while (tushare.is_holiday(date)):
        # 类型转换
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date + datetime.timedelta(days=-1)
        date = date.strftime('%Y-%m-%d')
    return date