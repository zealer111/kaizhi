#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''des 加密解密'''
from pyDes import *
from binascii import b2a_hex, a2b_hex


class Singleton(type):
    '''单例模式类
    使用demo:

    class A:
        __metaclass__ = Singleton
    '''

    def __init__(self, name, bases, class_dict):
        super(Singleton, self).__init__(name, bases, class_dict)
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = super(Singleton, self).__call__(*args, **kwargs)
        return self._instance


class DESEncryp(object):
    '''DES 加密解密类'''

    __metaclass__ = Singleton

    def __init__(self):
        KEY = "BHC#@*UM"    #密钥
        IV = "abcdefgh"     #偏转向量
        # 使用DES对称加密算法的CBC模式加密
        self.des = des(KEY, CBC, IV, pad=None, padmode=PAD_PKCS5)

    def encrypt(self, data):
        '''加密'''
        return b2a_hex(self.des.encrypt(str(data)))

    def decrypt(self, str):
        '''解密'''
        return self.des.decrypt(a2b_hex(str))

if __name__ == '__main__':
    d = DESEncryp()
    enStr = d.encrypt('/data/www/vhosts/kaizhi-git-server/repos/repo-org')
    print(enStr)
    print(d.decrypt(enStr))
