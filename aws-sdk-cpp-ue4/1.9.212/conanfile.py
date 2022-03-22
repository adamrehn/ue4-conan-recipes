from conans import ConanFile, CMake, tools


class AwsSdkCppUe4Conan(ConanFile):
    name = "aws-sdk-cpp-ue4"
    version = "1.9.212"
    license = "Apache-2.0"
    url = "https://github.com/adamrehn/ue4-conan-recipes/aws-sdk-cpp-ue4"
    description = "AWS SDK for C++ Custom Build for Unreal Engine"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "build_only": "ANY",  # A semicolon-delimited list of the AWS client libraries to build. If blank or not specified then all client libraries are built. It's advisable to set this option to just the libraries you need to minimize your build times.
    }
    default_options = {
        "build_only": None,
    }
    generators = "cmake"
    short_paths = True
    requires = ("libcxx/ue4@adamrehn/profile", "ue4util/ue4@adamrehn/profile")

    def requirements(self):
        if self.settings.os == "Windows":
            # On Windows the AWS SDK for C++ uses the OS libraries for HTTP and encryption so it doesn't have any external dependencies.
            pass
        else:
            self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
            self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
            self.requires("libcurl/ue4@adamrehn/{}".format(self.channel))

    def source(self):
        self.run("git clone --progress -c advice.detachedHead=false --recurse-submodules --single-branch --branch {} https://github.com/aws/aws-sdk-cpp".format(self.version))

    def cmake_flags(self):
        from ue4util import Utility

        flags = [
            "-DBUILD_SHARED_LIBS=OFF",
            "-DENABLE_UNITY_BUILD=1",
        ]

        if self.settings.os == "Windows":
            pass
        else:
            zlib = self.deps_cpp_info["zlib"]
            flags.extend(
                [
                    "-DZLIB_INCLUDE_DIR=" + zlib.include_paths[0],
                    "-DZLIB_LIBRARY=" + Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0]),
                ]
            )

            openssl = self.deps_cpp_info["OpenSSL"]
            flags.extend(
                [
                    "-DOPENSSL_SYSTEM_LIBRARIES={}".format(";".join(openssl.system_libs)),
                    "-DOPENSSL_USE_STATIC_LIBS=ON",
                    "-DOPENSSL_ROOT_DIR=" + openssl.rootpath,
                ]
            )

            curl = self.deps_cpp_info["libcurl"]
            flags.extend(
                [
                    "-DCURL_INCLUDE_DIR=" + curl.include_paths[0],
                    "-DCURL_LIBRARY=" + Utility.resolve_file(curl.lib_paths[0], curl.libs[0]),
                ]
            )

        if self.options.get_safe("build_only"):
            flags.append("-DBUILD_ONLY={}".format(self.options.build_only))

        return flags

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="aws-sdk-cpp", args=self.cmake_flags())
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            # This list of system libraries was derived from searching for `INTERFACE_LINK_LIBRARIES` in the '.cmake' files produced by a build. There may well be a more sophisticated way of fetching these from the CMake configuration using Conan facilities.
            self.cpp_info.system_libs = ["Bcrypt", "Kernel32", "Ws2_32", "Ncrypt", "Secur32", "Crypt32", "Shlwapi", "Userenv", "Version", "Wininet", "Winhttp", "Winmm"]
