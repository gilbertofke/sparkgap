from sparkgap.masking import mask


def test_keeps_first_and_last_two_characters():
    assert mask("abcdefghij") == "ab****ij"


def test_hides_length_of_long_values():
    assert mask("a" * 12) == mask("a" * 40)


def test_fully_masks_short_values():
    assert mask("abcdefgh") == "****"


def test_empty_value_stays_empty():
    assert mask("") == ""
