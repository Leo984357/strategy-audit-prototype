"""
生成课程论文 Word 文档
格式规范 (国内高校课程论文通用):
  标题: 黑体 二号 (22pt) 居中加粗
  节标题(一、二、): 黑体 三号 (16pt) 加粗
  子节标题(1.1): 黑体 四号 (14pt) 加粗
  正文: 宋体 小四 (12pt) 1.5倍行距
  摘要/关键词: 宋体 小四 (12pt)
  参考文献: 宋体 五号 (10.5pt)
  页边距: 上下2.54cm 左右3.18cm
"""
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from copy import deepcopy
import os

_bookmark_id_counter = [0]

def _new_bm_id():
    _bookmark_id_counter[0] += 1
    return _bookmark_id_counter[0]

def add_bookmark_to_paragraph(paragraph, bm_name):
    """Add a bookmark around the entire paragraph content."""
    bm_id = str(_new_bm_id())
    bm_start = OxmlElement('w:bookmarkStart')
    bm_start.set(qn('w:id'), bm_id)
    bm_start.set(qn('w:name'), bm_name)
    bm_end = OxmlElement('w:bookmarkEnd')
    bm_end.set(qn('w:id'), bm_id)
    paragraph._p.insert(0, bm_start)
    paragraph._p.append(bm_end)
    return paragraph

def add_bookmark_and_ref_to_run(paragraph, before_text, bm_name, display_text, after_text=""):
    """
    Add text like "如图" + [REF field to bm_name showing "图1"] + "所示"
    Inserts a REF field with a bookmark target around the figure caption.
    """
    # before text
    if before_text:
        run_before = paragraph.add_run(before_text)
        run_before.font.name = '宋体'
        run_before.font.size = Pt(12)
        run_before.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # REF field
    bm_id = str(_new_bm_id())
    r1 = OxmlElement('w:r')
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    r1.append(fld1)
    paragraph._p.append(r1)

    r2 = OxmlElement('w:r')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = f' REF {bm_name} \\h '
    r2.append(instr)
    paragraph._p.append(r2)

    r3 = OxmlElement('w:r')
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    r3.append(fld2)
    paragraph._p.append(r3)

    r4 = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = display_text
    r4.append(t)
    paragraph._p.append(r4)

    r5 = OxmlElement('w:r')
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    r5.append(fld3)
    paragraph._p.append(r5)

    # after text
    if after_text:
        run_after = paragraph.add_run(after_text)
        run_after.font.name = '宋体'
        run_after.font.size = Pt(12)
        run_after.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def add_body_with_ref(text, refs):
    """
    Create body paragraph where refs is a list of (bm_name, display_text) tuples.
    Text is split on '{}' placeholders.
    Example: add_body_with_ref("如图{}所示", [("Fig1", "图1")])
    """
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5

    parts = text.split('{}')
    for i, part in enumerate(parts):
        if part:
            run = p.add_run(part)
            set_font(run, '宋体', 'Times New Roman', 12)
        if i < len(refs):
            bm_name, display = refs[i]
            bm_id = str(_new_bm_id())
            r1 = OxmlElement('w:r')
            f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin'); r1.append(f1); p._p.append(r1)
            r2 = OxmlElement('w:r')
            instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve')
            instr.text = f' REF {bm_name} \\h '; r2.append(instr); p._p.append(r2)
            r3 = OxmlElement('w:r')
            f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'separate'); r3.append(f2); p._p.append(r3)
            r4 = OxmlElement('w:r')
            t = OxmlElement('w:t'); t.text = display; r4.append(t); p._p.append(r4)
            r5 = OxmlElement('w:r')
            f3 = OxmlElement('w:fldChar'); f3.set(qn('w:fldCharType'), 'end'); r5.append(f3); p._p.append(r5)
    return p

OUT_DIR = "/Users/leolee/Desktop/课程/大三下课程/区块链/课程论文"
FIG_DIR = os.path.join(OUT_DIR, "figures")

doc = Document()

settings = doc.settings.element
update_fields = OxmlElement('w:updateFields')
update_fields.set(qn('w:val'), 'true')
settings.append(update_fields)

for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(3.18)

style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def set_font(run, name_cn, name_en, size, bold=False, color=None):
    run.font.name = name_en
    run.font.size = Pt(size)
    run.bold = bold
    run.element.rPr.rFonts.set(qn('w:eastAsia'), name_cn)
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_title(text, size=22):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_font(run, '黑体', 'Times New Roman', size, bold=True)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    return p

_h1_counter = [0]
def add_heading1(text, bm_name=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '黑体', 'Times New Roman', 16, bold=True)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    if bm_name:
        add_bookmark_to_paragraph(p, bm_name)
    return p

def add_heading2(text, bm_name=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '黑体', 'Times New Roman', 14, bold=True)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    if bm_name:
        add_bookmark_to_paragraph(p, bm_name)
    return p

def add_body(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '宋体', 'Times New Roman', 12)
    p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p

def add_body_no_indent(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '宋体', 'Times New Roman', 12)
    p.paragraph_format.line_spacing = 1.5
    return p

def add_figure(fig_name, caption, bookmark_name=None):
    fig_path = os.path.join(FIG_DIR, fig_name)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(fig_path, width=Inches(5.2))
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = p2.add_run(caption)
    set_font(run2, '宋体', 'Times New Roman', 10.5)
    p2.paragraph_format.space_after = Pt(6)

    if bookmark_name:
        add_bookmark_to_paragraph(p2, bookmark_name)
    return p2

def add_formula(text, align_center=True):
    """Add a displayed formula (Cambria Math font for proper rendering)."""
    p = doc.add_paragraph()
    if align_center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    # Cambria Math is Word's built-in math font, supports all Unicode math chars
    run.font.name = 'Cambria Math'
    run.font.size = Pt(11)
    run.italic = True
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.25
    return p

def add_formula_explanation(formula, explanation):
    """Add a formula with its variable explanation."""
    add_formula(formula)
    p = doc.add_paragraph()
    run = p.add_run(explanation)
    set_font(run, '宋体', 'Times New Roman', 11)
    p.paragraph_format.first_line_indent = Pt(22)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    return p

def add_ref(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '宋体', 'Times New Roman', 10.5)
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p

TITLE = "基于联盟链的量化策略可信回测与程序化交易合规审计机制研究"

add_title(TITLE, 22)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("李硕仁")
set_font(run, '楷体', 'Times New Roman', 14)
p.paragraph_format.space_after = Pt(2)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("金融工程专业")
set_font(run, '宋体', 'Times New Roman', 12)
p.paragraph_format.space_after = Pt(12)

add_heading1("摘  要")

add_body(
    "量化投资策略从研发到实盘上线涉及数据获取、因子挖掘、策略回测、参数优化、合规报备等多个环节，"
    "每个环节都存在信任问题：数据版本混乱导致结果不可复现，回测参数可被事后调整（p-hacking），"
    "合规记录依赖内部纸质或电子文件缺乏第三方审计效力。针对上述问题，本文提出一种基于联盟链的量化策略全生命周期可信审计框架，"
    "利用联盟链的多方参与特性，结合智能合约实现策略注册、回测存证、合规检查、风控事件记录的自动化管理。"
    "系统采用链下存储原始数据、链上存储SHA-256哈希值的混合方案，在保证数据隐私的同时实现内容完整性验证。"
    "本文以沪深300多因子选股策略为案例，基于真实的QMT量化回测项目数据（144个Alpha因子、LightGBM模型、"
    "163组实验配置、4次完整回测），部署了基于Hardhat的Solidity智能合约原型，验证了策略全生命周期审计流程的可行性。"
    "实验结果表明，该系统能够增强量化策略研发中的数据可追溯性和防篡改能力，并为2025年上交所/深交所程序化交易新规下的合规审计提供技术支撑。"
    "需要指出的是，当前方案主要实现了链上哈希存证与合规状态自动化管理，距离\u201c过程可信\u201d（如回测环境复现、未来函数检测、因子计算验证等）仍有距离，相关讨论见第四节。"
)

p = doc.add_paragraph()
run = p.add_run("关键词：")
set_font(run, '黑体', 'Times New Roman', 12, bold=True)
run2 = p.add_run("联盟链；量化策略可信回测；程序化交易合规审计；智能合约；数据存证")
set_font(run2, '宋体', 'Times New Roman', 12)

doc.add_page_break()

# ============================================================
add_heading1("一、背景", bm_name="Sec1")

add_heading2("1.1 量化策略研发的信任困境", bm_name="Sec1_1")

add_body(
    "量化投资策略的完整生命周期涵盖数据获取、因子发现、策略回测、参数优化、模拟交易、实盘上线及运行监控等多个阶段。"
    "在这一链条中，每一环节均存在程度不同的信任问题。首先，数据版本管理混乱是最为常见的困难——"
    "同一策略可能在不同时间点使用不同版本的行情数据、财务数据或另类数据，导致回测结果无法被复现。"
    "其次，回测参数的事后调整（即p-hacking或data snooping）是量化策略研发中最为隐蔽的信任危机："
    "策略开发者可以通过反复调整回测参数筛选出表现最优的结果进行报告，而这一调整过程并不会被记录和审计。"
    "此外，幸存者偏差、未来函数、过拟合等技术问题进一步削弱了回测结果的可信度。"
)

add_body(
    "学术界对上述问题已有广泛讨论。Bailey等（2014）[2]的研究表明，在大量策略尝试中筛选出高夏普比率的策略存在严重的回测选择偏差"
    "（backtest overfitting），并提出Deflated Sharpe Ratio等修正指标。Harvey与Liu（2019）[3]对因子研究中的多重比较问题进行了系统分析。"
    "然而，现有解决方案主要从统计方法层面进行修正，缺乏底层基础设施对策略研发全过程的完整性进行保障。"
    "传统版本控制系统如Git能够追溯代码变更，但无法约束回测执行的完整性和参数声明的真实性——"
    "Git只能告诉你\"谁修改了什么代码\"，无法证明\"某次回测确实是使用声明中的参数和数据执行的\"。"
)

add_heading2("1.2 程序化交易合规监管的新要求")

add_body(
    "2025年，中国资本市场程序化交易监管进入新阶段。上海证券交易所与深圳证券交易所同步发布《程序化交易管理实施细则》"
    "（2025年7月7日起施行），对程序化交易提出了系统性监管要求[5][6]。核心要求包括：第一，程序化交易报告制度——"
    "策略类型、交易参数、服务器位置、交易系统信息等关键要素必须向交易所报备；第二，交易行为管理——禁止利用程序化交易"
    "实施市场操纵、异常交易等行为；第三，信息系统管理——交易系统须通过交易所测试方可接入；"
    "第四，高频交易管理——符合高频交易认定标准的策略需满足额外的报告和监控要求。"
    "与此同时，中国证监会发布《期货市场程序化交易管理规定》（2025），对期货市场的程序化交易提出了全过程监管要求[7]。"
)

add_body(
    "上述监管新规对量化投资机构的信息管理能力提出了极高要求。然而，当前行业实践中的合规手段"
    "仍依赖于机构内部的纸质或电子记录：策略报备材料以文档形式保存，合规检查记录存储于内部数据库，"
    "风控事件多通过邮件或日志留存。上述方式存在以下固有缺陷：记录可以被事后修改或删除而不留痕迹、"
    "缺乏独立第三方的审计机制、跨机构（如FOF基金管理人对子基金的策略审计）信任成本高昂。"
    "因此，构建一套技术上可验证、法律上可采信的策略全生命周期审计机制具有重要的现实意义。"
    "本文的详细方案设计将在第3节中阐述。"
)

add_heading2("1.3 以HS300多因子选股策略为案例引入")

add_body(
    "本文以一个真实的量化策略研发项目为案例：基于沪深300成分股的多因子选股策略。该项目包含144个Alpha因子库、"
    "LightGBM机器学习模型、10天调仓频率、163组实验配置，并通过MLflow对139次实验进行了系统追踪。"
    "该策略已完成完整的回测流程，生成了4份完整的回测报告。这一案例将贯穿全文，用于说明区块链审计机制的具体实施方案。"
    "选择这一案例的理由在于：它涵盖了因子定义、数据准备、模型训练、回测验证、参数优化等量化策略研发的完整环节，"
    "各环节均有完善的数字化产出物（代码、配置YAML、回测JSON报告、因子目录等），"
    "能够为区块链存证审计提供充分的实验数据支持。"
)

# ============================================================
add_heading1("二、区块链技术解决问题的逻辑", bm_name="Sec2")

add_heading2("2.1 联盟链作为审计基础设施的选择依据", bm_name="Sec2_1")

add_body(
    "区块链技术为上述问题的解决提供了全新的技术路径。在公有链、私有链与联盟链三种主要形态中，"
    "联盟链因其独特的属性成为量化策略审计场景的自然选择。"
)

add_body(
    "公有链（如以太坊主网）虽然具有最高的去中心化程度，但其性能瓶颈（以太坊主网TPS约15-30）"
    "无法支撑量化策略日频甚至高频的存证需求，且交易数据公开可查的属性与量化策略的知识产权保护要求存在根本冲突——"
    "策略代码的哈希值虽然不直接暴露策略内容，但频繁的哈希提交行为本身可能泄露策略的活跃程度和时间窗口信息。"
    "私有链虽然解决了性能和隐私问题，但其信任基础单一——由单一机构控制的区块链网络在审计场景中缺乏公信力，"
    "本质上与传统中心化数据库无异。"
)

add_body(
    "联盟链则兼顾了性能、隐私与信任三方需求。在联盟链架构中，策略研发团队、合规部门、风控部门、外部审计机构及监管机构"
    "组成有限节点网络，各节点根据角色分配不同的读写权限。共识机制可采用PBFT（Practical Byzantine Fault Tolerance）"
    "或Raft等高效算法，存证确认延迟可控制在秒级以内，完全满足量化策略日频的存证需求。"
    "Hyperledger Fabric[10]作为联盟链的代表性实现方案，提供了通道机制（channel）实现数据隔离、"
    "背书策略实现灵活权限控制等企业级特性，是为本系统的底层区块链平台候选方案。"
)

add_heading2("2.2 链下存储与链上哈希的核心范式")

add_body(
    "区块链的存储资源是稀缺且昂贵的。为在有限的链上资源条件下实现充分的数据完整性保障，"
    "本文采用\"链下存储原始数据、链上存储哈希摘要\"的混合存证范式。具体而言：策略的完整代码、"
    "历史行情数据、因子值矩阵、回测详细记录等体量庞大的原始数据存储于链下的分布式文件系统"
    "（如IPFS或企业内部NAS/S3），仅将这些数据文件的SHA-256哈希值存储于区块链上。"
)

add_body(
    "该范式的工作原理如下：当策略开发者完成一次策略修改或一次回测运行后，系统自动计算涉"
    "及的所有数据文件的SHA-256哈希值，并将这些哈希值打包提交至智能合约。智能合约记录提交者地址、"
    "提交时间戳（使用block.timestamp）以及哈希值本身，形成一条不可篡改的存证记录。"
    "事后审计时，审计节点从链下获取原始数据，重新计算哈希值，与链上记录的哈希值进行比对。"
    "若哈希值一致，则证明该数据与提交时的数据完全一致，未被任何形式的篡改。"
    "这一取证的简洁性（哈希比对结果为是/否）极大降低了审计过程的复杂度和争议空间。"
)

add_body(
    "此外，Merkle树结构被用于组织多版本策略文件或批量因子定义的哈希值，实现在O(log n)时间复杂度"
    "内对单个文件的独立验证——审计节点只需提供目标文件的Merkle路径即可完成验证，无需下载全部数据。"
    "这一机制在因子库版本管理场景中尤为实用：144个因子定义文件可以组织为一棵Merkle树，"
    "审计人员只需验证特定因子的Merkle路径即可确认其在某个时间点的存在性和完整性。"
)

add_body("SHA-256哈希函数的数学定义为：")

add_formula_explanation(
    "H(M) = SHA-256(M),  H ∈ {0,1}^256",
    "其中 M 为任意长度的输入消息（策略代码文件、回测配置文件等），H 为输出的256位哈希值。"
    "该函数具有三个关键性质：（1）抗原像性——给定H，难以找到M使得H(M)=H；"
    "（2）抗第二原像性——给定M₁，难以找到M₂≠M₁使得H(M₁)=H(M₂)；"
    "（3）抗碰撞性——难以找到任意M₁≠M₂使得H(M₁)=H(M₂)。"
    "上述性质确保了哈希值可以作为数据内容的唯一指纹使用。"
)

add_body("Merkle树验证的数学表达为：")

add_formula_explanation(
    "Root = H( H( H(Leaf₁) || H(Leaf₂) ) || H( H(Leaf₃) || H(Leaf₄) ) )",
    "其中 Leaf₁...Leaf₄ 为四个因子定义文件的哈希值，||表示字符串连接操作，"
    "Root为Merkle根哈希。验证单个Leafᵢ时，只需提供从该叶子到根的Merkle路径（log₂n个哈希值），"
    "无需提供所有叶子节点。"
)

add_heading2("2.3 智能合约实现流程控制")

add_body(
    "智能合约在本系统中的核心功能是实施策略生命周期的状态转换控制。策略的生命周期被划分为六个状态："
    "研发中（Created）、已回测（Backtested）、合规已通过（ComplianceApproved）、"
    "上线模拟（Live）、已暂停（Paused）、已终止（Terminated）。每一状态之间的转换均需满足前置条件："
    "从\"研发中\"到\"已回测\"需要代码哈希、数据哈希、配置哈希均已完成链上注册；"
    "从\"已回测\"到\"合规已通过\"需要所有合规检查条目均被合规节点标记为通过；"
    "从\"合规已通过\"到\"上线模拟\"需要监管节点签发上线授权。"
)

add_body(
    "这套流程控制机制确保了策略状态的每一次变更均有充分的链上记录作为前置条件支撑，"
    "杜绝了未经审计即上线的可能。智能合约本身作为在区块链上自动执行的代码，"
    "其逻辑对全网节点透明可见、执行过程不可干预，从技术上实现了\"法律即代码\"（Law is Code）"
    "的监管科技（RegTech）理念。"
)

# ============================================================
add_heading1("三、具体方案设计", bm_name="Sec3")

add_heading2("3.1 系统架构", bm_name="Sec3_1")

add_body_with_ref("本系统采用分层架构设计，自上而下依次为参与者节点层、联盟链共识层、智能合约层和数据存证层，"
                 "如{}所示。",
                 [("Fig1", "图1")])

add_figure("fig1_architecture.png",
           "图1  基于联盟链的量化策略可信审计系统架构",
           bookmark_name="Fig1")

add_body(
    "参与者节点层包含五类角色：策略研发团队负责策略代码的编写和回测执行，合规部门负责策略合规检查的审核签名，"
    "风控部门负责风控事件的监控和上报，外部审计机构负责独立审计验证，监管节点代表交易所或证监会接入系统。"
    "每类角色根据预设的权限策略拥有差异化的读写权限——例如，仅合规部门有权提交合规检查记录，但所有节点均可查询链上数据。"
)

add_body(
    "共识层采用PBFT或Raft共识算法，在有限节点网络中实现快速共识。PBFT在节点数不超过20时"
    "可提供秒级确认延迟，满足量化策略日频存证的性能需求。智能合约层是本系统的核心业务逻辑层，"
    "包含策略注册、回测验证、合规审计和异常记录四类合约功能，封装在StrategyAudit合约中统一对外提供服务。"
    "数据存证层实现了链下原始数据存储与链上哈希摘要存证的分离——链下使用文件系统或对象存储保存完整数据，"
    "链上仅保存SHA-256哈希值和元数据，兼顾完整性与隐私性。"
)

add_heading2("3.2 策略全生命周期审计流程")

add_body_with_ref("策略从研发到终止的完整生命周期状态迁移如{}所示，每一阶段均伴随相应的链上存证操作。",
                 [("Fig2", "图2")])

add_figure("fig2_lifecycle.png",
           "图2  策略全生命周期状态迁移",
           bookmark_name="Fig2")

add_body(
    "第一阶段为策略研发存证。每次策略代码修改触发Git hook，自动计算当前commit对应的代码树哈希"
    "并提交至智能合约。同时提交的还有使用数据的版本哈希和因子定义文件的Merkle根哈希。"
    "这一机制确保了策略代码、数据和因子定义的版本关系被永久记录——审计人员可在事后精确重建"
    "任意时间点的策略研发环境。智能合约确保策略版本一旦上链即视为时间戳锁定，开发者无法回溯性地修改历史版本。"
)

add_body(
    "第二阶段为回测过程可信存证。回测配置（包含调仓频率、交易成本假设、滑点、手续费等参数的YAML文件）"
    "首先上链存证。回测引擎参数（随机种子、训练/验证集切分比例、模型超参数）一并上链。回测完成后的关键指标"
    "（累计收益、年化收益、夏普比率、最大回撤、IC序列、换手率）计算哈希后提交至BacktestSubmitted事件。"
    "事后审计时，审计节点从链下获取相同的配置文件和参数，重新执行回测，"
    "将重新计算的指标哈希与链上记录的指标哈希进行比对——哈希一致则证明回测结果未经篡改。"
    "该机制特别关注三种典型数据操控行为：未来函数防御（通过数据切分时间戳验证）、"
    "幸存者偏差防御（通过退市公司数据完整性验证）、过拟合防御（通过样本外测试结果独立存证）。"
)

add_body("回测关键指标的计算公式如下：")

add_formula_explanation(
    "SR = (R̄ₚ − R̄_f) / σₚ",
    "其中 SR 为夏普比率（Sharpe Ratio），R̄ₚ 为策略年化收益率，R̄_f 为无风险利率（通常取3%），"
    "σₚ 为策略年化收益率标准差。夏普比率反映了单位风险所获得的风险溢价。"
)

add_formula_explanation(
    "MDD = max_{0≤i<j≤T} (Pᵢ − Pⱼ) / Pᵢ",
    "其中 MDD 为最大回撤（Max Drawdown），Pᵢ 为第 i 个交易日的净值，T 为回测总天数。"
    "最大回撤衡量了策略在历史回测中从峰值到谷底的最大损失幅度。"
)

add_formula_explanation(
    "IC = Corr(r̄ᵢ^{pred}, r̄ᵢ^{real}) = Cov(r̄ᵢ^{pred}, r̄ᵢ^{real}) / (σ^{pred} · σ^{real})",
    "其中 IC（Information Coefficient）为第 i 期因子预测收益与真实收益的秩相关系数，"
    "衡量因子对收益的预测能力。IC > 0 表示因子预测方向与真实方向正相关。"
)

add_body(
    "第三阶段为合规报备与上线审批。策略上线实盘前，智能合约逐一检查六项必选合规条件是否全部满足："
    "策略类型报备（《程序化交易管理实施细则》报告制度要求）、数据来源说明、回测参数锁定、"
    "风控阈值配置（异常交易管理要求）、交易系统测试（信息系统管理要求）、"
    "高频交易额外申报（如适用）。合约内置预设必选合规清单（mandatory checklist），"
    "通过complianceBitmap位图追踪每项条目的提交状态。每项检查通过后由合规节点签名确认，所有合规文件哈希上链。"
    "仅当六项条件全部提交且全部通过时，合约自动将策略状态更新为\"合规已通过\"，实盘交易系统方可接收该策略的交易信号。"
)

add_body(
    "第四阶段为实盘交易监控与事后审计。每个交易信号（选股名单、权重分配）的生成时间、参数和执行结果上链存证。"
    "风控规则触发记录（净值回撤超限、个股持仓超限、行业集中度超限等）由风控节点自动上链，不可事后删除。"
    "人工干预记录（暂停策略、修改参数、手动下单）由操作人员签名后单独存证。"
    "事后审计时，外部审计机构通过链上记录的交易信号索引，调取链下完整交易流水，"
    "验证实盘执行是否与回测声明的策略规则一致。"
)

add_heading2("3.3 智能合约核心设计")

add_body_with_ref("本文基于Solidity语言开发了StrategyAudit智能合约，在单合约中封装了角色权限管理、策略注册、"
                 "回测验证、合规检查和风控记录五类核心功能。合约定义了一个六元素枚举Role{None, Admin, Researcher, "
                 "ComplianceOfficer, RiskController, Auditor, Regulator}实现基于角色的访问控制（RBAC），"
                 "各角色拥有差异化的函数调用权限，交互流程如{}所示。",
                 [("Fig3", "图3")])

add_figure("fig3_contract_interaction.png",
           "图3  智能合约交互流程",
           bookmark_name="Fig3")

add_body(
    "角色权限的设计遵循最小权限原则。Researcher（策略研发方）有权调用registerStrategy()和submitBacktest()，"
    "但无权修改合规检查记录或验证回测结果。ComplianceOfficer（合规审核方）是唯一有权调用"
    "addComplianceCheck()的角色。Auditor（外部审计方）调用verifyBacktest()对回测结果进行独立验证。"
    "RiskController（风控方）调用recordRiskEvent()记录风控事件。Regulator（监管方）拥有只读查询权限。"
    "Admin（管理员）拥有最高权限，包括角色分配和所有函数的调用权限。"
    "合约通过onlyRole和onlyExisting两个修饰器实现权限检查：onlyRole确保调用者持有指定角色（或为Admin），"
    "onlyExisting确保操作针对已注册的策略。"
)

add_body(
    "策略注册函数registerStrategy()接收四个SHA-256哈希值作为参数：策略代码哈希codeHash、"
    "训练数据哈希dataHash、回测配置哈希configHash和因子库版本哈希factorLibHash。"
    "合约使用mapping(bytes32 => Strategy)结构存储所有策略信息，每个策略以codeHash为唯一标识。"
    "策略注册后自动进入\"研发中\"（Created）状态，并触发StrategyRegistered事件供前端订阅。"
)

add_body(
    "回测存证函数submitBacktest()接收策略标识codeHash、回测结果哈希resultHash和"
    "关键指标哈希metricsHash，将回测记录追加到策略对应的动态数组中。"
    "验证函数verifyBacktest()的核验逻辑可形式化为："
)

add_formula_explanation(
    "verify(codeHash, index, claimedHash) → { True if claimedHash = backtestRecords[codeHash][index].resultHash; False otherwise }",
    "审计节点从策略研发方获取原始回测数据和配置，重新执行回测后计算得claimedHash，"
    "提交至合约。合约将其与链上存证的resultHash进行比对，返回布尔值表示哈希是否一致。"
)

add_body(
    "合规检查函数的实现引入了预设必选合规清单（mandatory checklist）机制。合约内置六项必选检查条目："
    "（1）策略类型报备，（2）数据来源说明，（3）回测参数锁定，（4）风控阈值配置，"
    "（5）交易系统测试，（6）高频交易额外申报。合约通过complianceBitmap映射追踪每项必选条目的"
    "提交状态——低6位记录是否已提交，高6位记录是否被标记为不通过。"
    "在addComplianceCheck()中，合约首先判断提交的检查条目是否属于必选清单——若是，则通过位运算"
    "设置complianceBitmap中对应的位；若不是，则作为非必选的补充检查项存储。"
    "每次检查提交后，合约调用_allMandatoryPassed()判断是否所有6项必选条目均已提交且全部通过，"
    "若是则自动将策略状态更新为ComplianceApproved。函数recordRiskEvent()由RiskController角色调用，"
    "记录的事件一旦写入即不可修改或删除。"
)

add_body("合规状态自动转换的逻辑可表示为：")

add_formula_explanation(
    "Status → ComplianceApproved  iff  (∀i ∈ [0,NUM_MANDATORY), submitted[i] = True) ∧ (failed = 0)",
    "其中 NUM_MANDATORY = 6 为必选合规条目总数，submitted[i]表示第i项必选条目已被提交，"
    "failed表示全体必选条目中是否存在被标记为不通过的条目。当且仅当所有6项必选条目均已提交且无一被标记为不通过时，"
    "合约自动将策略状态置为ComplianceApproved（状态值2），无需人工干预。"
)

add_heading2("3.4 与现有系统的衔接——以QMT项目为例")

add_body_with_ref("为验证上述方案的可行性，本文以用户已有的QMT量化投资研究项目（qmt_investment_assistant）为案例，"
                 "实现了从现有量化研发系统到区块链存证系统的数据对接。该项目的核心组件与区块链接入方式对照如{}所示。",
                 [("Tab1", "表1")])

p = doc.add_paragraph()
run = p.add_run("表1  QMT项目组件与区块链接入方式对照")
set_font(run, '黑体', 'Times New Roman', 10.5, bold=True)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_bookmark_to_paragraph(p, "Tab1")

table = doc.add_table(rows=7, cols=2)
table.style = 'Table Grid'
# Convert to 三线表: only top, header-bottom, and bottom borders
tbl_pr = table._tbl.find(qn('w:tblPr'))
if tbl_pr is None:
    tbl_pr = OxmlElement('w:tblPr')
    table._tbl.insert(0, tbl_pr)
borders = OxmlElement('w:tblBorders')
for edge, sz, color, space in [
    ('top', 12, '000000', 0),
    ('bottom', 8, '000000', 0),
]:
    el = OxmlElement(f'w:{edge}')
    el.set(qn('w:val'), 'single')
    el.set(qn('w:sz'), str(sz))
    el.set(qn('w:color'), color)
    el.set(qn('w:space'), str(space))
    borders.append(el)
# Inside borders: none
for edge in ['left', 'right', 'insideH', 'insideV']:
    el = OxmlElement(f'w:{edge}')
    el.set(qn('w:val'), 'none')
    el.set(qn('w:color'), '000000')
    el.set(qn('w:space'), '0')
    borders.append(el)
tbl_pr.append(borders)
# Header row bottom border (三线表: 粗线分隔表头)
for cell in table.rows[0].cells:
    tc_pr = cell._tc.find(qn('w:tcPr'))
    if tc_pr is None:
        tc_pr = OxmlElement('w:tcPr')
        cell._tc.insert(0, tc_pr)
    tc_borders = OxmlElement('w:tcBorders')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:color'), '000000')
    bottom.set(qn('w:space'), '0')
    tc_borders.append(bottom)
    tc_pr.append(tc_borders)
headers = ["QMT项目组件", "区块链接入方式"]
data = [
    ["research_contract_v1.yaml\n(回测配置YAML)", "解析为configHash上链"],
    ["factor_catalog.py\n(144个Alpha因子定义)", "每个因子定义独立哈希，构建因子Merkle树"],
    ["configs/experiments/\n(163组实验配置)", "实验配置哈希与MLflow实验ID绑定上链"],
    ["artifacts/pipeline/xxxx.json\n(回测结果报告)", "核心指标（累计收益、夏普比、最大回撤等）计算metricsHash上链"],
    ["strategy_gate.py\n(IC>0.02, IC IR>0.15等)", "Gates检查结果作为合规检查项上链"],
    ["MLflow实验追踪\n(139次实验)", "实验配置哈希与结果哈希成对上链"],
]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    for p in cell.paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            set_font(run, '黑体', 'Times New Roman', 10.5, bold=True)

for row_idx, (col1, col2) in enumerate(data):
    for col_idx, val in enumerate([col1, col2]):
        cell = table.cell(row_idx + 1, col_idx)
        cell.text = val
        for p in cell.paragraphs:
            for run in p.runs:
                set_font(run, '宋体', 'Times New Roman', 10.5)

# Demo section
add_heading2("3.5 原型演示与结果分析")

add_body(
    "基于上述设计，本文在Hardhat开发环境中部署了StrategyAudit合约的Solidity实现，"
    "并编写了Python交互脚本（基于web3.py库，支持命令行参数配置）实现了从QMT项目到区块链的完整数据上链流程。"
    "演示环境配置为：Hardhat本地节点（模拟联盟链环境）、Solidity 0.8.20编译器、"
    "web3.py 7.16.0。部署后的合约地址为0x5FbDB2315678afecb367f032d93F642f64180aa3。"
)

add_body(
    "演示过程使用以下真实QMT项目数据作为存证输入：factor_catalog.py文件计算的SHA-256哈希"
    "作为factorLibHash（哈希值：0x1a3970...a2ecb8）；hs300_73_factors_ic_test_v1.yaml"
    "配置文件哈希作为configHash（0x8583fa...5c907）；最新的研究管线回测报告（包含LightGBM模型的"
    "累计收益70.03%、年化收益16.83%、夏普比率1.0928、最大回撤-11.99%、IC均值3.64%等关键指标）"
    "计算数据哈希和指标哈希。合约部署后依次执行了策略注册（Researcher角色）、回测提交（Researcher）、"
    "回测哈希验证（Auditor）、六项必选合规检查（ComplianceOfficer，全部通过）、风控事件记录"
    "（RiskController）等操作。六项必选合规检查全部提交通过后，合约自动将策略状态"
    "更新为ComplianceApproved，验证了预设合规清单机制的可行性。演示脚本的私钥和QMT路径均通过"
    "命令行参数或.env文件配置，不硬编码于代码中。"
)

add_body_with_ref("最终的链上数据查询结果如{}所示。",
                 [("Fig4", "图4")])

add_figure("fig4_demo_results.png",
           "图4  原型演示结果——链上存证统计与LightGBM回测指标",
           bookmark_name="Fig4")

add_body(
    "演示结果验证了以下关键能力：（1）真实量化项目数据的哈希存证——QMT项目的因子目录、"
    "策略配置和回测结果均成功计算SHA-256哈希并写入合约，实现了链上存证的完整性；"
    "（2）哈希值一致性验证——从链上读取的metricsHash与本地重新计算的JSON序列化哈希值完全一致"
    "（均为0x426fa2ecc0f4b4e2bd00247bc23046fd3460847269b3773e27d6bfb73510ae19），"
    "验证了\"链下数据→链上哈希→重新验证\"的完整审计回路；（3）合规检查的自动化流程控制——"
    "六项必选合规检查全部通过后，合约自动将策略状态更新为ComplianceApproved（状态值2），"
    "无需人工干预；（4）基于角色的访问控制——各核心函数均通过onlyRole修饰器进行了权限校验，"
    "仅持有对应角色的地址可调用相应函数。"
)

# ============================================================
add_heading1("四、需进一步解决的问题", bm_name="Sec4")
# ============================================================

add_heading2("4.0 当前方案的边界：哈希存证vs过程可信")

add_body(
    "需要着重指出的是，当前方案主要实现了文件级别的哈希存证与合规状态自动化管理，"
    "尚未做到完整意义上的\"过程可信回测\"。具体而言，以下关键信任环节仍未覆盖："
)

add_body(
    "第一，回测环境的可复现性问题。当前方案记录的是回测结果文件（JSON报告）的哈希值，"
    "但未记录回测执行环境的完整快照——包括操作系统版本、Python依赖包版本（pandas、numpy、scikit-learn等）、"
    "编译器参数和硬件配置等信息。缺乏环境复现能力的哈希存证只能证明\"某个文件在某个时间点存在\"，"
    "无法证明\"该文件中的指标是通过声明中的配置和数据计算得出的\"。完整的解决方案需引入容器化技术"
    "（如Docker）记录回测环境的镜像哈希，并与策略参数哈希绑定上链。"
)

add_body(
    "第二，未来函数与数据泄露问题。哈希存证只能保证数据内容的完整性，但无法检测数据本身是否包含未来信息"
    "（如使用未来时刻的财务数据进行因子计算）。这一问题的解决需要结合时间戳验证和数据切分审计——"
    "即审计节点重新执行回测时，验证训练数据的时间窗口是否严格早于测试数据的时间窗口。"
    "当前方案未实现这一逻辑，需要在审计节点软件中增加数据时间戳的交叉验证功能。"
)

add_body(
    "第三，因子计算正确性验证。当前方案记录了因子定义文件（factor_catalog.py）的哈希值，"
    "但未对因子计算过程的中间结果进行存证。审计人员在重跑因子计算时，可能因数据源差异、"
    "浮点数精度或代码版本不匹配等原因得到不一致的结果。更完善的方案需对因子计算的输入数据版本、"
    "计算中间变量和输出结果分别进行哈希存证，形成因子计算的完整审计链。"
)

add_body(
    "第四，交易成本假设的合理性。回测报告中的交易成本（滑点、手续费、冲击成本等）是影响回测结果"
    "的关键参数。当前方案虽然将回测配置YAML文件的哈希上链，但未对配置中交易成本参数的合理性"
    "进行独立验证。实践中，审计节点需要根据目标市场的实际交易成本水平，对回测中声明的成本假设"
    "进行合理性评估——例如，A股市场的单边交易成本约为万分之二至万分之三，"
    "若回测假设为万分之一，则可能低估了实际交易成本。"
)

add_body(
    "上述四个方面的改进方向说明，从\"哈希存证\"到\"过程可信\"是一个渐进的技术演进路径。"
    "当前方案构建了这一路径的基础设施层——链上存证框架与自动化合规流程，"
    "后续可在审计节点软件中逐步增加环境复现检查、数据时间窗口验证、因子中间结果存证"
    "和交易成本合理性校验等功能。本文第4.2节至4.4节讨论其他维度的挑战。"
)

add_heading2("4.1 性能与成本挑战")

add_body(
    "尽管采用链下存储+链上哈希的混合方案大幅降低了链上存储需求，但在高频交易场景下，"
    "秒级甚至毫秒级的交易信号存证仍将对联盟链的吞吐能力构成严峻考验。"
    "一个可能的解决路径是引入Layer-2扩容方案，在链下进行批量计算和存证压缩后，"
    "仅将最终的Merkle根提交至主链。此外，链上存储费用（Gas成本）虽然在联盟链场景下不涉及"
    "加密货币支付，但节点服务器的计算和存储资源仍需纳入成本考量。"
)

add_heading2("4.2 隐私与法律效力")

add_body(
    "策略代码哈希上链虽然不直接暴露策略内容，但频繁的哈希匹配行为仍可能通过关联分析泄露策略活性信息。"
    "零知识证明（Zero-Knowledge Proof）技术可以在不披露具体数据的前提下证明某个声明（如\"策略A的夏普比率大于1.0\"），"
    "为策略审计的隐私保护提供了理论可行的技术路径。从法律效力维度看，根据《最高人民法院关于互联网法院审理案件若干问题的规定》"
    "第11条（2018），区块链存证在满足\"真实、完整、不可篡改\"条件下可被司法采信。"
    "但不同司法管辖区的具体认定标准存在差异，需在跨机构场景下进一步明确法律适用规则。"
)

add_heading2("4.3 标准化与互操作性")

add_body(
    "不同量化投资机构的策略分类体系、回测指标计算口径存在差异。例如，夏普比率的年化方式"
    "（252个交易日 vs 250个交易日）、最大回撤的计算窗口（滚动回撤 vs 全局回撤）等"
    "关键指标的定义尚未形成行业统一标准。智能合约的接口标准化是实现跨机构审计的前提条件，"
    "建议参考中国量化投资学会或证券业协会的相关标准制定工作，推动形成行业共识。"
)

add_heading2("4.4 节点参与激励与治理")

add_body(
    "联盟链的节点参与动力是系统长期运行的关键。在机构内部场景下，参与节点属于同一机构的不同部门，"
    "运行节点的动力来源于制度约束，不涉及代币激励。但在跨机构场景（如FOF基金管理人对子基金的策略审计、"
    "托管银行对管理人的投资合规监督）中，需要设计合理的激励机制确保各参与方长期稳定地运行节点和参与验证。"
    "可参考Hyperledger Fabric的成员服务提供者（MSP）机制，结合机构间的服务协议实现治理。"
)

# ============================================================
add_heading1("五、参考文献")
# ============================================================

refs = [
    "[1] Nakamoto S. Bitcoin: A Peer-to-Peer Electronic Cash System[R]. 2008.",
    "[2] Bailey D H, Borwein J M, López de Prado M, et al. Pseudo-mathematics and financial charlatanism: The effects of backtest overfitting on out-of-sample performance[J]. Notices of the AMS, 2014, 61(5): 458-471.",
    "[3] Harvey C R, Liu Y. A census of the factor zoo[R]. SSRN Working Paper, 2019.",
    "[4] López de Prado M. Advances in Financial Machine Learning[M]. Hoboken: John Wiley & Sons, 2018.",
    "[5] 上海证券交易所. 上海证券交易所程序化交易管理实施细则[S]. 2025.",
    "[6] 深圳证券交易所. 深圳证券交易所程序化交易管理实施细则[S]. 2025.",
    "[7] 中国证监会. 期货市场程序化交易管理规定[S]. 2025.",
    "[8] Fama E F, French K R. Common risk factors in the returns on stocks and bonds[J]. Journal of Financial Economics, 1993, 33(1): 3-56.",
    "[9] Carhart M M. On persistence in mutual fund performance[J]. The Journal of Finance, 1997, 52(1): 57-82.",
    "[10] Androulaki E, Barger A, Bortnikov V, et al. Hyperledger Fabric: A distributed operating system for permissioned blockchains[C]. Proceedings of the Thirteenth EuroSys Conference, 2018: 1-15.",
    "[11] Buterin V. Ethereum: A next-generation smart contract and decentralized application platform[R]. 2014.",
    "[12] Castro M, Liskov B. Practical Byzantine fault tolerance[C]. OSDI, 1999, 99(1999): 173-186.",
    "[13] Szabo N. Smart contracts: Building blocks for digital markets[J]. Extropy, 1996, 16(18): 28.",
    "[14] Novy-Marx R. The other side of value: The gross profitability premium[J]. Journal of Financial Economics, 2013, 108(1): 1-28.",
]

for ref in refs:
    add_ref(ref)

doc.save(os.path.join(OUT_DIR, "论文正文.docx"))
print(f"Saved to {OUT_DIR}/论文正文.docx")
