# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: threat.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cthreat.proto\x12\x06threat\"4\n\rthreatRequest\x12\x11\n\tlongitude\x18\x01 \x01(\x03\x12\x10\n\x08latitude\x18\x02 \x01(\x03\" \n\x0ethreatResponse\x12\x0e\n\x06threat\x18\x01 \x01(\x02\x32K\n\x06Threat\x12\x41\n\x0egetThreatScore\x12\x15.threat.threatRequest\x1a\x16.threat.threatResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'threat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _THREATREQUEST._serialized_start=24
  _THREATREQUEST._serialized_end=76
  _THREATRESPONSE._serialized_start=78
  _THREATRESPONSE._serialized_end=110
  _THREAT._serialized_start=112
  _THREAT._serialized_end=187
# @@protoc_insertion_point(module_scope)
