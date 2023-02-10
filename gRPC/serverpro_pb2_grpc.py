# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import serverpro_pb2 as serverpro__pb2


class serverFuncStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.addUser = channel.unary_unary(
                '/serverFunc/addUser',
                request_serializer=serverpro__pb2.String.SerializeToString,
                response_deserializer=serverpro__pb2.Ints.FromString,
                )
        self.removeUser = channel.unary_unary(
                '/serverFunc/removeUser',
                request_serializer=serverpro__pb2.String.SerializeToString,
                response_deserializer=serverpro__pb2.Ints.FromString,
                )


class serverFuncServicer(object):
    """Missing associated documentation comment in .proto file."""

    def addUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def removeUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_serverFuncServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'addUser': grpc.unary_unary_rpc_method_handler(
                    servicer.addUser,
                    request_deserializer=serverpro__pb2.String.FromString,
                    response_serializer=serverpro__pb2.Ints.SerializeToString,
            ),
            'removeUser': grpc.unary_unary_rpc_method_handler(
                    servicer.removeUser,
                    request_deserializer=serverpro__pb2.String.FromString,
                    response_serializer=serverpro__pb2.Ints.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'serverFunc', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class serverFunc(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def addUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/serverFunc/addUser',
            serverpro__pb2.String.SerializeToString,
            serverpro__pb2.Ints.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def removeUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/serverFunc/removeUser',
            serverpro__pb2.String.SerializeToString,
            serverpro__pb2.Ints.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)