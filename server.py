import asyncio
import json
import websockets
from pig_game import PigGame

rooms = {}              # room_id -> PigGame
room_connections = {}   # room_id -> list of websockets


def get_room_id(path):
    parts = path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "room":
        return parts[1]
    return None


async def handler(websocket):
    path = websocket.request.path
    print("NEW CONNECTION:", path)

    room_id = get_room_id(path)
    if not room_id:
        await websocket.send(json.dumps({"error": "Invalid room"}))
        return

    # create room if not exists
    if room_id not in rooms:
        rooms[room_id] = PigGame(["A", "B"])
        room_connections[room_id] = []

    connections = room_connections[room_id]
    game = rooms[room_id]

    # room full
    if len(connections) >= 2:
        await websocket.send(json.dumps({"error": "Room full"}))
        return

    # assign player
    player_index = len(connections)
    connections.append(websocket)
    player_name = game.players[player_index]

    print(f"Player {player_name} joined room {room_id}")

    # tell client who they are
    await websocket.send(json.dumps({
        "type": "assign",
        "player": player_name
    }))

    # send initial game state
    await websocket.send(json.dumps({
        "type": "state",
        **game.get_state()
    }))

    try:
        async for message in websocket:
            print(f"Received from {player_name}: {message}")

            # enforce turn
            if player_index != game.current_player_index:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Not your turn"
                }))
                continue

            if message == "ROLL":
                state = game.roll()
            elif message == "HOLD":
                state = game.hold()
            elif message == "RESTART":
                game.reset()
                state = game.get_state()

            else:
                continue

            payload = json.dumps({
                "type": "state",
                **state
            })

            # broadcast to all players in room
            for ws in connections:
                await ws.send(payload)

    finally:
        print(f"Player {player_name} disconnected")
        connections.remove(websocket)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()


asyncio.run(main())
