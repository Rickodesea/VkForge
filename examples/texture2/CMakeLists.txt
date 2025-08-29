cmake_minimum_required(VERSION 3.14)

project(TRIANGLE
    VERSION 0.1.0
    DESCRIPTION "VKFORGE DEMONSTRATION"
    LANGUAGES C
)

add_executable(main main.c)
add_subdirectory(VkForge) # bash.sh first
target_link_libraries(main PRIVATE vkforge)

include(CxFileCopy.cmake)

CxFileCopy(main
    INPUT $<TARGET_FILE:vkforge>
    OUTPUT ${CMAKE_BINARY_DIR}/$<TARGET_FILE_NAME:vkforge>
    COMMENT "Copying vkforge lib to build dir"
)

