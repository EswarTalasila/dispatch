"""Location tiering: NC -> 0, TX -> 1, everywhere else -> 2, whole-word matching."""

import main
import server


def test_nc_variants():
    assert main.location_rank("Charlotte, NC") == 0
    assert main.location_rank("Raleigh, North Carolina") == 0
    assert main.location_rank("Durham, Research Triangle") == 0


def test_tx_variants():
    assert main.location_rank("Austin, TX") == 1
    assert main.location_rank("Dallas, Texas") == 1
    assert main.location_rank("Houston") == 1


def test_other_locations():
    assert main.location_rank("San Francisco, CA") == 2
    assert main.location_rank("Remote, US") == 2
    assert main.location_rank("") == 2


def test_nc_is_not_a_substring_match():
    # "nc" must not match inside unrelated words
    assert main.location_rank("Cincinnati, Ohio") == 2
    assert main.location_rank("Lawrenceville, GA") == 2


def test_server_tier_matches_main():
    assert server.location_tier("Charlotte, NC") == 0
    assert server.location_tier("Austin, TX") == 1
    assert server.location_tier("Cincinnati, OH") == 2
