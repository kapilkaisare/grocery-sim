"""Test"""
import sys

CUSTOMER_STATES = {"SHOPPING":1, "IN_LINE":2, "SERVICING":3, "CHECKED_OUT":4}

class Observer(object):
    """Observer"""

    def next(self):
        """next"""
        pass

class Subject(object):
    """Subject"""
    observable = {}
    observers = []

    def subscribe(self, observer):
        """Subscribe an observer."""
        self.observers.append(observer)

    def next(self):
        """Apprise observers of change in data."""
        for observer in self.observers:
            observer.next(self.observable)

class Customer(Subject):
    """A base class, from which we specialize our types."""

    def __init__(self, customer_id, arrival_time, item_count):
        self.customer_id = customer_id
        self.entry_time = arrival_time
        self.number_of_items = item_count
        self.status = CUSTOMER_STATES["SHOPPING"]

    def select_register(self, registers):
        """An empty method, to be implemented by it's children."""
        pass

    def process_items(self, reducer_constant):
        "Process items"
        self.number_of_items = self.number_of_items - 1/float(reducer_constant)



class CustomerA(Customer):
    """Type A Customer"""
    type = "A"

    def select_register(self, registers):
        """Customer Type A always chooses the register with the shortest line
        (least number of customers in line). If two or more registers have the
        shortest line, Customer Type A will choose the register with the lowest
        register number (e.g. register #1 would be chosen over register #3)."""
        self.status = CUSTOMER_STATES["IN_LINE"]
        sorted_registers = sorted(list(registers), key=lambda register: len(register.customers))
        sorted_registers[0].add_customer(self)

class CustomerB(Customer):
    """Type B Customer"""
    type = "B"

    def select_register(self, registers):
        """Customer Type B looks at the last customer in each line, and always
        chooses to be behind the customer with the fewest number of items left
        to check out, regardless of how many other customers are in the line or
        how many items they have. Customer Type B will always choose an empty
        line before a line with any customers in it."""
        self.status = CUSTOMER_STATES["IN_LINE"]
        empty_registers = [register for register in registers if len(register.customers) == 0]
        if empty_registers:
            empty_registers[0].add_customer(self)
        else:
            sorted_registers = sorted( \
                list(registers), \
                key=lambda register: \
                register.customers[len(register.customers) - 1].number_of_items)
            sorted_registers[0].add_customer(self)


class Register(Subject):
    """Register"""
    def __init__(self, num):
        self.number = num
        self.customers = []
        self.time_to_process_item = 1

    def add_customer(self, customer):
        """Add a customer to the queue."""
        print "    Customer #" + str(customer.customer_id) + " (type " + str(customer.type) + ") arrives with " + str(customer.number_of_items)+ "  items and goes to register #" + str(self.number)
        self.customers.append(customer)

    def is_serving_customers(self):
        """Is serving customers"""
        return len(self.customers) > 0

    def tick(self):
        """Tick"""
        if self.customers:
            customer = self.customers[0]
            if customer.number_of_items == 0:
                customer.status = CUSTOMER_STATES["CHECKED_OUT"]
                old_customer = self.customers[0]
                self.customers = self.customers[1:]
                print "    Customer #" + str(old_customer.customer_id) + " (type " + str(old_customer.type) + ") leaves."
            if self.customers:
                customer = self.customers[0]
                customer.status = CUSTOMER_STATES["SERVICING"]
                customer.process_items(self.time_to_process_item)
                print "    Register #" + str(self.number) + " is currently serving Customer #" + str(customer.customer_id) + " (" + str(customer.number_of_items) + ")"


class TrainingRegister(Register):
    """Training registers take twice as much time to process items as normal
    registers."""
    def __init__(self, num):
        Register.__init__(self, num)
        self.time_to_process_item = 2

class Grocery(Subject):
    """Grocery"""
    registers = []

    def add_register(self, register):
        """Adds a register to the grocery."""
        self.registers.append(register)

    def is_serving_customers(self):
        """Is serving customers"""
        return reduce(lambda x, y: x or y, \
            [register.is_serving_customers() for register in self.registers])

    def tick(self):
        """Tick"""
        for register in self.registers:
            register.tick()


class Simulator(Observer):
    """Simulator"""
    customers = []
    grocery = Grocery()
    current_tick = 0

    def __init__(self):
        self.grocery.subscribe(self)

    def set_up_grocery(self, register_count):
        """Set up the grocery by adding registers."""
        self.create_registers(register_count)

    def create_registers(self, register_count):
        """Create registers."""
        for i in range(register_count):
            if i < register_count - 1:
                register = Register(i + 1)
                register.subscribe(self)
                self.grocery.add_register(register)
        register = TrainingRegister(register_count)
        register.subscribe(self)
        self.grocery.add_register(register)

    def create_customer(self, customer_type, num, arrival_time, item_count):
        """Create customer."""
        if customer_type == 'A':
            self.customers.append(CustomerA(num, arrival_time, item_count))
        else:
            self.customers.append(CustomerB(num, arrival_time, item_count))

    def log(self):
        """Log"""
        log_message = "";
        if self.current_tick == 0:
            log_message = "Simulation starts with " + \
                str(len(self.grocery.registers)) + \
                " register(s)."
        print "* t=" + str(self.current_tick) + " : " + log_message

    def tick(self):
        """Tick"""
        self.current_tick = self.current_tick + 1
        self.log()
        ready_customers = [customer for customer in self.customers if customer.entry_time == self.current_tick]
        ready_customers = sorted(list(ready_customers), key= lambda customer: customer.number_of_items)
        for customer in ready_customers:
            customer.select_register(self.grocery.registers)
        self.grocery.tick()
        if (self.grocery.is_serving_customers()):
            self.tick()




if __name__ == '__main__':
    SIMULATOR = Simulator()

    with open(sys.argv[1]) as input_file:
        LINES = input_file.readlines()

    NUMBER_OF_REGISTERS = int(LINES[0])
    SIMULATOR.set_up_grocery(NUMBER_OF_REGISTERS)

    for index in range(1, len(LINES)):
        line_elements = LINES[index].split(" ")
        SIMULATOR.create_customer( \
            line_elements[0], \
            index, \
            int(line_elements[1]), \
            long(line_elements[2]) \
        )

    SIMULATOR.log()
    SIMULATOR.tick()

    print "Finished at t=" + str(SIMULATOR.current_tick) + " minutes"