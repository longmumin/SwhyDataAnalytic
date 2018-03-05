from django.shortcuts import render
from django.db import connection
import pandas as pd
from WindPy import *
from datetime import datetime

def insertDataToBondYTM(request):
    #建立wind连接
    w.start()

    #建立对应合约号和久期的dict
    durationDict = {'M1003983':'3M', 'M1003984':'6M', 'M1004093':'1Y', 'M1004094':'2Y', 'M1004095':'3Y', 'M1004096':'4Y',
                    'M1004097':'5Y', 'M1004098':'7Y', 'M1004099':'10Y', 'M1004122':'1M', 'M1004123':'3M', 'M1004124':'6M',
                    'M1004125':'9M', 'M1004126':'1Y', 'M1004127':'2Y', 'M1004128':'3Y', 'M1004129':'4Y', 'M1004130':'5Y',
                    'M1004131':'7Y', 'M1004132':'10Y', 'M1004136':'0Y', 'M1004677':'1M', 'M1004829':'2M', 'M1000155':'3M',
                    'M1000156':'6M', 'M1000157':'9M', 'M1000158':'1Y', 'M1000159':'2Y', 'M1000160':'3Y', 'M1000161':'4Y',
                    'M1000162':'5Y', 'M1000163':'6Y', 'M1000164':'7Y', 'M1000165':'8Y', 'M1004678':'9Y', 'M1000166':'10Y',
                    'M1000167':'15Y', 'M1000168':'20Y', 'M1000169':'30Y', 'M1004711':'40Y', 'M1000170':'50Y', 'M1004258':'0Y',
                    'M1004687':'1M', 'M1004259':'2M', 'M1004260':'3M', 'M1004261':'6M', 'M1004262':'9M', 'M1004263':'1Y',
                    'M1004264':'2Y', 'M1004265':'3Y', 'M1004266':'4Y', 'M1004267':'5Y', 'M1004268':'6Y', 'M1004269':'7Y',
                    'M1004270':'8Y', 'M1004688':'9Y', 'M1004271':'10Y', 'M1004272':'15Y', 'M1004273':'20Y', 'M1004274':'30Y',
                    'M1004275':'50Y', 'M1004138':'0Y', 'M1004685':'1M', 'M1000181':'3M', 'M1000182':'6M', 'M1000183':'9M',
                    'M1000184':'1Y', 'M1000185':'2Y', 'M1000186':'3Y', 'M1000187':'4Y', 'M1000188':'5Y', 'M1000189':'6Y',
                    'M1000190':'7Y', 'M1000191':'8Y', 'M1004686':'9Y', 'M1000192':'10Y', 'M1000193':'15Y', 'M1000194':'20Y',
                    'M1007661':'0Y', 'M1007662':'1M', 'M1007663':'3M', 'M1007664':'6M', 'M1007665':'9M', 'M1007666':'1Y',
                    'M1007667':'2Y', 'M1007668':'3Y', 'M1007669':'4Y', 'M1007670':'5Y', 'M1007671':'6Y', 'M1007672':'7Y',
                    'M1007673':'8Y', 'M1007674':'9Y', 'M1007675':'10Y', 'M1007676':'15Y', 'M1007677':'20Y'}

    # 建立数据库连接
    cursor = connection.cursor()

    #########SHIBOR3M############
    # 从wind获取利率互换
    windData = w.edb("M1003983, M1003984, M1004093, M1004094, M1004095, M1004096, M1004097, M1004098, "
                     "M1004099", "2018-02-25", "2018-02-25", "")

    #Wind数据整理
    timeList = [time.strftime('%Y-%m-%d') for time in windData.Times]
    print(windData)
    # 包装成DataFrame
    # df = pd.DataFrame([windData.Data], columns = windData.Codes, index = windData.Times)
    df = pd.DataFrame(index = timeList)
    for i in range(len(windData.Codes)):
        df[windData.Codes[i]] = windData.Data[i]
    print(df, len(df.index), len(df.columns))
    for i in range (0, len(df.index)):
        for j in range (0, len(df.columns)):
            print(i, j)
            print(df.iloc[i, j], df.index[i], df.columns[j])
            cursor.execute("INSERT INTO BONDYTM(BONDYTMTYPE, BONDID, BONDDURATION, BONDYTM, TIMESTAMP) "
                           "VALUES(%s, %s, %s, %s, %s)",('01', df.columns[j], durationDict[df.columns[j]], df.iloc[i, j], df.index[i]))

    #########SHIBOR3M############
    # 从wind获取利率互换
    windData = w.edb("M1004122, M1004123, M1004124, M1004125, M1004126,"
                    "M1004127, M1004128, M1004129, M1004130, M1004131, M1004132", "2018-02-15", "2018-02-24", "")

     # Wind数据整理
    timeList = [time.strftime('%Y-%m-%d') for time in windData.Times]
    print(windData)
    # 包装成DataFrame
    # df = pd.DataFrame([windData.Data], columns = windData.Codes, index = windData.Times)
    df = pd.DataFrame(index=timeList)
    for i in range(len(windData.Codes)):
        df[windData.Codes[i]] = windData.Data[i]
    print(df, len(df.index), len(df.columns))
    for i in range(0, len(df.index)):
        for j in range(0, len(df.columns)):
            print(i, j)
            print(df.iloc[i, j], df.index[i], df.columns[j])
            cursor.execute(
                "INSERT INTO BONDYTM(BONDYTMTYPE, BONDID, BONDDURATION, BONDYTM, TIMESTAMP) VALUES(%s, %s, %s, %s, %s)",
                ('06', df.columns[j], durationDict[df.columns[j]], df.iloc[i, j], df.index[i]))

    #########中债国债数据导入############
    windData = w.edb("M1004136,M1004677,M1004829,M1000155,M1000156,M1000157,M1000158,M1000159,M1000160,M1000161,"
          "M1000162,M1000163,M1000164,M1000165,M1004678,M1000166,M1000167,M1000168,M1000169,M1004711,M1000170",
        "2018-02-15", "2018-02-24", "")
    # Wind数据整理
    timeList = [time.strftime('%Y-%m-%d') for time in windData.Times]
    # 包装成DataFrame
    # df = pd.DataFrame([windData.Data], columns = windData.Codes, index = windData.Times)
    df = pd.DataFrame(index=timeList)
    for i in range(len(windData.Codes)):
        df[windData.Codes[i]] = windData.Data[i]
    print(df, len(df.index), len(df.columns))
    for i in range(0, len(df.index)):
        for j in range(0, len(df.columns)):
            print(i, j)
            print(df.iloc[i, j], df.index[i], df.columns[j])
            cursor.execute(
                "INSERT INTO BONDYTM(BONDYTMTYPE, BONDID, BONDDURATION, BONDYTM, TIMESTAMP) VALUES(%s, %s, %s, %s, %s)",
                ('02', df.columns[j], durationDict[df.columns[j]], df.iloc[i, j], df.index[i])
            )

    #########中债国开债数据导入############
    windData = w.edb("M1004258,M1004687,M1004259,M1004260,M1004261,M1004262,M1004263,M1004264,M1004265,M1004266,"
                     "M1004267,M1004268,M1004269,M1004270,M1004688,M1004271,M1004272,M1004273,M1004274,M1004275",
                     "2018-02-15", "2018-02-24", "")
    # Wind数据整理
    timeList = [time.strftime('%Y-%m-%d') for time in windData.Times]
    # 包装成DataFrame
    # df = pd.DataFrame([windData.Data], columns = windData.Codes, index = windData.Times)
    df = pd.DataFrame(index=timeList)
    for i in range(len(windData.Codes)):
        df[windData.Codes[i]] = windData.Data[i]
    print(df, len(df.index), len(df.columns))
    for i in range(0, len(df.index)):
        for j in range(0, len(df.columns)):
            print(i, j)
            print(df.iloc[i, j], df.index[i], df.columns[j])
            cursor.execute(
                "INSERT INTO BONDYTM(BONDYTMTYPE, BONDID, BONDDURATION, BONDYTM, TIMESTAMP) VALUES(%s, %s, %s, %s, %s)",
                ('03', df.columns[j], durationDict[df.columns[j]], df.iloc[i, j], df.index[i])
            )

    #########中债进出口债数据导入############
    windData = w.edb("M1004138,M1004685,M1000181,M1000182,M1000183,M1000184,M1000185,M1000186,M1000187,M1000188,"
                     "M1000189,M1000190,M1000191,M1004686,M1000192,M1000193,M1000194", "2018-02-15", "2018-02-24", "")
    # Wind数据整理
    timeList = [time.strftime('%Y-%m-%d') for time in windData.Times]
    # 包装成DataFrame
    # df = pd.DataFrame([windData.Data], columns = windData.Codes, index = windData.Times)
    df = pd.DataFrame(index=timeList)
    for i in range(len(windData.Codes)):
        df[windData.Codes[i]] = windData.Data[i]
    print(df, len(df.index), len(df.columns))
    for i in range(0, len(df.index)):
        for j in range(0, len(df.columns)):
            print(i, j)
            print(df.iloc[i, j], df.index[i], df.columns[j])
            cursor.execute(
                "INSERT INTO BONDYTM(BONDYTMTYPE, BONDID, BONDDURATION, BONDYTM, TIMESTAMP) VALUES(%s, %s, %s, %s, %s)",
                ('04', df.columns[j], durationDict[df.columns[j]], df.iloc[i, j], df.index[i])
            )

    #########中债农发行债数据导入############
    windData = w.edb("M1007661,M1007662,M1007663,M1007664,M1007665,M1007666,M1007667,M1007668,M1007669,M1007670,"
                     "M1007671,M1007672,M1007673,M1007674,M1007675,M1007676,M1007677", "2018-02-15", "2018-02-24", "")
    # Wind数据整理
    timeList = [time.strftime('%Y-%m-%d') for time in windData.Times]
    # 包装成DataFrame
    # df = pd.DataFrame([windData.Data], columns = windData.Codes, index = windData.Times)
    df = pd.DataFrame(index=timeList)
    for i in range(len(windData.Codes)):
        df[windData.Codes[i]] = windData.Data[i]
    print(df, len(df.index), len(df.columns))
    for i in range(0, len(df.index)):
        for j in range(0, len(df.columns)):
            print(i, j)
            print(df.iloc[i, j], df.index[i], df.columns[j])
            cursor.execute(
                "INSERT INTO BONDYTM(BONDYTMTYPE, BONDID, BONDDURATION, BONDYTM, TIMESTAMP) VALUES(%s, %s, %s, %s, %s)",
                ('05', df.columns[j], durationDict[df.columns[j]], df.iloc[i, j], df.index[i])
            )

    w.stop()

    #插入数据
    # cursor.execute("INSERT INTO test(num, data)VALUES(%s, %s)", (1, 'aaa'))
    print(cursor)
    cursor.close()
    return render(request, 'dao.html')

def insertDataToFutureInfo(request):
    contractCodeList = ['CU.SHF','AL.SHF','ZN.SHF','PB.SHF','NI.SHF','SN.SHF','AU.SHF',
                        'AG.SHF','RB.SHF','WR.SHF','HC.SHF','FU.SHF','BU.SHF','RU.SHF',
                        'WH.CZC','PM.CZC','CF.CZC','SR.CZC','TA.CZC','OI.CZC','RI.CZC',
                        'MA.CZC','FG.CZC','RS.CZC','RM.CZC','ZC.CZC','JR.CZC','LR.CZC',
                        'SF.CZC','SM.CZC','CY.CZC','AP.CZC','C.DCE','CS.DCE','A.DCE',
                        'B.DCE','M.DCE','Y.DCE','P.DCE','FB.DCE','BB.DCE','JD.DCE',
                        'I.DCE','V.DCE','PP.DCE','J.DCE','JM.DCE','I.DCE','IF.CFE',
                        'IC.CFE','IH.CFE','TF.CFE','T.CFE']

    # 建立wind连接
    w.start()

    # 建立数据库连接
    cursor = connection.cursor()

    fields = ["sccode", "mfprice", "contractmultiplier", "ltdated", "ddate", "changelt",
              "punit", "margin", "lasttrade_date", "lastdelivery_date", "contract_issuedate"]
    df = pd.DataFrame(index=fields)

    timeNow = datetime.now().strftime('%Y-%m-%d')
    print(timeNow)

    for contractCode in contractCodeList:
        windData1 = w.wset("futurecc", "startdate=2018-01-01;enddate=2018-02-28;wind_code=" + contractCode)
        print(windData1.Data[2])
        contractList = windData1.Data[2]
        for contract in contractList:
            # print(type(contract))
            windData2 = w.wsd(str(contract),
                              "sccode,mfprice,contractmultiplier,ltdated,ddate,changelt,"
                              "punit,margin,lasttrade_date,lastdelivery_date,contract_issuedate",
                              "2018-01-30", "2018-02-28", "")
            # print(windData2.Data, windData2.Codes)

            contractData = []
            for i in range(len(windData2.Data)):
                contractData.append(windData2.Data[i][len(windData2.Data[i]) - 1])
            print(len(contractData), len(contractList), len(windData2.Data), contractData)
            df[contract] = contractData
            # df = pd.DataFrame(contractData, index=contractList, columns=columns)

    print(df)

    for i in range(0, len(df.columns)):
        cursor.execute(
            "INSERT INTO fut_contract_info(contractid, sccode, mfprice, contractmultiplier, ltdated, ddated, changelt, punit,"
            "marign, lastdelivery_date, lasttrade_date, contract_issuedate, upg_date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (df.columns[i], df.iloc[0, i], df.iloc[1, i], df.iloc[2, i], df.iloc[3, i], df.iloc[4, i], df.iloc[5, i],
             df.iloc[6, i],
             df.iloc[7, i], df.iloc[8, i], df.iloc[9, i], df.iloc[10, i], timeNow))

    cursor.close()
    w.stop()

    return render(request, 'dao.html')


def insertDataToFutureDatabase(request):
    #获取当前时间
    timeNow = datetime.now().strftime('%Y-%m-%d')

    # 建立数据库连接
    cursor = connection.cursor()

    #取合约
    try:
        cursor.execute("select contract.contractid from fut_contract_info contract")
    except Exception as e:
        print("select table failed, ret = %s" % e.args[0])
        cursor.close()

    listData = cursor.fetchall()
    contractList = []
    for data in listData:
        contractList.append(data[0])
    print(contractList)

    w.start()

    #获取交易日
    windDate = w.tdays("2017-01-01", "2018-03-04", "")
    timeList = [time.strftime('%Y-%m-%d') for time in windDate.Times]
    fields = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'SETTLE', 'VOLUME', 'OI', 'AMT', 'CHG', 'CHG_SETTLEMENT', 'OI_CHG', 'PRE_SETTLE', 'DEALNUM']
    df = pd.DataFrame(index=timeList, columns=fields)

    for contract in contractList:
        print(contract)

        windData1 = w.wsd(contract,
                      "open,high,low,close,settle,volume,"
                      "oi,amt,chg,chg_settlement,oi_chg,pre_settle,dealnum,",
                      "2017-01-01", "2018-03-04", "")
        #print(windData1)
        #print(len(windData1.Data), len(windData1.Data[0]), len(windData1.Times))

        for i in range(0, len(windData1.Data)-1):
            df[windData1.Fields[i]] = windData1.Data[i]


        for i in range(0, len(df.index)):
            #print(df.index[i])

            cursor.execute(
                "INSERT INTO fut_mkt_quot_day(contractid, timestamp, open, high, low, close, settle, volume,"
                "oi, amt, chg, chg_settlement, oi_chg, pre_settle, dealnum, upd_time)"
                " VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (contract, df.index[i], df.iloc[i, 0], df.iloc[i, 1], df.iloc[i, 2], df.iloc[i, 3], df.iloc[i, 4], df.iloc[i, 5],
                    df.iloc[i, 6], df.iloc[i, 7], df.iloc[i, 8], df.iloc[i, 9], df.iloc[i, 10], df.iloc[i, 11], df.iloc[i, 12], timeNow))

    cursor.close()
    w.stop()

    return render(request, 'dao.html')

