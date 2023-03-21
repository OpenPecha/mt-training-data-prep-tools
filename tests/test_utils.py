from pathlib import Path

from op_mt_tools.utils import create_pecha


def test_create_pecha():
    # arrange
    text_path = Path("tests") / "data" / "text"

    # act
    initial_pecha_id, open_pecha_id = create_pecha(text_path, publish=False)

    # assert
    assert initial_pecha_id
    assert open_pecha_id
    assert type(initial_pecha_id) == str
    assert type(open_pecha_id) == str
