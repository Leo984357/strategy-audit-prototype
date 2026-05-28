// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract StrategyAudit {
    // ==================== Roles ====================
    enum Role { None, Admin, Researcher, ComplianceOfficer, RiskController, Auditor, Regulator }

    address public admin;
    mapping(address => Role) public userRoles;

    event RoleAssigned(address indexed user, Role role);

    modifier onlyRole(Role role) {
        require(msg.sender == admin || userRoles[msg.sender] == role, "Unauthorized");
        _;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    // ========== Mandatory Compliance Checklist ==========
    uint256 public constant NUM_MANDATORY = 6;
    string[6] public mandatoryItems = [
        unicode"策略类型报备",
        unicode"数据来源说明",
        unicode"回测参数锁定",
        unicode"风控阈值配置",
        unicode"交易系统测试",
        unicode"高频交易额外申报"
    ];

    // ==================== Strategy ====================
    enum StrategyStatus { Created, Backtested, ComplianceApproved, Live, Paused, Terminated }

    struct Strategy {
        bytes32 codeHash;
        bytes32 dataHash;
        bytes32 configHash;
        bytes32 factorLibHash;
        uint256 registerTime;
        address owner;
        StrategyStatus status;
        bool exists;
    }

    struct BacktestRecord {
        bytes32 resultHash;
        bytes32 metricsHash;
        uint256 timestamp;
        bool verified;
    }

    struct ComplianceCheck {
        string item;
        bool passed;
        uint256 timestamp;
        address checker;
    }

    struct RiskEvent {
        string eventType;
        bytes32 detailsHash;
        uint256 timestamp;
        address reporter;
    }

    // ==================== State ====================
    mapping(bytes32 => Strategy) public strategies;
    mapping(bytes32 => BacktestRecord[]) public backtestRecords;
    mapping(bytes32 => ComplianceCheck[]) public complianceChecks;
    mapping(bytes32 => RiskEvent[]) public riskEvents;
    mapping(bytes32 => uint256) public backtestCount;
    mapping(bytes32 => uint256) public complianceCount;

    // bits 0-5: mandatory item i has been submitted
    // bits 16-21: mandatory item i has failed (failed = submitted + NOT passed)
    mapping(bytes32 => uint256) public complianceBitmap;

    // ==================== Events ====================
    event StrategyRegistered(bytes32 indexed codeHash, address indexed owner, uint256 time);
    event BacktestSubmitted(bytes32 indexed codeHash, bytes32 resultHash, uint256 time);
    event BacktestVerified(bytes32 indexed codeHash, bytes32 resultHash, bool isMatch);
    event ComplianceChecked(bytes32 indexed codeHash, string item, bool passed);
    event StatusChanged(bytes32 indexed codeHash, StrategyStatus newStatus);
    event RiskEventRecorded(bytes32 indexed codeHash, string eventType);

    modifier onlyExisting(bytes32 codeHash) {
        require(strategies[codeHash].exists, "Not registered");
        _;
    }

    // ==================== Constructor ====================
    constructor() {
        admin = msg.sender;
        userRoles[msg.sender] = Role.Admin;
    }

    // ================ Role Management ================
    function assignRole(address user, Role role) external onlyAdmin {
        require(role != Role.None && role != Role.Admin, "Invalid role");
        userRoles[user] = role;
        emit RoleAssigned(user, role);
    }

    function revokeRole(address user) external onlyAdmin {
        require(user != admin, "Cannot revoke admin");
        userRoles[user] = Role.None;
        emit RoleAssigned(user, Role.None);
    }

    function hasRole(address user, Role role) external view returns (bool) {
        return user == admin || userRoles[user] == role;
    }

    // ================ Strategy Registration ================
    function registerStrategy(
        bytes32 codeHash,
        bytes32 dataHash,
        bytes32 configHash,
        bytes32 factorLibHash
    ) external onlyRole(Role.Researcher) returns (bool) {
        require(!strategies[codeHash].exists, "Duplicate");
        strategies[codeHash] = Strategy({
            codeHash: codeHash,
            dataHash: dataHash,
            configHash: configHash,
            factorLibHash: factorLibHash,
            registerTime: block.timestamp,
            owner: msg.sender,
            status: StrategyStatus.Created,
            exists: true
        });
        emit StrategyRegistered(codeHash, msg.sender, block.timestamp);
        return true;
    }

    // ================ Backtest Submission ================
    function submitBacktest(
        bytes32 codeHash,
        bytes32 resultHash,
        bytes32 metricsHash
    ) external onlyRole(Role.Researcher) onlyExisting(codeHash) returns (uint256) {
        backtestRecords[codeHash].push(BacktestRecord({
            resultHash: resultHash,
            metricsHash: metricsHash,
            timestamp: block.timestamp,
            verified: false
        }));
        backtestCount[codeHash]++;
        emit BacktestSubmitted(codeHash, resultHash, block.timestamp);
        return backtestCount[codeHash];
    }

    // ================ Backtest Verification ================
    function verifyBacktest(
        bytes32 codeHash,
        uint256 index,
        bytes32 claimedResultHash
    ) external onlyRole(Role.Auditor) onlyExisting(codeHash) returns (bool) {
        require(index < backtestRecords[codeHash].length, "Bad index");
        BacktestRecord storage r = backtestRecords[codeHash][index];
        bool ok = r.resultHash == claimedResultHash;
        r.verified = ok;
        emit BacktestVerified(codeHash, claimedResultHash, ok);
        return ok;
    }

    // ================ Compliance Check ================
    function addComplianceCheck(
        bytes32 codeHash,
        string calldata item,
        bool passed
    ) external onlyRole(Role.ComplianceOfficer) onlyExisting(codeHash) {
        _processMandatoryItem(codeHash, item, passed);

        complianceChecks[codeHash].push(ComplianceCheck({
            item: item,
            passed: passed,
            timestamp: block.timestamp,
            checker: msg.sender
        }));
        complianceCount[codeHash]++;
        emit ComplianceChecked(codeHash, item, passed);

        if (_allMandatoryPassed(codeHash)) {
            _setStatus(codeHash, StrategyStatus.ComplianceApproved);
        }
    }

    // ================ Risk Event ================
    function recordRiskEvent(
        bytes32 codeHash,
        string calldata eventType,
        bytes32 detailsHash
    ) external onlyRole(Role.RiskController) onlyExisting(codeHash) {
        riskEvents[codeHash].push(RiskEvent({
            eventType: eventType,
            detailsHash: detailsHash,
            timestamp: block.timestamp,
            reporter: msg.sender
        }));
        emit RiskEventRecorded(codeHash, eventType);
    }

    // ================ Status Update ================
    function updateStatus(bytes32 codeHash, StrategyStatus newStatus)
        external onlyExisting(codeHash)
    {
        require(msg.sender == strategies[codeHash].owner || msg.sender == admin, "Unauthorized");
        _setStatus(codeHash, newStatus);
    }

    // ================ Internal ================
    function _getMandatoryIndex(string memory item) internal view returns (int256) {
        bytes32 h = keccak256(bytes(item));
        for (uint256 i = 0; i < NUM_MANDATORY; i++) {
            if (keccak256(bytes(mandatoryItems[i])) == h) return int256(i);
        }
        return -1;
    }

    function _processMandatoryItem(bytes32 codeHash, string memory item, bool passed) internal {
        int256 idx = _getMandatoryIndex(item);
        if (idx < 0) return;
        uint256 bit = 1 << uint256(idx);
        require(complianceBitmap[codeHash] & bit == 0, "Duplicate mandatory item");
        complianceBitmap[codeHash] |= bit;
        if (!passed) {
            complianceBitmap[codeHash] |= (1 << (uint256(idx) + 16));
        }
    }

    function _allMandatoryPassed(bytes32 codeHash) internal view returns (bool) {
        uint256 b = complianceBitmap[codeHash];
        uint256 expected = (1 << NUM_MANDATORY) - 1; // lowest 6 bits
        // All 6 items submitted, none failed
        return (b & expected) == expected && (b >> 16) == 0;
    }

    function _setStatus(bytes32 codeHash, StrategyStatus newStatus) internal {
        strategies[codeHash].status = newStatus;
        emit StatusChanged(codeHash, newStatus);
    }

    // ================ Query ================
    function getStrategy(bytes32 codeHash) external view returns (Strategy memory) {
        require(strategies[codeHash].exists, "Not found");
        return strategies[codeHash];
    }

    function getBacktestCount(bytes32 codeHash) external view returns (uint256) {
        return backtestCount[codeHash];
    }

    function getComplianceCount(bytes32 codeHash) external view returns (uint256) {
        return complianceCount[codeHash];
    }

    function getMandatoryItem(uint256 index) external view returns (string memory) {
        require(index < NUM_MANDATORY, "Bad index");
        return mandatoryItems[index];
    }

    function allCompliancePassed(bytes32 codeHash) external view returns (bool) {
        return _allMandatoryPassed(codeHash);
    }
}
