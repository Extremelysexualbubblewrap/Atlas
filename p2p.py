import asyncio
import websockets
import json
from block import Block

# Define message types as constants for clarity
MESSAGE_TYPE = {
    'QUERY_LATEST': 0,
    'QUERY_ALL': 1,
    'RESPONSE_BLOCKCHAIN': 2,
    'NEW_TRANSACTION': 3,
    'NEW_BLOCK': 4,
}

class P2PServer:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.peers = set()

    async def handle_connection(self, websocket, path):
        """
        Handles a new peer connection. Registers the peer, sends a query
        for their latest block, and then listens for messages.
        """
        self.peers.add(websocket)
        print(f"New peer connected: {websocket.remote_address}. Total peers: {len(self.peers)}")

        # Ask the new peer for their latest block to see if we are in sync
        await self.send_message(websocket, {'type': MESSAGE_TYPE['QUERY_LATEST']})

        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(websocket, data)
        except websockets.exceptions.ConnectionClosed:
            print(f"Peer disconnected: {websocket.remote_address}")
        finally:
            self.peers.remove(websocket)

    async def handle_message(self, websocket, message):
        """
        Handles incoming messages from peers based on their type.
        """
        msg_type = message.get('type')

        if msg_type == MESSAGE_TYPE['QUERY_LATEST']:
            response = {'type': MESSAGE_TYPE['RESPONSE_BLOCKCHAIN'], 'data': json.dumps([self.blockchain.get_latest_block().to_dict()])}
            await self.send_message(websocket, response)

        elif msg_type == MESSAGE_TYPE['QUERY_ALL']:
            response = {'type': MESSAGE_TYPE['RESPONSE_BLOCKCHAIN'], 'data': json.dumps([b.to_dict() for b in self.blockchain.chain])}
            await self.send_message(websocket, response)

        elif msg_type == MESSAGE_TYPE['RESPONSE_BLOCKCHAIN']:
            received_blocks_data = json.loads(message['data'])
            received_blocks = [Block.from_dict(b) for b in received_blocks_data]
            await self.handle_blockchain_response(received_blocks)

        elif msg_type == MESSAGE_TYPE['NEW_BLOCK']:
            block_data = message['data']
            new_block = Block.from_dict(block_data)
            self.blockchain.add_block_from_peer(new_block)

        elif msg_type == MESSAGE_TYPE['NEW_TRANSACTION']:
            tx_data = message['data']
            self.blockchain.add_transaction(tx_data, broadcast=False)

        else:
            print(f"Received message of unknown type: {msg_type}")

    async def handle_blockchain_response(self, received_blocks):
        """
        Compares the received blockchain with the local one and decides whether to sync.
        """
        if not received_blocks:
            return

        latest_block_received = received_blocks[-1]
        latest_block_held = self.blockchain.get_latest_block()

        if latest_block_received.index > latest_block_held.index:
            if latest_block_held.hash == latest_block_received.previous_hash:
                print("Received next valid block. Appending to our chain.")
                self.blockchain.add_block_from_peer(latest_block_received)
            elif len(received_blocks) == 1:
                print("Chain has diverged. Requesting full chain from peers.")
                await self.broadcast({'type': MESSAGE_TYPE['QUERY_ALL']})
            else:
                print("Received a longer blockchain. Attempting to replace local chain.")
                self.blockchain.replace_chain(received_blocks)
        else:
            print("Received blockchain is not longer than local chain. No action needed.")

    async def send_message(self, websocket, message):
        await websocket.send(json.dumps(message))

    async def broadcast(self, message):
        if self.peers:
            message_json = json.dumps(message)
            tasks = [peer.send(message_json) for peer in self.peers]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_new_block(self, block):
        message = {'type': MESSAGE_TYPE['NEW_BLOCK'], 'data': block.to_dict()}
        await self.broadcast(message)

    async def broadcast_new_transaction(self, transaction):
        message = {'type': MESSAGE_TYPE['NEW_TRANSACTION'], 'data': transaction}
        await self.broadcast(message)

    async def start_server(self, host, port):
        server = await websockets.serve(self.handle_connection, host, port)
        print(f"P2P server listening on {host}:{port}")
        await server.wait_closed()

    async def connect_to_peer(self, uri):
        try:
            websocket = await websockets.connect(uri)
            asyncio.create_task(self.handle_connection(websocket, path=uri))
        except Exception as e:
            print(f"Failed to connect to peer {uri}: {e}")