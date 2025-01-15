import asyncio
import json
import logging
import os
from typing import Callable

from ai01.agent import Agent, AgentOptions, AgentsEvents
from ai01.providers.gemini.gemini_realtime import (
    GeminiConfig,
    GeminiOptions,
    GeminiRealtime,
)
from ai01.providers.openai import AudioTrack
from ai01.rtc import (
    HuddleClientOptions,
    ProduceOptions,
    Role,
    RoomEvents,
    RoomEventsData,
    RTCOptions,
)
from dotenv import load_dotenv
from google.genai import types

from apps.blackjack.functions.main import (
    calculate_hand_value,
    check_game_status,
    create_game_session_and_deal_initial_cards,
    dealer_turn,
    hit,
    tool_calculate_hand_value,
    tool_check_game_status,
    tool_create_game_session_and_deal_initial_cards,
    tool_dealer_turn,
    tool_hit,
)

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Chatbot")

bot_prompt = """
##Role: Blackjack Dealer
You are a BlackJack Dealer named Jack. Your role is to play a game of Blackjack with the customer.
These are the rules of the game:

"""


async def main():
    try:
        # Huddle01 API Key
        huddle_api_key = os.getenv("HUDDLE_API_KEY")

        # Huddle01 Project ID
        huddle_project_id = os.getenv("HUDDLE_PROJECT_ID")

        # gemini API Key
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not huddle_api_key or not huddle_project_id or not gemini_api_key:
            raise ValueError("Required Environment Variables are not set")

        # RTCOptions is the configuration for the RTC
        rtcOptions = RTCOptions(
            api_key=huddle_api_key,
            project_id=huddle_project_id,
            room_id="DAAO",
            role=Role.HOST,
            metadata={"displayName": "Agent"},
            huddle_client_options=HuddleClientOptions(
                autoConsume=True, volatileMessaging=False
            ),
        )

        # Agent is the Peer which is going to connect to the Room
        agent = Agent(
            options=AgentOptions(rtc_options=rtcOptions, audio_track=AudioTrack()),
        )

        # RealTimeModel is the Model which is going to be used by the Agent
        llm = GeminiRealtime(
            agent=agent,
            options=GeminiOptions(
                gemini_api_key=gemini_api_key,
                system_instruction=bot_prompt,
                config=GeminiConfig(
                    function_declaration=[
                        tool_hit,
                        tool_dealer_turn,
                        tool_calculate_hand_value,
                        tool_check_game_status,
                        tool_create_game_session_and_deal_initial_cards,
                    ],
                ),
            ),
        )

        # Join the dRTC Network, which creates a Room instance for the Agent to Join.
        room = await agent.join()

        # Room Events
        @room.on(RoomEvents.RoomJoined)
        def on_room_joined():
            logger.info("Room Joined")

        # @room.on(RoomEvents.NewPeerJoined)
        # def on_new_remote_peer(data: RoomEventsData.NewPeerJoined):
        #     logger.info(f"New Remote Peer: {data['remote_peer']}")

        # @room.on(RoomEvents.RemotePeerLeft)
        # def on_peer_left(data: RoomEventsData.RemotePeerLeft):
        #     logger.info(f"Peer Left: {data['remote_peer_id']}")

        # @room.on(RoomEvents.RoomClosed)
        # def on_room_closed(data: RoomEventsData.RoomClosed):
        #     logger.info("Room Closed")

        # @room.on(RoomEvents.RemoteProducerAdded)
        # def on_remote_producer_added(data: RoomEventsData.RemoteProducerAdded):
        #     logger.info(f"Remote Producer Added: {data['producer_id']}")

        # @room.on(RoomEvents.RemoteProducerClosed)
        # def on_remote_producer_closed(data: RoomEventsData.RemoteProducerClosed):
        #     logger.info(f"Remote Producer Closed: {data['producer_id']}")

        @room.on(RoomEvents.NewConsumerAdded)
        def on_remote_consumer_added(data: RoomEventsData.NewConsumerAdded):
            logger.info(f"Remote Consumer Added: {data}")

            if data["kind"] == "audio":
                track = data["consumer"].track

                if track is None:
                    logger.error("Consumer Track is None, This should never happen.")
                    return

                llm.conversation.add_track(data["consumer_id"], track)

        # @room.on(RoomEvents.ConsumerClosed)
        # def on_remote_consumer_closed(data: RoomEventsData.ConsumerClosed):
        #     logger.info(f"Remote Consumer Closed: {data['consumer_id']}")

        # @room.on(RoomEvents.ConsumerPaused)
        # def on_remote_consumer_paused(data: RoomEventsData.ConsumerPaused):
        #     logger.info(f"Remote Consumer Paused: {data['consumer_id']}")

        # @room.on(RoomEvents.ConsumerResumed)
        # def on_remote_consumer_resumed(data: RoomEventsData.ConsumerResumed):
        #     logger.info(f"Remote Consumer Resumed: {data['consumer_id']}")

        # # Agent Events
        @agent.on(AgentsEvents.Connected)
        def on_agent_connected():
            logger.info("Agent Connected")

        @agent.on(AgentsEvents.Disconnected)
        def on_agent_disconnected():
            logger.info("Agent Disconnected")

        @agent.on(AgentsEvents.Speaking)
        def on_agent_speaking():
            logger.info("Agent Speaking")

        @agent.on(AgentsEvents.Listening)
        def on_agent_listening():
            logger.info("Agent Listening")

        @agent.on(AgentsEvents.Thinking)
        def on_agent_thinking():
            logger.info("Agent Thinking")

        @agent.on(AgentsEvents.ToolCall)
        async def on_tool_call(callback: Callable, tool_call: types.LiveServerToolCall):
            logger.info(f"Tool Call: {tool_call}")
            function_responses = []

            if tool_call.function_calls:
                for function_call in tool_call.function_calls:
                    name = function_call.name
                    args = function_call.args
                    # Extract the numeric part from Gemini's function call ID
                    call_id = function_call.id
                    tool_response = {
                        "name": name,
                        "id": call_id,
                        "response": "",
                    }

                    if name == "create_game_session_and_deal_initial_cards":
                        if not args:
                            tool_response["response"] = "No arguments provided"
                            function_responses.append(tool_response)
                            continue

                        player_id = args["player_id"]
                        initial_state = create_game_session_and_deal_initial_cards(
                            player_id
                        )

                        tool_response["response"] = json.dumps(initial_state)
                        function_responses.append(tool_response)

                    elif name == "hit":
                        if not args:
                            tool_response["response"] = "No arguments provided"
                            function_responses.append(tool_response)
                            continue

                        player_id = args["player_id"]
                        recipient = args["recipient"]

                        hit_response = {
                            "card": hit(player_id, recipient),
                            "recipient": recipient,
                        }

                        tool_response["response"] = json.dumps(hit_response)
                        function_responses.append(tool_response)

                    elif name == "calculate_hand_value":
                        if not args:
                            tool_response["response"] = "No arguments provided"
                            function_responses.append(tool_response)
                            continue

                        player_id = args["player_id"]
                        recipient = args["recipient"]

                        hand_value = calculate_hand_value(player_id, recipient)
                        tool_response["response"] = json.dumps(hand_value)
                        function_responses.append(tool_response)

                    elif name == "dealer_turn":
                        if not args:
                            tool_response["response"] = "No arguments provided"
                            function_responses.append(tool_response)
                            continue
                        player_id = args["player_id"]
                        dealer_hand = {"dealer_hand": dealer_turn(player_id)}

                        tool_response["response"] = json.dumps(dealer_hand)
                        function_responses.append(tool_response)
                    elif name == "check_game_status":
                        if not args:
                            tool_response["response"] = "No arguments provided"
                            function_responses.append(tool_response)
                            continue
                        player_id = args["player_id"]
                        game_status = {"game_state": check_game_status(player_id)}

                        tool_response["response"] = json.dumps(game_status)
                        function_responses.append(tool_response)

            await callback(function_responses)

        # Connect to the LLM to the Room
        await llm.connect()

        # Connect the Agent to the Room
        await agent.connect()

        if agent.audio_track is not None:
            await agent.rtc.produce(
                options=ProduceOptions(
                    label="audio",
                    track=agent.audio_track,
                )
            )

        # @agent.on(RoomEvents.NewDataMessage)
        # def on_new_data_message(data: AgentEvent.NewDataMessage):
        #     print(f"New Data Message: {data['peer_id']} - {data['message']}")

        # Force the program to run indefinitely
        try:
            await asyncio.Future()
        except KeyboardInterrupt:
            logger.info("Exiting...")

    except KeyboardInterrupt:
        print("Exiting...")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
