import pytest

from web_app.models import DefaultBom, DefaultPart

PART = {
    'Pos.': '100',
    'Qty.': 1,
    'Part number': 'M-2022-100',
    'Part name': 'Sample part',
    'Supplier': 'None'
}

PART_LIST = [
    {
        'Pos.': '1',
        'Qty.': '1',
        'Part number': 'M-2022-01-00',
        'Part name': 'Assembly module',
        'Supplier': '',
        'Processed': {
            'to_order': 2,
            'type': 'production',
            'file_type': 'assembly',
            'Supplier': '',
            'parent': [],
            'parent_assembly': 'M-2022-00 Layout',
        }
    },
    {
        'Pos.': '1-1',
        'Qty.': '1',
        'Part number': '193 138',
        'Part name': 'Non-return valve GRLA',
        'Supplier': 'FESTO',
        'Processed': {
            'to_order': 2,
            'type': 'purchased',
            'file_type': 'part',
            'Supplier': 'Festo',
            'parent': ['1'],
            'parent_assembly': 'M-2022-01-00',
        }
    },
    {
        'Pos.': '1-1-1',
        'Qty.': '1',
        'Part number': 'Some junkie part',
        'Part name': 'Inside Festo GRLA',
        'Supplier': 'FESTO',
        'Processed': {
            'to_order': 2,
            'type': 'junk',
            'file_type': 'part',
            'Supplier': 'Festo',
            'parent': ['1', '1-1'],
            'parent_assembly': '193 138',
        }
    },
    {
        'Pos.': '1-7',
        'Qty.': '2',
        'Part number': 'DIN 912 M6 x 10',
        'Part name': 'Hexagon head screws',
        'Supplier': 'NORELEM',
        'Processed': {
            'to_order': 4,
            'type': 'fastener',
            'file_type': 'part',
            'Supplier': 'Norelem',
            'parent': ['1'],
            'parent_assembly': 'M-2022-01-00',
        }
    },
]

BOM_ATTRIBUTES = {
    'production_part_keywords': 'M-2022',
    'main_assembly_name': 'M-2022-00 Layout',
    'main_assembly_sets': '2',
    'part_position_column': 'Pos.',
    'part_quantity_column': 'Qty.',
    'part_number_column': 'Part number',
    'part_name_column': 'Part name',
    'junk_part_empty_fields': '',
    'junk_part_keywords': 'iMike',
    'normalized_columns': ['Supplier', ],
    'exported_columns': '',
}


class TestDefaultBom:
    @pytest.fixture
    def default_bom(self):
        """ Fixture of a Default Bom """
        default_bom = DefaultBom()

        # Set BOM Attributes:
        for key, value in BOM_ATTRIBUTES.items():
            setattr(default_bom, key, value)

        # Populate parts:
        for part in PART_LIST:
            default_bom.create_part(**part)

        return default_bom

    @pytest.fixture
    def part_created_by_default_bom(self, default_bom):
        """" Fixture of a Part created by Default Bom """
        default_part = default_bom.create_part(**PART)
        return default_part

    def test_create_default_part(self, default_bom, part_created_by_default_bom):
        """ Test whether Default Bom creates Default Part. """
        assert isinstance(part_created_by_default_bom, DefaultPart)

    def test_created_par_with_keywords(self, part_created_by_default_bom):
        """ Test whether part can be created with custom attributes. """
        for key, value in PART.items():
            assert getattr(part_created_by_default_bom, key) == value

    def test_process_part_list(self, default_bom):
        """ Test whether part list is correctly processed. """
        default_bom.process_part_list()
        # default_bom.print_part_list()
        for part in default_bom.part_list:
            testing_fields = getattr(part, 'Processed')
            for key, value in testing_fields.items():
                assert getattr(part, key) == value

    def test_delete_part(self, default_bom, part_created_by_default_bom):
        """ Test whether created part is correctly deleted. """
        default_bom.delete_part(part_created_by_default_bom)
        assert part_created_by_default_bom not in default_bom.part_list

    def test_delete_part_with_bad_data(self, default_bom):
        """ Test whether deleting a part that is not listed in the BOM raises an exception. """
        part_not_in_bom = DefaultPart()
        with pytest.raises(ValueError):
            default_bom.delete_part(part_not_in_bom)

    def test_delete_all_parts(self, default_bom):
        """ Test whether deleting all parts clears the part list. """
        default_bom.delete_all_parts()
        assert default_bom.get_part_count() == 0

    def test_get_part_count(self, default_bom):
        """ Test whether bom is able to count all the parts in a part list. """
        assert default_bom.get_part_count() == 4

    #
    # def test_import_csv(self):
    #     pass
    #
    # def test_export_to_xlsx(self):
    #     pass
    #

    def test_setting_main_assembly_sets(self, default_bom):
        """ Test whether setting the main assembly sets returns an int value. """
        samples = ['1', 1, ' 1 ']
        for sample in samples:
            default_bom.main_assembly_sets = sample
            assert default_bom.main_assembly_sets == 1

    def test_setting_main_assembly_sets_with_bad_data(self, default_bom):
        """ Test whether setting the main assembly sets with bad data returns exception. """
        samples = ['1.', 'lorem']
        for sample in samples:
            with pytest.raises(ValueError):
                default_bom.main_assembly_sets = sample
