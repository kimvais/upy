import asyncio
import datetime
import json
import os

import aiohttp
import envs

cloud_url = envs.env("CLOUD_URL")


async def send_to_cloud(payload):
    async with aiohttp.ClientSession() as session:
        await session.post(cloud_url, json=payload)


class ServerProtocol(asyncio.BaseProtocol):
    fp = None

    def connection_made(self, transport):
        self.fp = open("temperatures.csv", "a+")
        self.transport = transport

    def datagram_received(self, data, addr):
        message = json.loads(data.decode())
        print('{} from {}:{}'.format(message, *addr))
        for rom, temp in message['temps']:
            timestamp = int(datetime.datetime.utcnow().timestamp())
            node_id = message['node']
            sensor_id = rom
            dataline = '{0};"{1}";"{2}";{3};"{4}"\n'.format(
                timestamp,
                node_id,
                sensor_id,
                temp,
                addr[0],
            )
            coro = send_to_cloud(dict(timestamp=timestamp, node_id=node_id, sensor_id=sensor_id, temperature=temp))
            asyncio.get_running_loop().call_soon(coro)
            print(dataline)
            self.fp.write(dataline)
            self.fp.flush()
            os.fsync(self.fp.fileno())


def main():
    print("Starting UDP server")
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_event_loop()
    # One protocol instance will be created to serve all
    # client requests.
    listen = loop.create_datagram_endpoint(
        lambda: ServerProtocol(),
        local_addr=('0.0.0.0', 54724))
    transport, protocol = loop.run_until_complete(listen)
    try:
        loop.run_forever()
    finally:
        protocol.fp.close()
        transport.close()


if __name__ == "__main__":
    main()
