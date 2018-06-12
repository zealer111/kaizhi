#--*--coding:utf-8--*--
from apps.api.views.base_views import BaseHandler
from apps.api.utils import auth_decorator
from apps.api.logger import logger_decorator
from django.http import HttpResponse
from django.db import transaction
import json
import os
import re
import base64
from libs import git_client, des_encryption
from apps import settings
import shutil,string
from dulwich.repo import Repo
import git

import logging
logging.basicConfig(filename='/tmp/gitserver.log',level=logging.DEBUG)

from apps import log_utils
log_utils.default_logging_config()

logger = log_utils.getLogger(__name__)


class InitRepo(BaseHandler):
    # 创建git 仓库
    def post(self, request):
        dir_name = request.POST.get('dirname')
        branch = request.POST.get('branch', 'master')
        if not dir_name:
            return self.write_json({'errno': '100', 'msg': 'invalid params dirname'})
        repo_path = os.path.join(settings.REPO_ROOT, dir_name)
        client = git_client.GitServer(repo_path)
        #client.initRepo()
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        x = Repo.init(repo_path)
        client.cli.checkout(b=branch)
        file_path = os.path.join(repo_path, '.branch')
        with open(file_path, 'w+') as md:
            md.write('# create branch')

        client.cli.add(file_path)
        client.cli.commit(m='create branch %s' % file_path)
        result = {
            'errno': '0',
            'msg': 'success',
            'data': {
                'branch': branch,
                'repo': repo_path,
                'key': self.hash_file_path(repo_path)
            }
        }
        return self.write_json(result)


class Delete_Repo(BaseHandler):
    @auth_decorator
    def post(self,request):
        logger.info("Delete_Repo: %s %s" % (self.repo, self. branch))
        client = git_client.GitServer(self.repo)
        client.cli.checkout(self.branch)
        shutil.rmtree(self.repo)
        return self.write_json({'errno':'0','msg':'success'})


class Delete_Folder(BaseHandler):
    @auth_decorator
    def post(self,request):
        dir_name = request.POST.get('dir_name')
        logger.info("Delete_Folder: %s %s %s" % (self.repo, self.branch,dir_name))
        try:
            shutil.rmtree(dir_name)
        except:
            logger.info("Folder isnot exist : %s" % (dir_name,))
        client = git_client.GitServer(self.repo)
        client.cli.checkout(self.branch)
        client.cli.add('.')
        try:
            client.cli.commit(m='delete %s' % dir_name)
        except:
            logger.info("Folder is blank: %s" % (dir_name,))
        return self.write_json({'errno':'0','msg':'success'})


class Delete_File(BaseHandler):
    @auth_decorator
    def post(self,request):
        dir_name = request.POST.get('dir_name')
        logger.info("Delete_file: %s %s %s" % (self.repo, self.branch,dir_name))
        client = git_client.GitServer(self.repo)
        client.cli.checkout(self.branch)
        os.remove(dir_name)
        client.cli.add('.')
        client.cli.commit(m='delete %s' % dir_name)
        return self.write_json({'errno':'0','msg':'success'})


class Rename_Repo(BaseHandler):
    def post(self, request):
        print(request.POST)
        dir_name = request.POST.get('dirname')
        new_dir_name = request.POST.get('new_dirname')
        branch = request.POST.get('branch', 'master')
        path = request.POST.get('path')
        logger.info("Rename_Repo: %s %s %s %s %s" % (self.repo,branch,dir_name,new_dir_name,path))
        if not dir_name:
            return self.write_json({'errno': '100', 'msg': 'invalid params dirname'})
        repo_path = os.path.join(settings.REPO_ROOT, new_dir_name)
        os.rename(path,repo_path)
        result = {
            'errno': '0',
            'msg': 'success',
            'data': {
                'branch': branch,
                'repo': repo_path,
            }
        }
        return self.write_json(result)


class Rename_File(BaseHandler):
    @auth_decorator
    def post(self,request):
        _type = request.POST.get('_type')
        old_name = request.POST.get('old_name')
        new_name = request.POST.get('new_name')
        path = request.POST.get('path')
        folder_dir = request.POST.get('folder_dir')
        branch = request.POST.get('branch', 'master')
        logger.info("Rename_File: %s %s %s %s %s %s %s" %
                    (self.repo,_type,old_name,new_name,path,folder_dir,branch))
        if 'folder_dir' in request.POST:
            if '0' == _type:
                repo_path = os.path.join(self.repo,new_name)
                os.rename(path,repo_path)
                result = {
                    'errno': '0',
                    'msg': 'success',
                    'data': {
                        'branch': branch,
                        'repo': repo_path,
                    }
                }
                return self.write_json(result)
            elif '1' == _type:
                client = git_client.GitServer(self.repo)
                client.cli.checkout(self.branch)
                repo_path = os.path.join(folder_dir,new_name)
                old_path = os.path.join(folder_dir,old_name)
                os.rename(path,repo_path)
                client.cli.add(old_path)
                client.cli.commit(m='old_name %s' % old_path)
                client.cli.add(repo_path)
                client.cli.commit(m='new_name %s' % repo_path)
                result = {
                    'errno': '0',
                    'msg': 'success',
                    'data': {
                        'branch': branch,
                        'repo': repo_path,
                    }
                }
                return self.write_json(result)
            return self.write_json('ok')
        else:
            if '0' == _type:
                repo_path = os.path.join(self.repo,new_name)
                os.rename(path, repo_path)
                result = {
                    'errno': '0',
                    'msg': 'success',
                    'data': {
                        'branch': branch,
                        'repo': repo_path,
                    }
                }
                return self.write_json(result)
            elif '1' == _type:
                client = git_client.GitServer(self.repo)
                client.cli.checkout(self.branch)
                repo_path = os.path.join(os.path.dirname(path),new_name)
                os.rename(path, repo_path)
                client.cli.add(repo_path)
                client.cli.commit(m='rename %s %s' % (path, repo_path))
                result = {
                    'errno': '0',
                    'msg': 'success',
                    'data': {
                        'branch': branch,
                        'repo': repo_path,
                    }
                }
                return self.write_json(result)
            return self.write_json('ok')


class Modify_File(BaseHandler):
    @auth_decorator
    def post(self,request):
        try:
            dir_name = request.POST.get('dir_name')
            path = request.POST.get('path')
            branch = request.POST.get('branch')
            content = request.POST.get('file_content')
            #print(request.POST)
            #print(branch)
            _type = request.POST.get('type')
            logger.info("Modify_File: %s %s %s %s %s" % (self.repo,dir_name,path,branch,_type))
            if '0' == request.POST.get('type'):
                client = git_client.GitServer(self.repo)
                client.cli.checkout(branch)
                with open(dir_name,'w+') as md:
                    md.write(content)

                client.cli.add(dir_name)
                client.cli.commit(m='modify %s' % dir_name)
                result = {
                    'errno': '0',
                    'msg': 'success',
                    'data': {
                        'branch': branch,
                    }
                }
            if '1' == request.POST.get('type'):
                client = git_client.GitServer(self.repo)
                client.cli.checkout(self.branch)
                with open(dir_name,'w+') as md:
                    md.write(content)

                client.cli.add(dir_name)
                client.cli.commit(m='modify %s' % dir_name)

                result = {
                    'errno': '0',
                    'msg': 'success',
                    'data': {
                        'branch': branch,
                    }
                }
            return self.write_json(result)
        except BaseException:
            logger.info("Modify_File: 内容无更改")
            return self.write_json({'errno':1,'msg':'内容无更改'})


class Commit_File(BaseHandler):
    # 提交变更
    @auth_decorator
    def post(self, request):
        merge_branch = request.POST.get('merge_branch')
        client = git_client.GitServer(self.repo)
        logger.info("Commit Conflict File: %s %s %s" % (self.repo,self.branch,merge_branch))
        if '1' == request.POST.get('type'):
            client.cli.add('.')
            client.cli.commit(m='commit conflict file')
            repo = git.Repo(self.repo)
            s = repo.git.merge(merge_branch)
        if '2' == request.POST.get('type'):
            client.cli.add('.')
            client.cli.commit(m='commit conflict file')
            repo = git.Repo(self.repo)
            s = repo.git.merge(self.branch)
        return self.write_json({'errno': '0', 'msg': 'success'})


class Recover_File(BaseHandler):
    @auth_decorator
    def post(self,request):
    #    try:
            path = request.POST.get('path')
            count = request.POST.get('count')
            print(count)
            client = git_client.GitServer(self.repo)
            client.cli.checkout(self.branch)
            repo = git.Repo(self.repo)
            logger.info("Recover File: %s %s %s %s" % (self.repo,self.branch,path,count))
            commit_id = repo.git.log(path,skip=count,n=1,format='%H')
            repo.git.checkout(commit_id,path)
    #        client.cli.add(path)
    #        client.cli.commit(m='recover file : %s '%(path))
    #        repo.head.reset(commit_id, index=True, working_tree=True)
            content = ''
            with open(path) as fp:
                for line in fp:
                    content += line
            result = {
                'errno': '0',
                'msg': 'success',
                'content':content,
            }
            return self.write_json(result)
    #    except BaseException:
    #        return self.write_json({'errno':1,'msg':'内容无更改！！！'})


class Modify_Discuss_File(BaseHandler):
    @auth_decorator
    def post(self,request):
        try:
            new_name = request.POST.get('new_name')
            path = request.POST.get('path')
            branch = request.POST.get('branch', 'master')
            content = request.POST.get('file_content')
            logger.info("Modify Discuss File File: %s %s %s %s %s" %
                        (self.repo,self.branch,merge_branch))
            repo_path = os.path.join(self.repo,new_name)
            os.rename(path,repo_path)
            with open(repo_path,'w+') as md:
                md.write(content)

            client = git_client.GitServer(self.repo)
            client.cli.add(repo_path)
            client.cli.commit(m='modify %s' % repo_path)
            client.cli.checkout(self.branch)
            result = {
                'errno': '0',
                'msg': 'success',
                'data': {
                    'branch': branch,
                    'repo': repo_path,
                }
            }
            return self.write_json(result)
        except BaseException:
            return self.write_json({'errno':'1','msg':'内容无更改！！！'})


class CreateNewBranch(BaseHandler):
    # 创建branch
    @auth_decorator
    def post(self, request):
        try:
            client = git_client.GitServer(self.repo)
            client.cli.checkout(b=self.branch)
    #    file_path = os.path.join(self.repo, '.branch')
    #    with open(file_path, 'w+') as md:
    #        md.write('create branch %s' % self.branch)
    #    client.cli.add(file_path)
    #    client.cli.commit(m='init branch %s' % file_path)
            return self.write_json({'errno': '0', 'msg': 'success', 'data': {'branch': self.branch}})
        except BaseException:
            return self.write_json({'errno': '1', 'msg': '分支已存在！！！'})


class Delete_Branch(BaseHandler):
    # 删除branch
    @auth_decorator
    def post(self, request):
        client = git_client.GitServer(self.repo)
        del_branch = request.POST.get('del_branch')
        client.cli.checkout('master')
        client.cli.branch(D=del_branch)
        return self.write_json({'errno': '0', 'msg': 'success'})


class File_Diff(BaseHandler):
    # 分支对比
    @auth_decorator
    def post(self, request):
     #   try:
            file_path = request.POST.get('file_path')
            assi_branch = request.POST.get('assi_branch')

            logger.info("File_Diff: %s %s %s %s %s" % (self.repo, assi_branch, request.POST.get('type'), request.POST.get('role'), file_path))
            if '0' == request.POST.get('type'):
                client = git_client.GitServer(self.repo)
                client.cli.checkout(self.branch)
                repo = git.Repo(self.repo)
                s = repo.git.diff('master',assi_branch,file_path)
                return self.write_json({'errno': '0', 'msg': 'success','data':s})

            if '1' == request.POST.get('type'):
                if settings.GIT_ROLE_MASTER_TYPE == request.POST.get('role'):
                    client = git_client.GitServer(self.repo)
                    client.cli.checkout(self.branch)
                    repo = git.Repo(self.repo)
                    s = repo.git.log('-p','^'+'master' ,assi_branch),
                    return self.write_json({'errno': '0', 'msg': 'success','data':s})
                if settings.GIT_ROLE_BRANCH_TYPE == request.POST.get('role'):
                    logger.debug("BRANCHE")
                    client = git_client.GitServer(self.repo)
                    client.cli.checkout(assi_branch)
                    repo = git.Repo(self.repo)
                    s = repo.git.log('-p','^'+assi_branch,'master')
                    return self.write_json({'errno': '0', 'msg': 'success','data':s})

                if '2' == request.POST.get('role'):
                    client = git_client.GitServer(self.repo)
                    client.cli.checkout(assi_branch)
                    repo = git.Repo(self.repo)
                    s = repo.git.log('-p',assi_branch ,'^'+'master'),
                    return self.write_json({'errno': '0', 'msg': 'success','data':s})

            if '2' == request.POST.get('type'):
                client = git_client.GitServer(self.repo)
                client.cli.checkout(self.branch)
                repo = git.Repo(self.repo)
                commit_id = repo.git.log(file_path,skip=1,n=1,format='%H')
                s = repo.git.diff(commit_id,file_path)
                return self.write_json({'errno': '0', 'msg': 'success','data':s})

      #  except BaseException :
      #      return self.write_json({'errno': '1', 'msg': '该文件为新文件！！！'})


class Merge_Branch(BaseHandler):
    # 合并分支
    @auth_decorator
    def post(self, request):
        try:
            client = git_client.GitServer(self.repo)
            merge_branch = request.POST.get('merge_branch')
            logger.info("File_Diff: %s %s %s" % (self.repo, self.branch, merge_branch))
            if '0' == request.POST.get('type'):
                client.cli.checkout(self.branch)
                repo = git.Repo(self.repo)
                s = repo.git.merge(merge_branch)

            if '1' == request.POST.get('type'):
                client.cli.checkout(merge_branch)
                repo = git.Repo(self.repo)
                s = repo.git.merge(self.branch)
            return self.write_json({'errno': '0', 'msg': 'success'})
        except BaseException as e:
            repo = git.Repo(self.repo)
            s = repo.git.diff('--diff-filter=M','--name-only')
            data = []
            print(s)
            print(e)
            if s:
                ss= s.split('\n')
                content = ''
                for sp in ss:
                    path = os.path.join(self.repo,sp)
                    with open(path) as fp:
                        for line in fp:
                            content += line
                    data.append({
                        'file':path,
                        'branch':self.branch,
                        'content':content
                    })
                return self.write_json({'errno': '1', 'msg':'合并文件有冲突！！！','data':data})
            else:
                return self.write_json({'errno': '1', 'msg':'合并文件有冲突！！！','data':data})


class Checkout_Master(BaseHandler):
    @auth_decorator
    def post(self, request):
        try:
            client = git_client.GitServer(self.repo)
            client.cli.checkout(self.branch)
            return self.write_json({'errno': '0', 'msg': 'success'})
        except BaseException :
            return self.write_json({'errno': '1', 'msg': '分支未变更，无法合并！！！'})


class NewDirPath(BaseHandler):
    # 创建 目录
    @auth_decorator
    def post(self, request):
        client = git_client.GitServer(self.repo)
        client.cli.checkout(self.branch)
        dir_path = request.POST.get('dir_name')
        logger.info("Create Dir: %s %s %s" % (self.repo, self.branch, dir_path))
        if not dir_path:
            return self.write_json({'errno': '100', 'msg': 'invalid params'})
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        result = {
            'errno': '0',
            'msg': 'success',
            'data': {
                'key': self.hash_file_path(dir_path),
                'path': dir_path
            }
        }
        return self.write_json(result)


class CreateGitFile(BaseHandler):
    # 创建git 文件
    @auth_decorator
    def post(self, request):
        try:
            file_path = request.POST.get('dir_name')
            content = request.POST.get('file_content', '')
            if not file_path:
                return self.write_json({'errno': '100', 'msg': 'invalid params'})

            client = git_client.GitServer(self.repo)
            client.cli.checkout(self.branch)
            file_dir_path = os.path.dirname(file_path)

            logger.info("Create File: %s %s %s %s" % (self.repo, self.branch,file_path,content))
            if not os.path.exists(file_dir_path):
                os.makedirs(file_dir_path)

            with open(file_path, 'w+') as md:
                md.write(content)
            client.cli.add(file_path)
            client.cli.commit(m='create %s' % file_path)
            repo = git.Repo(self.repo)
            return self.write_json({'errno': '0', 'msg': 'success', 'data': {'repo':file_path}})
        except BaseException as e:
            return self.write_json({'errno': '1', 'msg': str(e)})


class Copy_File(BaseHandler):
    # 复制git 文件
    @auth_decorator
    def post(self, request):
        try:
            file_path = request.POST.get('dir_name')
            file_dir = request.POST.get('file_dir')
            path = request.POST.get('path')
            client = git_client.GitServer(self.repo)
            client.cli.checkout(self.branch)
            logger.info("Copy File: %s %s %s %s %s" % (self.repo,self.branch,file_path,file_dir,path))
            if '0' == request.POST.get('type'):
                shutil.copy(file_path,file_dir)
                client.cli.add('.')
                client.cli.commit(m='copy %s' % file_path + '  to  ' + file_dir)
                return self.write_json({'errno': '0', 'msg': 'success', 'data': {'repo':file_path}})
            if '1' == request.POST.get('type'):
                shutil.move(file_path,file_dir)

                client.cli.add(file_path)
                client.cli.commit(m='move  %s' % file_path)
                client.cli.add(path)
                client.cli.commit(m='move file %s' % path)
                return self.write_json({'errno': '0', 'msg': 'success', 'data': {'repo':file_path}})
        except BaseException as e:
            return self.write_json({'errno': '1', 'msg': str(e)})


class GitFiles(BaseHandler):

    # 获取 卡包 git 文件目录结构

    def path_to_dict(self, path):
        d = {'title': os.path.basename(path), 'key': self.hash_file_path(path)}
        if os.path.isdir(path) and '.git' not in path:
            d['type'] = "directory"
            d['children'] = [self.path_to_dict(os.path.join(path,x)) for x in os.listdir\
    (path)]
        else:
            d['type'] = "file"
        return d

    @auth_decorator
    def post(self, request):
        data = {}
        if os.path.isdir(self.repo):
            client = git_client.GitServer(self.repo)
            client.cli.checkout(self.branch)
            data = self.path_to_dict(self.repo)
        return self.write_json({'errno': '0', 'msg': 'success', 'data': data})


class Get_Dir(BaseHandler):
    def post(self,request):
        print(request.POST)
        path = request.POST.get('repo')
        obj = {}
        lines = []
        myfiles = []

        for root, dirs, files in os.walk(path, topdown=False):
            """xx = root.split("/")
            for i in range(len(xx)):
                set_obj(obj, xx[:i-1], i, xx[i])
            """
            for name in sorted(dirs) :
                xx = os.path.join(root, name).replace(path,"")
                if xx and xx.find(".git")==-1:
                    line = "obj"+xx.replace("/","']['")[2:]+'\'] = {\'children\':[]}'
                    lines.append(line)
            for name in sorted(files):

                xx = os.path.join(root, name).replace(path,"")
                if xx and xx.find(".git")==-1:
                    rr = root.replace(path,"")
                    if len(rr.split("/")) > 1:
                        line = "obj"+rr.replace("/","']['")[2:]+'\'][\'children\'].append(\'%s\')' % name
                    else:
                        line = "obj['files'].append(\'%s\')" % name
                    myfiles.append(line)
                    pass

        lines.reverse()
        for ll in lines:
            exec(ll)
        myfiles.reverse()
        for ll in myfiles:
            exec(ll)
        __obj = obj
        xobj = []

        def _getobj(_obj):
            obj = []

            if type(_obj)==type({}):
                for k,v in _obj.items():
                    cc = v.get('children')
                    if cc:
                        xx = {"title":k,'type':'directory',"children":[],}
                        xx['children'] = _getobj(cc)
                        obj.append(xx)
                    else:
                        obj.append({"title":k})

            elif type(_obj)==type([]):
                for v in _obj:
                    obj.append({"title":v})
            else:
                 pass

            return obj

        xobj = _getobj(__obj)

        return self.write_json({'errno':0,'msg':'sucess','data':xobj})


class RepoFileContent(BaseHandler):
    # 获取文件内容
    @auth_decorator
    def post(self, request):
        try:
            file_path = request.POST.get('file_path')
            branch = request.POST.get('branch')
            logger.info("Get Content: %s %s %s" % (self.repo,branch,file_path))
            if not file_path:
                return self.write_json({'errno': '100', 'msg': 'invalid params'})

            client = git_client.GitServer(self.repo)
            client.cli.checkout(branch)
            content = ''
            with open(file_path) as fp:
                for line in fp:
                    content += line
            return self.write_json({'errno': '0', 'msg': 'success', 'data': {'content': content}})
        except BaseException as e:
            content = ''
            with open(file_path) as fp:
                for line in fp:
                    content += line
            return self.write_json({'errno': '0', 'msg': 'success', 'data': {'content': content}})





