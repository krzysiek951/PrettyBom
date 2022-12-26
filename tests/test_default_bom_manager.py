import pytest

from web_app.models import *


class TestDefaultBomManager:
    @pytest.fixture
    def bm(self):
        """" Fixture of Default Bom Manager """
        return DefaultBomManager()

    @pytest.fixture
    def sample_bom(self, bm):
        """" Fixture of sample Bill of Materials """
        return bm.create_bom()

    def test_create_default_bom(self, sample_bom):
        """ Test whether default Bom Manager creates Default BOM """
        assert isinstance(sample_bom, DefaultBom)

    def test_sample_bom_in_bom_list(self, sample_bom, bm):
        """ Test whether created bom is added to bom list """
        assert sample_bom in bm.bom_list

    def test_crated_bom_count(self, bm):
        """ Test whether created bom are correctly counted """
        for _ in range(5):
            bm.create_bom()
        bom_count = bm.get_bom_count()
        assert bom_count == 5

    def test_delete_bom(self, bm):
        """ Test whether created bom is correctly deleted """
        bom1 = bm.create_bom()
        bm.delete_bom(bom1)
        assert bom1 not in bm.bom_list

    def test_delete_bom_with_bad_data(self, bm):
        """ Test whether deleting bom not listed in Bom Manager raises exception """
        bom_not_in_bm = DefaultBom()
        with pytest.raises(ValueError):
            bm.delete_bom(bom_not_in_bm)

    def test_reset_bom(self, bm):
        """ Test whether bom is correctly reset """
        bom_to_reset = bm.create_bom(**{'production_part_keywords': 'M-2022'})
        clean_bom = bm.create_bom()
        bom_to_reset = bm.reset_bom(bom_to_reset)
        assert bom_to_reset.__dict__ == clean_bom.__dict__

    def test_reset_bom_with_bad_data(self, bm):
        """ Test whether bad data raises error """
        bom_not_in_bm = DefaultBom()
        with pytest.raises(ValueError):
            bm.reset_bom(bom_not_in_bm)
