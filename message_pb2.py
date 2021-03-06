# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: message.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='message.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\rmessage.proto\"\x88\x03\n\nSecureChat\x12\"\n\x06sender\x18\x01 \x01(\x0b\x32\x12.SecureChat.Sender\x12(\n\trecepient\x18\x02 \x01(\x0b\x32\x15.SecureChat.Recepient\x12$\n\x07message\x18\x03 \x01(\x0b\x32\x13.SecureChat.Message\x1a\\\n\x06Sender\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tpublic_ip\x18\x02 \x01(\t\x12\x10\n\x08hostname\x18\x03 \x01(\t\x12\x0e\n\x06pubkey\x18\n \x01(\t\x12\x0f\n\x07pubcert\x18\x0b \x01(\t\x1a>\n\tRecepient\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tpublic_ip\x18\x02 \x01(\t\x12\x10\n\x08hostname\x18\x03 \x01(\t\x1ah\n\x07Message\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x1b\n\x13timestamp_generated\x18\x02 \x01(\x03\x12\x1c\n\x14timestamp_expiration\x18\x03 \x01(\x03\x12\x11\n\tsignature\x18\n \x01(\tb\x06proto3')
)




_SECURECHAT_SENDER = _descriptor.Descriptor(
  name='Sender',
  full_name='SecureChat.Sender',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='SecureChat.Sender.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='public_ip', full_name='SecureChat.Sender.public_ip', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hostname', full_name='SecureChat.Sender.hostname', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pubkey', full_name='SecureChat.Sender.pubkey', index=3,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pubcert', full_name='SecureChat.Sender.pubcert', index=4,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=148,
  serialized_end=240,
)

_SECURECHAT_RECEPIENT = _descriptor.Descriptor(
  name='Recepient',
  full_name='SecureChat.Recepient',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='SecureChat.Recepient.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='public_ip', full_name='SecureChat.Recepient.public_ip', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hostname', full_name='SecureChat.Recepient.hostname', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=242,
  serialized_end=304,
)

_SECURECHAT_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='SecureChat.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='SecureChat.Message.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp_generated', full_name='SecureChat.Message.timestamp_generated', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp_expiration', full_name='SecureChat.Message.timestamp_expiration', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature', full_name='SecureChat.Message.signature', index=3,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=306,
  serialized_end=410,
)

_SECURECHAT = _descriptor.Descriptor(
  name='SecureChat',
  full_name='SecureChat',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='SecureChat.sender', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='recepient', full_name='SecureChat.recepient', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message', full_name='SecureChat.message', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_SECURECHAT_SENDER, _SECURECHAT_RECEPIENT, _SECURECHAT_MESSAGE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=410,
)

_SECURECHAT_SENDER.containing_type = _SECURECHAT
_SECURECHAT_RECEPIENT.containing_type = _SECURECHAT
_SECURECHAT_MESSAGE.containing_type = _SECURECHAT
_SECURECHAT.fields_by_name['sender'].message_type = _SECURECHAT_SENDER
_SECURECHAT.fields_by_name['recepient'].message_type = _SECURECHAT_RECEPIENT
_SECURECHAT.fields_by_name['message'].message_type = _SECURECHAT_MESSAGE
DESCRIPTOR.message_types_by_name['SecureChat'] = _SECURECHAT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SecureChat = _reflection.GeneratedProtocolMessageType('SecureChat', (_message.Message,), dict(

  Sender = _reflection.GeneratedProtocolMessageType('Sender', (_message.Message,), dict(
    DESCRIPTOR = _SECURECHAT_SENDER,
    __module__ = 'message_pb2'
    # @@protoc_insertion_point(class_scope:SecureChat.Sender)
    ))
  ,

  Recepient = _reflection.GeneratedProtocolMessageType('Recepient', (_message.Message,), dict(
    DESCRIPTOR = _SECURECHAT_RECEPIENT,
    __module__ = 'message_pb2'
    # @@protoc_insertion_point(class_scope:SecureChat.Recepient)
    ))
  ,

  Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
    DESCRIPTOR = _SECURECHAT_MESSAGE,
    __module__ = 'message_pb2'
    # @@protoc_insertion_point(class_scope:SecureChat.Message)
    ))
  ,
  DESCRIPTOR = _SECURECHAT,
  __module__ = 'message_pb2'
  # @@protoc_insertion_point(class_scope:SecureChat)
  ))
_sym_db.RegisterMessage(SecureChat)
_sym_db.RegisterMessage(SecureChat.Sender)
_sym_db.RegisterMessage(SecureChat.Recepient)
_sym_db.RegisterMessage(SecureChat.Message)


# @@protoc_insertion_point(module_scope)
