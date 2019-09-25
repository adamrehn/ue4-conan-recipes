from conans import ConanFile, CMake, tools
import os, shutil

class PlayfabGSDKUe4Conan(ConanFile):
    name = "playfab-gsdk-ue4"
    version = "0.6.190103"
    license = "Apache-2.0"
    url = "https://github.com/adamrehn/ue4-conan-recipes/playfab-gsdk-ue4"
    description = "PlayFab Server SDK custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    exports_sources = ("CMakeLists.txt")
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def requirements(self):
        self.requires("libcurl/ue4@adamrehn/{}".format(self.channel))
        self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
    
    def cmake_flags(self):
        
        # Determine if we are building the SDK as a shared library or a static library
        shared = ["-DBUILD_SHARED_LIBS=ON"] if self.options.shared == True else []
        
        # Generate the CMake flags to use our custom dependencies
        from ue4util import Utility
        curl = self.deps_cpp_info["libcurl"]
        openssl = self.deps_cpp_info["OpenSSL"]
        return [
            "-DCURL_INCLUDE_DIR=" + curl.include_paths[0],
            "-DCURL_LIBRARY=" + Utility.resolve_file(curl.lib_paths[0], curl.libs[0]),
            "-DOPENSSL_USE_STATIC_LIBS=ON",
            "-DOPENSSL_ROOT_DIR=" + openssl.rootpath
        ] + shared
    
    def source(self):
        
        # This recipe currently only supports building the SDK for Linux
        if self.settings.os != "Linux":
            raise RuntimeError("unsupported platform {} - only Linux is currently supported".format(self.settings.os))
        
        # Clone the source code and checkout our target commit
        self.run("git clone --progress --recursive https://github.com/PlayFab/gsdk.git")
        with tools.chdir("gsdk"):
            self.run("git checkout 7d5d6bd")
        
        # Inject our CMakeLists.txt
        shutil.move("CMakeLists.txt", "gsdk/cpp/CMakeLists.txt")
        
        # Patch the Linux PCH file to include the bundled jsoncpp
        tools.replace_in_file(
            "gsdk/cpp/cppsdk/gsdkLinuxPch.h",
            '#include "jsoncpp/json/json.h"',
            '#include "json/json.h"'
        )
    
    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build the SDK
        cmake = CMake(self)
        cmake.configure(source_folder="gsdk/cpp", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
