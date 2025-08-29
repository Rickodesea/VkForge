#pragma once

#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>

#include "vkforge_typedecls.h"

#ifdef __cplusplus
extern "C" {
#endif

// Function Declarations

VkPipeline VkForge_CreatePipelineForDefault(VkAllocationCallbacks* allocator,
    void* next,
    VkDevice device,
    VkPipelineLayout pipeline_layout);



#ifdef __cplusplus
}
#endif
