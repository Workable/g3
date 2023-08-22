from typing import Optional

from github import Auth, Github
from github.Commit import Commit
from github.PullRequest import PullRequest

from g3.config import config
from g3.services.git.gitinfo import GitInfo


class Client:
    def __init__(self):
        self.github_token = config.github_token
        self.g = Github(auth=Auth.Token(self.github_token))
        git_info = GitInfo()
        self.repo = self.g.get_repo(f"{git_info.repo_owner}/{git_info.repo}")
        self.head = git_info.branch

    def get_commit(self, commit_hash: Optional[str] = None) -> Optional[Commit]:
        return self.repo.get_commit(sha=commit_hash) if commit_hash else None

    def get_pull_request(self, id) -> PullRequest:
        return self.repo.get_pull(id)

    def create_pull_request(self, title, body, base=None) -> PullRequest:
        if base is None:
            base = self.repo.default_branch

        return self.repo.create_pull(title=title, body=body, head=self.head, base=base)

    def update_pull_request(self, id, title, body):
        pull = self.get_pull_request(id)
        return pull.edit(title=title, body=body)
