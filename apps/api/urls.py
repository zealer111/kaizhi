#coding:utf-8
from django.conf.urls import url
from .views import views, user_views


#base
urlpatterns = [
    url('^user/list', user_views.UserList.as_view()),
    url('^create/new/repo', views.InitRepo.as_view()),
    url('^create/new/dirpath', views.NewDirPath.as_view()),
    url('^create/new/branch', views.CreateNewBranch.as_view()),
    url('^create/filestream', views.CreateGitFile.as_view()),
    url('^repo/file/list', views.GitFiles.as_view()),
    url('^repo/get/dir', views.Get_Dir.as_view()),
    url('^delete/repo', views.Delete_Repo.as_view()),
    url('^delete/folder', views.Delete_Folder.as_view()),
    url('^delete/file', views.Delete_File.as_view()),
    url('^delete/branch', views.Delete_Branch.as_view()),
    url('^rename/repo', views.Rename_Repo.as_view()),
    url('^rename/file', views.Rename_File.as_view()),
    url('^modify/discuss/file', views.Modify_Discuss_File.as_view()),
    url('^modify/file', views.Modify_File.as_view()),
    url('^repo/file/content', views.RepoFileContent.as_view()),
    url('^file/diff', views.File_Diff.as_view()),
    url('^copy/file', views.Copy_File.as_view()),
    url('^merge/branch', views.Merge_Branch.as_view()),
    url('^checkout/master', views.Checkout_Master.as_view()),
    url('^recover/file', views.Recover_File.as_view()),
    url('^commit/file', views.Commit_File.as_view()),
]
