
contract Contract {
    // money
    uint256 money_to_pay;
    uint256 money_paid;
    // addresses
    address customer_address;
    address payable courier_address;
    address payable owner_address;
    // status
    enum Status {
        CREATED,
        PENDING,
        COMPLETED
    }
    Status order_status;

    constructor (address customer, uint256 price) {
        owner_address = payable(msg.sender);
        customer_address = customer;

        money_to_pay = price;
        money_paid = 0;

        order_status = Status.CREATED;
    }

    modifier customer_only {
        require(msg.sender == customer_address, 'Invalid customer account.');
        _;
    }

    modifier owner_only {
        require(msg.sender == owner_address, 'Owner only.');
        _;
    }

    function add_money() external payable customer_only {
        require(order_status == Status.CREATED, 'Invalid status');
        require(money_to_pay > money_paid, 'Already paid.');
        money_paid += msg.value;
    }

    function add_courier(address payable courier) external owner_only {
        require(order_status == Status.CREATED, 'Delivery already pending or complete.');
        require(money_to_pay <= money_paid, 'Transfer not complete.');
        courier_address = courier;
        order_status = Status.PENDING;

    }

    function confirm_delivery() external owner_only {
        require(order_status == Status.PENDING, 'Delivery not complete.');
        owner_address.transfer((money_to_pay*4)/5);
        courier_address.transfer(money_paid - (money_to_pay*4)/5);
        order_status = Status.COMPLETED;
    }

    function get_owner_address() external view returns (address){
        return owner_address;
    }

    function get_to_pay() external view returns (uint256){
        return money_to_pay;
    }

    function get_paid() external view returns (uint256) {
        return money_paid;
    }

    function get_customer_address() external view returns (address){
        return customer_address;
    }

    function get_courier_address() external view returns (address){
        return courier_address;
    }


}