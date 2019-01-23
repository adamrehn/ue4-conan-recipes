from conans import AutoToolsBuildEnvironment, ConanFile, tools
import io, os

class PythonUe4Conan(ConanFile):
    name = "python-ue4"
    version = "3.6.8"
    license = "Python-2.0"
    url = "https://github.com/adamrehn/ue4-conan-recipes/python-ue4"
    description = "CPython custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    requires = ("libcxx/ue4@adamrehn/profile")
    
    def requirements(self):
        self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
    
    def _capture(self, command):
        output = io.StringIO()
        self.run(command, output=output)
        return output.getvalue().strip()
    
    def source(self):
        if self.settings.os != "Windows":
            
            # Clone the CPython source code
            self.run("git clone --progress --depth=1 https://github.com/python/cpython.git -b v{}".format(self.version))
            
            # Disable the use of the getrandom() function, since this causes issues when statically linking under Linux
            tools.replace_in_file("cpython/configure", "have_getrandom=yes", "have_getrandom=no")
            
            # Under Linux, the UE4-bundled version of zlib is typically named libz_fPIC.a, but CPython expects libz.a
            zlibName = self.deps_cpp_info["zlib"].libs[0]
            if zlibName != "z":
                tools.replace_in_file("cpython/setup.py", "find_library_file(lib_dirs, 'z')", "find_library_file(lib_dirs, '{}')".format(zlibName))
                tools.replace_in_file("cpython/setup.py", "libraries = ['z']", "libraries = ['{}']".format(zlibName))
            
            # Fix the OpenSSL issues regarding missing zlib symbols that are caused by static linking
            tools.replace_in_file("cpython/setup.py", "libraries = ['ssl', 'crypto']", "libraries = ['ssl', 'crypto', '{}']".format(zlibName))
    
    def build(self):
        if self.settings.os == "Windows":
            
            # TODO: retrieve and incorporate the Python development files so consumers can build native extensions
            
            # Under Windows we simply wrap the official embeddable distribution of CPython
            distributions = {
                "x86_64": {
                    "md5": "73df7cb2f1500ff36d7dbeeac3968711",
                    "suffix": "amd64"
                },
                "x86": {
                    "md5": "60470b4cceba52094121d43cd3f6ce3a",
                    "suffix": "win32"
                }
            }
            
            # Download and extract the appropriate zip file for the build architecture
            details = distributions[str(self.settings.arch)]
            url = "https://www.python.org/ftp/python/{}/python-{}-embed-{}.zip".format(self.version, self.version, details["suffix"])
            tools.get(url, md5=details["md5"], destination=self.package_folder)
            
        else:
            
            # Under Linux, restore CC and CXX if the current Conan profile has overridden them
            from libcxx import LibCxx
            LibCxx.set_vars(self)
            
            # Build CPython from source
            os.chdir("cpython")
            autotools = AutoToolsBuildEnvironment(self)
            LibCxx.fix_autotools(autotools)
            autotools.configure(args=["--disable-shared"])
            autotools.make()
            autotools.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        
        if self.settings.os != "Windows":
            
            # Retrieve the list of required system libraries from the config script
            os.chdir(os.path.join(self.package_folder, "bin"))
            output = self._capture("./python3.6-config --libs")
            libs = [lib.replace("-l", "") for lib in output.split(" ")]
            libs = [lib for lib in libs if lib not in self.cpp_info.libs + self.deps_cpp_info.libs]
            self.cpp_info.libs.extend(libs)
