from git import Repo
import os

class GitServer(object):

    def __init__(self, repo):
        self.repo_path = repo

    @property
    def cli(self):
        repo = Repo(self.repo_path)
        return repo.git

    def initRepo(self):
        '''
        init git
        '''
        if not os.path.isdir(self.repo_path):
            os.makedirs(self.repo_path)
        repo = Repo.init(self.repo_path)
        assert not repo.bare


if __name__ == '__main__':
    g = GitServer('/data/www/vhosts/kaizhi-git-server/repo/test-repo')
    print(g.initRepo())

