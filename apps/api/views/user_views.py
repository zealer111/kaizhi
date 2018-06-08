#--*--coding:utf-8--*--
from apps.api.views.base_views import BaseHandler
from django.contrib.auth.models import User


class UserList(BaseHandler):
    def get(self, request):
        data = {
            'list': list(range(10)),
            'data': {
                'icon': list(range(20))
            },
        }
        return self.write_json({'errno': 0, 'msg': 'success', 'data': data})
