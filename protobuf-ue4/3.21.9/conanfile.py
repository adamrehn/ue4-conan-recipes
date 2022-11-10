from conans import ConanFile, CMake, tools
import json

class ProtobufUe4Conan(ConanFile):
    name = "protobuf-ue4"
    version = "3.21.9"
    license = "BSD-3-Clause"
    url = "https://github.com/adamrehn/ue4-conan-recipes/protobuf-ue4"
    description = "Protocol Buffers custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def requirements(self):
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
    
    def cmake_flags(self):
        
        # Generate the CMake flags to ensure the UE4-bundled version of zlib is used
        from ue4util import Utility
        zlib = self.deps_cpp_info["zlib"]
        return [
            "-DBUILD_SHARED_LIBS=OFF",
            "-Dprotobuf_BUILD_TESTS=OFF",
            "-Dprotobuf_MSVC_STATIC_RUNTIME=OFF",
            "-DZLIB_INCLUDE_DIR=" + zlib.include_paths[0],
            "-DZLIB_LIBRARY=" + Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0])
        ]
    
    def source(self):
        self.run("git clone --progress --depth=1 https://github.com/protocolbuffers/protobuf.git -b v{}".format(self.version))
        
        # Prevent libprotobuf-lite from being included in our built package
        tools.replace_in_file(
            "protobuf/cmake/install.cmake",
            "set(_protobuf_libraries libprotobuf-lite libprotobuf)",
            "set(_protobuf_libraries libprotobuf)"
        )
    
    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build libprotobuf
        cmake = CMake(self)
        cmake.configure(source_folder="protobuf/cmake", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        
        # Disable RTTI when consuming the library or its generated code from the Unreal Engine
        self.cpp_info.defines = ["GOOGLE_PROTOBUF_NO_RTTI=1"]
        
        # Ensure the protobuf compiler is copied when precomputing dependency data with conan-ue4cli
        self.user_info.binaries = json.dumps(["protoc"])
