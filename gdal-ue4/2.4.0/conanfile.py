from conans import AutoToolsBuildEnvironment, ConanFile, tools

class GdalUe4Conan(ConanFile):
    name = "gdal-ue4"
    version = "2.4.0"
    license = "MIT"
    url = "https://github.com/adamrehn/ue4-conan-recipes/gdal-ue4"
    description = "GDAL custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def requirements(self):
        self.requires("geos-ue4/3.6.3@adamrehn/{}".format(self.channel))
        self.requires("proj-ue4/4.9.3@adamrehn/{}".format(self.channel))
        self.requires("UElibPNG/ue4@adamrehn/{}".format(self.channel))
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
    
    def configure_flags(self):
        
        # Determine the absolute path to `geos-config`
        from ue4util import Utility
        geos = self.deps_cpp_info["geos-ue4"]
        geosConfig = Utility.resolve_file(geos.bin_paths[0], "geos-config")
        
        return [
            "--prefix=" + self.package_folder,
            "--enable-static",
            "--disable-shared",
            "--without-libtool",
            "--enable-pdf-plugin=no",
            "--without-ld-shared",
            "--with-threads=yes",
            "--with-libz={}".format(self.deps_cpp_info["zlib"].rootpath),
            "--without-liblzma",
            "--without-libiconv-prefix",
            "--without-pg",
            "--without-grass",
            "--without-libgrass",
            "--without-cfitsio",
            "--without-pcraster",
            "--with-png={}".format(self.deps_cpp_info["UElibPNG"].rootpath),
            "--without-mrf",
            "--without-dds",
            "--without-gta",
            "--with-libtiff=internal",
            "--with-geotiff=internal",
            "--with-jpeg=internal",
            "--with-rename_internal_libtiff_symbols",
            "--with-rename_internal_libgeotiff_symbols",
            "--without-jpeg12",
            "--without-gif",
            "--without-ogdi",
            "--without-fme",
            "--without-sosi",
            "--without-mongocxx",
            "--without-hdf4",
            "--without-hdf5",
            "--without-kea",
            "--without-netcdf",
            "--without-jasper",
            "--without-openjpeg",
            "--without-fgdb",
            "--without-ecw",
            "--without-kakadu",
            "--without-mrsid",
            "--without-jp2mrsid",
            "--without-mrsid_lidar",
            "--without-msg",
            "--without-bsb",
            "--without-oci",
            "--without-oci-include",
            "--without-oci-lib",
            "--without-grib",
            "--without-mysql",
            "--without-ingres",
            "--without-xerces",
            "--without-expat",
            "--without-libkml",
            "--without-odbc",
            "--with-dods-root=no",
            "--without-curl",
            "--without-xml2",
            "--without-spatialite",
            "--without-sqlite3",
            "--without-pcre",
            "--without-idb",
            "--without-sde",
            "--without-epsilon",
            "--without-webp",
            "--without-qhull",
            "--with-freexl=no",
            "--with-libjson-c=internal",
            "--without-pam",
            "--without-poppler",
            "--without-podofo",
            "--without-pdfium",
            "--without-perl",
            "--without-python",
            "--without-java",
            "--without-mdb",
            "--without-rasdaman",
            "--without-armadillo",
            "--without-cryptopp",
            "--with-proj=yes",
            "--with-geos={}".format(geosConfig)
        ]
    
    def source(self):
        self.run("git clone --progress --depth=1 https://github.com/OSGeo/gdal.git -b v{}".format(self.version))
    
    def build(self):
        
        # Build GDAL using Visual Studio under Windows and autotools under other platforms
        with tools.chdir("./gdal/gdal"):
            if self.settings.os == "Windows":
                self.build_windows()
            else:
                self.build_unix()
    
    def build_windows(self):
        
        # TODO
        raise NotImplementedError
    
    def build_unix(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Run autogen.sh
        self.run("./autogen.sh")
        
        # Patch out iconv support under Linux, since the UE4 bundled toolchain doesn't include it
        if self.settings.os == "Linux":
            tools.replace_in_file("./configure", "iconv.h", "iconv_h")
        
        # Under Linux, the UE4-bundled version of zlib is typically named libz_fPIC.a, but GDAL expects libz.a
        zlibName = self.deps_cpp_info["zlib"].libs[0]
        if zlibName != "z":
            tools.replace_in_file("./configure", "-lz", "-l{}".format(zlibName))
        
        # Prepare the autotools build environment
        autotools = AutoToolsBuildEnvironment(self)
        LibCxx.fix_autotools(autotools)
        
        # Build using autotools
        autotools.configure(args=self.configure_flags())
        autotools.make(args=["-j1"])
        autotools.make(target="install")
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
