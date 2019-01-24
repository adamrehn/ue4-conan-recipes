from conans import ConanFile, CMake, tools

class MediaIPCUe4Conan(ConanFile):
    name = "MediaIPC-ue4"
    version = "0.0.2"
    license = "MIT"
    url = "https://github.com/adamrehn/ue4-conan-recipes/MediaIPC-ue4"
    description = "libMediaIPC custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    default_options = "boost:header_only=True"
    generators = "cmake",
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "boost/1.67.0@conan/stable"
    )
    
    def source(self):
        self.run("git clone --depth=1 https://github.com/adamrehn/MediaIPC.git -b v{}".format(self.version))
    
    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build libMediaIPC
        cmake = CMake(self)
        cmake.configure(source_folder="MediaIPC", args=["-DBUILD_EXAMPLES=OFF"])
        cmake.build()
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
