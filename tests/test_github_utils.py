import pytest

from op_mt_tools.github_utils import get_github_repos_with_prefix


@pytest.mark.skip(reason="Calling external API")
def test_get_github_repos_with_prefix():
    import os

    org = os.environ["MAI_GITHUB_ORG"]
    token = os.environ["GITHUB_TOKEN"]
    prefix = "TM"

    repos = get_github_repos_with_prefix(org, token, prefix)

    assert repos
