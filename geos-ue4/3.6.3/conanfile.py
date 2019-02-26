from conans import ConanFile, CMake, tools

class GeosUe4Conan(ConanFile):
    name = "geos-ue4"
    version = "3.6.3"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/adamrehn/ue4-conan-recipes/geos-ue4"
    description = "GEOS custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = ("libcxx/ue4@adamrehn/profile")
    
    def cmake_flags(self):
        return [
            "-DGEOS_BUILD_STATIC=ON",
            "-DGEOS_BUILD_SHARED=OFF",
            "-DGEOS_ENABLE_TESTS=OFF"
        ]
    
    def source(self):
        
        # Clone the source code
        self.run("git clone --progress --depth=1 https://github.com/libgeos/geos -b {}".format(self.version))
        
        # Force geos_c to be built as a static library
        tools.replace_in_file(
            "geos/capi/CMakeLists.txt",
            "geos_c SHARED",
            "geos_c STATIC"
        )
    
    def build(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build GEOS
        with tools.environment_append({"CI": "1"}):
            cmake = CMake(self)
            cmake.configure(source_folder="geos", args=self.cmake_flags())
            cmake.build()
            cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
