# III.C 公式修订与 IEEE 双栏排版

本次根据用户 2026-10-14 贴出的 III.C 和完整 LaTeX，只修改公式小节及其必要说明。新版完整源文件在 III.C 以外的文本与本次附件逐字一致（按统一换行读取比较）。

## 使用

- compliance_checking.tex：直接粘贴替换原 III.C；现有 amsmath 足够，无须新增宏包或全局排版设置。
- 2027_CSCWD_32_formulas_corrected.tex：已完成同一替换的完整论文源文件。Overleaf 中选择它作为主文件，使用 pdfLaTeX。
- overleaf_formula_revision.zip：上述主文件、公式小节、三幅原图和 reference.bib，可作为完整项目上传。
- formula_preview.pdf：独立公式预览，IEEEtran 标准栏宽；只在预览内于 actor 小标题前人工换栏，正文无强制换栏。
- full_layout_preview.pdf：全文排版预览，6 页；III.C 从第 3 页开始，7 个公式集中在第 4 页左栏。

图像从用户的第 32 版 PDF 原始嵌入对象提取，没有重新绘制。reference.bib 复用项目已有的 revision_20261011/references_18.bib，包含本次源文全部引文键。用户没有提供本次实际 reference.bib，因此全文预览的参考文献格式可能与用户原工程不同；整合时可继续用用户现有 .bib。

## 数学与排版

对照 Sun 作者稿 §4.3、Definitions 4–7（第 13–14 页）恢复匹配和三类违规定义。7 个公式去除纯排版控制符后，与上一轮逐项核对的原式数学记号序列一致。

- 恢复公共 C 候选集合，保留原存在量词、候选范围及严格不等号。
- 恢复 A_m/E_m/R_m 的活动、事件和执行者含义；不把 A_m 当作抽取后的动作集合。
- 删除 m_A/m_P、s、B、I、S 等新增辅助定义和等价改写。
- 长式在原表达式内部换行，未拆成两项分数，未增加新判据。
- 缺失动作和 actor 分数保留完整分子；顺序分子用三行连续书写，避免贯穿多行的高大括号和竖线。
- 正文字号和公式字号保持 IEEEtran 默认值，未使用 resizebox/scalebox/small/scriptsize 等整体缩放手段。
- 采用 Sun 的 actor 阈值记号 vartheta，并用一句话说明与原实验章节 theta 对应，避免修改图表。
- 公式标签保留仍在使用的 7 个标签，自动编号；本次附件中没有引用被移除辅助公式的交叉引用。

## 验证与编译

- 本地使用 Tectonic 0.17.0 编译并逐页检查最终 PNG；编译器来自官方发布，ZIP SHA-256 已核对：
  f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f。
- 主文件保持用户原导言区。Tectonic 使用 XeTeX，全文预览源 full_layout_preview.tex 仅在主文件之前额外加入 RequirePackage[OT1]{fontenc}，确保采用 IEEEtran 的 Times 字体而非 Unicode 编译的字体回退。这一行没有加入交付的论文主文件。
- 独立预览：1 页，无 overfull hbox/vbox。
- 全文预览：6 页，无 overfull hbox/vbox、未解析引用或字体替换。既有导言区仍有 cite/natbib、caption、inputenc 警告；旧算法宏包注释编码有警告，原摘要、引言和参考文献有 3 处 underfull 提示；本次 III.C 无这些段落警告。未为无关宏包或文字扩大修改范围。
- 最终校验详情、输入/输出哈希见 verification.json。
- 仅进行了文档检查，未运行实验 audit、代码/全量测试、LLM/API 或实验复算。

## 范围说明

本次保证原式转写和版面经过检查，不代表全文的实验结果已经重新验证。上一轮 REVIEW_AND_USE.md 所列的事件业务对象范围、表三和阈值曲线对应问题仍存在；本次未修改旧实验数值，也不把排版预览当作科学结果最终验收。

Git 空白检查说明：完整主文件第 65、367 行保留了用户附件原有的行尾空格；预览副本对应第 66、368 行。为维持 III.C 之外文本一致，未顺手清理这两处；新公式小节无行尾空白问题。
