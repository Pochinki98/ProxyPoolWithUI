# encoding: utf-8

import datetime

class Proxy(object):
    """
    代理，用于表示数据库中的一个记录
    """

    ddl = """
    CREATE TABLE IF NOT EXISTS proxies
    (
        fetcher_name VARCHAR(255) NOT NULL,
        protocal VARCHAR(32) NOT NULL,
        ip VARCHAR(255) NOT NULL,
        port INTEGER NOT NULL,
        validated BOOLEAN NOT NULL,
        validate_date TIMESTAMP,
        to_validate_date TIMESTAMP NOT NULL,
        validate_failed_cnt INTEGER NOT NULL,
        PRIMARY KEY (protocal, ip, port)
    )
    """

    def __init__(self):
        self.fetcher_name = None
        self.protocal = None
        self.ip = None
        self.port = None
        self.validated = False
        self.validate_date = None
        self.to_validate_date = datetime.datetime.now()
        self.validate_failed_cnt = 0
    
    def params(self):
        """
        返回一个元组，包含自身的全部属性
        """
        return (
            self.fetcher_name,
            self.protocal, self.ip, self.port,
            self.validated, self.validate_date, self.to_validate_date, self.validate_failed_cnt
        )
    
    def to_dict(self):
        """
        返回一个dict，包含自身的全部属性
        """
        return {
            'fetcher_name': self.fetcher_name,
            'protocal': self.protocal,
            'ip': self.ip,
            'port': self.port,
            'validated': self.validated,
            'validate_date': str(self.validate_date) if self.validate_date is not None else None,
            'to_validate_date': str(self.to_validate_date) if self.to_validate_date is not None else None,
            'validate_failed_cnt': self.validate_failed_cnt
        }
    
    @staticmethod
    def decode(row):
        """
        将sqlite返回的一行解析为Proxy
        row : sqlite返回的一行
        """
        assert len(row) == 8
        p = Proxy()
        p.fetcher_name = row[0]
        p.protocal = row[1]
        p.ip = row[2]
        p.port = row[3]
        p.validated = bool(row[4])
        p.validate_date = row[5]
        p.to_validate_date = row[6]
        p.validate_failed_cnt = row[7]
        return p
    
    def validate(self, success):
        """
        传入一次验证结果，根据验证结果调整自身属性，并返回是否删除这个代理
        success : True/False，表示本次验证是否成功
        返回 : True/False，True表示这个代理太差了，应该从数据库中删除
        """
        if success: # 验证成功
            self.validated = True
            self.validate_date = datetime.datetime.now()
            self.validate_failed_cnt = 0
            self.to_validate_date = datetime.datetime.now() + datetime.timedelta(minutes=5) # 5分钟之后继续验证
            return False
        else:
            self.validated = False
            self.validate_date = datetime.datetime.now()
            self.validate_failed_cnt = self.validate_failed_cnt + 1

            # 验证失败的次数越多，距离下次验证的时间越长
            delay_minutes = self.validate_failed_cnt * 5
            self.to_validate_date = datetime.datetime.now() + datetime.timedelta(minutes=delay_minutes)

            if self.validate_failed_cnt >= 3:
                return True
            else:
                return False
