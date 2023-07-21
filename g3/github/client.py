from github import Github
from github.PullRequest import PullRequest

from g3.config import config
from g3.git.gitinfo import GitInfo


class Client:
    def __init__(self):
        self.github_token = config.github_token
        self.g = Github(self.github_token)
        git_info = GitInfo()
        self.repo = self.g.get_repo(f"{git_info.repo_owner}/{git_info.repo}")
        self.head = git_info.branch

    def open_pull_request(self, title, body, base=None) -> PullRequest:
        if base is None:
            base = self.repo.default_branch

        return self.repo.create_pull(title=title, body=body, head=self.head, base=base)
