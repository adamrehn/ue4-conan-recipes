from conans import ConanFile, CMake, tools


class elzipUe4Conan(ConanFile):
    name = "elzip-ue4"
    version = "0.0.1"
    license = "MIT"
    author = "Benjamin Ritter Benjamin.Ritter@protonmail.com"
    url = "https://github.com/adamrehn/ue4-conan-recipes/11zip-ue4"
    description = "Small C++ zip library https://github.com/Sygmei/11Zip"
    topics = ("zip")
    settings = "os", "compiler", "build_type", "arch"
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile")
    _cmake = None

    def requirements(self):
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))

    def _configure_cmake(self):
        
        # Generate the CMake flags to ensure the UE4-bundled version of zlib is used
        from ue4util import Utility
        zlib = self.deps_cpp_info["zlib"]

        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["ZLIB_INCLUDE_DIR"] = zlib.include_paths[0]
        self._cmake.definitions["ZLIB_LIBRARY"] = Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0])
        if self.settings.os != "Windows":
            self._cmake.definitions["USE_FILESYSTEM_FALLBACK"] = True
        self._cmake.configure(source_dir="11zip")
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    def source(self):
        git = tools.Git(folder="11zip")
        git.clone("https://github.com/Sygmei/11Zip.git")
        if self.settings.os != "Windows":
            git = tools.Git(folder="11zip/include/tinydir")
            git.clone("https://github.com/cxong/tinydir.git")
            tools.replace_path_in_file("11zip/CMakeLists.txt", "target_link_libraries(elzip tinydir)", "add_subdirectory(include/tinydir)")



    def build(self):

        cmake = self._configure_cmake()
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.hpp", dst="include", src="11zip", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

