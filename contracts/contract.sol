pragma solidity ^0.4.21;

// Weather Oracle contract for Medium.com article
// use at your own risk
//
//
//
contract WeatherOracle {

    address public owner;
    uint public temp;
    uint public timestamp;

    event TempRequest(address sender);
    event FilledRequest(uint rtemp);
    event Farty(uint tt);
    event Toob();

    function constructor() public {
        temp = 0;
        owner = msg.sender;
    }

    function request() public returns (string) {
        emit TempRequest(msg.sender);
        return "sent";
    }

    function fill(uint rtemp) public returns (uint){
        temp = rtemp;
        emit FilledRequest(rtemp);
        return temp;
    }

    function getTemp() public returns (uint) {
        emit Farty(1);
        emit Toob();
        return temp;
    }


}


