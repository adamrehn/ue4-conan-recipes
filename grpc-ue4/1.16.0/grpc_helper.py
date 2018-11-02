import glob, json, os, subprocess

class Utility:
    '''
    Provides utility functionality for the `ProtoBuilder` class
    '''
    
    @staticmethod
    def resolve_file(searchdir, name):
        '''
        Helper method to resolve the absolute path to a header/library/binary/etc.
        '''
        matches = glob.glob(os.path.join(searchdir, "*{}*".format(name)))
        return matches[0] if len(matches) > 0 else None
    
    @staticmethod
    def interleave(*args):
        '''
        Generator to interleave two lists
        (Based on this example: <https://stackoverflow.com/a/50312321>)
        '''
        for vals in zip(*args):
            yield from vals


class ProtoCompiler():
    '''
    Provides a convenient interface to invoke the protobuf compiler to generate
    C++ source code for .proto files containing gRPC service definitions.
    
    Consumers can instantiate this class like so:
    
    ```
    from grpc_helper import ProtoCompiler
    compiler = ProtoCompiler(self.deps_user_info["grpc-ue4"].build_data)
    ```
    '''
    
    def __init__(self, build_data):
        '''
        Creates a new ProtoCompiler using the supplied builder data, which is provided
        by the `grpc-ue4` package to consumers via `user_info.build_data`
        '''
        
        # De-serialise the JSON build data
        protobuf, grpc = json.loads(build_data)
        
        # Retrieve the absolute path to protoc and the gRPC C++ plugin
        self.protoc = Utility.resolve_file(protobuf, "protoc")
        self.plugin = Utility.resolve_file(grpc, "grpc_cpp_plugin")
    
    def codegen(self, protos, outdir):
        '''
        Invokes the protobuf compiler to perform code generation for the specified .proto files
        '''
        includes = list(Utility.interleave(["-I" for proto in protos], [os.path.dirname(proto) for proto in protos]))
        subprocess.call([self.protoc] + includes + ["--grpc_out=" + outdir, "--plugin=protoc-gen-grpc=" + self.plugin] + protos)
        subprocess.call([self.protoc] + includes + ["--cpp_out=" + outdir] + protos)
