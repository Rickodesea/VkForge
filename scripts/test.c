#include <vulkan/vulkan.h>
#include "../examples/texture2/VkForge/vkforge_typedecls.h"
#include "../examples/texture2/VkForge/vkforge_funcdecls.h"
#include "../examples/texture2/VkForge/vkforge_layout.c"

/** TYPE DEFINITIONS **/
typedef struct VkForgePipelineLayout VkForgePipelineLayout;
typedef struct VkForgePipeline       VkForgePipeline;

struct VkForgePipelineLayout
{
    VkPipelineLayout                   pipelineLayout;
    VkForgeLayoutPipelineLayoutDesign* design;
    uint32_t                           pipeline_layout_index;
    uint8_t                            descriptor_set_count;
    VkDescriptorSetLayout              descriptor_set_layouts[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
    VkDescriptorSet                    descriptor_sets[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
    VkDescriptorPool                   descriptor_pool;
};

struct VkForgePipeline
{
    VkPipeline pipeline;
    uint32_t   pipeline_index;
};

struct VkForgeLayout
{
    VkSurfaceKHR          surface;
    VkPhysicalDevice      physical_device;
    VkDevice              device;
    
    // Descriptor Resources (temporary queue for writing)
    VkForgeDescriptorResourceQueue descriptor_resource_queue[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
    VkWriteDescriptorSet           write_descriptor_set     [VKFORGE_MAX_DESCRIPTOR_RESOURCES];
    uint32_t                       descriptor_resource_queue_count;
};


// Function declarations for the new API
VkForgePipelineLayout VkForge_CreateForgePipelineLayout      (VkForgeLayout* forgeLayout, const char* pipelineName);
void                  VkForge_DestroyForgePipelineLayout     (VkForgeLayout* forgeLayout, VkForgePipelineLayout* pipelineLayout);
bool                  VkForge_IsForgePipelineLayoutCompatible(VkForgeLayout* forgeLayout, const char* pipelineName, VkForgePipelineLayout forgePipelineLayout);
VkForgePipeline       VkForge_CreateForgePipeline            (VkForgeLayout* forgeLayout, const char* pipelineName, VkForgePipelineLayout compatibleForgePipelineLayout);
void                  VkForge_DestroyForgePipeline           (VkForgeLayout* forgeLayout, VkForgePipeline* pipeline);

#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>


/** FUNCTION IMPLEMENTATIONS **/

VkForgeLayout* VkForge_CreateForgeLayout(VkSurfaceKHR surface, VkPhysicalDevice physical_device, VkDevice device)
{
    assert(device);

    VkForgeLayout* layout = (VkForgeLayout*)SDL_malloc(sizeof(VkForgeLayout));
    if (!layout)
    {
        SDL_LogError(0, "Failed to allocate memory for VkForgeLayout");
        exit(1);
    }

    // Initialize all counts to 0
    SDL_memset(layout, 0, sizeof(VkForgeLayout));

    layout->surface = surface;
    layout->physical_device = physical_device;
    layout->device = device;
    return layout;
}

void VkForge_DestroyForgeLayout(VkForgeLayout* forgeLayout)
{
    if (forgeLayout)
    {
        SDL_free(forgeLayout);
    }
}

VkForgePipelineLayout VkForge_CreateForgePipelineLayout(
    VkForgeLayout* forgeLayout, 
    const char*    pipelineName
)
{
    assert(forgeLayout);
    assert(pipelineName);
    
    VkForgePipelineLayout result = {0};
    
    // Find the pipeline layout index in the global design
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipelineName);
    if (pipeline_layout_index == UINT32_MAX)
    {
        SDL_LogError(0, "Pipeline layout not found for %s", pipelineName);
        exit(1);
    }
    
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
        VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];
    
    // Create descriptor set layouts
    result.descriptor_set_count = pipeline_design->descriptorset_layout_design_count;
    for (uint32_t i = 0; i < result.descriptor_set_count; i++)
    {
        const VkForgeLayoutDescriptorSetLayoutDesign* set_design = 
            pipeline_design->descriptorset_layout_design_buffer[i];
        
        VkResult vkResult = CreateDescriptorSetLayout(forgeLayout->device, set_design, 
                                                    &result.descriptor_set_layouts[i]);
        if (vkResult != VK_SUCCESS)
        {
            SDL_LogError(0, "Failed to create descriptor set layout for set %u", i);
            // Clean up already created layouts
            for (uint32_t j = 0; j < i; j++)
            {
                vkDestroyDescriptorSetLayout(forgeLayout->device, result.descriptor_set_layouts[j], NULL);
            }
            exit(1);
        }
    }
    
    // Create pipeline layout
    VkPipelineLayoutCreateInfo layoutInfo = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .setLayoutCount = result.descriptor_set_count,
        .pSetLayouts = result.descriptor_set_layouts,
        .pushConstantRangeCount = 0,
        .pPushConstantRanges = NULL
    };
    
    VkResult vkResult = vkCreatePipelineLayout(forgeLayout->device, &layoutInfo, NULL, &result.pipelineLayout);
    if (vkResult != VK_SUCCESS)
    {
        SDL_LogError(0, "Failed to create pipeline layout");
        for (uint32_t i = 0; i < result.descriptor_set_count; i++)
        {
            vkDestroyDescriptorSetLayout(forgeLayout->device, result.descriptor_set_layouts[i], NULL);
        }
        exit(1);
    }
    
    // Create descriptor pool and allocate descriptor sets
    uint32_t             pool_sizes_count = 0;
    VkDescriptorPoolSize pool_sizes[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {0};
    
    GetDescriptorPoolRequirements(
        pipeline_design,
        pipeline_layout_index,
        &pool_sizes_count,
        pool_sizes
    );
    
    result.descriptor_pool = VkForge_CreateDescriptorPool(
        forgeLayout->device,
        result.descriptor_set_count,
        pool_sizes_count,
        pool_sizes
    );
    
    VkForge_AllocateDescriptorSet(
        forgeLayout->device,
        result.descriptor_pool,
        result.descriptor_set_count,
        result.descriptor_set_layouts,
        result.descriptor_sets
    );
    
    result.design = (VkForgeLayoutPipelineLayoutDesign*)pipeline_design;
    result.pipeline_layout_index = pipeline_layout_index;
    
    return result;
}

void VkForge_DestroyForgePipelineLayout(VkForgeLayout* forgeLayout, VkForgePipelineLayout* pipelineLayout)
{
    assert(forgeLayout);
    assert(pipelineLayout);
    
    if (pipelineLayout->pipelineLayout != VK_NULL_HANDLE)
    {
        vkDestroyPipelineLayout(forgeLayout->device, pipelineLayout->pipelineLayout, NULL);
        pipelineLayout->pipelineLayout = VK_NULL_HANDLE;
    }
    
    for (uint32_t i = 0; i < pipelineLayout->descriptor_set_count; i++)
    {
        if (pipelineLayout->descriptor_set_layouts[i] != VK_NULL_HANDLE)
        {
            vkDestroyDescriptorSetLayout(forgeLayout->device, pipelineLayout->descriptor_set_layouts[i], NULL);
            pipelineLayout->descriptor_set_layouts[i] = VK_NULL_HANDLE;
        }
    }
    
    if (pipelineLayout->descriptor_pool != VK_NULL_HANDLE)
    {
        vkDestroyDescriptorPool(forgeLayout->device, pipelineLayout->descriptor_pool, NULL);
        pipelineLayout->descriptor_pool = VK_NULL_HANDLE;
    }
    
    pipelineLayout->descriptor_set_count = 0;
}

bool VkForge_IsForgePipelineLayoutCompatible(
    VkForgeLayout* forgeLayout, 
    const char* pipelineName,
    VkForgePipelineLayout forgePipelineLayout
)
{
    assert(forgeLayout);
    assert(pipelineName);
    
    // Find the expected pipeline layout index
    uint32_t expected_layout_index = FindPipelineLayoutIndex(pipelineName);
    if (expected_layout_index == UINT32_MAX)
    {
        SDL_LogError(0, "Pipeline layout not found for %s", pipelineName);
        exit(1);
    }
    
    // Compare layout indices for compatibility
    return (forgePipelineLayout.pipeline_layout_index == expected_layout_index);
}

VkForgePipeline VkForge_CreateForgePipeline(
    VkForgeLayout*        forgeLayout, 
    const char*           pipelineName,
    VkForgePipelineLayout compatibleForgePipelineLayout
)
{
    assert(forgeLayout);
    assert(pipelineName);
    
    VkForgePipeline result = {0};
    
    // Verify compatibility first
    if (!VkForge_IsForgePipelineLayoutCompatible(forgeLayout, pipelineName, compatibleForgePipelineLayout))
    {
        SDL_LogError(0, "Pipeline layout is not compatible with pipeline %s", pipelineName);
        exit(1);
    }
    
    // Find the pipeline function
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipelineName);
    if (!pipeline_func)
    {
        SDL_LogError(0, "Pipeline creation function not found for %s", pipelineName);
        exit(1);
    }
    
    /// DYNAMIC RENDERING REQUIRED STRUCTURE ///
    VkSurfaceFormatKHR surfaceFormat = VkForge_GetSurfaceFormat(
        forgeLayout->surface,
        forgeLayout->physical_device,
        VKFORGE_DEFAULT_FORMAT
    );
    
    VkPipelineRenderingCreateInfo renderingInfo = {0};
    renderingInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO;
    renderingInfo.viewMask = 0;
    renderingInfo.colorAttachmentCount = 1;
    renderingInfo.pColorAttachmentFormats = &surfaceFormat.format;
    
    ///*************************************///
    
    // Create the pipeline
    VkPipeline pipeline = pipeline_func->CreatePipelineForFunc(
        NULL, // allocator
        &renderingInfo, // next Vulkan 1.3 dynamic rendering
        forgeLayout->device,
        compatibleForgePipelineLayout.pipelineLayout
    );
    
    if (pipeline == VK_NULL_HANDLE)
    {
        SDL_LogError(0, "Failed to create pipeline %s", pipelineName);
        exit(1);
    }
    
    result.pipeline = pipeline;
    result.pipeline_index = pipeline_func->pipeline_index;
    
    return result;
}

void VkForge_DestroyForgePipeline(VkForgeLayout* forgeLayout, VkForgePipeline* pipeline)
{
    assert(forgeLayout);
    assert(pipeline);
    
    if (pipeline->pipeline != VK_NULL_HANDLE)
    {
        vkDestroyPipeline(forgeLayout->device, pipeline->pipeline, NULL);
        pipeline->pipeline = VK_NULL_HANDLE;
    }
}

// Updated helper function for pool requirements
static void GetDescriptorPoolRequirements(
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design,
    uint32_t*                                outDescriptorPoolSizeCount,
    VkDescriptorPoolSize*                    outDescriptorPoolSizes
)
{
    if(!outDescriptorPoolSizeCount && !outDescriptorPoolSizes) return;

    uint32_t pool_size_count = 0;
    VkDescriptorPoolSize temp_pool_sizes[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {0};

    // Calculate required pool sizes
    for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
    {
        const VkForgeLayoutDescriptorSetLayoutDesign* set_design =
            pipeline_design->descriptorset_layout_design_buffer[i];

        if (!set_design) continue;

        for (uint32_t j = 0; j < set_design->bind_design_count; j++)
        {
            const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
            if (!bind) continue;

            bool found = false;
            for (uint32_t k = 0; k < pool_size_count; k++)
            {
                if (temp_pool_sizes[k].type == bind->type)
                {
                    temp_pool_sizes[k].descriptorCount += bind->count;
                    found = true;
                    break;
                }
            }

            if (!found)
            {
                temp_pool_sizes[pool_size_count].type = bind->type;
                temp_pool_sizes[pool_size_count].descriptorCount = bind->count;
                pool_size_count++;
            }
        }
    }

    // Return the count if requested
    if (outDescriptorPoolSizeCount)
    {
        *outDescriptorPoolSizeCount = pool_size_count;
    }

    // Return the actual pool sizes if requested
    if (outDescriptorPoolSizes)
    {
        for (uint32_t i = 0; i < pool_size_count; i++)
        {
            outDescriptorPoolSizes[i] = temp_pool_sizes[i];
        }
    }
}

// REMOVED FUNCTIONS:
// - VkForge_BuildPipeline
// - VkForge_BindPipeline
// - VkForge_BorrowPipeline
// - VkForge_SharePipelineLayoutDetails
// - The old CreatePipelineLayout function

// The following functions remain but now operate on VkForgePipelineLayout:
// - VkForge_QueueDescriptorResource (needs to be updated to accept VkForgePipelineLayout*)
// - VkForge_WriteDescriptorResources (needs to be updated)
// - VkForge_ClearDescriptorResourceQueue

/**
 * @brief Queues a descriptor resource for a specific pipeline layout
 * @param layout The VkForge layout instance
 * @param pipelineLayout The pipeline layout to queue the resource for
 * @param set The descriptor set index
 * @param binding The binding index within the set
 * @param resource The descriptor resource (image or buffer)
 */
void VkForge_QueueDescriptorResourceForForgePipelineLayout(
    VkForgeLayout* layout,
    VkForgePipelineLayout* pipelineLayout,
    uint16_t set,
    uint16_t binding,
    VkForgeDescriptorResource resource
)
{
    assert(layout);
    assert(pipelineLayout);

    if (set >= pipelineLayout->descriptor_set_count)
    {
        SDL_LogError(0, "Set %u out of bounds for pipeline layout (max: %u)", set, pipelineLayout->descriptor_set_count);
        exit(1);
    }

    // Get the pipeline layout design
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design = pipelineLayout->design;
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design =
        pipeline_design->descriptorset_layout_design_buffer[set];

    if (binding >= set_design->bind_design_count)
    {
        SDL_LogError(0, "Binding %u out of bounds for set %u", binding, set);
        exit(1);
    }

    const VkForgeLayoutBindDesign* bind_design = set_design->bind_design_buffer[binding];
    VkDescriptorType expected_type = bind_design->type;

    // Validate resource based on descriptor type
    if (VkForge_IsDescriptorTypeImage(expected_type))
    {
        // Validate image resource
        if (resource.image.imageView == VK_NULL_HANDLE)
        {
            SDL_LogError(0, "ImageView cannot be null for image descriptor type");
            exit(1);
        }
        if ((expected_type == VK_DESCRIPTOR_TYPE_SAMPLER ||
             expected_type == VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER) &&
            resource.image.sampler == VK_NULL_HANDLE)
        {
            SDL_LogError(0, "Sampler cannot be null for descriptor type %d", expected_type);
            exit(1);
        }
    }
    else if (VkForge_IsDescriptorTypeBuffer(expected_type))
    {
        // Validate buffer resource
        if (resource.buffer.buffer == VK_NULL_HANDLE)
        {
            SDL_LogError(0, "Buffer cannot be null for buffer descriptor type");
            exit(1);
        }
    }
    else
    {
        SDL_LogError(0, "Unsupported descriptor type: %d", expected_type);
        exit(1);
    }

    uint32_t already_queued_count = layout->descriptor_resource_queue_count;

    if(already_queued_count)
    {
        // Check if this set/binding is already queued for the same pipeline layout
        for (uint32_t i = 0; i < already_queued_count; i++)
        {
            if (layout->descriptor_resource_queue[i].set == set &&
                layout->descriptor_resource_queue[i].binding == binding &&
                layout->descriptor_resource_queue[i].pipeline_layout_index == pipelineLayout->pipeline_layout_index)
            {
                // Check if resource handles are different
                bool needs_update = false;

                if (VkForge_IsDescriptorTypeImage(expected_type))
                {
                    needs_update = (layout->descriptor_resource_queue[i].resource.image.imageView != resource.image.imageView ||
                                layout->descriptor_resource_queue[i].resource.image.sampler != resource.image.sampler ||
                                layout->descriptor_resource_queue[i].resource.image.imageLayout != resource.image.imageLayout);
                }
                else if (VkForge_IsDescriptorTypeBuffer(expected_type))
                {
                    needs_update = (layout->descriptor_resource_queue[i].resource.buffer.buffer != resource.buffer.buffer ||
                                layout->descriptor_resource_queue[i].resource.buffer.offset != resource.buffer.offset ||
                                layout->descriptor_resource_queue[i].resource.buffer.range != resource.buffer.range);
                }

                if (needs_update)
                {
                    // Update Resource
                    layout->descriptor_resource_queue[i].resource = resource;

                    SDL_Log("Queued Updated Resource for set %u binding %u", set, binding);
                }
                return;
            }
        }
    }

    // Check if queue is full
    if (layout->descriptor_resource_queue_count >= VKFORGE_MAX_DESCRIPTOR_RESOURCES)
    {
        SDL_LogError(0, "Descriptor Resource Queue is full: %d Max", VKFORGE_MAX_DESCRIPTOR_RESOURCES);
        exit(1);
    }

    // Add new entry to queue
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].resource = resource;
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].set = set;
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].binding = binding;
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].pipeline_layout_index = pipelineLayout->pipeline_layout_index;
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].type = expected_type;
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].count = bind_design->count;

    SDL_Log("Queued Resource for set %u binding %u", set, binding);

    layout->descriptor_resource_queue_count++;
}

/**
 * @brief Writes all queued descriptor resources to their respective descriptor sets
 * @param layout The VkForge layout instance containing the descriptor queue
 * @param pipelineLayout The pipeline layout to write descriptors for
 */
void VkForge_WriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(VkForgeLayout* layout, VkForgePipelineLayout* pipelineLayout)
{
    assert(layout);
    assert(pipelineLayout);

    if (layout->descriptor_resource_queue_count == 0)
    {
        return;
    }

    uint32_t write_count = 0;
    VkWriteDescriptorSet writes[VKFORGE_MAX_DESCRIPTOR_RESOURCES] = {0};

    // For each queued resource that belongs to this pipeline layout
    for (uint32_t i = 0; i < layout->descriptor_resource_queue_count; i++)
    {
        VkForgeDescriptorResourceQueue* entry = &layout->descriptor_resource_queue[i];
        
        // Only process entries for this specific pipeline layout
        if (entry->pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {
            continue;
        }

        if (entry->set >= pipelineLayout->descriptor_set_count)
        {
            SDL_LogError(0, "Set %u out of bounds for pipeline layout", entry->set);
            exit(1);
        }

        VkDescriptorSet descriptorset = pipelineLayout->descriptor_sets[entry->set];

        if (descriptorset == VK_NULL_HANDLE)
        {
            SDL_LogError(0, "Descriptor set not found for set %u", entry->set);
            exit(1);
        }

        // Prepare the write descriptor
        writes[write_count] = (VkWriteDescriptorSet){
            .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
            .dstSet = descriptorset,
            .dstBinding = entry->binding,
            .descriptorCount = entry->count,
            .descriptorType = entry->type,
        };

        // Set the appropriate descriptor info
        if (VkForge_IsDescriptorTypeImage(entry->type))
        {
            writes[write_count].pImageInfo = &entry->resource.image;
        }
        else if (VkForge_IsDescriptorTypeBuffer(entry->type))
        {
            writes[write_count].pBufferInfo = &entry->resource.buffer;
        }

        SDL_Log("Preparing to Write Resource for set %u binding %u", entry->set, entry->binding);
        write_count++;
    }

    if (write_count > 0)
    {
        // Update all descriptor sets
        vkUpdateDescriptorSets(
            layout->device,
            write_count,
            writes,
            0, NULL
        );

        SDL_Log("Wrote %u Resources for pipeline layout", write_count);
    }

    // Remove processed entries from the queue
    uint32_t new_index = 0;
    for (uint32_t i = 0; i < layout->descriptor_resource_queue_count; i++)
    {
        if (layout->descriptor_resource_queue[i].pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {
            // Keep entries for other pipeline layouts
            if (new_index != i)
            {
                layout->descriptor_resource_queue[new_index] = layout->descriptor_resource_queue[i];
            }
            new_index++;
        }
    }
    
    layout->descriptor_resource_queue_count = new_index;
}

/**
 * @brief Clears all queued descriptor resources for a specific pipeline layout
 * @param layout The VkForge layout instance
 * @param pipelineLayout The pipeline layout to clear queue for
 */
void VkForge_ClearDescriptorResourceQueueForForgePipelineLayout(VkForgeLayout* layout, VkForgePipelineLayout* pipelineLayout)
{
    assert(layout);
    assert(pipelineLayout);

    uint32_t new_index = 0;
    for (uint32_t i = 0; i < layout->descriptor_resource_queue_count; i++)
    {
        if (layout->descriptor_resource_queue[i].pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {
            // Keep entries for other pipeline layouts
            if (new_index != i)
            {
                layout->descriptor_resource_queue[new_index] = layout->descriptor_resource_queue[i];
            }
            new_index++;
        }
    }
    
    layout->descriptor_resource_queue_count = new_index;
}

/**
 * @brief Clears all queued descriptor resources
 * @param layout The VkForge layout instance
 */
void VkForge_ClearDescriptorResourceQueue(VkForgeLayout* layout)
{
    assert(layout);
    layout->descriptor_resource_queue_count = 0;
}

void VkForge_BindForgePipelineLayoutPerWriteDescriptorResourceQueue(){}