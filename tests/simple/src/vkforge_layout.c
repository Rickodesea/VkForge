#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>

#include "vkforge_typedecls.h"
#include "vkforge_funcdecls.h"
#include "vkforge_pipelines.h"
#include "vkforge_layout.h"

/** NO USER INCLUDES **/
typedef struct {int x; int y} Vertex;



typedef struct VkForgeLayoutBindDesign VkForgeLayoutBindDesign;
struct VkForgeLayoutBindDesign
{
    uint32_t  type;
    uint32_t  count;
    uint32_t  mode_count;
    uint32_t* mode_buffer;
};

typedef struct VkForgeLayoutDescriptorSetLayoutDesign VkForgeLayoutDescriptorSetLayoutDesign;
struct VkForgeLayoutDescriptorSetLayoutDesign
{
    uint32_t bind_design_count;
    VkForgeLayoutBindDesign** bind_design_buffer;
};
    
typedef struct VkForgeLayoutPipelineLayoutDesign VkForgeLayoutPipelineLayoutDesign;
struct VkForgeLayoutPipelineLayoutDesign
{
    uint32_t descriptorset_layout_design_count;
    VkForgeLayoutDescriptorSetLayoutDesign** descriptorset_layout_design_buffer;
};

typedef struct VkForgeLayoutReferenceDesign VkForgeLayoutReferenceDesign;
struct VkForgeLayoutReferenceDesign
{
    uint32_t    pipeline_layout_design_index; 
    const char* pipeline_name;
};

typedef struct VkForgeReferencedLayoutDesign VkForgeReferencedLayoutDesign;
struct VkForgeReferencedLayoutDesign
{
    uint32_t pipeline_layout_design_count;
    VkForgeLayoutPipelineLayoutDesign** pipeline_layout_design_buffer;
    uint32_t reference_count;
    VkForgeLayoutReferenceDesign** reference_buffer;
};

static uint32_t STAGE_UNIT_00[] = { VK_SHADER_STAGE_VERTEX_BIT };
static uint32_t STAGE_UNIT_01[] = { VK_SHADER_STAGE_FRAGMENT_BIT };

#define STAGE_0_0_0 STAGE_UNIT_00
#define STAGE_0_0_1 STAGE_UNIT_00
#define STAGE_0_0_2 STAGE_UNIT_00
#define STAGE_0_0_3 STAGE_UNIT_01
#define STAGE_0_0_4 STAGE_UNIT_01
#define STAGE_0_0_7 STAGE_UNIT_01
#define STAGE_0_0_8 STAGE_UNIT_01
#define STAGE_0_1_1 STAGE_UNIT_00
#define STAGE_0_1_5 STAGE_UNIT_01

static VkForgeLayoutBindDesign BIND_0_0_0 = {
    VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1, 1, STAGE_0_0_0
};
static VkForgeLayoutBindDesign BIND_0_0_1 = {
    VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1, 1, STAGE_0_0_1
};
static VkForgeLayoutBindDesign BIND_0_0_2 = {
    VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 4, 1, STAGE_0_0_2
};
static VkForgeLayoutBindDesign BIND_0_0_3 = {
    VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, 1, 1, STAGE_0_0_3
};
static VkForgeLayoutBindDesign BIND_0_0_4 = {
    VK_DESCRIPTOR_TYPE_SAMPLER, 1, 1, STAGE_0_0_4
};
static VkForgeLayoutBindDesign BIND_0_0_7 = {
    VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, 2, 1, STAGE_0_0_7
};
static VkForgeLayoutBindDesign BIND_0_0_8 = {
    VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, 1, 1, STAGE_0_0_8
};
static VkForgeLayoutBindDesign BIND_0_1_1 = {
    VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1, 1, STAGE_0_1_1
};
static VkForgeLayoutBindDesign BIND_0_1_5 = {
    VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, 1, 1, STAGE_0_1_5
};
static VkForgeLayoutBindDesign* BIND_DESIGNS_0_0[] = {
    &BIND_0_0_0, &BIND_0_0_1, &BIND_0_0_2, &BIND_0_0_3, &BIND_0_0_4, NULL, NULL, &BIND_0_0_7, &BIND_0_0_8
};
static VkForgeLayoutBindDesign* BIND_DESIGNS_0_1[] = {
    NULL, &BIND_0_1_1, NULL, NULL, NULL, &BIND_0_1_5, NULL, NULL
};

static VkForgeLayoutDescriptorSetLayoutDesign DESCRIPTOR_SET_LAYOUT_0_0 = {
    9, BIND_DESIGNS_0_0
};
static VkForgeLayoutDescriptorSetLayoutDesign DESCRIPTOR_SET_LAYOUT_0_1 = {
    8, BIND_DESIGNS_0_1
};
static VkForgeLayoutDescriptorSetLayoutDesign* DESCRIPTOR_SET_LAYOUTS_0[] = {
    &DESCRIPTOR_SET_LAYOUT_0_0, &DESCRIPTOR_SET_LAYOUT_0_1
};

static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_0 = {
    2, DESCRIPTOR_SET_LAYOUTS_0
};
static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_1 = {
    0, NULL
};
static VkForgeLayoutPipelineLayoutDesign* PIPELINE_LAYOUT_DESIGNS[] = {
    &PIPELINE_LAYOUT_0,
    &PIPELINE_LAYOUT_1
};

static VkForgeLayoutReferenceDesign REFERENCE_0 = {
    0, "Simple2"
};
static VkForgeLayoutReferenceDesign REFERENCE_1 = {
    0, "Simple3"
};
static VkForgeLayoutReferenceDesign REFERENCE_2 = {
    0, "Simple4"
};
static VkForgeLayoutReferenceDesign REFERENCE_3 = {
    1, "Simple"
};
static VkForgeLayoutReferenceDesign* REFERENCES[] = {
    &REFERENCE_0,
    &REFERENCE_1,
    &REFERENCE_2,
    &REFERENCE_3
};

static VkForgeReferencedLayoutDesign VKFORGE_REFERENCED_LAYOUT_DESIGN = 
{
    2,
    PIPELINE_LAYOUT_DESIGNS,
    4,
    REFERENCES
};

typedef struct VkForgePipelineFunction VkForgePipelineFunction;
struct VkForgePipelineFunction
{
    VkPipeline (*CreatePipelineForFunc)(
        VkAllocationCallbacks* allocator,
        void* next,
        VkDevice device,
        VkPipelineLayout pipeline_layout
    );
    const char* pipeline_name;
    uint32_t pipeline_index;
};

static VkForgePipelineFunction PIPELINE_FUNC_0 = {
    VkForge_CreatePipelineForSimple,
    "Simple",
    0
};
static VkForgePipelineFunction PIPELINE_FUNC_1 = {
    VkForge_CreatePipelineForSimple2,
    "Simple2",
    1
};
static VkForgePipelineFunction PIPELINE_FUNC_2 = {
    VkForge_CreatePipelineForSimple3,
    "Simple3",
    2
};
static VkForgePipelineFunction PIPELINE_FUNC_3 = {
    VkForge_CreatePipelineForSimple4,
    "Simple4",
    3
};
static VkForgePipelineFunction* PIPELINE_FUNCTIONS[] = {
    &PIPELINE_FUNC_0,
    &PIPELINE_FUNC_1,
    &PIPELINE_FUNC_2,
    &PIPELINE_FUNC_3
};

static VkForgePipelineFunction** VKFORGE_PIPELINE_FUNCTIONS = PIPELINE_FUNCTIONS;
static uint32_t VKFORGE_PIPELINE_FUNCTION_COUNT = 4;

VkForgeLayout* VkForge_CreateForgeLayout
(
    VkSurfaceKHR surface, 
    VkPhysicalDevice physical_device, 
    VkDevice device
)
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

VkForgeLayoutQueue* VkForge_CreateForgeLayoutQueue()
{
    VkForgeLayoutQueue* queue = (VkForgeLayoutQueue*)SDL_malloc(sizeof(VkForgeLayoutQueue));
    if (!queue)
    {
        SDL_LogError(0, "Failed to allocate memory for VkForgeLayoutQueue");
        exit(1);
    }

    SDL_memset(queue, 0, sizeof(VkForgeLayoutQueue));
    return queue;
}

void VkForge_DestroyForgeLayoutQueue(VkForgeLayoutQueue* queue)
{
    if (queue)
    {
        SDL_free(queue);
    }
}

static const VkForgePipelineFunction* FindPipelineFunction(const char* pipeline_name)
{
    for( uint32_t i = 0; i < VKFORGE_PIPELINE_FUNCTION_COUNT; i++ )
    {
        if( strcmp(pipeline_name, VKFORGE_PIPELINE_FUNCTIONS[i]->pipeline_name) == 0 )
        {
            return VKFORGE_PIPELINE_FUNCTIONS[i];
        }
    }
    return NULL;
}

static uint32_t FindPipelineLayoutIndex(const char* pipeline_name)
{
    for( uint32_t i = 0; i < VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_count; i++ )
    {
        if( strcmp(pipeline_name, VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_buffer[i]->pipeline_name) == 0 )
        {
            return VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_buffer[i]->pipeline_layout_design_index;
        }
    }
    return UINT32_MAX;
}

static VkShaderStageFlags BuildStageFlags(const VkForgeLayoutBindDesign* bind)
{
    if (!bind || bind->mode_count == 0) return 0;
    
    VkShaderStageFlags flags = bind->mode_buffer[0];
    for (uint32_t i = 1; i < bind->mode_count; i++)
    {
        flags |= bind->mode_buffer[i];
    }
    return flags;
}

static void CreateDescriptorSetLayoutBindings(
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    VkDescriptorSetLayoutBinding* out_bindings)
{
    for (uint32_t j = 0; j < set_design->bind_design_count; j++)
    {
        const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
        if( !bind ) continue;

        out_bindings[j] = (VkDescriptorSetLayoutBinding){
            .binding = j,
            .descriptorType = bind->type,
            .descriptorCount = bind->count,
            .stageFlags = BuildStageFlags(bind)
        };
    }
}

static VkResult CreateDescriptorSetLayout(
    VkDevice device,
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    VkDescriptorSetLayout* out_dsetLayout)
{
    VkDescriptorSetLayoutBinding bindings[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {0};
    CreateDescriptorSetLayoutBindings(set_design, bindings);

    VkDescriptorSetLayoutCreateInfo setLayoutInfo = {
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
        .bindingCount = set_design->bind_design_count,
        .pBindings = bindings
    };

    VkResult result = vkCreateDescriptorSetLayout(device, &setLayoutInfo, NULL, out_dsetLayout);

    return result;
}

// Updated helper function for pool requirements
static void GetDescriptorPoolRequirements(
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design,
    uint32_t*                                outDescriptorPoolSizeCount,
    VkDescriptorPoolSize*                    outDescriptorPoolSizes)
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

/**
 * @brief Queues a descriptor resource for a specific pipeline layout
 * @param queue The VkForge layout queue instance
 * @param pipelineLayout The pipeline layout to queue the resource for
 * @param set The descriptor set index
 * @param binding The binding index within the set
 * @param resource The descriptor resource (image or buffer)
 */
void VkForge_QueueDescriptorResourceForForgePipelineLayout(
    VkForgeLayoutQueue* queue,
    VkForgePipelineLayout* pipelineLayout,
    uint16_t set,
    uint16_t binding,
    VkForgeDescriptorResource resource
)
{
    assert(queue);
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

    uint32_t already_queued_count = queue->descriptor_resource_queue_count;

    if(already_queued_count)
    {
        // Check if this set/binding is already queued for the same pipeline layout
        for (uint32_t i = 0; i < already_queued_count; i++)
        {
            if (queue->descriptor_resource_queue[i].set == set &&
                queue->descriptor_resource_queue[i].binding == binding &&
                queue->descriptor_resource_queue[i].pipeline_layout_index == pipelineLayout->pipeline_layout_index)
            {
                // Check if resource handles are different
                bool needs_update = false;

                if (VkForge_IsDescriptorTypeImage(expected_type))
                {
                    needs_update = (queue->descriptor_resource_queue[i].resource.image.imageView != resource.image.imageView ||
                                queue->descriptor_resource_queue[i].resource.image.sampler != resource.image.sampler ||
                                queue->descriptor_resource_queue[i].resource.image.imageLayout != resource.image.imageLayout);
                }
                else if (VkForge_IsDescriptorTypeBuffer(expected_type))
                {
                    needs_update = (queue->descriptor_resource_queue[i].resource.buffer.buffer != resource.buffer.buffer ||
                                queue->descriptor_resource_queue[i].resource.buffer.offset != resource.buffer.offset ||
                                queue->descriptor_resource_queue[i].resource.buffer.range != resource.buffer.range);
                }

                if (needs_update)
                {
                    // Update Resource
                    queue->descriptor_resource_queue[i].resource = resource;

                    SDL_Log("Queued Updated Resource for set %u binding %u", set, binding);
                }
                return;
            }
        }
    }

    // Check if queue is full
    if (queue->descriptor_resource_queue_count >= VKFORGE_MAX_DESCRIPTOR_RESOURCES)
    {
        SDL_LogError(0, "Descriptor Resource Queue is full: %d Max", VKFORGE_MAX_DESCRIPTOR_RESOURCES);
        exit(1);
    }

    // Add new entry to queue
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].resource = resource;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].set = set;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].binding = binding;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].pipeline_layout_index = pipelineLayout->pipeline_layout_index;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].type = expected_type;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].count = bind_design->count;

    SDL_Log("Queued Resource for set %u binding %u", set, binding);

    queue->descriptor_resource_queue_count++;
}

/**
 * @brief Writes all queued descriptor resources to their respective descriptor sets
 * @param layout The VkForge layout instance
 * @param queue The VkForge layout queue instance containing the descriptor queue
 * @param pipelineLayout The pipeline layout to write descriptors for
 */
void VkForge_WriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(
    VkForgeLayout* layout, 
    VkForgeLayoutQueue* queue, 
    VkForgePipelineLayout* pipelineLayout)
{
    assert(layout);
    assert(queue);
    assert(pipelineLayout);

    if (queue->descriptor_resource_queue_count == 0)
    {
        return;
    }

    uint32_t write_count = 0;
    VkWriteDescriptorSet writes[VKFORGE_MAX_DESCRIPTOR_RESOURCES] = {0};

    // For each queued resource that belongs to this pipeline layout
    for (uint32_t i = 0; i < queue->descriptor_resource_queue_count; i++)
    {
        VkForgeDescriptorResourceQueue* entry = &queue->descriptor_resource_queue[i];
        
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
    for (uint32_t i = 0; i < queue->descriptor_resource_queue_count; i++)
    {
        if (queue->descriptor_resource_queue[i].pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {
            // Keep entries for other pipeline layouts
            if (new_index != i)
            {
                queue->descriptor_resource_queue[new_index] = queue->descriptor_resource_queue[i];
            }
            new_index++;
        }
    }
    
    queue->descriptor_resource_queue_count = new_index;
}

/**
 * @brief Clears all queued descriptor resources for a specific pipeline layout
 * @param queue The VkForge layout queue instance
 * @param pipelineLayout The pipeline layout to clear queue for
 */
void VkForge_ClearDescriptorResourceQueueForForgePipelineLayout(
    VkForgeLayoutQueue* queue, 
    VkForgePipelineLayout* pipelineLayout)
{
    assert(queue);
    assert(pipelineLayout);

    uint32_t new_index = 0;
    for (uint32_t i = 0; i < queue->descriptor_resource_queue_count; i++)
    {
        if (queue->descriptor_resource_queue[i].pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {
            // Keep entries for other pipeline layouts
            if (new_index != i)
            {
                queue->descriptor_resource_queue[new_index] = queue->descriptor_resource_queue[i];
            }
            new_index++;
        }
    }
    
    queue->descriptor_resource_queue_count = new_index;
}

/**
 * @brief Clears all queued descriptor resources
 * @param queue The VkForge layout queue instance
 */
void VkForge_ClearDescriptorResourceQueue(VkForgeLayoutQueue* queue)
{
    assert(queue);
    queue->descriptor_resource_queue_count = 0;
}

/**
 * @brief Binds descriptor sets for the current pipeline layout and writes queued resources
 * @param layout The VkForge layout instance
 * @param queue The VkForge layout queue instance
 * @param pipelineLayout The pipeline layout to bind
 * @param commandBuffer The command buffer to bind descriptor sets to
 */
void VkForge_BindForgePipelineLayoutPerWriteDescriptorResourceQueue(
    VkForgeLayout* layout,
    VkForgeLayoutQueue* queue,
    VkForgePipelineLayout* pipelineLayout,
    VkCommandBuffer commandBuffer)
{
    assert(layout);
    assert(queue);
    assert(pipelineLayout);
    assert(commandBuffer);

    // First write any queued descriptor resources
    VkForge_WriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(layout, queue, pipelineLayout);

    // Bind descriptor sets to the command buffer
    if (pipelineLayout->descriptor_set_count > 0)
    {
        vkCmdBindDescriptorSets(
            commandBuffer,
            VK_PIPELINE_BIND_POINT_GRAPHICS,
            pipelineLayout->pipelineLayout,
            0, // firstSet
            pipelineLayout->descriptor_set_count,
            pipelineLayout->descriptor_sets,
            0, // dynamicOffsetCount
            NULL // pDynamicOffsets
        );

        SDL_Log("Bound %u descriptor sets to command buffer", pipelineLayout->descriptor_set_count);
    }
}


