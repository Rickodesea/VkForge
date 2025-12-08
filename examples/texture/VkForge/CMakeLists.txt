cmake_minimum_required(VERSION 3.14)

project(VKFORGE
    VERSION 0.5.0
    DESCRIPTION "Vulkan User-End API Implementation Generator"
    LANGUAGES C
)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED TRUE)

add_compile_definitions(
    $<$<CONFIG:Debug>:DEBUG=1>
    $<$<CONFIG:Release>:NDEBUG=1>
)

add_library(vkforge_deps INTERFACE)

# SDL3 Configuration
find_package(SDL3 REQUIRED)
target_link_libraries(vkforge_deps INTERFACE SDL3::SDL3)

# if SDL3_image CMAKE find doesn't work so you need to copy the libary into your app directory
find_package(SDL3_image REQUIRED)
target_link_libraries(vkforge_deps INTERFACE SDL3_image::SDL3_image)

# Vulkan Configuration
find_package(Vulkan 1.3 REQUIRED)
target_link_libraries(vkforge_deps INTERFACE Vulkan::Vulkan)

add_library(vkforge SHARED
    vkforge_core.c
	vkforge_funcdecls.h
	vkforge_layout.c
	vkforge_layout.h
	vkforge_pipelines.c
	vkforge_pipelines.h
	vkforge_typedecls.h
	vkforge_utils.c
)

target_link_libraries(vkforge PUBLIC vkforge_deps)
