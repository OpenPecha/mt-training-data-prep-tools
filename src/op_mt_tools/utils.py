import os
import subprocess
from pathlib import Path
from typing import Tuple

from git import Repo, cmd
from openpecha.core import metadata
from openpecha.core.pecha import OpenPechaGitRepo

INITIAL_PECHA_ID = str  # OpenPecha initial pecha id
OPEN_PECHA_ID = str  # OpenPecha open pecha id


def create_pecha(
    path: Path, output_path: Path = None, publish=True
) -> Tuple[INITIAL_PECHA_ID, OPEN_PECHA_ID]:
    """create InitialPecha and OpenPecha from text files in path.

    Args:
        path (Path): path to text files
        publish (bool, optional): publish pecha to OpenPecha-Data. Defaults to True.

    Returns:
        tuple[str, str]: pecha_id of InitialPecha and OpenPecha
    """

    initial_pecha_meta = metadata.InitialPechaMetadata()
    open_pecha_meta = metadata.OpenPechaMetadata()

    OpenPechaGitRepo.is_private = (
        True  # TODO: make self.publish accept is_private param
    )
    initial_pecha = OpenPechaGitRepo(metadata=initial_pecha_meta)
    open_pecha = OpenPechaGitRepo(metadata=open_pecha_meta)

    for fn in path.glob("*.txt"):
        text = fn.read_text(encoding="utf-8")
        initial_pecha.set_base(text)
        open_pecha.set_base(text)

    initial_pecha.save(output_path=output_path)
    open_pecha.save(output_path=output_path)

    if publish:
        initial_pecha.publish(branch="master")
        open_pecha.publish(branch="master")

    return initial_pecha.pecha_id, open_pecha.pecha_id


def get_pkg_version():
    """get metadata of package

    Returns:
        dict: metadata of package
    """
    import pkg_resources

    return pkg_resources.get_distribution("op-mt-tools").version


def commit_and_push(collection_path: Path) -> None:
    """Commit and push collection."""
    # configure git users
    subprocess.run(
        f"git config --global user.name {os.environ['GITHUB_USERNAME']}".split()
    )
    subprocess.run(
        f"git config --global user.email {os.environ['GITHUB_EMAIL']}".split()
    )
    repo = Repo(collection_path)
    repo.git.add(".", "--all")
    repo.git.commit("-m", "Add text pair")
    repo.remotes.origin.push()


def clone_or_pull_repo(repo_url: str, local_repo_path: Path) -> None:
    """Clone or pull repo."""
    if local_repo_path.is_dir():
        repo = Repo(local_repo_path)
        repo.remotes.origin.pull()
    else:
        try:
            Repo.clone_from(repo_url, str(local_repo_path))
        except cmd.GitCommandError as e:
            print(e)
            raise ValueError(f"Repo({repo_url}) doesn't exist")
