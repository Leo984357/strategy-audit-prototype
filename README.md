# StrategyAudit — 基于联盟链的量化策略合规审计原型系统

一个基于 Hardhat 的 Solidity 原型，演示量化策略全生命周期的**区块链锚定合规审计**。
以 2025 年上交所/深交所程序化交易新规为监管背景，以真实 QMT 量化项目为案例。

## 动机

量化策略研发存在三个核心信任问题：

- **p-hacking / data snooping**：回测参数可在事后调整而不留痕迹
- **数据版本混乱**：同一策略在不同数据版本上运行，结果不可复现
- **合规记录可篡改**：内部审计日志可以被事后修改或删除

本方案采用**联盟链 + 链下原始数据 + 链上 SHA-256 哈希**的混合存证范式，在不暴露策略逻辑的前提下，为策略生命周期创建防篡改审计轨迹。

## 架构

```
┌──────────────────────────────────────────────────────────┐
│  参与者节点层                                              │
│  Researcher | ComplianceOfficer | RiskController          │
│  Auditor | Regulator | Admin                             │
├──────────────────────────────────────────────────────────┤
│  共识层 (PBFT / Raft — 可配置)                             │
├──────────────────────────────────────────────────────────┤
│  智能合约层 (StrategyAudit.sol)                            │
│  registerStrategy | submitBacktest | verifyBacktest       │
│  addComplianceCheck | recordRiskEvent | updateStatus      │
├──────────────────────────────────────────────────────────┤
│  数据层                                                   │
│  链下: 原始文件 (CSV, YAML, JSON, Python)                 │
│  链上: SHA-256 哈希值 + 元数据                             │
└──────────────────────────────────────────────────────────┘
```

## 智能合约 (StrategyAudit.sol)

### 基于角色的访问控制 (RBAC)
| 角色 | 权限 |
|---|---|
| Admin（管理员） | 所有函数 + 角色分配 |
| Researcher（策略研发方） | `registerStrategy`、`submitBacktest` |
| ComplianceOfficer（合规审核方） | `addComplianceCheck` |
| RiskController（风控方） | `recordRiskEvent` |
| Auditor（外部审计方） | `verifyBacktest` |
| Regulator（监管方） | 只读查询 |

### 预设必选合规清单（6 项）
1. 策略类型报备
2. 数据来源说明
3. 回测参数锁定
4. 风控阈值配置
5. 交易系统测试
6. 高频交易额外申报

六项全部提交且全部通过后，合约自动将策略状态更新为 `ComplianceApproved`。

### 策略生命周期状态
```
Created → Backtested → ComplianceApproved → Live → Paused → Terminated
```

## 技术栈

- **Solidity** 0.8.20（智能合约）
- **Hardhat** v2.28（开发与测试框架）
- **web3.py** 7.16（Python SDK）
- **Node.js** v22（Hardhat 运行时）

## 快速开始

```bash
# 安装依赖
npm install

# 启动本地 Hardhat 节点
npx hardhat node

# 另开终端：部署合约
npx hardhat run scripts/deploy.js --network localhost

# 运行 Demo（使用 QMT 真实数据）
python3 scripts/audit_demo.py \
  --qmt-root /path/to/quant/research/project \
  --contract 0x5FbDB2315678afecb367f032d93F642f64180aa3 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

```bash
# 运行测试（30 个测试用例）
npx hardhat test
```

## Demo 结果

使用真实 QMT 项目数据（144 个 Alpha 因子、LightGBM 模型、163 组实验配置）：

| 指标 | 值 |
|---|---|
| 累计收益 | 70.03% |
| 年化收益 | 16.83% |
| 夏普比率 | 1.0928 |
| 最大回撤 | -11.99% |
| IC 均值 | 3.64% |

所有数据成功上链存证，6 项合规检查全部通过后自动批准，哈希一致性验证通过。

## 配套论文

本原型系统配套中文学术论文：
- **标题**: 基于联盟链的量化策略可信回测与程序化交易合规审计机制研究
- **内容**: 系统架构设计、RBAC 权限模型、必选合规清单机制、真实数据案例、局限性讨论（环境复现、未来函数、因子验证、交易成本假设）

## 当前限制

本原型实现了**哈希存证 + 合规流程自动化**，但尚未达到完整的"过程可信"：

1. 回测环境可复现性（Docker 镜像哈希）
2. 未来函数检测（数据时间窗口交叉验证）
3. 因子计算中间结果验证
4. 交易成本假设合理性校验

以上内容在论文第四节中有详细讨论。

## License

MIT
