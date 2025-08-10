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

/** NO STAGES **/

/** NO BINDING **/

/** NO DESCRIPTORSET LAYOUTS **/

static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_0 = {
    0, NULL
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
    uint8_t               descriptorset_count;
    VkDescriptorSet       descriptorset_buffer[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
    uint8_t               pipeline_layout_count;
    VkPipelineLayout      pipeline_layout_buffer[VKFORGE_MAX_PIPELINE_LAYOUTS];
    uint8_t               descriptorset_layout_count;
    VkDescriptorSetLayout descriptorset_layout_buffer[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
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

void VkForge_DestroyLayout(VkForgeLayout* layout)
{
    if ( layout )
    {
        // Destroy all pipelines
        for (uint8_t i = 0; i < VKFORGE_MAX_PIPELINES; i++)
        {
            if(layout->pipeline_buffer[i]) vkDestroyPipeline(layout->device, layout->pipeline_buffer[i], 0);
        }

        // Destroy all descriptor sets and layouts
        for (uint8_t i = 0; i < layout->descriptorset_layout_count; i++)
        {
            vkDestroyDescriptorSetLayout(layout->device, layout->descriptorset_layout_buffer[i], 0);
        }

        // Destroy all pipeline layouts
        for (uint8_t i = 0; i < VKFORGE_MAX_PIPELINE_LAYOUTS; i++)
        {
            if(layout->pipeline_layout_buffer[i]) vkDestroyPipelineLayout(layout->device, layout->pipeline_layout_buffer[i], 0);
        }

        SDL_free(layout);
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
    if(set_design->bind_design_count)
    {
        uint32_t count = 0;

        for (uint32_t j = 0; j < set_design->bind_design_count; j++)
        {
            const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
            if(bind) count ++;
        }
    }

    return 0;
}

static VkResult CreateDescriptorSetLayoutBindings(
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    uint32_t binding_count,
    VkDescriptorSetLayoutBinding** out_bindings)
{
    if( binding_count )
    {
        VkDescriptorSetLayoutBinding* bindings = (VkDescriptorSetLayoutBinding*)SDL_malloc(
            sizeof(VkDescriptorSetLayoutBinding) * binding_count);

        if (!bindings)
        {
            SDL_LogError(0, "Failed to allocate memory for descriptor set bindings");
            return VK_ERROR_OUT_OF_HOST_MEMORY;
        }

        SDL_memset(bindings, 0, sizeof(VkDescriptorSetLayoutBinding) * binding_count);

        for (uint32_t j = 0; j < set_design->bind_design_count; j++)
        {
            const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
            if( !bind ) continue;

            bindings[j] = (VkDescriptorSetLayoutBinding){
                .binding = j,
                .descriptorType = bind->type,
                .descriptorCount = bind->count,
                .stageFlags = BuildStageFlags(bind)
            };
        }

        *out_bindings = bindings;
    }
    else
    {
        *out_bindings = NULL;
    }

    return VK_SUCCESS;
}

static VkResult CreateDescriptorSetLayout(
    VkDevice device,
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    VkDescriptorSetLayout* out_dsetLayout)
{
    VkResult result = VK_ERROR_UNKNOWN;

    if(set_design->bind_design_count)
    {
        uint32_t binding_count = CountDescriptorSetLayoutBindings(set_design);

        VkDescriptorSetLayoutBinding* bindings = NULL;
        result = CreateDescriptorSetLayoutBindings(set_design, binding_count, &bindings);

        if (result != VK_SUCCESS)
        {
            return result;
        }

        VkDescriptorSetLayoutCreateInfo setLayoutInfo = {
            .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
            .bindingCount = binding_count,
            .pBindings = bindings
        };

        result = vkCreateDescriptorSetLayout(device, &setLayoutInfo, NULL, out_dsetLayout);
        if(bindings) SDL_free(bindings);
    }
    else
    {
        out_dsetLayout = VK_NULL_HANDLE;
    }


    return result;
}

static VkResult CreatePipelineLayout(
    VkForgeLayout* layout,
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design,
    uint32_t layout_index)
{

    if( layout->pipeline_layout_buffer[layout_index] != VK_NULL_HANDLE )
    {
        SDL_LogError(0, "Pipeline Layout already created");
        return VK_SUCCESS;
    }

    if (layout->pipeline_layout_count < VKFORGE_MAX_PIPELINE_LAYOUTS)
    {
        VkDescriptorSetLayout* dsetLayouts = 0;

        if( pipeline_design->descriptorset_layout_design_count )
        {
            dsetLayouts = (VkDescriptorSetLayout*) SDL_malloc(
                sizeof(VkDescriptorSetLayout) * pipeline_design->descriptorset_layout_design_count
            );

            if ( !dsetLayouts )
            {
                SDL_LogError(0, "Failed to allocate memory for descriptor set layouts");
                return VK_ERROR_OUT_OF_HOST_MEMORY;
            }

            for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
            {
                const VkForgeLayoutDescriptorSetLayoutDesign* set_design =
                    pipeline_design->descriptorset_layout_design_buffer[i];

                if(set_design->bind_design_count)
                {
                    VkResult result = CreateDescriptorSetLayout(layout->device, set_design, &dsetLayouts[i]);
                    if (result != VK_SUCCESS)
                    {
                        SDL_LogError(0, "Failed to create descriptor set layout");
                        for (uint32_t j = 0; j < i; j++)
                        {
                            vkDestroyDescriptorSetLayout(layout->device, dsetLayouts[j], NULL);
                        }
                        SDL_free(dsetLayouts);
                        return result;
                    }

                    // Store the created descriptor set layout
                    if(layout->descriptorset_layout_count < VKFORGE_MAX_DESCRIPTORSET_LAYOUTS)
                    {
                        if(dsetLayouts[i])
                            layout->descriptorset_layout_buffer[layout->descriptorset_layout_count++] = dsetLayouts[i];
                    }
                    else
                    {
                        SDL_LogError(0, "Can not store newly created DescriptorSet. VKFORGE_MAX_DESCRIPTORSET_LAYOUTS exceeded!");
                        return VK_ERROR_UNKNOWN;
                    }
                }
                else
                {
                    dsetLayouts[i] = VK_NULL_HANDLE;
                }
            }
        }



        VkPipelineLayoutCreateInfo layoutInfo = {
            .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
            .setLayoutCount = pipeline_design->descriptorset_layout_design_count,
            .pSetLayouts = dsetLayouts,
            .pushConstantRangeCount = 0,
            .pPushConstantRanges = NULL
        };

        VkPipelineLayout pipelineLayout;
        VkResult result = vkCreatePipelineLayout(layout->device, &layoutInfo, NULL, &pipelineLayout);
        SDL_free(dsetLayouts);

        if (result != VK_SUCCESS)
        {
            SDL_LogError(0, "Failed to create pipeline layout");
            return result;
        }

        // Store the created pipeline layout
        layout->pipeline_layout_buffer[layout_index] = pipelineLayout;
        layout->pipeline_layout_count ++;
    }
    else
    {
        SDL_LogError(0, "Pipeline Layout Buffer exceeded when attempted to create new pipeline layout");
        return VK_ERROR_UNKNOWN;
    }

    return VK_SUCCESS;
}

VkResult VkForge_CreatePipeline(VkForgeLayout* layout, const char* pipeline_name)
{
    assert(layout);
    assert(pipeline_name);
    assert(layout->device);

    // Check if pipeline already exists
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {
        SDL_LogError(0, "Pipeline creation function not found for %s", pipeline_name);
        return VK_ERROR_UNKNOWN;
    }

    if (layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {
        SDL_Log("Pipeline %s already exists", pipeline_name);
        return VK_SUCCESS;
    }

    if (layout->pipeline_count < VKFORGE_MAX_PIPELINES)
    {

        // Find the pipeline layout index in the global design
        uint32_t layout_index = FindPipelineLayoutIndex(pipeline_name);
        if (layout_index == UINT32_MAX)
        {
            SDL_LogError(0, "Pipeline layout not found for %s", pipeline_name);
            return VK_ERROR_UNKNOWN;
        }

        // Create pipeline layout if it doesn't exist
        if (layout->pipeline_layout_buffer[layout_index] == VK_NULL_HANDLE)
        {
            const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
                VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[layout_index];

            VkResult result = CreatePipelineLayout(layout, pipeline_design, layout_index);
            if (result != VK_SUCCESS)
            {
                return result;
            }
        }

        /// DYNAMIC RENDERING REQUIRED STRUCTURE ///
        VkSurfaceFormatKHR surfaceFormat = VkForge_GetSurfaceFormat(
            layout->surface,
            layout->physical_device,
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
            layout->device,
            layout->pipeline_layout_buffer[layout_index]
        );

        if (pipeline == VK_NULL_HANDLE)
        {
            SDL_LogError(0, "Failed to create pipeline %s", pipeline_name);
            return VK_ERROR_UNKNOWN;
        }

        // Store the pipeline at its predefined index
        layout->pipeline_buffer[pipeline_func->pipeline_index] = pipeline;
        layout->pipeline_count ++;
    }
    else
    {
        SDL_LogError(0, "Pipeline Buffer exceeded when attempted to create new pipeline %s", pipeline_name);
        return VK_ERROR_UNKNOWN;
    }

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


