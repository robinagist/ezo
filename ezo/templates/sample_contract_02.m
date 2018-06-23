pragma solidity ^0.4.21;

// Timestamp Oracle
// Generated by ezo
//
// use at your own risk
//

contract TimestampRequestOracle {

    address public owner;
    uint public _timestamp;

    event TimeRequest(address sender);
    event RequestFilled(address sender,uint timestamp);


    function constructor() public {
        _timestamp = 0;
        owner = msg.sender;
    }

    function sendTimestampRequest() public {
        emit TimeRequest(msg.sender);
    }

    function setTimestamp(uint timestamp) public {
        _timestamp = timestamp;
        emit RequestFilled(msg.sender, _timestamp);
    }

    function getTimestamp() public returns (uint) {
        return _timestamp;
    }

}
