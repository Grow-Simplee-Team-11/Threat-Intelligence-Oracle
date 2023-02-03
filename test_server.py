import pytest

import sys
import grpc
from grpc import StatusCode

from threat_pb2 import threatRequest, threatResponse
from threat_pb2_grpc import ThreatStub, add_ThreatServicer_to_server

from server import Threat
from concurrent import futures


@pytest.fixture
def server():
    port = '8080'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_ThreatServicer_to_server(Threat(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    yield server
    server.stop(0)


@pytest.fixture
def stub(server):
    channel = grpc.insecure_channel('localhost:8080')
    stub = ThreatStub(channel)
    return stub


def test_threat(stub):
    request = threatRequest()
    request.latitude = 19076582
    request.longitude = 72872488
    response = stub.getThreatScore(request)
    assert isinstance(response, threatResponse)
    assert isinstance(response.threat, float)


def test_threat_error(stub):
    request = threatRequest()
    request.latitude = 10**18
    request.longitude = 10**18
    try:
        response = stub.getThreatScore(request)
    except grpc.RpcError as e:
        assert e.code() == StatusCode.INVALID_ARGUMENT or e.code() == StatusCode.UNKNOWN
