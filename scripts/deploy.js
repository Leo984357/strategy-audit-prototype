const hre = require("hardhat");

async function main() {
  const StrategyAudit = await hre.ethers.getContractFactory("StrategyAudit");
  const contract = await StrategyAudit.deploy();
  await contract.waitForDeployment();
  const addr = await contract.getAddress();
  console.log("StrategyAudit deployed to:", addr);
}

main().catch(console.error);
