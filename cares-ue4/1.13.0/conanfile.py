from conans import ConanFile, CMake, tools

class CaresUe4Conan(ConanFile):
    name = "cares-ue4"
    version = "1.13.0"
    license = "MIT"
    url = "https://github.com/adamrehn/ue4-conan-recipes/cares-ue4"
    description = "c-ares custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = ("libcxx/ue4@adamrehn/profile")
    
    def cmake_flags(self):
        return [
            "-DCARES_STATIC=ON",
            "-DCARES_SHARED=OFF",
            "-DCARES_STATIC_PIC=ON"
        ]
    
    def source(self):
        self.run("git clone --progress --depth=1 https://github.com/c-ares/c-ares.git -b cares-{}".format(self.version.replace('.', '_')))
    
    def build(self):
        
        # Under Linux, restore CC and CXX if the current Conan profile has overridden them
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build c-ares
        cmake = CMake(self)
        cmake.configure(source_folder="c-ares", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
