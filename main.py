from flask import Flask, request, jsonify
import time
from multiprocessing import Process, Manager
from models.blocks import Block

NETWORK_FACTOR = 4
CONSUMER_FACTOR = 2
BLOCK_POOL_CAPACITY = 99
MAX_LOG_SIZE = 1000


# todo proper typing
def block_producer(pool):
    while True:
        if 0 <= len(pool) <= BLOCK_POOL_CAPACITY:
            new_block = Block()
            # todo appending a dict is inefficient, but will be easier to locate for the consumer
            pool.append(new_block.to_dict())
        else:
            print("simulate log - WARNING - block pool at full capacity")
        time.sleep(NETWORK_FACTOR)


def block_consumer(pool, block_state_log):
    while True:
        try:
            if pool:
                block = pool.pop(0)
                if any(len(transaction['register']) >= 3 for transaction in block['transactions']):
                    process_block(block, block_state_log)
        except Exception as e:
            print(f"Error: {e}")


def process_block(block, block_container):
    block_id = str(block['id'])
    block_container[block_id] = block

    if len(block_container) > MAX_LOG_SIZE:
        oldest_block_ids = sorted(block_container.keys())[:len(block_container) - MAX_LOG_SIZE]
        for block_id_to_remove in oldest_block_ids:
            del block_container[block_id_to_remove]


app = Flask(__name__)


@app.route('/state', methods=['GET'])
def get_state():
    file_name = request.args.get('fileName')
    block_number = int(request.args.get('blockNumber', 0))
    if block_number > 0:
        block_id_to_find = str(block_number)

        if str(block_id_to_find) in block_state_log:
            block_data_transactions = block_state_log[str(block_id_to_find)]['transactions']

            operator_ids = {entry['operator_id'] for transaction in block_data_transactions for entry in
                            transaction.get('register', [])}
            operators = [{'id': operator_id} for operator_id in operator_ids]

            operator_validator_mapping = {operator['id']: [] for operator in operators}

            validators = []
            for transaction in block_data_transactions:
                validator = {
                    'id': len(validators),  # Assign a unique ID to each validator
                    'address': transaction['address'],
                    'operators': [operator['operator_id'] for operator in transaction.get('register', [])],
                }
                validators.append(validator)

                for operator_id in validator['operators']:
                    operator_validator_mapping[operator_id].append(len(validators) - 1)  # Append the validator ID

            for operator in operators:
                operator_id = operator['id']
                operator['validators'] = operator_validator_mapping.get(operator_id, [])

            response = {
                'validators': validators,
                'operators': operators,
            }

        else:
            response = {
                'fileName': file_name,
                'blockNumber': block_number,
                'state': 'Block not found'
            }
    else:
        response = {
            'fileName': file_name,
            'blockNumber': block_number,
            'state': 'Invalid block number'
        }

    return jsonify(response)


if __name__ == '__main__':
    try:
        manager = Manager()
        # block_state_log = manager.dict()
        block_manager = manager.dict()
        block_pool = manager.list()

        # with Manager() as manager:
        # block_pool = manager.list()
        producer_process = Process(target=block_producer, args=(block_pool,))
        producer_process.start()
        consumer_process = Process(target=block_consumer, args=(block_pool, block_manager))
        consumer_process.start()

        block_state_log = block_manager

        app.run(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("Terminating processes...")

    finally:
        print("Main process terminated")
