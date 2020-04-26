Conan recipes for UE4-compatible library packages
=================================================

This repository contains Conan recipes for a variety of libraries to facilitate their use with Unreal Engine 4. The recipes make use of the infrastructure from [conan-ue4cli](https://github.com/adamrehn/conan-ue4cli) to provide compatibility with UE4-bundled third-party libraries and avoid symbol interposition issues, as well as ensuring everything is built against the UE4-bundled version of libc++ under Linux.

To build the packages, you will need the following:

- Unreal Engine 4.19.0 or newer
- Python 3.5 or newer
- [ue4cli](https://github.com/adamrehn/ue4cli) and [conan-ue4cli](https://github.com/adamrehn/conan-ue4cli)

Starting from conan-ue4cli version 0.0.8, the recipes from this repository are automatically stored in the conan-ue4cli recipe cache and are available by default when building packages (unless the `--no-cache` flag is specified.)

To build all of the packages, run the following command (either from the root directory of this repository for conan-ue4cli version 0.0.7 and older, or any directory under newer versions of conan-ue4cli):

```
ue4 conan build all
```

(Note that if you attempt to run the above command from the root directory of this repository using newer versions of conan-ue4cli you will get a [recipe conflict](https://github.com/adamrehn/ue4-conan-recipes/issues/2), since cloning this repository is no longer necessary unless you are contributing to the development of its recipes. Users should run the command from another directory as per the instructions above, whilst contributors should specify the `--no-cache` flag to ensure your modified recipes are used instead of the current upstream versions.)

Alternatively, you can specify a list of individual packages (with optional version numbers), like so:

```
ue4 conan build PACKAGE1 PACKAGE2==1.2.3 PACKAGE3
```

See the output of `ue4 conan build --help` for full usage details.

It is recommended that you build the packages from this repository inside the `ue4-full` Docker image from [ue4-docker](https://github.com/adamrehn/ue4-docker) and then upload the built packages to a Conan remote so that they can be pulled from there for further use.


## Legal

All of the recipe code and associated build infrastructure in this repository is licensed under the MIT License, see the file [LICENSE](./LICENSE) for details. See the individual Conan recipes for the license details of the libraries that they build.

Development of the Python 3.6.8 recipe was funded by [Deepdrive, Inc](https://deepdrive.io/).
