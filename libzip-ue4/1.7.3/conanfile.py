from logging import FATAL
from conans import ConanFile, CMake, tools


class LibzipUe4Conan(ConanFile):
    name = "libzip-ue4"
    version = "1.7.3"
    license = "BSD"
    author = "Benjamin Ritter benjamin.ritter@protonmail.com"
    url = "https://github.com/adamrehn/ue4-conan-recipes/libzip-ue4"
    description = "libZip for UE4"
    settings = "os", "compiler", "build_type", "arch"
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile")
    _cmake = None

    def requirements(self):
        self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
        self.requires("bzip2/1.0.8")
        self.requires("xz_utils/5.2.4")
        self.requires("zstd/1.4.5 ")
        self.requires("mbedtls/2.16.3-gpl")

    def _configure_cmake(self):
        
        # Generate the CMake flags to ensure the UE4-bundled version of zlib is used
        from ue4util import Utility
        zlib = self.deps_cpp_info["zlib"]
        openssl = self.deps_cpp_info["OpenSSL"]

        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_REGRESS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOC"] = False

        self._cmake.definitions["ENABLE_LZMA"] = False
        self._cmake.definitions["ENABLE_BZIP2"] = False
        self._cmake.definitions["ENABLE_ZSTD"] = True

        self._cmake.definitions["ENABLE_COMMONCRYPTO"] = False  # TODO: We need CommonCrypto package
        self._cmake.definitions["ENABLE_GNUTLS"] = False  # TODO: We need GnuTLS package

        self._cmake.definitions["ENABLE_MBEDTLS"] = False
        self._cmake.definitions["ENABLE_OPENSSL"] = False
        self._cmake.definitions["ENABLE_WINDOWS_CRYPTO"] = False

        self._cmake.definitions["ZLIB_INCLUDE_DIR"] = zlib.include_paths[0]
        self._cmake.definitions["ZLIB_LIBRARY"] = Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0])
        

        self._cmake.configure(source_dir="libzip")
        # return [
        #     "-DZLIB_INCLUDE_DIR=" + zlib.include_paths[0],
        #     "-DZLIB_LIBRARY=" + Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0]),
        #     "-DOPENSSL_SYSTEM_LIBRARIES={}".format(";".join(openssl.system_libs)),
        #     "-DOPENSSL_USE_STATIC_LIBS=ON",
        #     "-DOPENSSL_ROOT_DIR=" + openssl.rootpath,
        #     "-DENABLE_GNUTLS = False",
        #     "-DENABLE_COMMONCRYPTO = False"
        # ]
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        git = tools.Git(folder="libzip")
        git.clone("https://github.com/nih-at/libzip.git", "v{}".format(self.version) )
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
#         tools.replace_in_file("libzip/CMakeLists.txt", '''project(libzip
#   VERSION 1.7.3
#   LANGUAGES C)''',
#                               '''project(libzip
#   VERSION 1.7.3
#   LANGUAGES C)
# include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
# conan_basic_setup()''')

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

