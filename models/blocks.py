import secrets
import random


class Operator:

    def __init__(self):
        self.id = random.randint(101, 109)


class Transaction:

    next_transaction_id = 0
    length_of_hex_string = 40
    max_number_of_operators = 4

    def __init__(self):
        self.id = Transaction.next_transaction_id
        Transaction.next_transaction_id += 1
        self.address = self.generate_random_hex_string()
        self.register = self.register_random_operators()

    def generate_random_hex_string(self):
        return secrets.token_hex(self.length_of_hex_string)

    def register_random_operators(self):
        num_operators = random.randint(0, self.max_number_of_operators)
        operators = [Operator() for _ in range(num_operators)]
        return operators

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'register': [{'operator_id': operator.id} for operator in self.register]
        }


class Block:

    next_block_id = 0
    max_num_of_transactions = 6

    def __init__(self):
        self.id = Block.next_block_id
        Block.next_block_id += 1
        self.transactions = self.generate_random_transactions()

    def generate_random_transactions(self):
        num_transactions = random.randint(1, self.max_num_of_transactions)
        transactions = [Transaction() for _ in range(num_transactions)]
        return transactions

    def to_dict(self):
        return {
            'id': self.id,
            'transactions': [transaction.to_dict() for transaction in self.transactions]
        }
