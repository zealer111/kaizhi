#coding: utf-8
from functools import wraps
from django.utils.decorators import available_attrs
import datetime
import json
import random
from django.http import HttpResponse
import time
from hashlib import md5
import re
import uuid
from django.forms import forms


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def write_json(obj):
    """return json obj"""
    return HttpResponse(json.dumps(obj), content_type='application/json')
    #return HttpResponse(json.dumps(obj))

def timestampTodate(timestamp):
    return datetime.fromtimestamp(timestamp)

def auth_decorator(method):
    """api 验证装饰器"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        branch = self.request.POST.get("branch", "").strip()
        repo = self.request.POST.get("repo", "").strip()
        if not branch or not repo:
            return write_json({"errno": 500, "msg": "branch or repo empty"})
        self.branch = branch
        self.repo = repo
        return method(self, *args, **kwargs)
    return wrapper


def separate(num):
    """千位分隔, 用于金额分隔"""
    try:
        num = float('%0.2f'% float(num))
        return '{:,}'.format(num)
    except Exception as e:
        return num

    #return num

def generate_password(password):
    """generate password"""
    pwd = "%s%s" % (password, "this_is_shennan_application")
    return md5(pwd).hexdigest()

def validate_phone(phone):
    return re.match(r'1(3|4|5|7|8)\d{9}', str(phone))

def get_random_code(length=6):
    """随机数"""
    return "".join(random.sample('0123456789', length))
