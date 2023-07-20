from dataclasses import dataclass
from typing import List

from g3.git.diff import Diff, get_filenames, get_files_changed
from g3.git.shell import Shell


@dataclass
class ModelData:
    filenames: List[str]
    diffs: List[Diff]
    repo_name: str
    branch_name: str


def get_data_for_model() -> ModelData:
    sh = Shell()
    assert sh.is_git()

    return ModelData(
        filenames=get_filenames(sh),
        diffs=[diff for diff in get_files_changed(sh)],
        repo_name=sh.repo_name,
        branch_name=sh.branch_name,
    )
