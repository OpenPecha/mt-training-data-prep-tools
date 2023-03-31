from pathlib import Path
from typing import Tuple

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
