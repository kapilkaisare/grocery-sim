"""Coding Challenge:
You are to write a program to implement a grocery store / cashier line
simulation. This program should read input from a file, and print the resulting
score to the console. The program should be a console-only program. The program
should take a single command line parameter: the name of the input file.

Customers in a grocery store arrive at a set of registers to check out. Each
register is run by a cashier who serves customers on a first-come, first-served
basis. The goal of the problem is to determine when all customers are done
checking out.

One of the most important criteria for a successful solution is that it
correctly implements the problem to be solved. This will be determined by code
inspection, acceptance testing using the 5 examples demonstrated below, as well
as additional test cases not provided on this page.

We will also be considering your overall approach to the problem and your
programming style. This assignment is an opportunity to show off how you can
use your object-oriented analysis and design skills to produce an elegant,
readable, and maintainable solution. Please do NOT submit a multi-threaded or
real-time solution. Please DO use what you would consider best practice in
developing your solution.

## Deliverables (all of the following)

The following should be available in your resulting solution zip file:

1. Source Code
  * The source code should be in Python, using version 2.7 (or any minor
  revision thereafter)
  * Unit tests ([unittest](http://docs.python.org/2/library/unittest.html) or
  [nose](https://nose.readthedocs.org/en/latest/) preferred)
1. Any other supporting code or other binaries that you used to develop the
solution (even if it is not required to run the solution). If a resource is
easily accessible on the web you can just provide a link to it rather than
including the files.

## Problem Details

1. The number of registers is specified by the problem input file. Registers
are numbered 1, 2, 3, ..., n for n registers.
1. Time (`t`) is measured in minutes.
1. The grocery store always has a single cashier in training. This cashier is
always assigned to the highest numbered register.
1. Regular registers take one minute to process each customer's item. The
register staffed by the cashier in training takes two minutes for each item. So
a customer with `n` items at a regular register takes `n` minutes to check out.
However, if the customer ends up at the last register, it will take `2n`
minutes to check out.
1. The simulation starts at `t=0`. At that time all registers are empty (i.e.
no customers are in line).
1. Two types of customers arrive at the registers:
  * Customer Type A always chooses the register with the shortest line (least
  number of customers in line). If two or more registers have the shortest line,
   Customer Type A will choose the register with the lowest register number
   (e.g. register #1 would be chosen over register #3).
  * Customer Type B looks at the last customer in each line, and always chooses
  to be behind the customer with the fewest number of items left to check out,
  regardless of how many other customers are in the line or how many items they
  have. Customer Type B will always choose an empty line before a line with any
  customers in it.
1. Customers just finishing checking out do not count as being in line (for
either kind of customer).
1. If two or more customers arrive at the same time, those with fewer items
choose registers before those with more items. If the customers have the same
number of items, then type A customers choose before type B customers.

## Input Format

The first line of the input file is a single integer specifying the number of
registers.

Each additional line is a whitespace-separated list of values. Each list
specifies the customer type, customer arrival time (in minutes), and how many
items that customer has respectively.

"""

import sys

class CustomerType(object):
    """Customer Type"""
    pass

class TypeA(CustomerType):
    """Customer Type A"""

    def __init__(self):
        self.type = "A"
        self.order = 1

    def __str__(self):
        return self.type

    def select_register(self, registers):
        """Customer Type A always chooses the register with the shortest line
        (least number of customers in line). If two or more registers have the
        shortest line, Customer Type A will choose the register with the lowest
        register number (e.g. register #1 would be chosen over register #3).
        """
        return sorted(list(registers), \
            key=lambda register: (len(register.customers), register.number))[0]

class TypeB(CustomerType):
    """Customer Type B"""

    def __init__(self):
        self.type = "B"
        self.order = 2

    def __str__(self):
        return self.type

    def select_register(self, registers):
        """Customer Type B looks at the last customer in each line, and always
        chooses to be behind the customer with the fewest number of items left
        to check out, regardless of how many other customers are in the line or
        how many items they have. Customer Type B will always choose an empty
        line before a line with any customers in it.
        """
        empty_registers = [register for register in registers if len(register.customers) == 0]
        if empty_registers:
            return empty_registers[0]
        else:
            sorted_registers = sorted( \
                list(registers), \
                key=lambda register: \
                register.customers[len(register.customers) - 1].number_of_items)
            return sorted_registers[0]



class Customer(object):
    """Customer"""

    def __init__(self, number, customer_type, checkout_time, number_of_items):
        self.number = number
        self.type = customer_type
        self.checkout_time = checkout_time
        self.number_of_items = number_of_items
        self.processing_countdown = number_of_items

    def __str__(self):
        return "Customer #" + str(self.number) + \
        " (Type " + self.type + ") with " + str(self.number_of_items) + \
        " items."
    
    def process_items(self, time_to_process):
        """Process Items"""
        self.processing_countdown = self.processing_countdown - float(1/time_to_process)

class Register(object):
    """Registers are numbered 1, 2, 3, ..., n for n registers."""

    def __init__(self, number):
        self.number = number
        self.customers = []
        self.time_to_process = 1

    def __str__(self):
        return "Register #" + str(self.number)

    def tick(self, time):
        """Tick"""
        if self.customers and self.customers[0].processing_countdown == 0:
            self.customers = self.customers[1:]
        if self.customers:
            self.customers[0].process_items(float(self.time_to_process))

    def empty(self):
        """Empty"""
        return len(self.customers) == 0

    def add_customer(self, customer):
        """Add customer"""
        self.customers.append(customer)


class TrainingRegister(Register):
    """Training registers"""

    def __init__(self, number):
        Register.__init__(self, number)
        self.time_to_process = 2

    def __str__(self):
        return "TrainingRegister #" + str(self.number)

class CashierLine(object):
    """CashierLine"""

    def __init__(self, number_of_registers):
        self.registers = []
        self.set_up_registers(number_of_registers)

    def set_up_registers(self, number_of_registers):
        """The grocery store always has a single cashier in training. This
        cashier is always assigned to the highest numbered register. """
        self.registers = []
        for i in range(number_of_registers - 1):
            self.registers.append(Register(i))
        self.registers.append(TrainingRegister(number_of_registers))

    def tick(self, time):
        """Tick"""
        for register in self.registers:
            register.tick(time)

    def empty(self):
        """Empty"""
        return reduce(lambda x, y: x and y, [register.empty() for register in self.registers])

    def add_customer(self, customer):
        """Add customer"""
        customer.type.select_register(self.registers).add_customer(customer)

class ShoppingAisle(object):
    """Essentially a collection of customers"""

    def __init__(self):
        self.customers = []
        self.cashier_line = None

    def add_customer(self, number, config):
        """Add customer"""
        customer_type = TypeA()
        if config[0] == 'B':
            customer_type = TypeB()
        self.customers.append(Customer(number, customer_type, int(config[1]), int(config[2])))

    def tick(self, time):
        """Tick"""
        ready_customers = [c for c in self.customers if c.checkout_time == time]
        ready_customers = sorted(list(ready_customers), \
            key=lambda customer: \
            (customer.number_of_items, customer.type.order))
        for customer in ready_customers:
            self.customers.remove(customer)
            self.cashier_line.add_customer(customer)


    def empty(self):
        """Empty"""
        return len(self.customers) == 0

class Grocery(object):
    """The simulator"""

    def __init__(self, cashier_line, shopping_aisle):
        self.time = 0
        self.cashier_line = cashier_line
        self.shopping_aisle = shopping_aisle
        self.shopping_aisle.cashier_line = self.cashier_line

    def tick(self):
        """Tick"""
        self.shopping_aisle.tick(self.time)
        self.cashier_line.tick(self.time)

    def run(self):
        """Run"""
        while not self.shopping_aisle.empty() or not self.cashier_line.empty():
            self.time = self.time + 1
            self.tick()

def create_customers(shopping_aisle, input_data):
    """Create customers"""
    i = 0
    for customer_configuration in [line.split() for line in input_data]:
        i = i + 1
        shopping_aisle.add_customer(i, customer_configuration)



if __name__ == '__main__':
    NUMBER_OF_REGISTERS = 0

    # Assume an input file will ALWAYS be provided
    with open(sys.argv[1]) as input_file:
        INPUT_DATA = input_file.readlines()

    NUMBER_OF_REGISTERS = int(INPUT_DATA[0])
    CASHIER_LINE = CashierLine(NUMBER_OF_REGISTERS)
    SHOPPING_AISLE = ShoppingAisle()
    create_customers(SHOPPING_AISLE, INPUT_DATA[1:])
    GROCERY = Grocery(CASHIER_LINE, SHOPPING_AISLE)
    GROCERY.run()
    print "Finished at: t=" + str(GROCERY.time) + " minutes"

