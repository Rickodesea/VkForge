#pragma once

#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>

#include "vkforge_typedecls.h"

#ifdef __cplusplus
extern "C" {
#endif

/** DEFINES **/
#define VKFORGE_MAX_DESCRIPTOR_RESOURCES VKFORGE_MAX_DESCRIPTOR_BINDINGS

    /** Main Types **/
    typedef struct VkForgeLayout VkForgeLayout;
    typedef struct VkForgePipelineLayout VkForgePipelineLayout;
    typedef struct VkForgePipeline VkForgePipeline;
    typedef struct VkForgeLayoutQueue VkForgeLayoutQueue;

    // Extern Types
    typedef struct VkForgeLayoutPipelineLayoutDesign VkForgeLayoutPipelineLayoutDesign;

    // Other Types
    typedef struct VkForgeDescriptorResourceQueue VkForgeDescriptorResourceQueue;

    struct VkForgeDescriptorResourceQueue
    {
        VkForgeDescriptorResource resource;
        uint16_t set;
        uint16_t binding;
        uint16_t pipeline_layout_index;
        VkDescriptorType type;
        uint16_t count;
        const char *logname;
    };

    struct VkForgeLayout
    {
        VkSurfaceKHR surface;
        VkPhysicalDevice physical_device;
        VkDevice device;
    };

    struct VkForgeLayoutQueue
    {
        VkForgeDescriptorResourceQueue descriptor_resource_queue[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
        VkWriteDescriptorSet write_descriptor_set[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
        uint32_t descriptor_resource_queue_count;
    };

    struct VkForgePipelineLayout
    {
        VkPipelineLayout pipelineLayout;
        VkForgeLayoutPipelineLayoutDesign *design;
        uint32_t pipeline_layout_index;
        uint8_t descriptor_set_count;
        VkDescriptorSetLayout descriptor_set_layouts[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
        VkDescriptorSet descriptor_sets[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
        VkDescriptorPool descriptor_pool;
    };

    struct VkForgePipeline
    {
        VkPipeline pipeline;
        uint32_t pipeline_index;
    };

    /** API **/
    // Layout management
    VkForgeLayout *VkForge_CreateForgeLayout(VkSurfaceKHR surface, VkPhysicalDevice physical_device, VkDevice device);
    void VkForge_DestroyForgeLayout(VkForgeLayout *forgeLayout);

    // Layout queue management
    VkForgeLayoutQueue *VkForge_CreateForgeLayoutQueue(void);
    void VkForge_DestroyForgeLayoutQueue(VkForgeLayoutQueue *queue);

    // Pipeline layout management
    VkForgePipelineLayout VkForge_CreateForgePipelineLayout(VkForgeLayout *forgeLayout, const char *pipelineName);
    void VkForge_DestroyForgePipelineLayout(VkForgeLayout *forgeLayout, VkForgePipelineLayout *pipelineLayout);
    bool VkForge_IsForgePipelineLayoutCompatible(VkForgeLayout *forgeLayout, const char *pipelineName, VkForgePipelineLayout forgePipelineLayout);

    // Pipeline management
    VkForgePipeline VkForge_CreateForgePipeline(VkForgeLayout *forgeLayout, const char *pipelineName, VkForgePipelineLayout compatibleForgePipelineLayout);
    void VkForge_DestroyForgePipeline(VkForgeLayout *forgeLayout, VkForgePipeline *pipeline);

    // Descriptor resource queueing
    void VkForge_QueueDescriptorResourceForForgePipelineLayout(
        VkForgeLayoutQueue *queue,
        VkForgePipelineLayout *pipelineLayout,
        uint16_t set,
        uint16_t binding,
        VkForgeDescriptorResource resource);

    // Descriptor writing and binding
    void VkForge_WriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(
        VkForgeLayout *layout,
        VkForgeLayoutQueue *queue,
        VkForgePipelineLayout *pipelineLayout);

    void VkForge_BindForgePipelineLayoutPerWriteDescriptorResourceQueue(
        VkForgeLayout *layout,
        VkForgeLayoutQueue *queue,
        VkForgePipelineLayout *pipelineLayout,
        VkCommandBuffer commandBuffer);

    // Queue clearing
    void VkForge_ClearDescriptorResourceQueueForForgePipelineLayout(
        VkForgeLayoutQueue *queue,
        VkForgePipelineLayout *pipelineLayout);

    void VkForge_ClearDescriptorResourceQueue(VkForgeLayoutQueue *queue);


#ifdef __cplusplus
}
#endif
