# See: https://github.com/Rickodesea/Cmake-Extensions
#
# CxFileCopy - Copy a single file with target association
#
# Usage:
#   CxFileCopy(<target>
#       INPUT <src-file>
#       OUTPUT <dst-file>
#       [COMMENT <message>]
#   )
#
# Parameters:
#   target  - Target to associate the copy operation with
#   INPUT   - Source file to copy
#   OUTPUT  - Destination path for the copy
#   COMMENT - Optional custom comment message

#####################################
## Internal helper functions
#####################################

function(CxInternalGetRelPath path out_var)
  string(REGEX MATCH "\\$<.*>" is_gen "${path}")
  if(is_gen)
    set(${out_var} "${path}" PARENT_SCOPE)
  else()
    file(RELATIVE_PATH result "${CMAKE_SOURCE_DIR}" "${path}")
    set(${out_var} "${result}" PARENT_SCOPE)
  endif()
endfunction()

#####################################
## Main function
#####################################

function(CxFileCopy target)
    set(req_params INPUT OUTPUT)
    set(single_values ${req_params} COMMENT)  # COMMENT must be in single_values
    set(opt_params)  # Empty since COMMENT is in single_values
    set(multi_values)
    set(options)

    cmake_parse_arguments(
        parsed
        "${options}"
        "${single_values}"
        "${multi_values}"
        ${ARGN}
    )

    foreach(param IN LISTS req_params)
        if(NOT parsed_${param})
            message(FATAL_ERROR "CxFileCopy: Missing required keyword: ${param}")
        endif()
    endforeach()

    set(src ${parsed_INPUT})
    set(dst ${parsed_OUTPUT})

    CxInternalGetRelPath("${src}" display_input)
    CxInternalGetRelPath("${dst}" display_output)

    set(comment_text "CxFileCopy(${target}): Copying ${display_input} to ${display_output}")
    if(DEFINED parsed_COMMENT AND NOT "${parsed_COMMENT}" STREQUAL "")
        set(comment_text "${parsed_COMMENT}")
    endif()

    add_custom_command(
        TARGET ${target} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "${src}" "${dst}"
        COMMENT "${comment_text}"
    )
endfunction()