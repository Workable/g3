from typing import Generator, List

from pydantic import BaseModel

from g3.config.exclude import EXCLUDED_FILES
from g3.git.shell import Shell


class Diff(BaseModel):
    filename: str
    patch: str


def get_filenames(sh: Shell) -> List[str]:
    return sh.git("diff", "--name-only", "--staged", "HEAD").splitlines()


def get_files_changed(sh: Shell) -> Generator[Diff, None, None]:
    diffs = get_filenames(sh)
    diffs = exclude_files(diffs)
    for diff in diffs:
        patch = sh.git("diff", "HEAD", "--function-context", diff)
        yield Diff(filename=diff, patch=patch)


def exclude_files(files: List[str]) -> List[str]:
    return list(filter(lambda x: x not in EXCLUDED_FILES, files))
