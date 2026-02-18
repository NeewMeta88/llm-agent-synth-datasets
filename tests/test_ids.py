import pytest

from dataset_generator.core.ids import IdFactory, slugify


def test_prefix_applied() -> None:
    factory = IdFactory("uc_")
    assert factory.new("My Use Case") == "uc_my-use-case"


def test_uniqueness_on_collision() -> None:
    factory = IdFactory("tc_")
    first = factory.new("Same Seed")
    second = factory.new("Same Seed")
    third = factory.new("Same Seed")

    assert first != second
    assert second != third
    assert third.endswith("_3")


def test_slugify_stable() -> None:
    text = "  Hello,  World! "
    assert slugify(text) == "hello-world"
    assert slugify(text) == "hello-world"


def test_invalid_prefix() -> None:
    with pytest.raises(ValueError):
        IdFactory("bad_")
