import pytest

from takeoff_bench import prompts
from takeoff_bench.schema import Item


def item() -> Item:
    return Item(
        item_id="x",
        family="f",
        sheet="s.pdf",
        page=1,
        question="Trace every room.",
        convention="Use the inside face of walls. Include every instance on the sheet.",
        output_type="polygons",
        gt="g.json",
    )


def test_baseline_contains_all_sections():
    text = prompts.build_prompt(item(), "baseline")
    assert text.startswith("Task:")
    assert "Convention:" in text
    assert "Coordinates are normalized" in text
    assert text.rstrip().endswith(prompts.SCHEMAS["polygons"])


def test_schema_first_moves_schema_to_front():
    text = prompts.build_prompt(item(), "schema_first")
    assert text.startswith("Return exactly this JSON shape:")
    assert text.count(prompts.SCHEMAS["polygons"]) == 1
    assert "Task:" in text


def test_compressed_preserves_constraint_text():
    text = prompts.build_prompt(item(), "compressed")
    assert "Include every instance on the sheet." in text
    assert "Do not merge adjacent instances" in text
    assert "\n\n" in text  # still separates the schema instruction


def test_control_drops_two_constraints_only():
    text = prompts.build_prompt(item(), "control_drop_constraints")
    assert "Include every instance on the sheet." not in text
    assert "Do not merge adjacent instances" not in text
    assert "Emit one closed polygon per real-world instance." in text


def test_variants_are_distinct():
    texts = {variant: prompts.build_prompt(item(), variant) for variant in prompts.VARIANTS}
    assert len(set(texts.values())) == len(texts)


def test_unknown_variant_rejected():
    with pytest.raises(ValueError, match="unknown prompt variant"):
        prompts.build_prompt(item(), "nope")
