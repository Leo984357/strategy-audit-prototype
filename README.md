# StrategyAudit — On-Chain Audit for Quantitative Trading Strategies

A Hardhat-based Solidity prototype that demonstrates **blockchain-anchored compliance auditing** for the full lifecycle of quantitative trading strategy development, backtesting, and deployment. Built as a response to China's 2025 SSE/SZSE programmatic trading regulations.

## Motivation

Quantitative strategy development faces a fundamental trust problem:
- **p-hacking / data snooping**: backtest parameters can be tuned post-hoc without trace
- **data versioning chaos**: same strategy run against different data versions yields irreproducible results
- **compliance records are mutable**: internal audit logs can be altered or deleted without detection

This project uses a **permissioned blockchain** approach — on-chain SHA-256 hashes + off-chain raw data — to create tamper-proof audit trails for the strategy lifecycle, without exposing proprietary strategy logic.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Participant Layer                                       │
│  Researcher | Compliance Officer | Risk Controller       │
│  Auditor | Regulator | Admin                            │
├─────────────────────────────────────────────────────────┤
│  Consensus Layer (PBFT / Raft — configurable)            │
├─────────────────────────────────────────────────────────┤
│  Smart Contract Layer (StrategyAudit.sol)                │
│  registerStrategy | submitBacktest | verifyBacktest     │
│  addComplianceCheck | recordRiskEvent | updateStatus    │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                              │
│  Off-chain: raw files (CSV, YAML, JSON, Python)          │
│  On-chain: SHA-256 hashes + metadata                    │
└─────────────────────────────────────────────────────────┘
```

## Smart Contract: StrategyAudit.sol

### Role-Based Access Control
| Role | Permissions |
|---|---|
| Admin | All functions, role assignment |
| Researcher | `registerStrategy`, `submitBacktest` |
| ComplianceOfficer | `addComplianceCheck` |
| RiskController | `recordRiskEvent` |
| Auditor | `verifyBacktest` |
| Regulator | Read-only queries |

### Mandatory Compliance Checklist (6 items)
1. 策略类型报备 (Strategy type registration)
2. 数据来源说明 (Data source declaration)
3. 回测参数锁定 (Backtest parameter lock)
4. 风控阈值配置 (Risk control threshold config)
5. 交易系统测试 (Trading system test)
6. 高频交易额外申报 (High-frequency trading declaration)

All 6 items must be submitted AND passed before the contract auto-transitions the strategy to `ComplianceApproved` status.

### Strategy Lifecycle States
```
Created → Backtested → ComplianceApproved → Live → Paused → Terminated
```

## Tech Stack

- **Solidity** 0.8.20 (smart contract)
- **Hardhat** v2.28 (development & testing)
- **web3.py** 7.16 (Python SDK)
- **Node.js** v22 (Hardhat runtime)

## Quick Start

```bash
# Install dependencies
npm install

# Start local Hardhat node
npx hardhat node

# In another terminal: deploy contract
npx hardhat run scripts/deploy.js --network localhost

# Run the demo with real data
python3 scripts/audit_demo.py \
  --qmt-root /path/to/quant/research/project \
  --contract 0x5FbDB2315678afecb367f032d93F642f64180aa3 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

```bash
# Run tests (30 test cases)
npx hardhat test
```

## Demo Results

Using real quant research data (144 Alpha factors, LightGBM model, 163 experiment configs):

| Metric | Value |
|---|---|
| Total Return | 70.03% |
| Annual Return | 16.83% |
| Sharpe Ratio | 1.0928 |
| Max Drawdown | -11.99% |
| IC (mean) | 3.64% |

All data successfully hashed on-chain, compliance auto-approved after 6 checks, hash verification confirmed.

## Paper

This prototype accompanies a Chinese-language academic paper:
- **Title**: 基于联盟链的量化策略可信回测与程序化交易合规审计机制研究
- **Content**: Full system design, RBAC model, mandatory compliance checklist, real-data case study, and discussion of limitations (environment reproducibility, look-ahead bias, factor computation verification, transaction cost assumptions)

## Limitations

This prototype achieves **hash anchoring + compliance workflow automation**. It does NOT yet achieve full "process trust" — specifically:
1. Backtest environment reproducibility (Docker image hashing)
2. Look-ahead bias detection (data time-window cross-validation)
3. Factor computation intermediate result verification
4. Transaction cost reasonableness validation

These are documented as future work in the paper.

## License

MIT
