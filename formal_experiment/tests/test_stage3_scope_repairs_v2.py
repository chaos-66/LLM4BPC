import json
from pathlib import Path

from bpc_hybrid.stage3_scope_repairs_v2 import constituents, replace_scopes, scope_indexes
from bpc_hybrid.stage3_reproduction_repairs_v1 import mask_tokens

ROOT = Path(__file__).resolve().parents[1]


def markers():
    return {f: [e['surface'].casefold() for e in json.loads(
        (ROOT/f'resources/lexicon/{s}_markers_en_v2.json').read_text(encoding='utf-8'))['entries']]
        for f, s in [('conditions', 'condition'), ('constraints', 'constraint'), ('exceptions', 'exception')]}


def test_actual_legal_clause_retains_main_duty_and_information_complement():
    evidence = ROOT/'outputs/evidence/stage3_reproduction_repair_20261012_v1'
    sentence = json.loads((evidence/'corenlp_annotations.json').read_text(encoding='utf-8'))['R5-D-01']['sentences'][0]
    records = json.loads((evidence/'sun_original_records.json').read_text(encoding='utf-8'))['records']
    clause = next(r['record']['clauses'][0] for r in records if r['requirement_id']=='R5-D-01')
    sources = json.loads((ROOT/'data/development/stage3_winter_paper_rerun_20261010_v1/regulation_sources.json').read_text(encoding='utf-8'))['rules']
    text = next(r['text'] for r in sources if r['rule_id']=='R5-D-01')
    repaired = replace_scopes(clause, sentence, text, markers())
    masked = set(mask_tokens(sentence, repaired))
    surviving = [t['word'] for i, t in enumerate(sentence['tokens']) if i not in masked]
    assert 'provide' in surviving and 'controller' in surviving and 'information' in surviving
    assert 'Where' not in surviving and 'prior' not in surviving and 'shall' not in surviving
    assert not repaired['exceptions']


def test_marker_in_object_does_not_erase_matrix_predicate():
    parse='(ROOT (S (NP (NN controller)) (VP (VB provide) (NP (NN information) (PP (IN on) (NP (NN purpose)))))))'
    tokens=[{'word':w,'pos':p} for w,p in zip('controller provide information on purpose'.split(),['NN','VB','NN','IN','NN'])]
    sentence={'parse':parse,'tokens':tokens}
    assert not any(scope_indexes(sentence, markers()).values())
    assert len(constituents(parse,len(tokens)))>len(tokens)


def test_temporal_scope_does_not_swallow_attached_with_complement():
    parse='(ROOT (VP (VB provide) (NP (NN information)) (PP (IN before) (NP (NP (NN processing)) (PP (IN with) (NP (NN details)))))))'
    sentence={'parse':parse,'tokens':[{'word':w,'pos':p} for w,p in zip(
        'provide information before processing with details'.split(), ['VB','NN','IN','NN','IN','NN'])]}
    result=scope_indexes(sentence, markers())
    assert [2,3] in result['constraints']
    assert not any(4 in m for m in result['constraints'])
