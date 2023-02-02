import pytest

from grpc import StatusCode

from threat_pb2 import threatRequest, threatResponse, Empty
from threat_pb2_grpc import ThreatServicer, ThreatStub


@pytest.fixture(scope='module')
def grpc_add_to_server():
    return ThreatServicer.add_ThreatServicer_to_server


@pytest.fixture(scope='module')
def grpc_servicer():
    from servicer import EchoService
    return EchoService()


@pytest.fixture(scope='module')
def grpc_stub_cls(grpc_channel):
    from stub.test_pb2_grpc import EchoServiceStub

    return EchoServiceStub
