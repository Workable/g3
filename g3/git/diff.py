from dataclasses import dataclass
from typing import Generator, List

from g3.git.shell import Shell


@dataclass
class Diff:
    filename: str
    patch: str


def get_filenames(sh: Shell) -> List[str]:
    return sh.git("diff", "--name-only", "--staged", "HEAD").splitlines()


def get_files_changed(sh: Shell) -> Generator[Diff, None, None]:
    diffs = get_filenames(sh)
    for diff in diffs:
        patch = sh.git("diff", "HEAD", "--function-context", diff)
        yield Diff(filename=diff, patch=patch)
