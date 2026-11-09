"""Basic checklist loading tests."""

from src.checklist import get_checklist, load_checklists


def test_checklists_load_with_five_items_per_equipment() -> None:
    checklists = load_checklists()

    assert set(checklists) == {"IT equipment", "Lab instruments"}
    assert all(len(category["inspection_items"]) == 5 for category in checklists.values())
    assert checklists["IT equipment"]["equipment_options"] == ["Desktop computer", "Projector"]


def test_get_checklist_returns_desktop_checklist() -> None:
    assert len(get_checklist("IT equipment")) == 5
