
CREATE TABLE FUT_CONTRACT_INFO (
contractid TEXT NOT NULL,
sccode TEXT NULL,
mfprice TEXT NULL,
contractmultiplier TEXT NULL,
ltdated TEXT NULL,
ddated TEXT NULL,
changelt TEXT NULL,
punit TEXT NULL,
marign TEXT NULL,
lastdelivery_date DATE NULL,
lasttrade_date DATE NULL
)



OB_OBJECT_ID 对象ID VARCHAR2(38)       原始 
F1_3512 标准合约代码 VARCHAR2(20)       原始 
F2_3512 标准合约名称 VARCHAR2(40)       原始 
F3_3512 合约规格 NUMBER(20, 4) 每手交易单位     原始 
F4_3512 最小报价单位说明 VARCHAR2(200)       原始 
F5_3512 合约乘数 NUMBER(20, 4)       原始 
F6_3512 最小报价单位[英文] VARCHAR2(200)       原始 
F7_3512 [废弃]涨跌停板幅度(%) NUMBER(20, 4)   ％   原始 
F8_3512 [废弃]保证金比例(%) NUMBER(20, 4)   ％   原始 
F9_3512 最后交易日说明 VARCHAR2(200)       原始 
F10_3512 交割日期说明 VARCHAR2(400)       原始 
F11_3512 交割地点说明 VARCHAR2(400)       原始 
F12_3512 交割方式 VARCHAR2(400)       原始 
F13_3512 上市交易所英文简称 VARCHAR2(20)     指向：TB_OBJECT_0002.F1_0002
关联条件：TB_OBJECT_3512.F13_3512=TB_OBJECT_0002.F4_0002 原始 
F14_3512 交易计量单位 VARCHAR2(40)       原始 
F15_3512 标准合约名称(英文) VARCHAR2(100)       原始 
F16_3512 合约月份说明[英文] VARCHAR2(200)       原始 
F17_3512 合约上市日期 VARCHAR2(8)       原始 
F18_3512 交易时间说明 VARCHAR2(800)       原始 
F19_3512 最后交易日交易时间说明 VARCHAR2(400)       原始 
F20_3512 合约价值说明 VARCHAR2(200)       原始 
F21_3512 日涨跌幅限制说明 VARCHAR2(800)       原始 
