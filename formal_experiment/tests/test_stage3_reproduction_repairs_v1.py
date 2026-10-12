from types import SimpleNamespace
from xml.dom import minidom
from pathlib import Path
import os
import shutil
import subprocess

import pytest

from bpc_hybrid.stage3_reproduction_repairs_v1 import (
    accept_role, align_winter_model, mask_tokens, rebuild_clause, source_segments, span_text,
)


def tokens_for(text, words, lemmas=None, poses=None):
    tokens=[]
    position=0
    for i, word in enumerate(words):
        start=text.index(word,position)
        tokens.append({"word":word,"lemma":lemmas[i] if lemmas else word.casefold(),
                       "pos":poses[i] if poses else "NN", "characterOffsetBegin":start,
                       "characterOffsetEnd":start+len(word)})
        position=start+len(word)
    return tokens


def test_surgery_segments_keep_object_after_removed_constraint():
    text="provide information before processing with relevant details"
    tokens=tokens_for(text,text.split())
    segments=source_segments(text,tokens,[0,1,4,5,6])
    assert span_text({"segments":segments},text)=="provide information with relevant details"
    assert all("before" not in s["text"] for s in segments)
    with pytest.raises(ValueError,match="drift"):
        span_text({"segments":[{"start":0,"end":7,"text":"invent"}]},text)


def test_frozen_canonical_clause_scope_masks_modal_and_constraint():
    text='controller shall inform before processing'
    tokens=tokens_for(text,text.split(),poses=['NN','MD','VB','IN','NN'])
    clause={'clause_span':{'start':0,'end':len(text)},
            'constraints':[{'start':text.index('before'),'end':len(text)}]}
    assert mask_tokens({'tokens':tokens},clause)==[1,3,4]


@pytest.mark.parametrize("phrase,lemmas,head,accepted",[
    ("the controller",["the","controller"],1,True),
    ("The data subject",["the","data","subject"],2,True),
    ("certification bodies",["certification","body"],1,True),
    ("the business year of the controller",["the","business","year","of","the","controller"],2,False),
])
def test_role_head_and_multiword_coverage(phrase,lemmas,head,accepted):
    tokens=tokens_for(phrase,phrase.split(),lemmas)
    assert accept_role(tokens,list(range(len(tokens))),head,frozenset({"controller","body"})) is accepted


def test_post_surgery_vp_and_subject_ownership_no_condition_action():
    text="If controllers collect data the processor shall provide information"
    tokens=tokens_for(text,text.split(),poses=["IN","NNS","VBP","NN","DT","NN","MD","VB","NN"])
    sentence={"tokens":tokens,"basicDependencies":[
        {"dep":"ROOT","governor":0,"dependent":8},
        {"dep":"nsubj","governor":8,"dependent":6},
        {"dep":"obj","governor":8,"dependent":9}]}
    clause={"clause_id":"test.c1","span":{"start":0,"end":len(text)}}
    rebuilt=rebuild_clause(clause,text,sentence,[{"field":"action","indexes":[7,8]},
                                              {"field":"actor","indexes":[4,5]}],frozenset({"processor"}))
    assert [a["semantic_text"] for a in rebuilt["actions"]]==["provide information"]
    assert len(rebuilt["actor_action_map"])==1
    assert rebuilt["actors"][0]["text"]=="the processor"


def test_winter_empty_end_does_not_shift_action_identity():
    doc=minidom.parseString('<process><startEvent id="Start" name="context"/><endEvent id="End"/>'
                           '<task id="Activity_1" name="inform"/><task id="Activity_2" name="lift"/></process>')
    nodes=[n for n in doc.documentElement.childNodes if n.nodeType==n.ELEMENT_NODE]
    process=SimpleNamespace(participant="Controller",obligation_list=nodes,
                            obligation_list_labels_lemmatized=[["context"],["inform"],["lift"]])
    model=SimpleNamespace(processes=[process])
    assert align_winter_model(model)==1
    from bpc_hybrid.winter_stage3.winter_pair import WinterPair
    pair=object.__new__(WinterPair)
    pair.sim=SimpleNamespace(text_model_obligation=lambda a,b:1.0 if b==["inform"] else 0.0)
    matched=pair._max_text_obligation_to_model(SimpleNamespace(lemmatized="inform"),
                                               model.obligations,model.lemmatized_obligations)
    assert matched[0].getAttribute("id")=="Activity_1"
    assert len(model.obligations["Controller"])==len(model.lemmatized_obligations["Controller"])


def test_live_tsurgeon_preserves_discontinuous_original_leaf_indexes(tmp_path):
    runtime=Path('D:/environment/stanford-corenlp-4.5.10')
    if not runtime.exists() or not shutil.which('javac') or not shutil.which('java'):
        pytest.skip('external CoreNLP/Java runtime unavailable')
    source=Path(__file__).resolve().parents[1]/'tools/corenlp/SunPart3PhraseRepairBridgeV1.java'
    jars=os.pathsep.join(str(p) for p in sorted(runtime.glob('*.jar')))
    classes=tmp_path/'classes'
    classes.mkdir()
    subprocess.run(['javac','--release','8','-encoding','UTF-8','-cp',jars,'-d',str(classes),str(source)],
                   capture_output=True,check=True,timeout=30)
    data=tmp_path/'trees.tsv'
    data.write_text('example\t2,3\t(ROOT (S (VP (VB provide) (NP (NN information)) '
                    '(PP (IN before) (NP (NN processing))) (PP (IN with) (NP (NN details))))))\n',encoding='utf-8')
    result=subprocess.run(['java','-cp',str(classes)+os.pathsep+jars,'SunPart3PhraseRepairBridgeV1',str(data)],
                          capture_output=True,check=True,text=True,encoding='utf-8',timeout=30)
    assert 'example\taction\t0,1,4,5' in result.stdout
    assert 'Tsurgeon prune operations: 2' in result.stderr
