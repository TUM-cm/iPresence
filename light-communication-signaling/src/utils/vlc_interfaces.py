from utils.custom_enum import enum_name

SenderAction = enum_name("send", "pattern", "feedback fail", "feedback success")
SenderDevice = enum_name("high", "low")

ReceiverAction = enum_name("start", "stop")
ReceiverDevice = enum_name("pd", "led")
