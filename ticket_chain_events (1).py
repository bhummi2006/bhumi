import hashlib
import json
import time
import uuid
from typing import List, Dict, Any


class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict[str, Any]], previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), [{"system": "genesis"}], "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, block: Block) -> str:
        block.nonce = 0
        computed_hash = block.compute_hash()
        target = '0' * self.difficulty
        while not computed_hash.startswith(target):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block: Block, proof: str) -> bool:
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block: Block, block_hash: str) -> bool:
        return (block_hash.startswith('0' * self.difficulty) and block_hash == block.compute_hash())

    def mine_block(self, transactions: List[Dict[str, Any]]):
        new_block = Block(index=self.last_block.index + 1,
                          timestamp=time.time(),
                          transactions=transactions,
                          previous_hash=self.last_block.hash)
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        return new_block

    def issue_ticket(self, event_name: str, buyer_name: str) -> Dict[str, Any]:
        raw_id = str(uuid.uuid4())
        tid_hash = hashlib.sha256(raw_id.encode()).hexdigest()
        ticket_id = f"TKT-{tid_hash[:12]}"
        ticket = {
            "type": "ISSUE",
            "ticket_id": ticket_id,
            "event": event_name,
            "buyer": buyer_name,
            "timestamp": time.ctime()
        }
        block = self.mine_block([ticket])
        return {"ticket": ticket, "block_index": block.index, "block_hash": block.hash}


if __name__ == "__main__":
    bc = Blockchain(difficulty=3)

    events = [
        ("Dandiya Night", "Aarav"),
        ("Painting Competition", "Bhumi"),
        ("Movie Screening", "Rahul"),
        ("Carnival", "Isha"),
        ("DJ Night", "Kabir")
    ]

    for ev, buyer in events:
        result = bc.issue_ticket(event_name=ev, buyer_name=buyer)
        print("\n🎟️ Ticket Issued & Block Mined")
        print("Block Index:", result["block_index"])
        print("Block Hash:", result["block_hash"])
        print("Ticket Details:", result["ticket"])

    print("\n\n================ Blockchain Explorer ================")
    for block in bc.chain:
        print(f"\nBlock #{block.index}")
        print("Timestamp:", time.ctime(block.timestamp))
        print("Hash:", block.hash)
        print("Previous Hash:", block.previous_hash)
        print("Transactions:", block.transactions)
