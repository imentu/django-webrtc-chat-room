from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import logger

USERNAME_CHANEELNAME_MAPPER = {}


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        url_args = self.scope['url_route']['kwargs']
        self.room_name = url_args['room']
        self.user_name = url_args['name']

        await self.accept()
        USERNAME_CHANEELNAME_MAPPER[self.user_name] = self.channel_name

        await self.add_user_to_room()

    async def add_user_to_room(self):
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        logger.info(
            f'[JoinRoom]user:[{self.user_name}] connected to room:[{self.room_name}]')

        await self.broadcast_new_peer_in_room()

    async def broadcast_new_peer_in_room(self):
        await self.channel_layer.group_send(self.room_name, {'type': 'send_content', 'content': {'event': 'NewPeer', 'peerUserName': self.user_name}})
        logger.info(
            f'[Broadcast]NewPeer user:[{self.user_name}] join the room:[{self.room_name}]')

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        logger.info(
            f'[LeaveRoom]user:[{self.user_name}] leaved from [{self.room_name}]')

    async def receive_json(self, content, **kwargs):
        event = content['event']

        if event == 'PeerOffer' or event == 'PeerAnswer':
            await self.handle_peer_interchange(event, content)
        elif event == 'PeerCandidate':
            receiver = content['peerUserName']
            if receiver not in USERNAME_CHANEELNAME_MAPPER.keys():
                return

            receiver_channel_name = USERNAME_CHANEELNAME_MAPPER[receiver]
            sender = self.user_name
            await self.send_json_to_channel(receiver_channel_name, {'event': 'PeerCandidate', 'peerUserName': sender, 'sdpMLineIndex': content['sdpMLineIndex'], 'candidate': content['candidate']})

    async def handle_peer_interchange(self, event, content):
        receiver = content['peerUserName']
        if receiver not in USERNAME_CHANEELNAME_MAPPER.keys():
            return

        receiver_channel_name = USERNAME_CHANEELNAME_MAPPER[receiver]
        sender = self.user_name
        await self.send_json_to_channel(receiver_channel_name, {'event': event, 'peerUserName': sender, 'SDP': content['SDP']})
        logger.info(
            f'[PeerInterchange]user:[{self.user_name}] sent event[{event}] to user:[{receiver}]')

    async def send_json_to_channel(self, channel_name, content):
        await self.channel_layer.send(channel_name, {'type': 'send_content', 'content': content})

    async def send_content(self, context):
        await self.send_json(context['content'])
