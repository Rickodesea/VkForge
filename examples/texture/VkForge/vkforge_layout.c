#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>

#include "vkforge_typedecls.h"
#include "vkforge_funcdecls.h"
#include "vkforge_pipelines.h"

#include "../entity.h"

/** NO USER DECLARATIONS **/

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
    uint8_t               descriptorset_layout_count[VKFORGE_MAX_PIPELINE_LAYOUTS];
    VkDescriptorSetLayout descriptorset_layout_buffer[VKFORGE_MAX_PIPELINE_LAYOUTS][VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
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

static VkResult CreatePipelineLayout(
    VkForgeLayout* forge_layout,
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design,
    uint32_t pipeline_layout_index)
{

    if( forge_layout->pipeline_layout_buffer[pipeline_layout_index] != VK_NULL_HANDLE )
    {
        SDL_LogError(0, "Pipeline Layout already created");
        return VK_SUCCESS;
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
                    return result;
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
        return result;
    }

    // Store the created pipeline forge_layout
    forge_layout->pipeline_layout_buffer[pipeline_layout_index] = pipelineLayout;
    forge_layout->pipeline_layout_count ++;

    return VK_SUCCESS;
}

VkResult VkForge_CreatePipeline(VkForgeLayout* forge_layout, const char* pipeline_name)
{
    assert(forge_layout);
    assert(pipeline_name);
    assert(forge_layout->device);

    // Check if pipeline already exists
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {
        SDL_LogError(0, "Pipeline creation function not found for %s", pipeline_name);
        return VK_ERROR_UNKNOWN;
    }

    if (forge_layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {
        SDL_Log("Pipeline %s already exists", pipeline_name);
        return VK_SUCCESS;
    }

    // Find the pipeline forge_layout index in the global design
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipeline_name);
    if (pipeline_layout_index == UINT32_MAX)
    {
        SDL_LogError(0, "Pipeline forge_layout not found for %s", pipeline_name);
        return VK_ERROR_UNKNOWN;
    }

    // Create pipeline forge_layout if it doesn't exist
    if (forge_layout->pipeline_layout_buffer[pipeline_layout_index] == VK_NULL_HANDLE)
    {
        const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
            VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

        VkResult result = CreatePipelineLayout(forge_layout, pipeline_design, pipeline_layout_index);
        if (result != VK_SUCCESS)
        {
            return result;
        }
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
        return VK_ERROR_UNKNOWN;
    }

    // Store the pipeline at its predefined index
    forge_layout->pipeline_buffer[pipeline_func->pipeline_index] = pipeline;
    forge_layout->pipeline_count ++;

    return VK_SUCCESS;
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
/// @param outPipelineLayouts
/// @param outDescriptorSetLayoutCount
/// @param outDescriptorSetLayouts  user must pass a buffer of VKFORGE_MAX_DESCRIPTORSET_LAYOUTS size
/// @param outDescriptorPoolSizeCount
/// @param outDescriptorPoolSizes  user must pass a buffer of VKFORGE_MAX_DESCRIPTOR_BINDINGS
void VkForge_SharePipelineLayoutDetails(
    VkForgeLayout* forge_layout,
    const char* pipeline_name,
    VkPipelineLayout* outPipelineLayouts,
    uint32_t* outDescriptorSetLayoutCount,
    VkDescriptorSetLayout* outDescriptorSetLayouts,
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
    if (outPipelineLayouts)
    {
        outPipelineLayouts[0] = forge_layout->pipeline_layout_buffer[pipeline_layout_index];
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


