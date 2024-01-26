# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: outbound_call.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13outbound_call.proto\x12\x14\x43\x61mpaignOutboundCall"\x90\x02\n\x1b\x43\x61mpiagnOutboundCallRequest\x12\x14\n\x0cworkspace_id\x18\x01 \x01(\t\x12\r\n\x05\x66rom_\x18\x02 \x01(\t\x12\n\n\x02to\x18\x03 \x01(\t\x12\x10\n\x08\x63\x61ll_sid\x18\x04 \x01(\t\x12\x16\n\x0e\x63hild_call_sid\x18\x05 \x01(\t\x12\x17\n\x0fparent_call_sid\x18\x06 \x01(\t\x12\x16\n\x0e\x63onference_sid\x18\x07 \x01(\t\x12\x1a\n\x12total_participants\x18\x08 \x01(\x05\x12\x38\n\rbilling_types\x18\t \x03(\x0e\x32!.CampaignOutboundCall.BillingType\x12\x0f\n\x07remarks\x18\n \x01(\t"\x94\x01\n\x0cGrpcResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12.\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1f.CampaignOutboundCall.GrpcError\x12\x43\n\x07payload\x18\x03 \x01(\x0b\x32\x32.CampaignOutboundCall.CampiagnOutboundCallResponse"K\n\x1c\x43\x61mpiagnOutboundCallResponse\x12\x14\n\x0cworkspace_id\x18\x01 \x01(\t\x12\x15\n\rcharge_amount\x18\x02 \x01(\x02"*\n\tGrpcError\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t*E\n\x0b\x42illingType\x12\x0e\n\nSIP_CHARGE\x10\x00\x12\x15\n\x11\x43ONFERENCE_CHARGE\x10\x01\x12\x0f\n\x0b\x43\x41LL_CHARGE\x10\x02\x32\x92\x01\n\x1a\x43\x61mpaignOutboundCallCharge\x12t\n\x19\x45xecutePaymentTransaction\x12\x31.CampaignOutboundCall.CampiagnOutboundCallRequest\x1a".CampaignOutboundCall.GrpcResponse"\x00\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "outbound_call_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _BILLINGTYPE._serialized_start = 592
    _BILLINGTYPE._serialized_end = 661
    _CAMPIAGNOUTBOUNDCALLREQUEST._serialized_start = 46
    _CAMPIAGNOUTBOUNDCALLREQUEST._serialized_end = 318
    _GRPCRESPONSE._serialized_start = 321
    _GRPCRESPONSE._serialized_end = 469
    _CAMPIAGNOUTBOUNDCALLRESPONSE._serialized_start = 471
    _CAMPIAGNOUTBOUNDCALLRESPONSE._serialized_end = 546
    _GRPCERROR._serialized_start = 548
    _GRPCERROR._serialized_end = 590
    _CAMPAIGNOUTBOUNDCALLCHARGE._serialized_start = 664
    _CAMPAIGNOUTBOUNDCALLCHARGE._serialized_end = 810
# @@protoc_insertion_point(module_scope)