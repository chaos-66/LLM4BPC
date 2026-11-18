"""Build the original Chinese course report from a completed, verified run."""
from pathlib import Path
import argparse
import json
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak


def build(result_dir, output):
    r = json.loads((result_dir / "results.json").read_text(encoding="utf-8"))
    manifest = json.loads((result_dir / "manifest.json").read_text(encoding="utf-8"))
    pdfmetrics.registerFont(TTFont("Song", r"C:\Windows\Fonts\simsun.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont("Hei", r"C:\Windows\Fonts\simhei.ttf"))
    pdfmetrics.registerFontFamily("Song", normal="Song", bold="Hei", italic="Song", boldItalic="Hei")
    ink, teal, light, grey = map(colors.HexColor, ["#182D3E", "#1E6A78", "#EDF4F6", "#607181"])
    styles = {
        "title": ParagraphStyle("title", fontName="Hei", fontSize=24, leading=32, textColor=ink, spaceAfter=12),
        "h1": ParagraphStyle("h1", fontName="Hei", fontSize=17, leading=23, textColor=ink, spaceAfter=12),
        "h2": ParagraphStyle("h2", fontName="Hei", fontSize=11.8, leading=18, textColor=teal, spaceBefore=9, spaceAfter=5),
        "body": ParagraphStyle("body", fontName="Song", fontSize=10.5, leading=16.3, textColor=ink, spaceAfter=7, wordWrap="CJK"),
        "small": ParagraphStyle("small", fontName="Song", fontSize=9, leading=13.8, textColor=grey, spaceAfter=5, wordWrap="CJK"),
        "cell": ParagraphStyle("cell", fontName="Song", fontSize=9, leading=13, textColor=ink, wordWrap="CJK"),
        "head": ParagraphStyle("head", fontName="Hei", fontSize=9, leading=13, textColor=colors.white, wordWrap="CJK"),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=8, leading=12, textColor=ink, spaceAfter=7),
        "caption": ParagraphStyle("caption", fontName="Song", fontSize=9, leading=13, textColor=grey, spaceAfter=8, alignment=TA_CENTER),
    }
    story = []
    width = A4[0] - 88
    def normalize(text):
        return str(text).translate(str.maketrans({"−": "-", "–": "-", "—": "-", "₀": "0", "ⱼ": "j"}))
    def p(text, style="body"):
        story.append(Paragraph(normalize(text), styles[style]))
    def heading(text): p(text, "h1")
    def sub(text): p(text, "h2")
    def page(): story.append(PageBreak())
    def table(rows, widths=None, font="cell"):
        parsed = [[Paragraph(escape(normalize(x)).replace("\n", "<br/>"), styles["head" if i == 0 else font])
                   for x in row] for i, row in enumerate(rows)]
        obj = Table(parsed, colWidths=widths, repeatRows=1, hAlign="LEFT")
        obj.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), teal),
             ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light]),
             ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
             ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
             ("LINEBELOW", (0, -1), (-1, -1), .5, colors.HexColor("#C7D8DF"))]))
        story.append(obj)
        story.append(Spacer(1, 8))
    def figure(name, w=width):
        from PIL import Image as PILImage
        with PILImage.open(result_dir / name) as img:
            iw, ih = img.size
        story.append(Image(str(result_dir / name), width=w, height=w * ih / iw))
    def f(value): return f"{value:.4f}"
    def pct(value): return f"{value * 100:.2f}%"
    names = ["Majority baseline", "Logistic regression", "Random forest", "XGBoost"]
    zh = dict(zip(names, ["多数类基线", "逻辑回归", "随机森林", "XGBoost"]))
    M = r["models"]
    audit = r["data"]
    lr0, lr1 = M[names[1]]["test_default"], M[names[1]]["test_selected"]
    rf = M[names[2]]["test_selected"]

    # 01: question definition, no empty decorative cover.
    p("课内实验三 / 分类学习与模型比较", "small")
    p("红葡萄酒高等级筛选\n的分类学习与模型比较".replace("\n", "<br/>"), "title")
    p("基于 UCI Wine Quality 的可复现实验 · 2026 年 11 月 18 日", "small")
    heading("1　实验题目与分类研究问题")
    p("本实验比较逻辑回归、随机森林和 XGBoost 对高等级红葡萄酒的识别能力。研究目标是在理化检测完成后、人工感官评分未知时，将可能获得较高评分的样本送交人工复评。模型提供筛选建议，不能替代品鉴或质量认证。")
    table([["要素", "本实验定义"],
        ["研究对象与观察单位", "葡萄牙北部 Vinho Verde 红葡萄酒样本；一行是一条酒样理化检测与感官评分记录，不是一个客户或一笔订单。"],
        ["目标变量", "由原始 quality 构造 high_quality = 1[quality ≥ 7]。阈值在建模前固定，是本实验的操作性定义，不是法定等级。"],
        ["正类 / 负类", "正类 1：quality ≥ 7；负类 0：quality < 7。负类只表示未达本实验高等级门槛，不等于不合格或不安全。"],
        ["预测时点与可用信息", "理化检测完成、人工评分未知时；使用 11 个理化变量。quality 只用于构造标签，禁止进入模型。"],
        ["误报 FP", "实际未达高等级却被推荐复评，增加一次人工复评或营销筛选成本。"],
        ["漏报 FN", "实际达到高等级却未被推荐，可能错失优质酒的识别机会。"],
        ["成本假设", "教学情景设 FP 成本为 1、FN 成本为 3，故优先减少漏报，同时控制误报；该比例不是实际财务估计。"]], [98, width - 98])
    sub("主要观察")
    p("默认阈值 0.50 下，XGBoost 的测试 F1 最高（0.4483），随机森林的准确率和查准率最高。按验证集成本事先选出的方案是随机森林、阈值 0.30；其测试 F1 为 0.5316。逻辑回归、阈值 0.30 的测试 F1 为 0.5974，表现更好，但不能据此回头改写测试前的选择规则。")
    p("报告依照指导书的八部分结构展开；仅报告真实运行值。完整数据读取、训练、评价和绘图代码另行提交。", "small")

    # 02: provenance + complete variable dictionary.
    page(); heading("2　数据来源与变量字典")
    p('数据集：Cortez 等（2009），<b>Wine Quality</b>，UCI Machine Learning Repository，DOI：10.24432/C56S3T。仅使用 <b>winequality-red.csv</b>，不混入白葡萄酒表。官方页面、数据包及说明文件均于 <b>2026-11-18</b> 查询 / 下载。原表为 1,599 行 × 12 列。')
    p('来源：<link href="https://archive.ics.uci.edu/dataset/186/wine+quality" color="#1E6A78">UCI 数据集页面</link>；下载：<link href="https://archive.ics.uci.edu/static/public/186/wine+quality.zip" color="#1E6A78">UCI 官方数据包</link>。UCI 标注许可为 <link href="https://creativecommons.org/licenses/by/4.0/" color="#1E6A78">CC BY 4.0</link>，允许在署名条件下共享和改编。报告已注明作者、来源和变换：完全重复行去重、quality 二值化。数据不含姓名、电话、品牌、客户编号等识别信息。')
    dictionary = [
        ("fixed acidity", "固定酸度", "连续数值"), ("volatile acidity", "挥发性酸度", "连续数值"),
        ("citric acid", "柠檬酸", "连续数值"), ("residual sugar", "残糖", "连续数值"),
        ("chlorides", "氯化物", "连续数值"), ("free sulfur dioxide", "游离二氧化硫", "连续数值"),
        ("total sulfur dioxide", "总二氧化硫", "连续数值"), ("density", "密度", "连续数值"),
        ("pH", "酸碱度", "连续数值"), ("sulphates", "硫酸盐", "连续数值"),
        ("alcohol", "酒精度", "连续数值"), ("quality", "感官质量评分，原定义 0 至 10；本表实际 3 至 8", "有序评分；仅作标签来源"),
        ("high_quality", "quality ≥ 7 记为 1，否则为 0", "派生二分类目标"),
        ("source_row_id", "原 CSV 数据行编号，不含表头；仅为追溯而生成", "辅助编号；不作输入")]
    table([["字段名", "含义", "类型 / 用途"]] + [list(x) for x in dictionary], [143, 241, width - 384])
    p("11 个输入均为数值变量，因此没有需要独热编码的输入类别变量。采用原始数值量纲，不凭空补充源说明未明确标注的单位。感官评分是至少三名专家评价的中位数；不是通过这 11 个输入字段直接计算的确定公式。", "small")
    p("官方红酒 CSV 的 SHA-256：<br/>" + manifest["data_sha256"][:32] + "<br/>" + manifest["data_sha256"][32:], "small")

    # 03: audit and preprocessing.
    page(); heading("3　数据检查、类别比例与预处理")
    table([["检查项", "结果与处理"],
       ["行列数 / 完全重复", "1,599 × 12；发现 240 条重复于先前行的记录（15.01%），保留首次出现，得到 1,359 × 12。"],
       ["缺失 / 非有限数值", "12 列缺失数均为 0、比例均为 0%；NaN / ±∞ 检查通过。"],
       ["重复对象风险", "原表无酒样实体 ID，无法确认相同记录是否独立复测；为避免相同观测跨集合，以完整 12 列去重。去重后相同 11 特征组合数为 0。"],
       ["基本合理性", "输入非负、pH 位于 [0,14]、游离二氧化硫不超过总量、quality 位于 [0,10]；上述检查未发现异常。仅说明通过有限规则，并非专业检测认证。"],
       ["泄漏字段", "排除 quality、high_quality 和追溯编号；无时间戳、处置结果或事后评论字段。"]], [105, width-105])
    table([["数据阶段", "负类数 / 比例", "正类数 / 比例"],
       ["原始 1,599 条", "1,382 / 86.43%", "217 / 13.57%"],
       ["去重后 1,359 条", "1,175 / 86.46%", "184 / 13.54%"]], [145, 180, width-325])
    p("正类属于少数类。全部预测为负类也能获得约 86% 的准确率，却完全漏掉高等级酒。因此评价必须同时看正类查准率、查全率、F1 和错误成本。没有采用过采样或类别权重；用相同数据、固定参数和验证集阈值比较三种模型。")
    sub("极端值检查（训练集 IQR 界限应用于去重后全表）")
    short = {x[0]: x[1] for x in dictionary[:11]}
    table([["变量", "最小值", "最大值", "IQR 标记数"]] +
          [[short[x["feature"]], f'{x["min"]:.5g}', f'{x["max"]:.5g}', x["iqr_flagged_clean"]] for x in audit["features"]],
          [168, 105, 105, width-378])
    p("标记规则为低于 Q1−1.5×IQR 或高于 Q3+1.5×IQR；各列可重复标记同一行，不可相加当作样本总数。极端不等于错误：未据此删样本或截尾，以免抹去少数类。中位数填补器作为流水线防护保留，本次无缺失因而不改变数据；逻辑回归另做标准化，树模型不做。", "small")

    # 04: split and baseline.
    page(); heading("4　数据划分与多数类基线")
    sub("4.1　分层划分与训练范围")
    p("先按目标变量分层，把去重后的数据划分为开发集 80%、测试集 20%；再在开发集中按 75% / 25% 分层划分训练与验证子集。两次划分随机种子均为 42，最终比例约为 60% / 20% / 20%。验证集用于选择阈值与方案，测试集在选择完成后才用于评价。")
    table([["集合", "样本数", "负类", "正类", "正类比例", "用途"]] +
          [[{"train":"训练", "validation":"验证", "test":"测试"}[k], v["n"], v["negative"], v["positive"], pct(v["positive_rate"]),
             {"train":"拟合模型和预处理", "validation":"选择阈值和模型", "test":"最终留出评价"}[k]] for k,v in audit["split"].items()],
          [57, 60, 56, 56, 77, width-306])
    p("三个集合的正类比例相差约 0.11 个百分点。索引交集为空，跨集合的相同特征组合交集也为空。数据没有采样日期和批次 ID，不能执行或验证时间 / 批次外推。本题是在同源酒样中做横截面筛选，随机分层可以服务本实验，但不能声称预测了未来年份的表现。")
    sub("4.2　预处理边界")
    table([["操作", "拟合 / 确定范围", "验证与测试如何使用"],
       ["去重与目标定义", "建模前的固定规则", "不依照模型表现调整去重或正类门槛"],
       ["中位数填补", "仅 815 条训练样本", "直接使用训练中位数；本次无缺失"],
       ["逻辑回归标准化", "仅训练集均值和标准差", "直接 transform；不重新 fit"],
       ["异常 IQR 界限", "仅训练集分位数", "仅诊断，不删行、不变换"],
       ["模型参数 / 阈值", "参数事先固定；阈值由验证集确定", "测试集不选择参数、阈值或特征"]], [114, 159, width-273])
    sub("4.3　多数类基线先于三个分类模型训练")
    p("训练集负类 705 条，多于正类 110 条，故基线始终预测 0。其测试混淆矩阵为 TN=235、FP=0、FN=37、TP=0。")
    table([["准确率", "查准率", "查全率", "F1", "FP + 3FN"],
           ["0.8640", "0.0000", "0.0000", "0.0000", "111"]], [100, 100, 100, 100, width-400])
    p("基线没有预测正类，查准率的数学分母为 0。本实验按 zero_division=0 报告为 0，并明确这一约定；不是把它解释成经过可靠测量的零精度。高准确率并不能弥补全部漏报。")

    # 05: model explanations.
    page(); heading("5　三个分类模型：设置与学习机制")
    sub("5.1　逻辑回归")
    p("模型先计算 z = b₀ + Σbⱼxⱼ，再通过 p = 1 / (1 + exp(−z)) 给出正类概率估计。predict_proba 的正类列在代码中核对为 classes_=[0,1] 的第 2 列；本实验显式采用 p≥t 判为正类，默认 t=0.50。概率不是最终类别，改变阈值不会重新拟合系数。")
    p("11 个变量量纲不同，先按训练均值和标准差标准化。固定 C=1、L2 正则、lbfgs 求解器、max_iter=2000。在其他变量保持不变时，正系数意味着模型中的正类对数优势增加，负系数相反；这属于条件关联而非因果。线性对数优势关系便于解释、训练快，但难以自动表示复杂非线性与交互。")
    sub("5.2　随机森林")
    p("单棵决策树按特征阈值把样本分区，容易因训练样本小幅变化而改变结构。随机森林对训练记录有放回抽样，并在节点分裂时随机选择候选特征，从而构建多棵不完全相同的树。本次实现平均各树的类别概率，再按阈值分类；多树平均能缓解单树高方差，但不能保证不发生过拟合。")
    p("固定 300 棵树、max_depth=8、min_samples_leaf=3、max_features=sqrt、bootstrap=True。树的分裂基于特征顺序，通常不需要标准化。相比逻辑回归，它更容易表示分段非线性和变量交互。局限是整体决策难以用一组简单系数解释，相关特征会影响重要性分配。")
    sub("5.3　XGBoost")
    p("本题全部是数值输入，选择 XGBoost 的浅树提升模型即可，不需要 CatBoost 的类别特征处理优势。固定二分类 logistic 目标、200 轮、树深 3、学习率 0.05、subsample=0.8、colsample_bytree=0.8、min_child_weight=3、reg_lambda=2；采用 CPU hist，单线程，种子 42。未使用测试集 early stopping，也未进行超参数搜索。")
    p("随机森林中的树主要独立训练后平均；Boosting 则顺序添加新树，沿当前损失的梯度方向修正此前模型未学好的模式。学习率控制每轮贡献，浅树、采样与正则限制复杂度。连续修正能表示复杂关系，也可能追随噪声；模型更复杂或分数更高不等于必然更适合部署。")
    sub("公平比较约定")
    p("三种模型使用完全相同的输入特征、训练记录、验证记录、测试记录和正类定义；均不使用类别权重或重采样。模型参数在测试评价前固定，三个候选均获得相同的 19 个阈值候选。拟合仅使用 815 条训练样本；选定后不把验证样本并回重训，以避免改变已确定阈值的含义。")
    p("默认阈值表回答“同一 0.50 决策规则下有什么差异”；验证集确定的阈值表回答“考虑既定错误成本后如何选择”。两张表不能混用。", "small")

    # 06: default results and overfitting.
    page(); heading("5（续）　模型运行结果与过拟合检查")
    sub("默认阈值 0.50：测试集 n=272")
    table([["模型", "准确率", "查准率", "查全率", "F1", "主要错误"]] +
          [[zh[name]] + [f(M[name]["test_default"][k]) for k in ["accuracy","precision","recall","f1"]] +
           [f'FN={M[name]["test_default"]["fn"]}\nFP={M[name]["test_default"]["fp"]}'] for name in names],
          [100, 76, 76, 76, 76, width-404])
    figure("model_comparison.png")
    p("图 1　默认阈值下四项测试指标。所有查准率、查全率和 F1 都针对正类 1。", "caption")
    p("三个分类模型的 F1 均高于多数类基线；但默认阈值仍漏掉大多数正类。XGBoost 的 F1=0.4483 和召回率=0.3514 高于另外两种模型；随机森林准确率=0.8897、查准率=0.7333 更高。不同指标回答不同问题，不能只按准确率排名。")
    sub("相同默认阈值下的训练、验证与测试差异")
    table([["模型", "训练 F1", "验证 F1", "测试 F1", "训练−测试差"]] +
          [[zh[name], f(M[name]["train_default"]["f1"]), f(M[name]["validation_default"]["f1"]),
            f(M[name]["test_default"]["f1"]), f(M[name]["train_default"]["f1"]-M[name]["test_default"]["f1"])] for name in names[1:]],
          [115, 98, 98, 98, width-409])
    p("逻辑回归训练 / 测试 F1 相差 0.0168；随机森林相差 0.3615，XGBoost 相差 0.3136，树集成存在明显泛化落差。该差异是过拟合风险信号，不证明每一处差异都由过拟合造成。这里只做一次固定划分，没有交叉验证置信区间，不能宣称某模型在总体上显著优于其他模型。")

    # 07: confusion matrices and exact formula check.
    page(); heading("6　混淆矩阵与分类评价")
    p("图中行是真实类别、列是预测类别，两轴顺序均为 0、1。左上 TN：普通酒判普通；右上 FP：普通酒判高等级；左下 FN：高等级酒判普通；右下 TP：高等级酒判高等级。每个矩阵总和均为 272，真实正类行之和均为 37。")
    figure("confusion_matrices.png", w=width-12)
    p("图 2　多数类基线和三个模型的测试混淆矩阵（阈值 0.50）。", "caption")
    table([["指标", "公式", "对应问题"],
       ["准确率 Accuracy", "(TP+TN) / (TP+TN+FP+FN)", "全部样本有多少判对"],
       ["查准率 Precision", "TP / (TP+FP)", "推荐复评的酒有多少确为高等级"],
       ["查全率 Recall", "TP / (TP+FN)", "所有高等级酒中找到了多少"],
       ["F1", "2TP / (2TP+FP+FN)", "查准率与查全率的调和平均"]], [102, 225, width-327])
    p("以逻辑回归为例：Accuracy=(227+11)/272=0.8750，Precision=11/(11+8)=0.5789，Recall=11/(11+26)=0.2973，F1=22/(22+8+26)=0.3929。代码对所有模型、所有评价阈值都独立按计数复算，并与 sklearn 结果断言一致。")

    # 08: LR threshold shift.
    page(); heading("6（续）　逻辑回归阈值分析")
    p("模型拟合后，在验证集上比较 t∈{0.05,0.10,…,0.95}，按 FP+3FN 最小选择阈值。平局依次选 F1 较高、查准率较高、阈值较高者。逻辑回归选出 t=0.30；不是在看过测试指标后挑选 0.30。验证成本由默认的 87 降至 71。")
    figure("threshold_validation.png")
    p("图 3　仅验证集上的阈值曲线；虚线标示选出的阈值。", "caption")
    table([["测试指标", "t=0.50", "t=0.30", "变化"]] +
        [["预测为正类数", 19, 40, "+21"], ["准确率", f(lr0["accuracy"]), f(lr1["accuracy"]), "+0.0110"],
         ["查准率", f(lr0["precision"]), f(lr1["precision"]), "−0.0039"],
         ["查全率", f(lr0["recall"]), f(lr1["recall"]), "+0.3243"],
         ["F1", f(lr0["f1"]), f(lr1["f1"]), "+0.2045"],
         ["TN / FP / FN / TP", "227 / 8 / 26 / 11", "218 / 17 / 14 / 23", "FP+9；FN−12"],
         ["FP + 3FN", 86, 59, "−27"]], [133, 125, 125, width-383])
    p("降低阈值后，多推荐了 21 个样本，其中增加 12 个真正例和 9 个假正例。召回率明显上升，查准率略降，代价从 86 降至 59，符合本实验“漏报更贵”的假设。准确率此次也上升，但这是当前样本的结果，不是降低阈值必然提高准确率。")
    sub("阈值选择的业务边界")
    p("若误报成本为 cFP、漏报成本为 cFN，这次变化的成本差为 9cFP−12cFN。只有 cFN/cFP&gt;0.75 时，t=0.30 在这组测试计数上才比 t=0.50 更省成本。若推荐会直接触发昂贵宣传、而不是低成本人工复评，成本结构会不同，应在新的验证数据上重新确定阈值。")
    p("对经过良好校准的概率，1:3 成本对应的理论阈值为 1/(1+3)=0.25；本实验没有验证概率校准，因此采用验证集的离散经验选择，不能把输出 0.30 直接解释为精确的真实发生频率。", "small")

    # 09: selection and computational cost.
    page(); heading("7　模型比较与最终选择")
    sub("7.1　按同一成本规则在验证集选择")
    table([["模型", "选出阈值", "验证 F1", "验证 FP/FN", "验证成本"]] +
          [[zh[n], f'{M[n]["selected_threshold"]:.2f}', f(M[n]["validation_selected"]["f1"]),
           f'{M[n]["validation_selected"]["fp"]}/{M[n]["validation_selected"]["fn"]}', M[n]["validation_selected"]["cost"]] for n in names],
          [118, 83, 99, 110, width-410])
    p("随机森林的验证成本 58 最低，且验证 F1=0.6000，高于逻辑回归 0.5185 和 XGBoost 0.5505。按事先规则，本次保留的方案为<b>随机森林 + 阈值 0.30</b>。这一选择在首次测试评价前完成。")
    sub("7.2　将各自验证阈值固定后，进行测试评价")
    table([["模型", "阈值", "准确率", "查准率", "查全率", "F1", "成本"]] +
          [[zh[n], f'{M[n]["selected_threshold"]:.2f}'] + [f(M[n]["test_selected"][k]) for k in ["accuracy","precision","recall","f1"]] +
           [M[n]["test_selected"]["cost"]] for n in names],
          [97, 49, 74, 74, 74, 74, width-442])
    p("在各自验证阈值下，逻辑回归的测试 F1=0.5974、成本=59，优于已选随机森林的 0.5316、69。XGBoost 的召回率最高（0.7568），但产生 49 个 FP，成本仍为 76。证据表明：验证排序与测试排序可能变化，复杂模型的优势并不稳定。不能为了报告更好看而把逻辑回归改写为“测试前已选最优模型”。")
    sub("7.3　计算成本、解释性与应用取舍")
    table([["模型", "训练耗时（秒）", "272 条预测（毫秒）", "解释性 / 适用性"]] +
          [[zh[n], f'{M[n]["fit_seconds"]:.4f}', f'{M[n]["predict_seconds_test_batch"]*1000:.3f}',
            {names[1]:"系数与方向清楚；适合透明筛选", names[2]:"表示非线性；整体机制较难解释", names[3]:"逐轮优化损失；参数和维护更复杂"}[n]] for n in names[1:]],
          [100, 103, 125, width-328])
    p("耗时为本机单线程的一次实测，包含流水线，不含下载、导入、绘图与解释计算；毫秒级结果受调度影响，不作稳定性能基准。11 个数值特征、815 条训练样本使三者均可运行，逻辑回归训练更轻量，也最容易向会计或管理人员解释。")
    p("最终保留验证集选出的随机森林用于本次留出评价；若讨论实际落地，当前测试证据支持把更简单的逻辑回归作为下一轮独立验证候选。任何上线决定都还需要真实成本、复评容量、校准和新批次验证；本报告不宣布可直接生产部署。", "small")

    # 10: error analysis.
    page(); heading("7（续）　测试误分类样本分析")
    p("分析对象为测试前已选出的随机森林（t=0.30）：TN=214、FP=21、FN=16、TP=21。固定按原始数据行号升序，取前三个 FP 与前三个 FN，避免只挑支持结论的案例。编号是原 CSV 数据行号，不是客户或企业身份。")
    table([["行号", "原评分", "真实→预测", "正类概率", "错误", "酒精度 / 挥发酸 / 硫酸盐"]] +
          [[e["source_row_id"], e["quality"], f'{e["actual"]}→{e["prediction_selected"]}', f(e["probability"]), e["error"],
            f'{e["alcohol"]:.1f} / {e["volatile acidity"]:.2f} / {e["sulphates"]:.2f}'] for e in r["error_examples"]],
          [48, 52, 78, 80, 48, width-306])
    table([["样本", "可观察事实", "可能原因与不能推断的内容"],
       ["143（FP）", "quality=6，酒精度 14.0，p=0.4763；默认 0.50 判对，降低阈值后成为 FP。", "较高酒精度与部分高等级样本相似，阈值变更使其入选。不能因此推断评分错误或应提高酒精度。"],
       ["337（FP）", "quality=6，酒精度 12.5、硫酸盐 0.70，p=0.4075。", "理化特征可能呈现高等级相关模式，但不足以完整预测感官评分。与 7 分门槛只差 1 分，二值化放大相邻等级差异。"],
       ["485（FP）", "quality=6，残糖 4.1、酒精度 13.4，p=0.3861。", "残糖超过训练 IQR 上界，可能处于较稀疏区域；这只是诊断假设，不是删除该记录的理由。"],
       ["8（FN）", "quality=7，酒精度 10.0、挥发酸 0.65、硫酸盐 0.47，p=0.0759。", "部分特征不像模型所学的典型高等级组合；缺少香气等感官信息、正类不足或模型表达限制均可能影响。"],
       ["201（FN）", "quality=7，p=0.2856，距离阈值 0.30 仅约 0.0144。", "典型阈值附近样本。降低阈值可能挽回它，但会引入其他 FP；不能为了修正单个测试案例重新选阈值。"],
       ["210（FN）", "quality=7，酒精度 10.5、硫酸盐 0.88，p=0.1663。", "不同变量给出的相关信号不一致，说明高等级样本具有异质性。单变量高低不能决定最终品质。"]], [68, 205, width-273])
    sub("错误来源的分层判断")
    p("数据质量方面：已排查显式缺失、重复与基本不合理值，但没有原始检测档案，不能证明不存在测量或评分误差。变量方面：公开表缺少香气、品种、产地细分等潜在信息。模型方面：有限正类、树的平滑、非线性表达与阈值策略都可能影响。以上是与记录一致的解释假设，不是对单个预测路径的因果证明。")

    # 11: interpretation and limits.
    page(); heading("8　结果边界与模型解释")
    figure("interpretation.png", w=440)
    p("图 4　左：逻辑回归标准化系数（绝对值前六）；右：已选随机森林在验证集上的置换重要性（前六）。误差线为 10 次置换的标准差。", "caption")
    coef = {x["feature"]: x for x in r["lr_coefficients"]}
    table([["变量", "标准化系数", "每增加 1 个训练标准差的优势比", "方向解释"]] +
          [[short[k], f(coef[k]["coefficient"]), f(coef[k]["odds_ratio_per_sd"]),
            "模型条件正关联" if coef[k]["coefficient"] > 0 else "模型条件负关联"]
            for k in ["alcohol", "sulphates", "fixed acidity", "volatile acidity", "chlorides", "density"]],
          [110, 100, 183, width-393])
    p("例如酒精度系数 0.8138，表示其他标准化变量不变时，增加 1 个训练标准差的酒精度，对应模型正类优势乘以 exp(0.8138)=2.2565；不是概率直接增加 81.38 个百分点。挥发酸系数 −0.6597，对应优势比 0.5170。特征相关和正则化可能改变系数方向与大小。")
    p("置换重要性在验证集上打乱一个特征，观察 Average Precision（AP）下降；AP 是补充的正类排序指标，不代替必需的四项分类指标。相关变量可能分摊重要性，置换也可能破坏真实联合分布；该图不能解释干预某项理化指标会怎样改变酒的质量。")
    sub("结果能够支持什么，不能支持什么")
    p("本结果支持同源、去重酒样的一次分层留出比较。测试集只有 37 个正类，一个正类判别变化就使召回率变化约 2.70 个百分点；当前差距可能受划分影响，不能给出普遍或显著优势结论。")
    p("原表没有时间、生产批次或酒庄 ID，去重不能消除未知批次依赖。不能直接推广到其他年份、地区、白葡萄酒或其他企业客户；应先做按时间 / 生产批次划分的外部验证。评分 ≥7 的门槛改变也会形成另一个任务。")
    p("模型学到的是观测数据中的预测关联。没有随机干预、混杂控制或因果识别设计，因此不能从系数、树重要性或预测概率推出“增加某成分会导致评分上升”。即使最复杂模型得分最高，仍需同时评估真实错误成本、解释要求、运行成本、校准和维护条件。")

    # 12: reproducibility and honest AI attribution.
    page(); heading("8（续）　复现信息、AI 核验与参考来源")
    sub("运行环境与步骤")
    p(f'本次使用 Python {r["environment"]["python"]}，Windows 11 x64，CPU 执行；逻辑 / 树模型和数值线程均限制为 1。处理器：Intel64 Family 6 Model 183 Stepping 1。数据获取日期和实验记录日期为 2026-11-18，划分及模型随机种子均为 42。')
    table([["依赖", "版本", "依赖", "版本"],
        ["NumPy", "2.3.5", "pandas", "3.0.1"], ["SciPy", "1.18.1", "scikit-learn", "1.7.2"],
        ["Matplotlib", "3.10.7", "XGBoost", "3.1.1"], ["threadpoolctl", "3.8.0", "joblib", "1.6.0"]], [140, 110, 140, width-390])
    p("先在独立 Python 环境按代码文件顶部说明安装固定依赖，再运行下列命令。代码从 UCI 官方包读取红酒表并校验 SHA-256；离线时加 --data 指向同一官方 CSV。输出目录必须尚不存在，以免覆盖此前结果。")
    p("python classification_lab3.py --output lab3_results", "code")
    p("结果目录生成数据检查、split_indices.json、metrics.csv、predictions.csv、validation_thresholds.csv、error_examples.csv、四幅图、results.json 和 manifest.json。manifest 记录数据 / 代码 / 输出哈希及模型参数；耗时和运行时间戳随机器与运行变化，不要求字节相同。", "small")
    sub("AI 使用说明与已经完成的自动核验")
    p("使用 AI 辅助理解任务、生成和修改 Python 代码、排查环境与输出问题、整理报告。下表是本次脚本与产物检查实际完成的自动核验；不将其冒称为提交者本人已完成的人工复核。")
    table([["核验内容", "证据 / 处理"],
       ["目标、类别与输入", "断言 quality≥7 为 1；classes_=[0,1]；输入仅限列白名单，quality 和编号未入模。"],
       ["划分与预处理", "索引和特征组合跨集合无交集；填补中位数、缩放均值与训练集统计一致，scaler 记录的拟合样本数为 815。"],
       ["评价与比较公平性", "混淆矩阵总数正确；Accuracy / Precision / Recall / F1 按公式复算并与 sklearn 对照；阈值和模型仅按验证集确定。"],
       ["生成过程中的修正", "首次运行在清单输出时发现 XGBoost 的 NaN 缺失值标记不符合严格 JSON；修正为字符串记载后完整执行成功。数据、参数与划分没有据测试结果调整。"],
       ["解释与个人复核边界", "明确区分优势比与概率、关联与因果、验证选择与测试排序。提交者应亲自运行并解释上述关键环节，不能把 AI 自动核验声明为本人已核验。"]], [125, width-125])
    sub("参考来源")
    p('[1] Cortez, P., Cerdeira, A., Almeida, F., Matos, T., &amp; Reis, J. (2009). Wine Quality [Dataset]. UCI. <link href="https://doi.org/10.24432/C56S3T" color="#1E6A78">doi:10.24432/C56S3T</link>；官方包内 winequality.names。<br/>[2] Cortez et al. (2009). Modeling wine preferences by data mining from physicochemical properties. Decision Support Systems, 47(4), 547–553. <link href="https://doi.org/10.1016/j.dss.2009.05.016" color="#1E6A78">doi:10.1016/j.dss.2009.05.016</link>。<br/>[3] 用户提供的《课内实验指导书：实验三——分类学习与模型比较》，任务、报告结构及提交要求。', "small")

    def furniture(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CAD8DD"))
        canvas.line(44, A4[1]-39, A4[0]-44, A4[1]-39)
        canvas.setFont("Hei", 8)
        canvas.setFillColor(grey)
        canvas.drawString(44, A4[1]-29, "分类学习与模型比较  |  UCI 红葡萄酒质量")
        canvas.setFont("Song", 8)
        canvas.drawRightString(A4[0]-44, 26, f"第 {doc.page} 页")
        canvas.drawString(44, 26, "固定种子 42 · 独立测试评价 · AI 辅助与自动核验已披露")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=44, leftMargin=44,
        topMargin=54, bottomMargin=45, title="实验三：分类学习与模型比较——红葡萄酒高等级筛选",
        author="课程实验材料（AI辅助生成）", subject="UCI Wine Quality；逻辑回归、随机森林与XGBoost")
    doc.build(story, onFirstPage=furniture, onLaterPages=furniture)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.results, args.output)
