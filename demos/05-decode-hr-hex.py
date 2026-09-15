#!/usr/bin/env python3
import argparse

from libAnt.constants import EXT_FLAG_CHANNEL_ID, MESSAGE_CHANNEL_BROADCAST_DATA
from libAnt.message import BroadcastMessage
from libAnt.profiles.factory import Factory


HEART_RATE_DEVICE_TYPE = 120


def decode_hr_payload(hex_string, device_number=0, trans_type=0):
    payload = bytes.fromhex(hex_string.replace(" ", ""))
    if len(payload) != 8:
        raise ValueError("Heart-rate broadcast payload must be exactly 8 bytes")

    decoded = []

    def collect(profile_message):
        decoded.append(profile_message)

    raw = (
        bytes([0])
        + payload
        + bytes([EXT_FLAG_CHANNEL_ID])
        + device_number.to_bytes(2, byteorder="little", signed=False)
        + bytes([HEART_RATE_DEVICE_TYPE, trans_type])
    )

    broadcast = BroadcastMessage(MESSAGE_CHANNEL_BROADCAST_DATA, raw).build(raw)
    Factory(collect).parseMessage(broadcast)

    if not decoded:
        raise ValueError("Payload was not decoded as a heart-rate message")

    return decoded[0]


def main():
    parser = argparse.ArgumentParser(description="Decode an 8-byte ANT+ heart-rate payload hex string")
    parser.add_argument("hex_string", help="Example: 00ffffff41f21f42")
    parser.add_argument("--device-number", type=int, default=0)
    parser.add_argument("--trans-type", type=lambda value: int(value, 0), default=0)
    args = parser.parse_args()

    message = decode_hr_payload(args.hex_string, args.device_number, args.trans_type)
    print(message.json())


if __name__ == "__main__":
    main()
