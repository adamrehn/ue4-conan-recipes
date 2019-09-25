cmake_minimum_required(VERSION 3.8)
project(PlayFab_GSDK)

# Allow users to configure whether we build a shared library or a static library
option(BUILD_SHARED_LIBS "Build the SDK as a shared library instead of a static library" OFF)

# Set the C++ standard to C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Locate curl and OpenSSL
find_package(CURL REQUIRED)
find_package(OpenSSL REQUIRED)

# Configure our preprocessor definitions and header search directories
add_definitions(-DGSDK_LINUX)
include_directories(cppsdk)
include_directories(cppsdk/include)
include_directories(${CURL_INCLUDE_DIRS} SYSTEM)

# Build the SDK
add_library(GSDK_CPP_Linux
	cppsdk/jsoncpp.cpp
	cppsdk/gsdk.cpp
	cppsdk/gsdkConfig.cpp
	cppsdk/gsdkLog.cpp
	cppsdk/gsdkUtils.cpp
	cppsdk/ManualResetEvent.cpp
	cppsdk/source/playfab/PlayFabAdminApi.cpp
	cppsdk/source/playfab/PlayFabClientApi.cpp
	cppsdk/source/playfab/PlayFabEntityApi.cpp
	cppsdk/source/playfab/PlayFabError.cpp
	cppsdk/source/playfab/PlayFabHttp.cpp
	cppsdk/source/playfab/PlayFabMatchmakerApi.cpp
	cppsdk/source/playfab/PlayFabServerApi.cpp
	cppsdk/source/playfab/PlayFabSettings.cpp
)

# Link against curl, OpenSSL and pthreads
target_link_libraries(GSDK_CPP_Linux
	${CURL_LIBRARIES}
	OpenSSL::SSL
	OpenSSL::Crypto
	pthread
)

# Installation rules
install(DIRECTORY cppsdk/include/playfab/ DESTINATION include/playfab FILES_MATCHING PATTERN "*.h")
install(DIRECTORY cppsdk/json/ DESTINATION include/json FILES_MATCHING PATTERN "*.h")
install(FILES
	cppsdk/gsdk.h
	cppsdk/gsdkConfig.h
	cppsdk/gsdkInternal.h
	cppsdk/gsdkLog.h
	cppsdk/gsdkUtils.h
	cppsdk/gsdkCommonPch.h
	cppsdk/gsdkLinuxPch.h
	cppsdk/ManualResetEvent.h
	DESTINATION include
)
install(
	TARGETS GSDK_CPP_Linux
	ARCHIVE DESTINATION lib
	LIBRARY DESTINATION lib
)
