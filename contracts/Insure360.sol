// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract Insure360 {

  string[] _schemes;
  string[] _schemeid;
  string[] _farmername;
  string[] _farmerid;
  string[] _bankaccount;
  string[] _premiumamount;
  string[] _date;
  uint[] _ids;
  uint[] _statuses;
  string[] _farmeremails;

  uint id;
  constructor(){
    id=0;
  }

  function applyScheme(string memory scheme,string memory schemeid,string memory farmername,string memory farmerid,string memory bankaccount,string memory premiumaccount,string memory date,string memory farmeremail) public {
    _schemes.push(scheme);
    _schemeid.push(schemeid);
    _farmername.push(farmername);
    _farmerid.push(farmerid);
    _bankaccount.push(bankaccount);
    _premiumamount.push(premiumaccount);
    _date.push(date);
    id+=1;
    _ids.push(id);
    _statuses.push(0);
    _farmeremails.push(farmeremail);
  }

  function viewSchemes() public view returns(string[] memory,string[] memory,string[] memory,string[] memory,string[] memory,string[] memory,string[] memory,uint[] memory,string[] memory,uint[] memory){
    return(_schemes,_schemeid,_farmername,_farmerid,_bankaccount,_premiumamount,_date,_ids,_farmeremails,_statuses);
  }

  function claimScheme(uint id1,uint status) public{
    uint i;

    for(i=0;i<_ids.length;i++){
      if(id1==_ids[i])
        _statuses[i]=status;
    }
  }

}
