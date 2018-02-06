from django.http import JsonResponse
from django.db import connection
import json

def getSysCode(request):
    #获取request中的数据
    if (request.method == 'POST'):
        try:
            codeType = request.POST['codeType']
        except Exception as e:
            print("get request error, ret = %s" % e.args[0])

    # 建立数据库连接
    cursor = connection.cursor()
    # 查询数据
    try:
        cursor.execute("select sys_code.code, sys_code.codename, sys_code.sortorder from sys_code where codetype = %s", [codeType])
    except Exception as e:
        print("select table failed, ret = %s" % e.args[0])
        cursor.close()

    codeData = cursor.fetchall()
    cursor.close()
    codeData = sorted(codeData, key=lambda s: s[2])
    keys = ['val', 'text', 'sortorder']
    codeData = list2dict(keys, codeData)
    print(codeData)
    return JsonResponse(json.dumps(codeData, ensure_ascii=False, sort_keys=True), safe=False)


def list2dict(keys, values):
    dictData = []
    for value in values:
        row = {}
        value = list(value)
        for i in range(0, len(keys)):
            row[keys[i]] = str(value[i])
        #时间戳作为keys
        dictData.append(row)
    return dictData