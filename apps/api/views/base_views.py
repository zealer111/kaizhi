"""base views"""
from django.views.generic.base import View
from django.http import HttpResponse
import json
from libs import des_encryption

class BaseHandler(View):
    def write_json(self, _dict):
        """return json obj"""
        return HttpResponse(json.dumps(_dict, indent=4, sort_keys=False, ensure_ascii=False), content_type='application/json')

    def hash_file_path(self, path):
        '''文件目录地址加密方法'''

        des = des_encryption.DESEncryp()
        key = path.encode('utf-8')
        return des.encrypt(key).decode()
        
