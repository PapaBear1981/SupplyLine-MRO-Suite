"""
Comprehensive tests for utils/lot_utils.py module.

Tests cover:
- Lot number generation with letter suffixes
- Child lot number sequencing
- Chemical splitting/transfer operations
- Lot lineage tracking (parent, children, siblings)
"""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from utils.lot_utils import (
    generate_child_lot_number,
    get_next_child_lot_number,
    create_child_chemical,
    get_lot_lineage
)
from models import Chemical, db


class TestGenerateChildLotNumber:
    """Tests for generate_child_lot_number function."""

    def test_sequence_zero_returns_a(self):
        """Sequence 0 should return suffix A."""
        result = generate_child_lot_number("LOT001", 0)
        assert result == "LOT001-A"

    def test_sequence_one_returns_b(self):
        """Sequence 1 should return suffix B."""
        result = generate_child_lot_number("LOT001", 1)
        assert result == "LOT001-B"

    def test_sequence_25_returns_z(self):
        """Sequence 25 should return suffix Z."""
        result = generate_child_lot_number("LOT001", 25)
        assert result == "LOT001-Z"

    def test_sequence_26_returns_aa(self):
        """Sequence 26 should return suffix AA."""
        result = generate_child_lot_number("LOT001", 26)
        assert result == "LOT001-AA"

    def test_sequence_27_returns_ab(self):
        """Sequence 27 should return suffix AB."""
        result = generate_child_lot_number("LOT001", 27)
        assert result == "LOT001-AB"

    def test_sequence_51_returns_az(self):
        """Sequence 51 should return suffix AZ."""
        result = generate_child_lot_number("LOT001", 51)
        assert result == "LOT001-AZ"

    def test_sequence_52_returns_ba(self):
        """Sequence 52 should return suffix BA."""
        result = generate_child_lot_number("LOT001", 52)
        assert result == "LOT001-BA"

    def test_sequence_701_returns_zz(self):
        """Sequence 701 should return suffix ZZ."""
        result = generate_child_lot_number("LOT001", 701)
        assert result == "LOT001-ZZ"

    def test_sequence_702_returns_aaa(self):
        """Sequence 702 should return suffix AAA."""
        result = generate_child_lot_number("LOT001", 702)
        assert result == "LOT001-AAA"

    def test_various_parent_lot_numbers(self):
        """Test with various parent lot number formats."""
        assert generate_child_lot_number("ABC123", 0) == "ABC123-A"
        assert generate_child_lot_number("LOT-2024-001", 0) == "LOT-2024-001-A"
        assert generate_child_lot_number("12345", 0) == "12345-A"
        assert generate_child_lot_number("X", 0) == "X-A"

    def test_empty_parent_lot_number(self):
        """Test with empty parent lot number."""
        result = generate_child_lot_number("", 0)
        assert result == "-A"

    def test_large_sequence_numbers(self):
        """Test with very large sequence numbers."""
        # Test that large sequences are handled correctly
        result = generate_child_lot_number("LOT", 18277)
        assert result.startswith("LOT-")
        assert len(result) > 5  # Should have multi-character suffix


class TestGetNextChildLotNumber:
    """Tests for get_next_child_lot_number function."""

    def test_first_child_lot_no_sequence(self, app, db_session, test_chemical):
        """Test getting first child lot when parent has no sequence set."""
        test_chemical.lot_sequence = None
        db_session.commit()

        child_lot, sequence = get_next_child_lot_number(test_chemical)

        assert child_lot == "L001-A"
        assert sequence == 0
        assert test_chemical.lot_sequence == 1

    def test_first_child_lot_sequence_zero(self, app, db_session, test_chemical):
        """Test getting first child lot when parent sequence is 0."""
        test_chemical.lot_sequence = 0
        db_session.commit()

        child_lot, sequence = get_next_child_lot_number(test_chemical)

        assert child_lot == "L001-A"
        assert sequence == 0
        assert test_chemical.lot_sequence == 1

    def test_second_child_lot(self, app, db_session, test_chemical):
        """Test getting second child lot number."""
        test_chemical.lot_sequence = 1
        db_session.commit()

        child_lot, sequence = get_next_child_lot_number(test_chemical)

        assert child_lot == "L001-B"
        assert sequence == 1
        assert test_chemical.lot_sequence == 2

    def test_increments_parent_sequence(self, app, db_session, test_chemical):
        """Test that parent's lot_sequence is properly incremented."""
        test_chemical.lot_sequence = 5
        db_session.commit()

        get_next_child_lot_number(test_chemical)

        assert test_chemical.lot_sequence == 6

    def test_collision_detection(self, app, db_session, test_chemical):
        """Test that collision detection increments sequence when lot exists."""
        test_chemical.lot_sequence = 0

        # Create a conflicting child lot
        conflicting_child = Chemical(
            part_number="C001",
            lot_number="L001-A",  # This would normally be the next child lot
            description="Conflicting Child",
            manufacturer="Test",
            quantity=10.0,
            unit="ml",
            location="Test",
            category="Testing",
            status="available"
        )
        db_session.add(conflicting_child)
        db_session.commit()

        child_lot, sequence = get_next_child_lot_number(test_chemical)

        # Should skip A and go to B due to collision
        assert child_lot == "L001-B"
        assert sequence == 1
        assert test_chemical.lot_sequence == 2

    def test_multiple_sequential_calls(self, app, db_session, test_chemical):
        """Test multiple sequential calls to get_next_child_lot_number."""
        test_chemical.lot_sequence = 0
        db_session.commit()

        # First call
        lot1, seq1 = get_next_child_lot_number(test_chemical)
        assert lot1 == "L001-A"
        assert seq1 == 0

        # Second call
        lot2, seq2 = get_next_child_lot_number(test_chemical)
        assert lot2 == "L001-B"
        assert seq2 == 1

        # Third call
        lot3, seq3 = get_next_child_lot_number(test_chemical)
        assert lot3 == "L001-C"
        assert seq3 == 2

        assert test_chemical.lot_sequence == 3


class TestCreateChildChemical:
    """Tests for create_child_chemical function."""

    def test_create_child_with_valid_quantity(self, app, db_session, test_chemical):
        """Test creating child chemical with valid quantity."""
        test_chemical.lot_sequence = 0
        test_chemical.expiration_date = date.today() + timedelta(days=365)
        test_chemical.minimum_stock_level = 10
        db_session.commit()

        child = create_child_chemical(test_chemical, 25)

        assert child.part_number == test_chemical.part_number
        assert child.lot_number == "L001-A"
        assert child.description == test_chemical.description
        assert child.manufacturer == test_chemical.manufacturer
        assert child.quantity == 25
        assert child.unit == test_chemical.unit
        assert child.location == test_chemical.location
        assert child.category == test_chemical.category
        assert child.status == "available"
        assert child.expiration_date == test_chemical.expiration_date
        assert child.minimum_stock_level == test_chemical.minimum_stock_level
        assert "Split from L001" in child.notes
        assert child.parent_lot_number == test_chemical.lot_number
        assert child.lot_sequence == 0

    def test_parent_quantity_reduced(self, app, db_session, test_chemical):
        """Test that parent quantity is reduced after split."""
        test_chemical.lot_sequence = 0
        initial_quantity = test_chemical.quantity  # 100
        db_session.commit()

        create_child_chemical(test_chemical, 30)

        assert test_chemical.quantity == initial_quantity - 30  # 70

    def test_parent_status_unchanged_when_not_depleted(self, app, db_session, test_chemical):
        """Test parent status remains unchanged when not fully depleted."""
        test_chemical.lot_sequence = 0
        test_chemical.status = "available"
        db_session.commit()

        create_child_chemical(test_chemical, 50)

        assert test_chemical.status == "available"
        assert test_chemical.quantity == 50

    def test_parent_status_depleted_when_fully_transferred(self, app, db_session, test_chemical):
        """Test parent status changes to depleted when fully transferred."""
        test_chemical.lot_sequence = 0
        test_chemical.status = "available"
        db_session.commit()

        create_child_chemical(test_chemical, 100)  # Transfer all

        assert test_chemical.status == "depleted"
        assert test_chemical.quantity == 0

    def test_warehouse_id_passed_to_child(self, app, db_session, test_chemical):
        """Test destination warehouse ID is set on child."""
        test_chemical.lot_sequence = 0
        db_session.commit()

        child = create_child_chemical(test_chemical, 20, destination_warehouse_id=5)

        assert child.warehouse_id == 5

    def test_kit_id_parameter_accepted(self, app, db_session, test_chemical):
        """Test destination kit ID parameter is accepted."""
        test_chemical.lot_sequence = 0
        db_session.commit()

        # The kit_id parameter is accepted but not stored on Chemical model
        # This tests that the function accepts the parameter without error
        child = create_child_chemical(test_chemical, 20, destination_kit_id=10)

        assert child is not None
        assert child.quantity == 20

    def test_zero_quantity_raises_error(self, app, db_session, test_chemical):
        """Test that zero quantity raises ValueError."""
        test_chemical.lot_sequence = 0
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            create_child_chemical(test_chemical, 0)

        assert "Quantity must be greater than 0" in str(exc_info.value)

    def test_negative_quantity_raises_error(self, app, db_session, test_chemical):
        """Test that negative quantity raises ValueError."""
        test_chemical.lot_sequence = 0
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            create_child_chemical(test_chemical, -10)

        assert "Quantity must be greater than 0" in str(exc_info.value)

    def test_excess_quantity_raises_error(self, app, db_session, test_chemical):
        """Test that quantity exceeding available raises ValueError."""
        test_chemical.lot_sequence = 0
        test_chemical.quantity = 50
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            create_child_chemical(test_chemical, 100)

        error_msg = str(exc_info.value)
        assert "Cannot transfer 100" in error_msg
        assert "Only 50" in error_msg
        assert test_chemical.unit in error_msg

    def test_exact_available_quantity_succeeds(self, app, db_session, test_chemical):
        """Test transferring exactly available quantity succeeds."""
        test_chemical.lot_sequence = 0
        test_chemical.quantity = 75
        db_session.commit()

        child = create_child_chemical(test_chemical, 75)

        assert child.quantity == 75
        assert test_chemical.quantity == 0
        assert test_chemical.status == "depleted"

    def test_child_notes_contain_parent_reference(self, app, db_session, test_chemical):
        """Test that child notes reference parent lot number."""
        test_chemical.lot_sequence = 0
        db_session.commit()

        child = create_child_chemical(test_chemical, 10)

        assert f"Split from {test_chemical.lot_number}" in child.notes

    def test_child_lot_sequence_starts_at_zero(self, app, db_session, test_chemical):
        """Test that child chemical starts with lot_sequence = 0."""
        test_chemical.lot_sequence = 5
        db_session.commit()

        child = create_child_chemical(test_chemical, 10)

        assert child.lot_sequence == 0

    def test_multiple_children_created_sequentially(self, app, db_session, test_chemical):
        """Test creating multiple children from same parent."""
        test_chemical.lot_sequence = 0
        test_chemical.quantity = 100
        db_session.commit()

        child1 = create_child_chemical(test_chemical, 30)
        child2 = create_child_chemical(test_chemical, 30)
        child3 = create_child_chemical(test_chemical, 30)

        assert child1.lot_number == "L001-A"
        assert child2.lot_number == "L001-B"
        assert child3.lot_number == "L001-C"
        assert test_chemical.quantity == 10
        assert test_chemical.status == "available"


class TestGetLotLineage:
    """Tests for get_lot_lineage function."""

    def test_lineage_for_standalone_chemical(self, app, db_session, test_chemical):
        """Test lineage for chemical with no parent or children."""
        test_chemical.parent_lot_number = None
        db_session.commit()

        lineage = get_lot_lineage(test_chemical)

        assert lineage["current"]["id"] == test_chemical.id
        assert lineage["parent"] is None
        assert lineage["children"] == []
        assert lineage["siblings"] == []

    def test_lineage_shows_children(self, app, db_session, test_chemical):
        """Test lineage includes children of the chemical."""
        test_chemical.parent_lot_number = None

        # Create children
        child1 = Chemical(
            part_number="C001",
            lot_number="L001-A",
            description="Child 1",
            manufacturer="Test",
            quantity=25,
            unit="ml",
            location="Test",
            category="Testing",
            status="available",
            parent_lot_number=test_chemical.lot_number
        )
        child2 = Chemical(
            part_number="C001",
            lot_number="L001-B",
            description="Child 2",
            manufacturer="Test",
            quantity=25,
            unit="ml",
            location="Test",
            category="Testing",
            status="available",
            parent_lot_number=test_chemical.lot_number
        )
        db_session.add(child1)
        db_session.add(child2)
        db_session.commit()

        lineage = get_lot_lineage(test_chemical)

        assert lineage["parent"] is None
        assert len(lineage["children"]) == 2
        child_lot_numbers = [c["lot_number"] for c in lineage["children"]]
        assert "L001-A" in child_lot_numbers
        assert "L001-B" in child_lot_numbers
        assert lineage["siblings"] == []

    def test_lineage_shows_parent(self, app, db_session, test_chemical):
        """Test lineage includes parent of the chemical."""
        # Create parent
        parent = Chemical(
            part_number="C001",
            lot_number="PARENT-LOT",
            description="Parent Chemical",
            manufacturer="Test",
            quantity=50,
            unit="ml",
            location="Test",
            category="Testing",
            status="available"
        )
        db_session.add(parent)
        db_session.commit()

        # Set test_chemical as child of parent
        test_chemical.parent_lot_number = parent.lot_number
        db_session.commit()

        lineage = get_lot_lineage(test_chemical)

        assert lineage["parent"]["id"] == parent.id
        assert lineage["parent"]["lot_number"] == "PARENT-LOT"
        assert lineage["children"] == []

    def test_lineage_shows_siblings(self, app, db_session, test_chemical):
        """Test lineage includes siblings (other children of same parent)."""
        # Create parent
        parent = Chemical(
            part_number="C001",
            lot_number="PARENT-LOT",
            description="Parent Chemical",
            manufacturer="Test",
            quantity=50,
            unit="ml",
            location="Test",
            category="Testing",
            status="available"
        )
        db_session.add(parent)
        db_session.commit()

        # Set test_chemical as child of parent
        test_chemical.parent_lot_number = parent.lot_number

        # Create siblings
        sibling1 = Chemical(
            part_number="C001",
            lot_number="PARENT-LOT-B",
            description="Sibling 1",
            manufacturer="Test",
            quantity=25,
            unit="ml",
            location="Test",
            category="Testing",
            status="available",
            parent_lot_number=parent.lot_number
        )
        sibling2 = Chemical(
            part_number="C001",
            lot_number="PARENT-LOT-C",
            description="Sibling 2",
            manufacturer="Test",
            quantity=25,
            unit="ml",
            location="Test",
            category="Testing",
            status="available",
            parent_lot_number=parent.lot_number
        )
        db_session.add(sibling1)
        db_session.add(sibling2)
        db_session.commit()

        lineage = get_lot_lineage(test_chemical)

        assert lineage["parent"]["id"] == parent.id
        assert len(lineage["siblings"]) == 2
        sibling_lot_numbers = [s["lot_number"] for s in lineage["siblings"]]
        assert "PARENT-LOT-B" in sibling_lot_numbers
        assert "PARENT-LOT-C" in sibling_lot_numbers
        # Current chemical should not be in siblings
        assert test_chemical.lot_number not in sibling_lot_numbers

    def test_lineage_parent_not_found(self, app, db_session, test_chemical):
        """Test lineage when parent lot number is set but parent doesn't exist."""
        test_chemical.parent_lot_number = "NONEXISTENT-LOT"
        db_session.commit()

        lineage = get_lot_lineage(test_chemical)

        assert lineage["parent"] is None
        assert lineage["siblings"] == []

    def test_lineage_complete_family_tree(self, app, db_session, test_chemical):
        """Test complete lineage with parent, children, and siblings."""
        # Create parent
        parent = Chemical(
            part_number="C001",
            lot_number="PARENT",
            description="Parent",
            manufacturer="Test",
            quantity=10,
            unit="ml",
            location="Test",
            category="Testing",
            status="available"
        )
        db_session.add(parent)
        db_session.commit()

        # Set test_chemical as child
        test_chemical.parent_lot_number = "PARENT"

        # Create sibling
        sibling = Chemical(
            part_number="C001",
            lot_number="SIBLING",
            description="Sibling",
            manufacturer="Test",
            quantity=25,
            unit="ml",
            location="Test",
            category="Testing",
            status="available",
            parent_lot_number="PARENT"
        )
        db_session.add(sibling)

        # Create children of test_chemical
        grandchild = Chemical(
            part_number="C001",
            lot_number="GRANDCHILD",
            description="Grandchild",
            manufacturer="Test",
            quantity=10,
            unit="ml",
            location="Test",
            category="Testing",
            status="available",
            parent_lot_number=test_chemical.lot_number
        )
        db_session.add(grandchild)
        db_session.commit()

        lineage = get_lot_lineage(test_chemical)

        assert lineage["current"]["lot_number"] == test_chemical.lot_number
        assert lineage["parent"]["lot_number"] == "PARENT"
        assert len(lineage["siblings"]) == 1
        assert lineage["siblings"][0]["lot_number"] == "SIBLING"
        assert len(lineage["children"]) == 1
        assert lineage["children"][0]["lot_number"] == "GRANDCHILD"

    def test_lineage_current_dict_representation(self, app, db_session, test_chemical):
        """Test that current chemical is properly converted to dict."""
        lineage = get_lot_lineage(test_chemical)

        current = lineage["current"]
        assert "id" in current
        assert "part_number" in current
        assert "lot_number" in current
        assert "description" in current
        assert "manufacturer" in current
        assert "quantity" in current
        assert "unit" in current
        assert current["lot_number"] == test_chemical.lot_number

    def test_lineage_no_duplicate_in_siblings(self, app, db_session, test_chemical):
        """Test that current chemical is excluded from siblings list."""
        # Create parent
        parent = Chemical(
            part_number="C001",
            lot_number="PARENT",
            description="Parent",
            manufacturer="Test",
            quantity=10,
            unit="ml",
            location="Test",
            category="Testing",
            status="available"
        )
        db_session.add(parent)
        db_session.commit()

        test_chemical.parent_lot_number = "PARENT"
        db_session.commit()

        lineage = get_lot_lineage(test_chemical)

        sibling_ids = [s["id"] for s in lineage["siblings"]]
        assert test_chemical.id not in sibling_ids


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_generate_lot_with_special_characters(self):
        """Test lot number generation with special characters."""
        result = generate_child_lot_number("LOT-2024/001#A", 0)
        assert result == "LOT-2024/001#A-A"

    def test_generate_lot_with_unicode(self):
        """Test lot number generation with unicode characters."""
        result = generate_child_lot_number("LOT-αβγ", 0)
        assert result == "LOT-αβγ-A"

    def test_very_long_parent_lot_number(self):
        """Test with very long parent lot number."""
        long_lot = "LOT" * 100
        result = generate_child_lot_number(long_lot, 0)
        assert result == f"{long_lot}-A"

    def test_sequence_pattern_consistency(self):
        """Test that sequence pattern is consistent across ranges."""
        # Verify pattern: A-Z, AA-AZ, BA-BZ, ..., ZA-ZZ, AAA-...
        assert generate_child_lot_number("L", 0) == "L-A"
        assert generate_child_lot_number("L", 25) == "L-Z"
        assert generate_child_lot_number("L", 26) == "L-AA"
        assert generate_child_lot_number("L", 51) == "L-AZ"
        assert generate_child_lot_number("L", 52) == "L-BA"
        assert generate_child_lot_number("L", 77) == "L-BZ"
        assert generate_child_lot_number("L", 78) == "L-CA"

    def test_chemical_with_none_expiration(self, app, db_session, test_chemical):
        """Test creating child when parent has no expiration date."""
        test_chemical.lot_sequence = 0
        test_chemical.expiration_date = None
        db_session.commit()

        child = create_child_chemical(test_chemical, 10)

        assert child.expiration_date is None

    def test_chemical_with_none_minimum_stock(self, app, db_session, test_chemical):
        """Test creating child when parent has no minimum stock level."""
        test_chemical.lot_sequence = 0
        test_chemical.minimum_stock_level = None
        db_session.commit()

        child = create_child_chemical(test_chemical, 10)

        assert child.minimum_stock_level is None

    def test_fractional_quantity_transfer(self, app, db_session, test_chemical):
        """Test transfer with fractional quantities."""
        test_chemical.lot_sequence = 0
        test_chemical.quantity = 100.5
        db_session.commit()

        child = create_child_chemical(test_chemical, 50.25)

        assert child.quantity == 50.25
        assert test_chemical.quantity == 50.25

    def test_small_quantity_transfer(self, app, db_session, test_chemical):
        """Test transfer with very small quantity."""
        test_chemical.lot_sequence = 0
        test_chemical.quantity = 1.0
        db_session.commit()

        child = create_child_chemical(test_chemical, 0.001)

        assert child.quantity == 0.001
        assert test_chemical.quantity == pytest.approx(0.999, rel=1e-6)
