import tempfile
from pathlib import Path

from op_mt_tools.utils import create_pecha


def test_create_pecha():
    # arrange
    text_path = Path("tests") / "data" / "text"

    # act
    with tempfile.TemporaryDirectory() as tmpdir:
        initial_pecha_id, open_pecha_id = create_pecha(
            text_path, publish=False, output_path=Path(tmpdir)
        )

    # assert
    assert initial_pecha_id
    assert open_pecha_id
    assert type(initial_pecha_id) == str
    assert type(open_pecha_id) == str
