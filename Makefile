all:
	python -m grpc_tools.protoc -I protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/threat.proto

clean:
	rm -rf threat_pb2.py threat_pb2_grpc.py threat_pb2.pyi threat_pb2_grpc.pyi