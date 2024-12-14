// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Fundraiser {
    address public owner; // Owner of the contract
    uint256 public maxFundAmount; // Maximum amount to be raised (in Wei)
    uint256 public totalFunds; // Current total funds raised
    bool public checkReleased = false; // Current state of the contract
    string public nodeID;

    mapping(address => uint256) public contributions; // Track contributions per address

    error OverFunded(uint256 overBy);

    event FundReceived(address indexed contributor, uint256 amount);
    event FundsReleased(uint256 totalAmount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action.");
        _;
    }

    constructor(uint256 _maxFundAmount, string memory _nodeID) {
        require(_maxFundAmount > 0, "Max fund amount must be greater than zero.");
        owner = msg.sender;
        nodeID = _nodeID;
        maxFundAmount = _maxFundAmount;
    }

    // Function to contribute funds
    function contribute() public payable {
        require(msg.value > 0, "Contribution must be greater than zero.");

        if (totalFunds + msg.value > maxFundAmount) {
            uint256 overBy = totalFunds + msg.value - maxFundAmount;
            revert OverFunded(overBy);
        }
        require(totalFunds < maxFundAmount, "Funding goal already reached.");

        // Update contributions and total funds
        contributions[msg.sender] += msg.value;
        totalFunds += msg.value;

        emit FundReceived(msg.sender, msg.value);

        // Check if the funding goal is met
        if (totalFunds >= maxFundAmount) {
            releaseFunds();
        }
    }

    // Internal function to release funds to the owner's wallet
    function releaseFunds() internal {
        require(totalFunds >= maxFundAmount, "Funding goal not yet reached.");

        uint256 amountToTransfer = address(this).balance;
        (bool success, ) = owner.call{value: amountToTransfer}("");
        require(success, "Transfer failed.");

        emit FundsReleased(amountToTransfer);
    }

    // View function to check how much is left to reach the goal
    function remainingFunds() public view returns (uint256) {
        if (totalFunds >= maxFundAmount) {
            return 0;
        }
        return maxFundAmount - totalFunds;
    }
}
