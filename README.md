# Block Queue Manager Simulator
The Queue Manger Simulator processes blocks and maintains Validator and Operator entities registration.

## tl;dr,
* clone, build and run docker
`docker build -t blox-app .`  
`docker run blox-app`  
* or clone, `pip install --no-cache-dir -r requirements.txt`, python ./main.py
 * http://127.0.0.1:5000/state?fileName={blocks.json}&blockNumber={2}  
* please give the system few seconds to generate log

## The Queue Manager
I see three key challenges:
* Keeping everything in app memory, no special-purpose DBs, MQs, DSs.
* Limited domain-specific understanding of relations between entities, data structures, etc., that is, what to expect.
* Handling a dedicated listener, concurrently with an API service

So my solution is therefore a multiprocess (not trivial in Python), queue-manager-like, producer-subscriber app:
### (1) A producer-like process
While not strictly required, it is an app memory simulator, which generates blocks and throw them in a queue.
this allows:
* to emulate DMs handling of related entities
* to forever keeping the system going (within configurable reason)

### (2) A concurrent subscriber-like consumer process
This process simulates the processing of tasks in the queue by:
* maintaining the state of Validators and Operators to be ready for an api get_state request
* popping ('processing') blocks from the queue (avoiding such issues as locking, dead-lettering, re-queueing, etc.)
* introducing a receiver-worker which can be multiplied according to need easily.

### (3) A concurrent light-weight api server
* Exposed as http://127.0.0.1:5000/state?fileName={blocks.json}&blockNumber={2}
* Single-threaded app within a multiprocess environment (could get clunky)
* Returns a json as per instructions

## So, what's next? (excluding separating concerns, stricter typing, best practicing, for example)
* (1) producer - a specialized data management system, preferably, one that handles relations between validators and operators, like PostgresSQL
* (2) consumer - a production-grade QM - which can be scaled with clusters and handle fifo ops - Rabbit, SQS, Kafka.
* (3) API - any REST production framework should do, FastApi, NestJS, etc.
