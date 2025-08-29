#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>

#include "vkforge_typedecls.h"
#include "vkforge_funcdecls.h"
#include "vkforge_pipelines.h"

#include "../entity.h"

/** NO USER DECLARATIONS **/

#define VKFORGE_MAX_DESCRIPTOR_RESOURCES VKFORGE_MAX_DESCRIPTOR_BINDINGS

typedef struct VkForgeDescriptorResourceQueue VkForgeDescriptorResourceQueue;

struct VkForgeDescriptorResourceQueue
{
    VkForgeDescriptorResource resource;
    uint16_t                  set;
    uint16_t                  binding;
    uint16_t                  pipeline_layout_index;
    VkDescriptorType          type;
    uint16_t                  count;
    const char*               logname;
};

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

static uint32_t STAGE_0_0_0[] = { VK_SHADER_STAGE_FRAGMENT_BIT };

static VkForgeLayoutBindDesign BIND_0_0_0 = {
    VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, 1, 1, STAGE_0_0_0
};
static VkForgeLayoutBindDesign* BIND_DESIGNS_0_0[] = {
    &BIND_0_0_0
};

static VkForgeLayoutDescriptorSetLayoutDesign DESCRIPTOR_SET_LAYOUT_0_0 = {
    1, BIND_DESIGNS_0_0
};
static VkForgeLayoutDescriptorSetLayoutDesign* DESCRIPTOR_SET_LAYOUTS_0[] = {
    &DESCRIPTOR_SET_LAYOUT_0_0
};

static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_0 = {
    1, DESCRIPTOR_SET_LAYOUTS_0
};
static VkForgeLayoutPipelineLayoutDesign* PIPELINE_LAYOUT_DESIGNS[] = {
    &PIPELINE_LAYOUT_0
};

static VkForgeLayoutReferenceDesign REFERENCE_0 = {
    0, "Default"
};
static VkForgeLayoutReferenceDesign* REFERENCES[] = {
    &REFERENCE_0
};

static VkForgeReferencedLayoutDesign VKFORGE_REFERENCED_LAYOUT_DESIGN = 
{
    1,
    PIPELINE_LAYOUT_DESIGNS,
    1,
    REFERENCES
};

struct VkForgeLayout
{
    VkSurfaceKHR          surface;
    VkPhysicalDevice      physical_device;
    VkDevice              device;
    uint8_t               pipeline_count;
    VkPipeline            pipeline_buffer[VKFORGE_MAX_PIPELINES];
    uint8_t               pipeline_layout_count;
    VkPipelineLayout      pipeline_layout_buffer[VKFORGE_MAX_PIPELINE_LAYOUTS];
    VkDescriptorPool      descriptor_pools[VKFORGE_MAX_PIPELINE_LAYOUTS];
    uint8_t               descriptorset_layout_count[VKFORGE_MAX_PIPELINE_LAYOUTS];
    VkDescriptorSetLayout descriptorset_layout_buffer[VKFORGE_MAX_PIPELINE_LAYOUTS][VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
    VkDescriptorSet       descriptorset_buffer[VKFORGE_MAX_PIPELINE_LAYOUTS][VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];

    // Descriptor Resources
    VkForgeDescriptorResourceQueue descriptor_resource_queue[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
    VkWriteDescriptorSet           write_descriptor_set[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
    uint32_t                       descriptor_resource_queue_count;
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
    VkForge_CreatePipelineForDefault,
    "Default",
    0
};
static VkForgePipelineFunction* PIPELINE_FUNCTIONS[] = {
    &PIPELINE_FUNC_0
};

static VkForgePipelineFunction** VKFORGE_PIPELINE_FUNCTIONS = PIPELINE_FUNCTIONS;
static uint32_t VKFORGE_PIPELINE_FUNCTION_COUNT = 1;

VkForgeLayout* VkForge_CreateLayout(VkSurfaceKHR surface, VkPhysicalDevice physical_device, VkDevice device)
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

void VkForge_DestroyLayout(VkForgeLayout* forge_layout)
{
    if ( forge_layout )
    {
        // Destroy all pipelines
        for (uint8_t i = 0; i < VKFORGE_MAX_PIPELINES; i++)
        {
            if(forge_layout->pipeline_buffer[i]) vkDestroyPipeline(forge_layout->device, forge_layout->pipeline_buffer[i], 0);
        }

        // Destroy all pipeline layouts
        for (uint8_t i = 0; i < VKFORGE_MAX_PIPELINE_LAYOUTS; i++)
        {
            // Destroy all descriptor sets and layouts
            for (uint8_t j = 0; j < forge_layout->descriptorset_layout_count[i]; j++)
            {
                if(forge_layout->descriptorset_layout_buffer[i][j]) vkDestroyDescriptorSetLayout(forge_layout->device, forge_layout->descriptorset_layout_buffer[i][j], 0);
            }
            if(forge_layout->descriptor_pools[i]) vkDestroyDescriptorPool(forge_layout->device, forge_layout->descriptor_pools[i], 0);
            if(forge_layout->pipeline_layout_buffer[i]) vkDestroyPipelineLayout(forge_layout->device, forge_layout->pipeline_layout_buffer[i], 0);
        }

        SDL_free(forge_layout);
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

static uint32_t CountDescriptorSetLayoutBindings(const VkForgeLayoutDescriptorSetLayoutDesign* set_design)
{
    uint32_t count = 0;

    if(set_design->bind_design_count)
    {
        for (uint32_t j = 0; j < set_design->bind_design_count; j++)
        {
            const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
            if(bind) count ++;
        }
    }

    return count;
}

/// @brief
/// @param set_design
/// @param out_bindings Ensure it is large enough using VKFORGE_MAX_DESCRIPTOR_BINDINGS
/// @return
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
        .bindingCount = CountDescriptorSetLayoutBindings(set_design),
        .pBindings = bindings
    };

    VkResult result = vkCreateDescriptorSetLayout(device, &setLayoutInfo, NULL, out_dsetLayout);

    return result;
}

static void CreatePipelineLayout(
    VkForgeLayout* forge_layout,
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design,
    uint32_t pipeline_layout_index)
{

    if( forge_layout->pipeline_layout_buffer[pipeline_layout_index] != VK_NULL_HANDLE )
    {
        SDL_LogError(0, "Pipeline Layout already created");
        return;
    }

    if( pipeline_design->descriptorset_layout_design_count )
    {
        for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
        {
            const VkForgeLayoutDescriptorSetLayoutDesign* set_design = pipeline_design->descriptorset_layout_design_buffer[i];
            forge_layout->descriptorset_layout_count[pipeline_layout_index] = pipeline_design->descriptorset_layout_design_count;

            if(set_design->bind_design_count)
            {
                VkResult result = CreateDescriptorSetLayout(forge_layout->device, set_design, &forge_layout->descriptorset_layout_buffer[pipeline_layout_index][i]);
                if (result != VK_SUCCESS)
                {
                    SDL_LogError(0, "Failed to create descriptor set forge_layout");
                    for (uint32_t j = 0; j < i; j++)
                    {
                        vkDestroyDescriptorSetLayout(forge_layout->device, forge_layout->descriptorset_layout_buffer[pipeline_layout_index][j], NULL);
                    }
                    exit(1);
                }
            }
            else
            {
                forge_layout->descriptorset_layout_buffer[pipeline_layout_index][i] = VK_NULL_HANDLE;
            }
        }
    }

    VkPipelineLayoutCreateInfo layoutInfo = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .setLayoutCount = pipeline_design->descriptorset_layout_design_count,
        .pSetLayouts = forge_layout->descriptorset_layout_buffer[pipeline_layout_index],
        .pushConstantRangeCount = 0,
        .pPushConstantRanges = NULL
    };

    VkPipelineLayout pipelineLayout;
    VkResult result = vkCreatePipelineLayout(forge_layout->device, &layoutInfo, NULL, &pipelineLayout);

    if (result != VK_SUCCESS)
    {
        SDL_LogError(0, "Failed to create pipeline forge_layout");
        exit(1);
    }

    // Store the created pipeline forge_layout
    forge_layout->pipeline_layout_buffer[pipeline_layout_index] = pipelineLayout;
    forge_layout->pipeline_layout_count ++;
}

/// @brief Get descriptor pool size requirements for a pipeline layout
/// @param forge_layout Pointer to the VkForge layout structure
/// @param pipeline_name Name of the pipeline to query
/// @param outDescriptorPoolSizeCount Output parameter for number of pool size entries
/// @param outDescriptorPoolSizes Output buffer for pool size entries (must be VKFORGE_MAX_DESCRIPTOR_BINDINGS size)
/// @note User must not free any resource returned
static void GetDescriptorPoolRequirements
(
    VkForgeLayout* forge_layout,
    uint32_t pipeline_layout_index,
    uint32_t* outDescriptorPoolSizeCount,
    VkDescriptorPoolSize* outDescriptorPoolSizes
)
{
    assert(forge_layout);
    assert(forge_layout->device);

    if(!outDescriptorPoolSizeCount && !outDescriptorPoolSizes) return;

    const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
        VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

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

void VkForge_BuildPipeline(VkForgeLayout* forge_layout, const char* pipeline_name)
{
    assert(forge_layout);
    assert(pipeline_name);
    assert(forge_layout->device);

    // Check if pipeline already exists
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {
        SDL_LogError(0, "Pipeline creation function not found for %s", pipeline_name);
        exit(1);
    }

    if (forge_layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {
        SDL_Log("Pipeline %s already exists", pipeline_name);
        return;
    }

    // Find the pipeline forge_layout index in the global design
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipeline_name);
    if (pipeline_layout_index == UINT32_MAX)
    {
        SDL_LogError(0, "Pipeline forge_layout not found for %s", pipeline_name);
        exit(1);
    }

    // Create pipeline forge_layout if it doesn't exist
    if (forge_layout->pipeline_layout_buffer[pipeline_layout_index] == VK_NULL_HANDLE)
    {
        const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
            VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

        CreatePipelineLayout(forge_layout, pipeline_design, pipeline_layout_index);
    }

    /// DYNAMIC RENDERING REQUIRED STRUCTURE ///
    VkSurfaceFormatKHR surfaceFormat = VkForge_GetSurfaceFormat(
        forge_layout->surface,
        forge_layout->physical_device,
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
        forge_layout->device,
        forge_layout->pipeline_layout_buffer[pipeline_layout_index]
    );

    if (pipeline == VK_NULL_HANDLE)
    {
        SDL_LogError(0, "Failed to create pipeline %s", pipeline_name);
        exit(1);
    }

    // Store the pipeline at its predefined index
    forge_layout->pipeline_buffer[pipeline_func->pipeline_index] = pipeline;
    forge_layout->pipeline_count ++;
}

void VkForge_BindPipeline(VkForgeLayout* layout, const char* pipeline_name, VkCommandBuffer cmdbuf)
{
    assert(layout);
    assert(pipeline_name);
    assert(layout->device);
    assert(cmdbuf);

    // Find the pipeline
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {
        SDL_LogError(0, "Pipeline %s not found", pipeline_name);
        return;
    }

    if (pipeline_func->pipeline_index < layout->pipeline_count &&
        layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {
        vkCmdBindPipeline(
            cmdbuf, 
            VK_PIPELINE_BIND_POINT_GRAPHICS, 
            layout->pipeline_buffer[pipeline_func->pipeline_index]
        );
        return;
    }

    SDL_LogError(0, "Pipeline %s not created", pipeline_name);
}

/// @brief User must not free any resource returned
/// @param forge_layout
/// @param pipeline_name
/// @return
VkPipeline VkForge_BorrowPipeline(VkForgeLayout* forge_layout, const char* pipeline_name)
{
    assert(forge_layout);
    assert(pipeline_name);
    assert(forge_layout->device);

    // Find the pipeline
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {
        SDL_LogError(0, "Pipeline %s not found", pipeline_name);
        return VK_NULL_HANDLE;
    }

    if (pipeline_func->pipeline_index < forge_layout->pipeline_count &&
        forge_layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {
        return forge_layout->pipeline_buffer[pipeline_func->pipeline_index];
    }

    SDL_LogError(0, "Pipeline %s not created", pipeline_name);
    return VK_NULL_HANDLE;
}

/// @brief User must not free any resource returned.
/// @param forge_layout
/// @param pipeline_name
/// @param outPipelineLayout
/// @param outDescriptorSetLayoutCount
/// @param outDescriptorSetLayouts  user must pass a buffer of VKFORGE_MAX_DESCRIPTORSET_LAYOUTS size
/// @param outDescriptorSets user must pass a buffer of VKFORGE_MAX_DESCRIPTORSET_LAYOUTS size
/// @param outDescriptorPoolSizeCount
/// @param outDescriptorPoolSizes  user must pass a buffer of VKFORGE_MAX_DESCRIPTOR_BINDINGS
void VkForge_SharePipelineLayoutDetails(
    VkForgeLayout* forge_layout,
    const char* pipeline_name,
    VkPipelineLayout* outPipelineLayout,
    uint32_t* outDescriptorSetLayoutCount,
    VkDescriptorSetLayout* outDescriptorSetLayouts,
    VkDescriptorSet* outDescriptorSets,
    uint32_t* outDescriptorPoolSizeCount,
    VkDescriptorPoolSize* outDescriptorPoolSizes
)
{
    assert(forge_layout);
    assert(pipeline_name);
    assert(forge_layout->device);

    // Find the pipeline layout index
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipeline_name);
    if (pipeline_layout_index == UINT32_MAX)
    {
        SDL_LogError(0, "Pipeline layout not found for %s", pipeline_name);
        exit(1);
    }

    // Handle pipeline layout buffer requests
    if (outPipelineLayout)
    {
        outPipelineLayout[0] = forge_layout->pipeline_layout_buffer[pipeline_layout_index];
    }

    // Handle descriptor set layout count/buffer requests
    if (outDescriptorSetLayoutCount)
    {
        *outDescriptorSetLayoutCount = forge_layout->descriptorset_layout_count[pipeline_layout_index];
    }
    if (outDescriptorSetLayouts)
    {
        for (uint32_t i = 0; i < forge_layout->descriptorset_layout_count[pipeline_layout_index]; i++)
        {
            outDescriptorSetLayouts[i] = forge_layout->descriptorset_layout_buffer[pipeline_layout_index][i];
        }
    }
    if (outDescriptorSets)
    {
        for (uint32_t i = 0; i < forge_layout->descriptorset_layout_count[pipeline_layout_index]; i++)
        {
            outDescriptorSets[i] = forge_layout->descriptorset_buffer[pipeline_layout_index][i];
        }
    }

    // Handle descriptor pool size calculations
    if (outDescriptorPoolSizeCount || outDescriptorPoolSizes)
    {
        const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
            VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

        uint32_t pool_size_count = 0;
        VkDescriptorPoolSize temp_pool_sizes[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {0};

        // First pass: calculate required pool sizes
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
}

static bool DoesDescriptorResourceQueueHaveValue(VkForgeDescriptorResourceQueue queued)
{
    if(queued.resource.image.imageView && VkForge_IsDescriptorTypeImage(queued.type))
        return true;
    if(queued.resource.buffer.buffer && VkForge_IsDescriptorTypeBuffer(queued.type))
        return true;

    return false;
}

static uint32_t GetAlreadyQueuedDescriptorResourceCount(VkForgeLayout* layout)
{
    uint32_t count = 0;
    for (uint32_t i = 0; i < VKFORGE_MAX_DESCRIPTOR_RESOURCES; i++)
    {
        VkForgeDescriptorResourceQueue queueSlot = layout->descriptor_resource_queue[i];
        if(DoesDescriptorResourceQueueHaveValue(queueSlot))
        {
            count ++;
        }
        else
        {
            return count;
        }
    }

    return count;
}

/**
 * @brief Queues a descriptor resource for a specific pipeline layout
 * @param layout The VkForge layout instance
 * @param pipelineName The pipeline name to select the correct layout and descriptor set array
 * @param set The descriptor set index
 * @param binding The binding index within the set
 * @param resource The descriptor resource (image or buffer)
 */
void VkForge_QueueDescriptorResource(
    VkForgeLayout* layout,
    const char* pipelineName,
    uint16_t set,
    uint16_t binding,
    VkForgeDescriptorResource resource
)
{
    assert(layout);
    assert(pipelineName);

    // Find the pipeline layout index for the given pipeline name
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipelineName);
    if (pipeline_layout_index == UINT32_MAX || pipeline_layout_index >= VKFORGE_MAX_PIPELINE_LAYOUTS)
    {
        SDL_LogError(0, "Pipeline layout not found for pipeline: %s", pipelineName);
        exit(1);
    }

    // Get the pipeline layout design
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
        VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

    if (set >= pipeline_design->descriptorset_layout_design_count)
    {
        SDL_LogError(0, "Set %u out of bounds for pipeline layout %u", set, pipeline_layout_index);
        exit(1);
    }

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

    uint32_t already_queued_count = GetAlreadyQueuedDescriptorResourceCount(layout);

    if( already_queued_count )
    {
        // Check if this set/binding is already queued for the same pipeline layout
        for (uint32_t i = 0; i < already_queued_count; i++)
        {
            if (layout->descriptor_resource_queue[i].set == set &&
                layout->descriptor_resource_queue[i].binding == binding &&
                layout->descriptor_resource_queue[i].pipeline_layout_index == pipeline_layout_index)
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

    if(layout->descriptor_pools[pipeline_layout_index] == VK_NULL_HANDLE)
    {
        uint32_t pool_sizes_count = 0;
        VkDescriptorPoolSize pool_sizes[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {0};

        GetDescriptorPoolRequirements(
            layout,
            pipeline_layout_index,
            &pool_sizes_count,
            pool_sizes
        );

        layout->descriptor_pools[pipeline_layout_index] = VkForge_CreateDescriptorPool(
            layout->device,
            layout->descriptorset_layout_count[pipeline_layout_index],
            pool_sizes_count,
            pool_sizes
        );
    }

    // Allocate Descriptorsets if they do not exist
    if(
        layout->descriptorset_buffer[pipeline_layout_index]
        [0] //TODO: Make More Efficient
            //    : Is it possible that the first descriptorset is NULL by design?
            //    : Need to check the design of complex layout
            //    : Use a most efficient method to check like using design to determine which FIRST position to check
        == VK_NULL_HANDLE
    )
    {
        VkForge_AllocateDescriptorSet(
            layout->device,
            layout->descriptor_pools[pipeline_layout_index],
            layout->descriptorset_layout_count[pipeline_layout_index],
            layout->descriptorset_layout_buffer[pipeline_layout_index],
            layout->descriptorset_buffer[pipeline_layout_index]
        );
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
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].pipeline_layout_index = pipeline_layout_index;
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].type = expected_type;
    layout->descriptor_resource_queue[layout->descriptor_resource_queue_count].count = bind_design->count;

    SDL_Log("Queued Resource for set %u binding %u", set, binding);

    layout->descriptor_resource_queue_count++;
}

/**
 * @brief Writes all queued descriptor resources to their respective descriptor sets
 * @param layout The VkForge layout instance containing the descriptor sets
 */
void VkForge_WriteDescriptorResources(VkForgeLayout* layout)
{
    assert(layout);

    if (layout->descriptor_resource_queue_count == 0)
    {
        return;
    }

    // For each unique pipeline layout, update the descriptor sets
    for (uint32_t i = 0; i < layout->descriptor_resource_queue_count; i++)
    {
        VkForgeDescriptorResourceQueue* entry = &layout->descriptor_resource_queue[i];
        VkDescriptorSet descriptorset = layout->descriptorset_buffer[entry->pipeline_layout_index][entry->set];

        if (descriptorset == VK_NULL_HANDLE)
        {
            SDL_LogError(0, "Descriptor set not found for layout %u, set %u.",
                        entry->pipeline_layout_index, entry->set);
            exit(1);
        }

        // Update the dstSet for the corresponding write descriptor
        layout->write_descriptor_set[i] =
        (VkWriteDescriptorSet){
            .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
            .dstSet = descriptorset,
            .dstBinding = entry->binding,
            .descriptorCount = entry->count,
            .descriptorType = entry->type,
        };

        // Set the appropriate descriptor info
        if (VkForge_IsDescriptorTypeImage(entry->type))
        {
            layout->write_descriptor_set[i].pImageInfo =
                &layout->descriptor_resource_queue[i].resource.image;
        }
        else if (VkForge_IsDescriptorTypeBuffer(entry->type))
        {
            layout->write_descriptor_set[i].pBufferInfo =
                &layout->descriptor_resource_queue[i].resource.buffer;
        }

        SDL_Log("Preparing to Write Resource for set %u binding %u", entry->set, entry->binding);
    }

    // Update all descriptor sets
    vkUpdateDescriptorSets(
        layout->device,
        layout->descriptor_resource_queue_count,
        layout->write_descriptor_set,
        0, NULL
    );

    SDL_Log("Wrote all Resources");

    // Reset the queues
    layout->descriptor_resource_queue_count = 0;
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


