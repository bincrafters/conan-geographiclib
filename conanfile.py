from conans import ConanFile, CMake, tools
import os
import shutil


class GeographiclibConan(ConanFile):
    name = "geographiclib"
    version = "1.50"
    description = "Convert geographic units and solve geodesic problems"
    url = "https://github.com/bincrafters/conan-geographiclib"
    homepage = "https://geographiclib.sourceforge.io"
    license = "MIT"
    exports = ["LICENSE.txt"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            self.options.remove("fPIC")

    def source(self):
        source_url = "https://sourceforge.net/projects/geographiclib/files/distrib"
        name = "GeographicLib"
        filename = "{0}-{1}.tar.gz".format(self.name, self.version)
        tools.download("{0}/{1}-{2}.tar.gz".format(source_url, name, self.version), filename=filename)
        tools.unzip(filename)
        extracted_dir = name + '-' + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['GEOGRAPHICLIB_LIB_TYPE'] = 'SHARED' if self.options.shared else 'STATIC'
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        # it does not work on Windows but is not needed
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "add_subdirectory (js)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # there is no option to disable subdirectories
        for folder in ["share", os.path.join("lib", "python"), "sbin", "python", "matlab", "doc"]:
            shutil.rmtree(os.path.join(self.package_folder, folder), ignore_errors=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append('GEOGRAPHICLIB_SHARED_LIB={}'.format("1" if self.options.shared else "0"))
