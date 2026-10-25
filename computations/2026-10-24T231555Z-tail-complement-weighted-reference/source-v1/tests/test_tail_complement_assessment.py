"""Research acceptance must distinguish a tail compression from a cross norm."""
import copy

import pytest

from scripts import verify_tail_complement_inputs as independent
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_tail_complement_assessment as source


@pytest.fixture(scope='module')
def fresh_packet():
    return source.generate()


def test_tail_norm_cannot_replace_full_cross_block_norm(fresh_packet):
    packet = copy.deepcopy(fresh_packet)
    packet['cross_norm_upper'] = packet['rho_tail_upper_exact']
    packet['selection']['cross_norm_upper'] = packet['rho_tail_upper_exact']
    with pytest.raises(validation.InputRejected, match='selection contract'):
        source.validate_packet(packet)


def test_reference_cannot_be_raised_by_editing_both_metadata_copies(fresh_packet):
    packet = copy.deepcopy(fresh_packet)
    packet['mu_reference_exact'] = '1'
    packet['selection']['mu_reference_exact'] = '1'
    with pytest.raises(validation.InputRejected, match='selection contract'):
        source.validate_packet(packet)


def test_native_reconstruction_rejects_an_optimistic_scalar_enclosure(fresh_packet, tmp_path):
    packet = copy.deepcopy(fresh_packet)
    packet['complement'] = [1 << source.BITS, 1 << source.BITS]
    path = tmp_path/'optimistic-complement.json.gz'
    source.save(path, packet)
    with pytest.raises(validation.InputRejected, match='complement'):
        independent.audit(path)


def test_refinement_cannot_change_the_declared_accuracy_schedule():
    initial = source.selection()['boundary']
    with pytest.raises(validation.InputRejected, match='geometric head ladder'):
        source.selection(initial+2)
