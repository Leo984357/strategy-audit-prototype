import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUT = "/Users/leolee/Desktop/课程/大三下课程/区块链/课程论文/figures"
os.makedirs(OUT, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Heiti TC", "Songti SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def fig1_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    layers = [
        (0.5, 6.5, 9, 1.2, "#E8F0FE", "参与者节点\n策略团队 | 合规部门 | 风控部门 | 外部审计 | 监管机构"),
        (0.5, 5.0, 9, 1.2, "#E6F4EA", "联盟链共识层\nPBFT / Raft 共识算法"),
        (0.5, 3.2, 9, 1.5, "#FFF3E0", "智能合约层\n策略注册合约 | 回测验证合约 | 合规审计合约 | 异常记录合约"),
        (0.5, 1.0, 9, 1.8, "#F3E5F5", "数据存证层\n链下存储: 策略代码/行情数据/因子矩阵/回测报告\n链上存证: SHA-256哈希值 / Merkle树 / 时间戳"),
    ]
    colors = ["#4A90D9", "#34A853", "#FBBC04", "#9C27B0"]
    for (x, y, w, h, bg, label), c in zip(layers, colors):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                             facecolor=bg, edgecolor=c, linewidth=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=9, linespacing=1.5)

    for y_start, y_end in [(6.3, 6.2), (4.8, 4.7), (3.0, 3.1)]:
        ax.annotate("", xy=(5, y_end), xytext=(5, y_start),
                    arrowprops=dict(arrowstyle="->", color="#666", lw=1.5))

    ax.text(0.5, 7.8, "图1  基于联盟链的量化策略可信审计系统架构", fontsize=11, ha="left")
    fig.savefig(f"{OUT}/fig1_architecture.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("fig1 done")


def fig2_lifecycle():
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis("off")

    states = [
        (0.5, 2.0, "策略研发\n(研发中)", "#E8F0FE", 1),
        (3.0, 2.0, "回测验证\n(已回测)", "#E6F4EA", 2),
        (5.5, 2.0, "合规报备\n(合规已通过)", "#FFF3E0", 3),
        (8.0, 2.0, "模拟交易\n(模拟中)", "#F3E5F5", 4),
        (10.5, 2.0, "实盘上线\n(已批准)", "#FFE0B2", 5),
        (13.0, 2.0, "终止\n(已终止)", "#FFCDD2", 6),
    ]

    for x, y, label, color, _ in states:
        box = FancyBboxPatch((x, y), 1.2, 0.8, boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor="#333", linewidth=1.5)
        ax.add_patch(box)
        ax.text(x + 0.6, y + 0.4, label, ha="center", va="center", fontsize=8, linespacing=1.4)

    ax.text(0.5, 4.5, "图2  策略全生命周期状态迁移", fontsize=11, ha="left")

    for i in range(len(states) - 1):
        x1 = states[i][0] + 1.2
        y1 = states[i][1] + 0.4
        x2 = states[i + 1][0]
        y2 = states[i + 1][1] + 0.4
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#333", lw=1.5))

    checks = [
        ("代码/数据哈希上链", 1.8, 3.3),
        ("回测参数验证\n指标哈希比对", 4.3, 3.3),
        ("程序化交易报备\n合规节点签名", 6.8, 3.3),
        ("风控规则检查\n模拟交易记录", 9.3, 3.3),
        ("上线授权签发\n实盘监控启动", 11.8, 3.3),
    ]
    for label, x, y in checks:
        ax.annotate("", xy=(x + 0.6, 2.8), xytext=(x + 0.6, y + 0.3),
                    arrowprops=dict(arrowstyle="->", color="#666", lw=1, ls="dashed"))
        ax.text(x, y, label, ha="center", va="bottom", fontsize=7, color="#555")

    fig.savefig(f"{OUT}/fig2_lifecycle.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("fig2 done")


def fig3_contract_interaction():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    roles = {
        "策略团队": (1, 5, "#4A90D9"),
        "合规部门": (1, 3.5, "#34A853"),
        "风控部门": (1, 2, "#FBBC04"),
        "外部审计": (1, 0.5, "#9C27B0"),
    }
    contract = (5.5, 2, 4, 3.5)
    contract_box = FancyBboxPatch((contract[0], contract[1]),
                                   contract[2], contract[3],
                                   boxstyle="round,pad=0.1",
                                   facecolor="#FFF8E1", edgecolor="#F57C00", lw=2)
    ax.add_patch(contract_box)
    ax.text(contract[0] + contract[2]/2, contract[1] + contract[3]/2,
            "StrategyAudit 智能合约\n\n"
            "registerStrategy()\n"
            "submitBacktest()\n"
            "verifyBacktest()\n"
            "addComplianceCheck()\n"
            "recordRiskEvent()\n"
            "updateStatus()\n"
            "getStrategy()",
            ha="center", va="center", fontsize=8, linespacing=1.6)

    interactions = {
        "策略团队": [(5, 5, 5, 3.7), (3.7, 3.7, 5, 3.7)],
        "合规部门": [(5, 3.5, 5, 3.2), (3.7, 3.2, 5, 3.2)],
        "风控部门": [(5, 2, 5, 2.5), (3.7, 2.5, 5, 2.5)],
        "外部审计": [(5, 0.5, 5, 2.2), (3.7, 2.2, 5, 2.2)],
    }

    for role, (x, y, color) in roles.items():
        circle = plt.Circle((x, y), 0.3, facecolor=color, edgecolor="#333", lw=2)
        ax.add_patch(circle)
        ax.text(x, y - 0.5, role, ha="center", va="top", fontsize=9, fontweight="bold")

    labels = [
        (3.2, 3.9, "注册策略/提交回测"),
        (3.2, 3.4, "合规检查签名"),
        (3.2, 2.7, "风控事件上报"),
        (3.2, 2.3, "验证回测结果"),
    ]
    for lx, ly, label in labels:
        ax.text(lx, ly, label, ha="right", va="center", fontsize=7, color="#333")

    ax.text(0.5, 5.8, "图3  智能合约交互流程", fontsize=11, ha="left")
    fig.savefig(f"{OUT}/fig3_contract_interaction.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("fig3 done")


def fig4_demo_results():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    strategies = ["策略注册", "回测存证", "合规检查", "风控事件"]
    counts = [1, 1, 4, 1]
    colors = ["#4A90D9", "#34A853", "#FBBC04", "#FF7043"]

    axes[0].bar(strategies, counts, color=colors, edgecolor="#333", lw=0.8)
    axes[0].set_ylabel("交易数量", fontsize=10)
    axes[0].set_title("链上存证统计", fontsize=11, fontweight="bold")
    axes[0].tick_params(labelsize=9)
    for i, v in enumerate(counts):
        axes[0].text(i, v + 0.05, str(v), ha="center", va="bottom", fontsize=10)

    metrics = {
        "累计收益": 70.03,
        "年化收益": 16.83,
        "夏普比": 1.09,
        "最大回撤": -11.99,
        "IC": 3.64,
    }
    names = list(metrics.keys())
    vals = list(metrics.values())
    bars = axes[1].bar(names, vals, color=["#34A853", "#4A90D9", "#FBBC04", "#FF7043", "#9C27B0"],
                       edgecolor="#333", lw=0.8)
    axes[1].set_ylabel("数值", fontsize=10)
    axes[1].set_title("LightGBM 回测关键指标", fontsize=11, fontweight="bold")
    axes[1].tick_params(labelsize=8)

    for bar, v in zip(bars, vals):
        y_pos = bar.get_height() if v >= 0 else bar.get_height() - 2
        axes[1].text(bar.get_x() + bar.get_width()/2, y_pos,
                     f'{v:.2f}{"%" if abs(v) < 1 else ""}',
                     ha="center", va="bottom" if v >= 0 else "top", fontsize=8)

    fig.suptitle("图4  原型演示结果", fontsize=12, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig4_demo_results.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("fig4 done")


fig1_architecture()
fig2_lifecycle()
fig3_contract_interaction()
fig4_demo_results()
print(f"\nAll figures saved to {OUT}")
