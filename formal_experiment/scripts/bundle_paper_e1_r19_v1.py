"""Publish aggregate paper tables and the threshold figure after offline scoring."""
from __future__ import annotations

import io
import math
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import build_sun_modality_fewshot_report_v1 as paired
import run_paper_e1_r19_v1 as dispatch
import score_paper_e1_r19_v1 as score

pre = dispatch.pre
OUTPUT = score.PAPER / "06_unified_E1_R19"


def billing(events, plan, auth):
    """Replay every reservation and reprice completions from provider token counts."""
    reserved = {}
    costs = Counter()
    settled = Counter()
    statuses = Counter()
    models = Counter()
    usage = Counter()
    inputs = {name:dict(pairs) for name,pairs in pre.datasets().items()}
    output_checks = {}
    max_at_risk = 0.0
    for row in events:
        sid = row["sample_id"]
        group = "/".join(sid.split("|")[:2])
        timestamp = datetime.fromisoformat(row["timestamp"])
        window, rates = pre.llm_se.rate_for(timestamp)
        if window != "off_peak":
            raise ValueError(f"Timestamp outside the authorized billing window: {group}")
        if row["kind"] == "started":
            reserved[sid] = row["reserved_cny"]
            if row["price_window"] != window:
                raise ValueError("Reservation window differs from provider schedule")
        else:
            if dispatch.transport.failed(row) or not dispatch.transport.usage_valid(row["usage"]):
                raise ValueError("Open transport, model or billing issue")
            cost = pre.llm_se.cost_cny(row["usage"],rates)
            if row["cost_cny"] != cost or cost > reserved.pop(sid):
                raise ValueError("Actual cost differs or exceeds its reservation")
            costs[group] += cost
            settled[group] += 1
            statuses[row["request_status"]] += 1
            models[row["returned_model"]] += 1
            dataset,arm,sample = sid.split("|")
            text = inputs[dataset][sample]
            raw = pre.llm_se._extract_json_object(row["raw_content"])
            extracted = dispatch.canonical((dataset,arm,sample),text,row)
            check = output_checks.setdefault(group,{"invalid_json":0,"source_text_echo_differs":0,
                                                     "empty_or_failed_readout":0})
            check["invalid_json"] += raw is None
            check["source_text_echo_differs"] += raw is not None and raw.get("source_text") != text
            check["empty_or_failed_readout"] += (extracted["label"] is None if dataset == "german"
                                                 else extracted["request_status"] != "ok")
            for field in ("prompt_tokens","completion_tokens","prompt_cache_hit_tokens","prompt_cache_miss_tokens"):
                usage[field] += row["usage"][field]
        max_at_risk = max(max_at_risk,sum(costs.values()) + sum(reserved.values()))
    if (reserved or settled != plan["new_calls_by_group"] or max_at_risk > auth["max_cost_cny"]
            or sum(settled.values()) != auth["max_new_calls"]):
        raise ValueError("Incomplete population or spending outside authorization")
    return {"first_reserved_utc":events[0]["timestamp"],"last_settled_utc":events[-1]["timestamp"],
            "calls":sum(settled.values()),"calls_by_group":dict(settled),"request_status":dict(statuses),
            "response_models":dict(models),"usage_tokens":dict(usage),"cost_cny_by_group":dict(costs),
            "cost_cny":sum(costs.values()),"peak_spent_plus_open_reservations_cny":max_at_risk,
            "unsettled":0,"retries":0,"extraction_checks_by_group":output_checks,
            "cost_basis":"Provider usage at the published off-peak CNY rates."}


def german_comparison(events, methods):
    gold = {r.sample_id:r.label for r in pre.data.load_split("test")}
    path = score.DEV / "s28_sun_modality_five_way_v1/sun/local_only/test_predictions.jsonl"
    sun = {r["sample_id"]:r["predicted"] for r in score.jsonlines(path)}
    ours = {r["sample_id"].split("|")[2]:r["label"] for r in events
            if r["kind"]=="finished" and r["sample_id"].startswith("german|111|")}
    if set(ours) != set(sun) or set(ours) != set(gold) or len(ours) != 426:
        raise ValueError("Unpaired German samples")
    labels = list(gold.values())
    old, new = [sun[k] for k in gold], [ours[k] for k in gold]
    for name, predictions in (("sun",old),("LLM-SE",new)):
        if paired.evaluate(labels,predictions)["macro_f1"] != methods[name]["primary_426"]["macro_f1"]:
            raise ValueError("Paired Macro-F1 differs from the reported primary result")
    interval = paired.bootstrap_delta(labels,old,new)
    interval["delta"] = "Revised LLM-SE minus the local Sun reconstruction"
    return {"delta_macro_f1":methods["LLM-SE"]["primary_426"]["macro_f1"]-methods["sun"]["primary_426"]["macro_f1"],
            "paired_correctness":paired.paired(labels,old,new),"paired_bootstrap":interval}


def figure(points):
    # Use the plotting environment and one-column dimensions of the previous paper figure.
    sys.path.insert(0,str(pre.ROOT / ".tmp/fig3_plot_runtime"))
    os.environ["MPLCONFIGDIR"] = str(pre.ROOT / ".tmp/fig3_matplotlib_cache")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter
    by_point = {(row["gamma"],row["theta"]):row["methods"] for row in points}
    if len(points) != 9 or len(by_point) != 9:
        raise ValueError("Figure 3 requires nine distinct operating points")
    values = [s["f1"] for row in points for s in row["methods"].values()]
    lo,hi = .35,.60
    if min(values)<lo or max(values)>hi:
        lo,hi = max(0,math.floor((min(values)-.02)*20)/20),min(1,math.ceil((max(values)+.02)*20)/20)
    plt.rcParams.update({"font.family":"serif","font.serif":["Times New Roman"],"mathtext.fontset":"stix",
                         "font.size":7,"axes.titlesize":7.5,"xtick.labelsize":6.3,"ytick.labelsize":6.3,
                         "axes.linewidth":.7,"pdf.fonttype":42})
    fig,axes = plt.subplots(1,2,figsize=(3.5,1.52))
    fig.subplots_adjust(left=.12,right=.965,bottom=.29,top=.845,wspace=.52)
    sweeps = ([(g,.45) for g in (.35,.45,.55,.65,.75)],[(.55,t) for t in (.25,.35,.45,.55,.65)])
    for i,(ax,sweep) in enumerate(zip(axes,sweeps)):
        ticks = [pair[i] for pair in sweep]
        for method,label,color,marker in (("sun","Sun et al.","#707070","s"),("ours","LLM-SE (Ours)","#0064ab","o")):
            ax.plot(ticks,[by_point[p][method]["f1"] for p in sweep],color=color,marker=marker,label=label,
                    lw=1.1,ms=3.3,mew=.4,clip_on=False)
        ax.set(xlim=(ticks[0]-.006,ticks[-1]+.006),xticks=ticks,ylim=(lo,hi))
        ax.set_yticks([round(lo+j*.05,2) for j in range(round((hi-lo)/.05)+1)])
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.grid(axis="y",color="#d9d9d9",lw=.45,ls="--")
        ax.set_axisbelow(True)
        ax.spines[["top","right"]].set_visible(False)
        ax.tick_params(length=2.3,width=.65,pad=1.8)
        ax.set_ylabel(r"$F_1$",rotation=0,labelpad=6)
        ax.set_xlabel((r"Action threshold $\gamma$",r"Actor threshold $\theta$")[i],labelpad=3)
        ax.set_title((r"$\theta$ fixed at 0.45",r"$\gamma$ fixed at 0.55")[i],pad=5)
    fig.legend(*axes[0].get_legend_handles_labels(),loc="lower center",bbox_to_anchor=(.55,-.005),
               ncol=2,frameon=False,handlelength=1.7,columnspacing=1.2,handletextpad=.5,borderaxespad=0)
    out = io.BytesIO()
    fig.savefig(out,format="pdf",metadata={"CreationDate":None})
    plt.close(fig)
    return out.getvalue()


def main():
    plan = pre.read(pre.REPORT)
    summary = pre.read(score.REPORTS / "paper_e1_r19_v1_scores.json")
    gdpr = pre.read(score.REPORTS / "paper_e1_r19_v1_gdpr.json")
    events = pre.boundary.read_events(dispatch.JOURNAL)
    ledger = billing(events,plan,pre.read(dispatch.AUTH))
    if (summary["requests_sha256"] != plan["requests_sha256"] or summary["journal_sha256"] != events[-1]["event_hash"]
            or abs(summary["cost_cny"]-ledger["cost_cny"])>1e-8
            or summary["table_I"]["LLM-SE"] != summary["table_II"]["111"]):
        raise ValueError("Run or table bindings disagree")
    baseline = next(r for r in gdpr["figure_3"] if (r["gamma"],r["theta"]) == (.55,.45))
    if baseline["methods"] != gdpr["sun_and_ours"] or gdpr["secondary_development_grid_fixed_mpnet"]["count"] != 81:
        raise ValueError("Threshold population or Figure 3 reference point differs")
    canonical = {"run_id":plan["run_id"],"model":plan["model"],"model_settings":plan["settings"],
                 "full_system_sha256":plan["revised_system_sha256"],"requests_sha256":plan["requests_sha256"],
                 "table_I":{"population":150,"metric":"Overlap-F1, micro over the five original-span fields; four-class modality scored separately",
                            "methods":summary["table_I"]},
                 "table_II":{"population_per_arm":150,"factor_order":["E","S","J"],
                             "shares_table_I_full_predictions":True,"historical_request_identical_arms":["000","001"],
                             "arms":summary["table_II"]},
                 "table_III":{"scope":"GDPR development","requirements":33,"bpmn_cases":115,"scored_units":201,
                              "gamma":.55,"theta":.45,"tau":.8,"failed_llm_extractions":summary["gdpr_native_failures"],
                              "methods":{"Sun":baseline["methods"]["sun"],"Winter":gdpr["Winter"],"LLM-SE":baseline["methods"]["ours"]}},
                 "figure_3":gdpr["figure_3"],
                 "german":{"population":426,"readout":"First non-empty clause modality; all test items in the denominator.",
                           "scope":"Test-informed prompt development; secondary 424-item sensitivity omits two pre-existing near matches.",
                           "methods":{name if name=="LLM-SE" else ("Sun" if name=="sun" else name.upper()):v
                                      for name,v in summary["german"].items()},
                           "LLM_SE_minus_Sun":german_comparison(events,summary["german"])}}
    score.save(OUTPUT / "paper_results.json",canonical)
    pre.frozen(OUTPUT / "fig3.pdf",figure(gdpr["figure_3"]))
    files = [OUTPUT / "paper_results.json",OUTPUT / "fig3.pdf",pre.REPORT,dispatch.DRY,dispatch.AUTH,
             score.REPORTS / "paper_e1_r19_v1_scores.json",score.REPORTS / "paper_e1_r19_v1_gdpr.json"]
    score.save(score.REPORTS / "paper_e1_r19_v1_manifest.json",{
        "run_id":pre.NAME,"status":"completed","accounting":ledger,"journal_sha256":events[-1]["event_hash"],
        "input_sha256":plan["fixed_input_sha256"],"historical_control_responses":300,
        "historical_controls_sha256":pre.read(dispatch.DRY)["control_responses_sha256"],
        "operational_budget":{"max_calls":1359,"max_cost_cny":65,"window":"off_peak_only"},
        "artifacts_sha256":{p.relative_to(pre.ROOT).as_posix():pre.digest(p.read_bytes()) for p in files}})
    print("Verified billing and published aggregate tables and Figure 3.")


if __name__ == "__main__":
    main()
