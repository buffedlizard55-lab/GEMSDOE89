import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from submission_readiness import scientific_blockers, audit_card


def test_missing_evidence_cannot_pass():
    assert scientific_blockers({})
    assert audit_card({})['status'] == 'DO_NOT_SUBMIT'


def test_negative_card_stays_blocked_even_if_status_is_relabelled():
    card = json.loads((ROOT / 'registry/run_card_condedge_20261024.json').read_text())
    card['verdict'] = 'promote'
    card['submission']['download_submit_status'] = 'OK_TO_SUBMIT'
    report = audit_card(card)
    assert report['status'] == 'DO_NOT_SUBMIT'
    assert any('holdout improvement' in b for b in report['blockers'])
    assert any('registry coverage' in b for b in report['blockers'])
    assert not any('format validation' in b for b in report['blockers'])
    assert report['format_gates'] and all(g['ok'] for g in report['format_gates'])
    assert report['safe_to_submit'] is False


def test_tampered_hash_blocks():
    card = json.loads((ROOT / 'registry/run_card_condedge_20261024.json').read_text())
    card['raster']['sha256'] = 'incorrect'
    assert 'Raster hash differs from run card' in audit_card(card)['blockers']


def test_nonfinite_score_is_not_improvement():
    card = json.loads((ROOT / 'registry/run_card_condedge_20261024.json').read_text())
    card['holdout_protocol']['candidate']['value'] = float('inf')
    assert any('holdout improvement' in b for b in scientific_blockers(card))


def test_scientific_gate_can_pass_only_with_complete_positive_evidence():
    card = json.loads((ROOT / 'registry/run_card_condedge_20261024.json').read_text())
    card = copy.deepcopy(card)
    card['verdict'] = 'promote'
    hp = card['holdout_protocol']
    hp['candidate']['value'] = .25
    hp['candidate']['ci95'] = {'lower_95': .22, 'upper_95': .28}
    hp['paired_delta_candidate_minus_R0']['ci95']['lower_95'] = .01
    hp['comparator_is_locked_current_best'] = True
    card['registry_uniqueness']['complete_registry_coverage'] = True
    assert scientific_blockers(card) == []
    # This is a synthetic gate test, not evidence permitting a real upload.
    del card['registry_uniqueness']['before_placement']
    assert any('before_placement' in b for b in scientific_blockers(card))
