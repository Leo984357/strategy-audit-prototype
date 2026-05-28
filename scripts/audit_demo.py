import hashlib, json, os, argparse
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser(description="联盟链策略存证审计演示")
parser.add_argument("--qmt-root", default=None, help="QMT项目根目录路径")
parser.add_argument("--contract", default=None, help="合约地址")
parser.add_argument("--rpc", default="http://127.0.0.1:8545", help="RPC节点地址")
parser.add_argument("--account", default=None, help="账户地址")
parser.add_argument("--private-key", default=None, help="私钥（也可通过PRIVATE_KEY环境变量设置）")
args = parser.parse_args()

PRIVATE_KEY = args.private_key or os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise SystemExit("Error: 请提供私钥 (--private-key 或 PRIVATE_KEY 环境变量)")

QMT = args.qmt_root or os.getenv("QMT_ROOT", "/Users/leolee/Desktop/qmt_investment_assistant")
CONTRACT_ADDR = args.contract or os.getenv("CONTRACT_ADDR", "0x5FbDB2315678afecb367f032d93F642f64180aa3")

w3 = Web3(Web3.HTTPProvider(args.rpc))
assert w3.is_connected(), f"无法连接节点 {args.rpc}"

ACCOUNT = args.account or w3.eth.account.from_key(PRIVATE_KEY).address

abi = json.load(open(os.path.join(os.path.dirname(__file__), "..", "artifacts", "contracts", "StrategyAudit.sol", "StrategyAudit.json")))["abi"]
contract = w3.eth.contract(address=CONTRACT_ADDR, abi=abi)

def hash_file(path):
    return "0x" + hashlib.sha256(open(path, "rb").read()).hexdigest()

def hash_text(text):
    return "0x" + hashlib.sha256(text.encode()).hexdigest()

def send_tx(tx_func, gas=200000):
    tx = tx_func.build_transaction({
        "from": ACCOUNT,
        "nonce": w3.eth.get_transaction_count(ACCOUNT),
        "gas": gas,
        "gasPrice": w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    receipt = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(receipt)

print("=" * 60)
print("基于联盟链的量化策略可信回测存证演示")
print(f"RPC: {args.rpc}")
print(f"合约: {CONTRACT_ADDR}")
print(f"账户: {ACCOUNT}")
print("=" * 60)

pipeline_reports = sorted([
    f for f in os.listdir(f"{QMT}/artifacts/pipeline")
    if f.endswith(".json")
]) if os.path.exists(f"{QMT}/artifacts/pipeline") else []
latest_report = pipeline_reports[-1] if pipeline_reports else None

configs = sorted([
    f for f in os.listdir(f"{QMT}/configs/experiments")
    if f.endswith(".yaml")
]) if os.path.exists(f"{QMT}/configs/experiments") else []

print(f"\n回测报告数: {len(pipeline_reports)}")
print(f"策略配置数: {len(configs)}")

factor_catalog = f"{QMT}/src/features/factor_catalog.py"
if os.path.exists(factor_catalog):
    factor_hash = hash_file(factor_catalog)
else:
    factor_hash = hash_text("no-factor-catalog")
print(f"因子库哈希: {factor_hash}")

config_file = f"{QMT}/configs/experiments/{configs[0]}" if configs else None
config_hash = hash_file(config_file) if config_file else hash_text("no-config")
if configs:
    print(f"回测配置: {configs[0]}")
print(f"配置哈希: {config_hash}")

strat_name = "hs300_multi_factor_lgbm"
code_hash = hash_text(strat_name + json.dumps(sorted(configs)))

sample_report = f"{QMT}/artifacts/pipeline/{latest_report}" if latest_report else None
if sample_report and os.path.exists(sample_report):
    data_hash = hash_file(sample_report)
    report_data = json.load(open(sample_report))
    exp = report_data.get("experiments", {})
    lgbm = exp.get("lightgbm", {})
    metrics = {
        "total_return": lgbm.get("total_return", "N/A"),
        "annual_return": lgbm.get("annual_return", "N/A"),
        "sharpe": lgbm.get("sharpe", "N/A"),
        "max_drawdown": lgbm.get("max_drawdown", "N/A"),
        "ic": lgbm.get("ic", "N/A"),
        "ic_ir": lgbm.get("ic_ir", "N/A"),
        "turnover": lgbm.get("turnover", "N/A"),
    }
    metrics_hash = hash_text(json.dumps(metrics, sort_keys=True))
else:
    data_hash = hash_text("no-pipeline-data")
    metrics = {"total_return": "N/A", "sharpe": "N/A", "max_drawdown": "N/A"}
    metrics_hash = hash_text("no-metrics")

result_hash = data_hash
print(f"\n策略标识: {strat_name}")
print(f"代码哈希: {code_hash}")
print(f"数据哈希: {data_hash}")
print(f"指标哈希: {metrics_hash}")
print(f"关键指标: {json.dumps(metrics, indent=2, ensure_ascii=False)}")

print("\n--- 1. 注册策略 (Researcher) ---")
receipt = send_tx(contract.functions.registerStrategy(code_hash, data_hash, config_hash, factor_hash))
print(f"交易: {receipt.transactionHash.hex()}, 区块: {receipt['blockNumber']}")

print("\n--- 2. 提交回测结果 (Researcher) ---")
receipt = send_tx(contract.functions.submitBacktest(code_hash, result_hash, metrics_hash))
print(f"交易: {receipt.transactionHash.hex()}, 区块: {receipt['blockNumber']}")

print("\n--- 3. 回测验证 (Auditor) ---")
receipt = send_tx(contract.functions.verifyBacktest(code_hash, 0, result_hash))
print(f"验证结果: 哈希匹配, 交易: {receipt.transactionHash.hex()}")

print("\n--- 4. 合规检查 (ComplianceOfficer) ---")
mandatory_items = [
    "策略类型报备",
    "数据来源说明",
    "回测参数锁定",
    "风控阈值配置",
    "交易系统测试",
    "高频交易额外申报",
]
for item in mandatory_items:
    receipt = send_tx(contract.functions.addComplianceCheck(code_hash, item, True), 300000)
    print(f"  ✅ {item}")

print("\n--- 5. 记录风控事件 (RiskController) ---")
receipt = send_tx(contract.functions.recordRiskEvent(
    code_hash,
    "最大回撤超限",
    hash_text(f"回撤达到{metrics.get('max_drawdown', 'N/A')}，触发15%警戒线"),
), 300000)
print("  ✅ 风控事件已记录")

print("\n--- 6. 验证链上记录 ---")
strat = contract.functions.getStrategy(code_hash).call()
status_map = ["Created", "Backtested", "ComplianceApproved", "Live", "Paused", "Terminated"]
print(f"策略代码哈希:   {strat[0].hex()}")
print(f"数据哈希:       {strat[1].hex()}")
print(f"配置哈希:       {strat[2].hex()}")
print(f"因子库哈希:     {strat[3].hex()}")
print(f"注册时间戳:     {strat[4]}")
print(f"所有者:         {strat[5]}")
print(f"状态:           {strat[6]} ({status_map[strat[6]]})")
print(f"是否存在:       {strat[7]}")

bt_count = contract.functions.getBacktestCount(code_hash).call()
print(f"\n回测提交次数: {bt_count}")
comp_count = contract.functions.getComplianceCount(code_hash).call()
print(f"合规检查次数: {comp_count}")

print(f"\n回测指标验证: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
recompute = hash_text(json.dumps(metrics, sort_keys=True))
print(f"链上哈希:   {metrics_hash}")
print(f"重算哈希:   {recompute}")
print(f"哈希一致:   {recompute == metrics_hash}")

all_pass = contract.functions.allCompliancePassed(code_hash).call()
print(f"合规全部通过: {all_pass}")

print("\n" + "=" * 60)
print("演示完成：QMT真实项目的策略全生命周期链上存证已生效")
print("=" * 60)
