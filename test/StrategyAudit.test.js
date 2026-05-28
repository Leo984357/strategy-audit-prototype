const { expect } = require("chai");
const { ethers } = require("hardhat");

const Role = { None: 0, Admin: 1, Researcher: 2, ComplianceOfficer: 3, RiskController: 4, Auditor: 5, Regulator: 6 };
const Status = { Created: 0, Backtested: 1, ComplianceApproved: 2, Live: 3, Paused: 4, Terminated: 5 };

async function deployFixture() {
  const [admin, researcher, compliance, riskCtrl, auditor, regulator, other] =
    await ethers.getSigners();

  const Factory = await ethers.getContractFactory("StrategyAudit");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  await contract.connect(admin).assignRole(researcher.address, Role.Researcher);
  await contract.connect(admin).assignRole(compliance.address, Role.ComplianceOfficer);
  await contract.connect(admin).assignRole(riskCtrl.address, Role.RiskController);
  await contract.connect(admin).assignRole(auditor.address, Role.Auditor);
  await contract.connect(admin).assignRole(regulator.address, Role.Regulator);

  const H = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
  const codeHash = H("strategy-v1");
  const dataHash = H("data-v1");
  const configHash = H("config-v1");
  const factorHash = H("factors-v1");
  const resultHash = H("result-v1");
  const metricsHash = H("metrics-v1");
  const wrongHash = H("wrong");

  return { contract, admin, researcher, compliance, riskCtrl, auditor, regulator, other, codeHash, dataHash, configHash, factorHash, resultHash, metricsHash, wrongHash };
}

async function registerFixture() {
  const ctx = await deployFixture();
  await ctx.contract.connect(ctx.researcher).registerStrategy(ctx.codeHash, ctx.dataHash, ctx.configHash, ctx.factorHash);
  return ctx;
}

describe("StrategyAudit", function () {

  describe("Deployment & Roles", function () {
    it("should set admin to deployer", async function () {
      const { contract, admin } = await deployFixture();
      expect(await contract.admin()).to.equal(admin.address);
    });

    it("should assign roles correctly", async function () {
      const { contract, researcher, compliance, auditor } = await deployFixture();
      expect(await contract.userRoles(researcher.address)).to.equal(Role.Researcher);
      expect(await contract.userRoles(compliance.address)).to.equal(Role.ComplianceOfficer);
      expect(await contract.userRoles(auditor.address)).to.equal(Role.Auditor);
    });

    it("should reject non-admin assignRole", async function () {
      const { contract, other } = await deployFixture();
      await expect(contract.connect(other).assignRole(other.address, Role.Researcher))
        .to.be.revertedWith("Not admin");
    });

    it("should reject invalid role assignment", async function () {
      const { contract, admin, other } = await deployFixture();
      await expect(contract.connect(admin).assignRole(other.address, Role.None))
        .to.be.revertedWith("Invalid role");
      await expect(contract.connect(admin).assignRole(other.address, Role.Admin))
        .to.be.revertedWith("Invalid role");
    });

    it("should revoke role", async function () {
      const { contract, admin, researcher } = await deployFixture();
      await contract.connect(admin).revokeRole(researcher.address);
      expect(await contract.userRoles(researcher.address)).to.equal(Role.None);
    });

    it("should not revoke admin", async function () {
      const { contract, admin } = await deployFixture();
      await expect(contract.connect(admin).revokeRole(admin.address))
        .to.be.revertedWith("Cannot revoke admin");
    });
  });

  describe("Strategy Registration", function () {
    it("should register as Researcher", async function () {
      const { contract, researcher, codeHash, dataHash, configHash, factorHash } = await deployFixture();
      await contract.connect(researcher).registerStrategy(codeHash, dataHash, configHash, factorHash);
      const s = await contract.getStrategy(codeHash);
      expect(s.exists).to.be.true;
      expect(s.owner).to.equal(researcher.address);
      expect(s.status).to.equal(Status.Created);
    });

    it("should allow admin to register", async function () {
      const { contract, admin, codeHash, dataHash, configHash, factorHash } = await deployFixture();
      await contract.connect(admin).registerStrategy(codeHash, dataHash, configHash, factorHash);
      const s = await contract.getStrategy(codeHash);
      expect(s.exists).to.be.true;
    });

    it("should reject duplicate registration", async function () {
      const { contract, researcher, codeHash, dataHash, configHash, factorHash } = await deployFixture();
      await contract.connect(researcher).registerStrategy(codeHash, dataHash, configHash, factorHash);
      await expect(
        contract.connect(researcher).registerStrategy(codeHash, dataHash, configHash, factorHash)
      ).to.be.revertedWith("Duplicate");
    });

    it("should reject non-Researcher registration", async function () {
      const { contract, compliance, codeHash, dataHash, configHash, factorHash } = await deployFixture();
      await expect(
        contract.connect(compliance).registerStrategy(codeHash, dataHash, configHash, factorHash)
      ).to.be.revertedWith("Unauthorized");
    });

    it("should reject unregistered strategy query", async function () {
      const { contract, codeHash } = await deployFixture();
      await expect(contract.getStrategy(codeHash)).to.be.revertedWith("Not found");
    });
  });

  describe("Backtest Submission", function () {
    it("should submit as Researcher", async function () {
      const { contract, researcher, codeHash, resultHash, metricsHash } = await registerFixture();
      await contract.connect(researcher).submitBacktest(codeHash, resultHash, metricsHash);
      expect(await contract.getBacktestCount(codeHash)).to.equal(1n);
    });

    it("should allow multiple submissions", async function () {
      const { contract, researcher, codeHash, resultHash, metricsHash } = await registerFixture();
      await contract.connect(researcher).submitBacktest(codeHash, resultHash, metricsHash);
      await contract.connect(researcher).submitBacktest(codeHash, resultHash, metricsHash);
      expect(await contract.getBacktestCount(codeHash)).to.equal(2n);
    });

    it("should reject non-Researcher submission", async function () {
      const { contract, compliance, codeHash, resultHash, metricsHash } = await registerFixture();
      await expect(
        contract.connect(compliance).submitBacktest(codeHash, resultHash, metricsHash)
      ).to.be.revertedWith("Unauthorized");
    });

    it("should reject submission for unregistered strategy", async function () {
      const { contract, researcher, wrongHash, resultHash, metricsHash } = await registerFixture();
      await expect(
        contract.connect(researcher).submitBacktest(wrongHash, resultHash, metricsHash)
      ).to.be.revertedWith("Not registered");
    });
  });

  describe("Backtest Verification", function () {
    it("should verify matching hash as Auditor", async function () {
      const { contract, researcher, auditor, codeHash, resultHash, metricsHash } = await registerFixture();
      await contract.connect(researcher).submitBacktest(codeHash, resultHash, metricsHash);
      await expect(
        contract.connect(auditor).verifyBacktest(codeHash, 0, resultHash)
      ).to.emit(contract, "BacktestVerified").withArgs(codeHash, resultHash, true);
    });

    it("should detect hash mismatch", async function () {
      const { contract, researcher, auditor, codeHash, resultHash, metricsHash, wrongHash } = await registerFixture();
      await contract.connect(researcher).submitBacktest(codeHash, resultHash, metricsHash);
      await expect(
        contract.connect(auditor).verifyBacktest(codeHash, 0, wrongHash)
      ).to.emit(contract, "BacktestVerified").withArgs(codeHash, wrongHash, false);
    });

    it("should reject non-Auditor verification", async function () {
      const { contract, researcher, compliance, codeHash, resultHash, metricsHash } = await registerFixture();
      await contract.connect(researcher).submitBacktest(codeHash, resultHash, metricsHash);
      await expect(
        contract.connect(compliance).verifyBacktest(codeHash, 0, resultHash)
      ).to.be.revertedWith("Unauthorized");
    });

    it("should reject out-of-bounds index", async function () {
      const { contract, researcher, auditor, codeHash, resultHash, metricsHash } = await registerFixture();
      await expect(
        contract.connect(auditor).verifyBacktest(codeHash, 99, resultHash)
      ).to.be.revertedWith("Bad index");
    });
  });

  describe("Compliance", function () {
    it("should not approve before all 6 mandatory items pass", async function () {
      const { contract, researcher, compliance, codeHash, resultHash, metricsHash } = await registerFixture();
      await contract.connect(researcher).submitBacktest(codeHash, resultHash, metricsHash);
      await contract.connect(compliance).addComplianceCheck(codeHash, "策略类型报备", true);
      const s = await contract.getStrategy(codeHash);
      expect(s.status).to.equal(Status.Created);
    });

    it("should auto-approve when all 6 mandatory items pass", async function () {
      const { contract, compliance, codeHash } = await registerFixture();
      const items = [
        "策略类型报备", "数据来源说明", "回测参数锁定",
        "风控阈值配置", "交易系统测试", "高频交易额外申报"
      ];
      for (const item of items) {
        await contract.connect(compliance).addComplianceCheck(codeHash, item, true);
      }
      const s = await contract.getStrategy(codeHash);
      expect(s.status).to.equal(Status.ComplianceApproved);
      expect(await contract.allCompliancePassed(codeHash)).to.be.true;
    });

    it("should NOT approve if any mandatory item fails", async function () {
      const { contract, compliance, codeHash } = await registerFixture();
      const items = ["策略类型报备", "数据来源说明", "回测参数锁定", "风控阈值配置", "交易系统测试"];
      for (const item of items) {
        await contract.connect(compliance).addComplianceCheck(codeHash, item, true);
      }
      await contract.connect(compliance).addComplianceCheck(codeHash, "高频交易额外申报", false);
      const s = await contract.getStrategy(codeHash);
      expect(s.status).to.equal(Status.Created);
      expect(await contract.allCompliancePassed(codeHash)).to.be.false;
    });

    it("should reject duplicate mandatory item", async function () {
      const { contract, compliance, codeHash } = await registerFixture();
      await contract.connect(compliance).addComplianceCheck(codeHash, "策略类型报备", true);
      await expect(
        contract.connect(compliance).addComplianceCheck(codeHash, "策略类型报备", true)
      ).to.be.revertedWith("Duplicate mandatory item");
    });

    it("should reject non-ComplianceOfficer check", async function () {
      const { contract, researcher, codeHash } = await registerFixture();
      await expect(
        contract.connect(researcher).addComplianceCheck(codeHash, "策略类型报备", true)
      ).to.be.revertedWith("Unauthorized");
    });

    it("should allow non-mandatory items freely", async function () {
      const { contract, compliance, codeHash } = await registerFixture();
      await contract.connect(compliance).addComplianceCheck(codeHash, "自定义检查项", true);
      const c = await contract.getComplianceCount(codeHash);
      expect(c).to.equal(1n);
    });
  });

  describe("Risk Events", function () {
    it("should record event as RiskController", async function () {
      const { contract, riskCtrl, codeHash } = await registerFixture();
      const details = ethers.keccak256(ethers.toUtf8Bytes("max drawdown exceeded"));
      await expect(
        contract.connect(riskCtrl).recordRiskEvent(codeHash, "最大回撤超限", details)
      ).to.emit(contract, "RiskEventRecorded").withArgs(codeHash, "最大回撤超限");
    });

    it("should reject non-RiskController event", async function () {
      const { contract, researcher, codeHash } = await registerFixture();
      await expect(
        contract.connect(researcher).recordRiskEvent(codeHash, "test", ethers.ZeroHash)
      ).to.be.revertedWith("Unauthorized");
    });
  });

  describe("Status Transitions", function () {
    it("should allow owner to update status", async function () {
      const { contract, researcher, codeHash } = await registerFixture();
      await contract.connect(researcher).updateStatus(codeHash, Status.Live);
      const s = await contract.getStrategy(codeHash);
      expect(s.status).to.equal(Status.Live);
    });

    it("should allow admin to update status", async function () {
      const { contract, admin, codeHash } = await registerFixture();
      await contract.connect(admin).updateStatus(codeHash, Status.Terminated);
      const s = await contract.getStrategy(codeHash);
      expect(s.status).to.equal(Status.Terminated);
    });

    it("should reject unauthorized status update", async function () {
      const { contract, compliance, codeHash } = await registerFixture();
      await expect(
        contract.connect(compliance).updateStatus(codeHash, Status.Live)
      ).to.be.revertedWith("Unauthorized");
    });
  });
});
