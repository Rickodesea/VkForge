from vkforge.context import VkForgeContext
from vkforge.mappings import *

def Create_LayoutMaxes(ctx: VkForgeContext) -> str:
    content = """\
"""
    output = content.format()

    return output

def BuildStageArray(stages, index):
    """Generate a static stage array with a unique name based on index"""
    stage_str = "static uint32_t STAGE_{0}[] = {{ ".format(index)
    for i, stage in enumerate(stages):
        stage_str += f"{stage}"
        if i < len(stages) - 1:
            stage_str += ", "
    stage_str += " };"
    return stage_str
  
def BuildBind(bindTuple: tuple, index: int, indent=0):
    """Build a bind structure with proper static stage array"""
    bind = "\n"
    bind += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    
    if bindTuple:
        type1, count, stages = bindTuple
        stages = list(stages)

        type1 = map_value(DESCRIPTOR_TYPE_MAP, type1)
        for i in range(len(stages)):
            stages[i] = map_value(SHADER_STAGE_MAP, stages[i])

        bind += "\t" * child_indent + f"{type1},\n"
        bind += "\t" * child_indent + f"{count},\n"
        bind += "\t" * child_indent + f"{len(stages)},\n"
        bind += "\t" * child_indent + f"STAGE_{index}\n"  # Reference static array
    else:
        bind += "\t" * child_indent + "0, 0, 0, NULL\n"
    
    bind += "\t" * indent + "}"  # close bracket
    return bind

def BuildSet1(setList: list, set_index: int, indent=0):
    """Build a descriptor set layout with unique binding names"""
    set1 = "\n"
    set1 += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    
    if setList:
        set1 += "\t" * child_indent + "/** Bindings **/\n"
        set1 += "\t" * child_indent + f"{len(setList)},\n"
        set1 += "\t" * child_indent + "{"  # child open
        child_indent2 = child_indent + 1
        
        # Generate all stage arrays first
        stage_arrays = []
        bind_structures = []
        for i, bind in enumerate(setList):
            if bind:  # Only generate for non-empty bindings
                _, _, stages = bind
                stage_arrays.append(BuildStageArray(stages, f"{set_index}_{i}"))
                bind_structures.append(BuildBind(bind, f"{set_index}_{i}", child_indent2))
        
        # Add stage arrays to the output
        if stage_arrays:
            set1 = "\n".join(stage_arrays) + "\n" + set1
        
        # Add bind structures
        for bind_struct in bind_structures:
            set1 += bind_struct + ",\n"
            
        set1 += "\t" * child_indent + "}\n"  # child close
    else:
        set1 += "\n"
        set1 += "\t" * child_indent + "{0}\n"
    
    set1 += "\t" * indent + "}"  # close bracket
    return set1

def BuildPipelineLayout(layoutList: list, layout_index: int, indent=0):
    """Build a pipeline layout with unique set names"""
    layout = "\n"
    layout += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    
    if layoutList:
        layout += "\t" * child_indent + "/** DescriptorSet Layouts **/\n"
        layout += "\t" * child_indent + f"{len(layoutList)},\n"
        layout += "\t" * child_indent + "{"  # child open
        child_indent2 = child_indent + 1
        
        for i, set1 in enumerate(layoutList):
            layout += BuildSet1(set1, f"{layout_index}_{i}", child_indent2) + ",\n"
            
        layout += "\t" * child_indent + "}\n"  # child close
    else:
        layout += "\n"
        layout += "\t" * child_indent + "{0}\n"
    
    layout += "\t" * indent + "}"  # close bracket
    return layout

def BuildReference(key: str, val: int, indent=0):
    """Build a reference structure"""
    reference = "\n"
    reference += "\t" * indent + "{ "  # open bracket
    reference += f'{val}, "{key}"'
    reference += " }"  # close bracket
    return reference

def BuildReferencedLayoutDesign(layoutsList: list, references: dict, indent=0):
    """Build the complete referenced layout design with all static arrays"""
    layouts = "\n"
    layouts += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    child_indent2 = child_indent + 1
    
    if layoutsList:
        layouts += "\t" * child_indent + "/** Pipeline Layouts **/\n"
        layouts += "\t" * child_indent + f"{len(layoutsList)},\n"
        layouts += "\t" * child_indent + "{"  # child open
        
        # First collect all stage arrays to put at the beginning
        all_stage_arrays = []
        layout_structures = []
        for i, pipeline_layout in enumerate(layoutsList):
            # We'll let BuildPipelineLayout handle the stage arrays
            layout_structures.append(BuildPipelineLayout(pipeline_layout, i, child_indent2) + ",\n")
        
        # Add layout structures
        for layout_struct in layout_structures:
            layouts += layout_struct
            
        layouts += "\t" * child_indent + "},\n"  # child close

        layouts += "\t" * child_indent + "/** References **/\n"
        layouts += "\t" * child_indent + f"{len(references)},\n"
        layouts += "\t" * child_indent + "{"  # child open
        
        for key, val in references.items():
            layouts += BuildReference(key, val, child_indent2) + ","
            
        layouts += "\n" + "\t" * child_indent + "}\n"  # child close
    else:
        layouts += "\n"
        layouts += "\t" * child_indent + "0, {0}, 0, {0}\n"
    
    layouts += "\t" * indent + "}"  # close bracket
    return layouts

def CreateForgeReferencedLayoutDesign(ctx: VkForgeContext) -> str:
    """Create the complete referenced layout design with all global variables"""
    content = """\
typedef struct VkForgeLayoutBindDesign VkForgeLayoutBindDesign;
struct VkForgeLayoutBindDesign
{{
    uint32_t  type;
    uint32_t  count;
    uint32_t  mode_count;
    uint32_t* mode_buffer;
}};

typedef struct VkForgeLayoutDescriptorSetLayoutDesign VkForgeLayoutDescriptorSetLayoutDesign;
struct VkForgeLayoutDescriptorSetLayoutDesign
{{
    uint32_t bind_design_count;
    VkForgeLayoutBindDesign** bind_design_buffer;
}};
    
typedef struct VkForgeLayoutPipelineLayoutDesign VkForgeLayoutPipelineLayoutDesign;
struct VkForgeLayoutPipelineLayoutDesign
{{
    uint32_t descriptorset_layout_design_count;
    VkForgeLayoutDescriptorSetLayoutDesign** descriptorset_layout_design_buffer;
}};

typedef struct VkForgeLayoutReferenceDesign VkForgeLayoutReferenceDesign;
struct VkForgeLayoutReferenceDesign
{{
    uint32_t    pipeline_layout_design_index; 
    const char* pipeline_name;
}};

typedef struct VkForgeReferencedLayoutDesign VkForgeReferencedLayoutDesign;
struct VkForgeReferencedLayoutDesign
{{
    uint32_t pipeline_layout_design_count;
    VkForgeLayoutPipelineLayoutDesign** pipeline_layout_design_buffer;
    uint32_t reference_count;
    VkForgeLayoutReferenceDesign** reference_buffer;
}};

{static_arrays}

{static_bind_designs}

{static_descriptor_set_layouts}

{static_pipeline_layouts}

{static_references}

static VkForgeReferencedLayoutDesign VKFORGE_REFERENCED_LAYOUT_DESIGN = 
{{
    {pipeline_layout_design_count},
    {pipeline_layout_design_buffer},
    {reference_count},
    {reference_buffer}
}};
"""
    if ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]:
        layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
        references = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.REFERENCES]
        
        # Generate all the static components
        static_components = GetStaticSubComponents(layouts, references)
        
        output = content.format(
            static_arrays=static_components['static_arrays'],
            static_bind_designs=static_components['static_bind_designs'],
            static_descriptor_set_layouts=static_components['static_descriptor_set_layouts'],
            static_pipeline_layouts=static_components['static_pipeline_layouts'],
            static_references=static_components['static_references'],
            pipeline_layout_design_count=len(layouts),
            pipeline_layout_design_buffer="PIPELINE_LAYOUT_DESIGNS",
            reference_count=len(references),
            reference_buffer="REFERENCES"
        )
    else:
        output = content.format(
            static_arrays="",
            static_bind_designs="",
            static_descriptor_set_layouts="",
            static_pipeline_layouts="",
            static_references="",
            pipeline_layout_design_count=0,
            pipeline_layout_design_buffer="NULL",
            reference_count=0,
            reference_buffer="NULL"
        )
    
    return output

def GetStaticSubComponents(layouts, references):
    """Generate all static components needed for the global variable"""
    components = {
        'static_arrays': "",
        'static_bind_designs': "",
        'static_descriptor_set_layouts': "",
        'static_pipeline_layouts': "",
        'static_references': ""
    }
    
    # Generate stage arrays
    stage_arrays = []
    stage_index = 0
    for layout_idx, layout in enumerate(layouts):
        if layout:
            for set_idx, set1 in enumerate(layout):
                if set1:
                    for bind_idx, bind in enumerate(set1):
                        if bind:  # Only for non-empty bindings
                            _, _, stages = bind
                            stages = [map_value(SHADER_STAGE_MAP, stage) for stage in stages]
                            stage_arrays.append(f"static uint32_t STAGE_{layout_idx}_{set_idx}_{bind_idx}[] = {{ {', '.join(map(str, stages))} }};")
                            stage_index += 1
        else:
            stage_arrays.append("/** NO STAGES **/")

    components['static_arrays'] = "\n".join(stage_arrays)
    
    # Generate bind designs
    bind_designs = []
    bind_design_arrays = []
    for layout_idx, layout in enumerate(layouts):
        if layout:
            for set_idx, set1 in enumerate(layout):
                set_bind_designs = []
                if set1:
                    for bind_idx, bind in enumerate(set1):
                        if bind:
                            type1, count, _ = bind
                            type1 = map_value(DESCRIPTOR_TYPE_MAP, type1)
                            bind_designs.append(
                                f"static VkForgeLayoutBindDesign BIND_{layout_idx}_{set_idx}_{bind_idx} = {{\n"
                                f"    {type1}, {count}, {len(stages)}, STAGE_{layout_idx}_{set_idx}_{bind_idx}\n"
                                "};"
                            )
                            set_bind_designs.append(f"&BIND_{layout_idx}_{set_idx}_{bind_idx}")
                        else:
                            set_bind_designs.append("NULL")
                    
                    # Create array for this set's bind designs
                    bind_design_arrays.append(
                        f"static VkForgeLayoutBindDesign* BIND_DESIGNS_{layout_idx}_{set_idx}[] = {{\n"
                        f"    {', '.join(set_bind_designs)}\n"
                        "};"
                    )
        else:
            bind_design_arrays.append("/** NO BINDING **/")
    
    components['static_bind_designs'] = "\n".join(bind_designs + bind_design_arrays)
    
    # Generate descriptor set layouts
    descriptor_set_layouts = []
    descriptor_set_layout_arrays = []
    for layout_idx, layout in enumerate(layouts):
        layout_descriptor_sets = []
        if layout:
            for set_idx, set1 in enumerate(layout):
                if set1:
                    descriptor_set_layouts.append(
                        f"static VkForgeLayoutDescriptorSetLayoutDesign DESCRIPTOR_SET_LAYOUT_{layout_idx}_{set_idx} = {{\n"
                        f"    {len(set1)}, BIND_DESIGNS_{layout_idx}_{set_idx}\n"
                        "};"
                    )
                    layout_descriptor_sets.append(f"&DESCRIPTOR_SET_LAYOUT_{layout_idx}_{set_idx}")
            
            # Create array for this layout's descriptor sets
            descriptor_set_layout_arrays.append(
                f"static VkForgeLayoutDescriptorSetLayoutDesign* DESCRIPTOR_SET_LAYOUTS_{layout_idx}[] = {{\n"
                f"    {', '.join(layout_descriptor_sets) if layout_descriptor_sets else "0, NULL"}\n"
                "};"
            )
        else:
            descriptor_set_layout_arrays.append("/** NO DESCRIPTORSET LAYOUTS **/")
    
    components['static_descriptor_set_layouts'] = "\n".join(descriptor_set_layouts + descriptor_set_layout_arrays)
    
    # Generate pipeline layouts
    pipeline_layouts = []
    for layout_idx, layout in enumerate(layouts):
        layout_str = ""
        layout_str += f"static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_{layout_idx} = {{\n"
        if layout:
            layout_str += f"    {len(layout)}, DESCRIPTOR_SET_LAYOUTS_{layout_idx}\n"
        else:
            layout_str += f"    0, NULL\n"
        layout_str +=  "};"
        pipeline_layouts.append(
            layout_str
        )
    
    # Create array of all pipeline layouts
    pipeline_layout_array = (
        "static VkForgeLayoutPipelineLayoutDesign* PIPELINE_LAYOUT_DESIGNS[] = {{\n"
        "    " + ",\n    ".join([f"&PIPELINE_LAYOUT_{i}" for i in range(len(layouts))]) + "\n"
        "}};"
    )
    
    components['static_pipeline_layouts'] = "\n".join(pipeline_layouts) + "\n" + pipeline_layout_array
    
    # Generate references
    references_list = []
    for i, (key, val) in enumerate(references.items()):
        references_list.append(
            f"static VkForgeLayoutReferenceDesign REFERENCE_{i} = {{\n"
            f"    {val}, \"{key}\"\n"
            "};"
        )
    
    # Create array of references
    references_array = (
        "static VkForgeLayoutReferenceDesign* REFERENCES[] = {{\n"
        "    " + ",\n    ".join([f"&REFERENCE_{i}" for i in range(len(references))]) + "\n"
        "}};"
    )
    
    components['static_references'] = "\n".join(references_list) + "\n" + references_array
    
    return components

def CreatePipelineFunctionStruct(ctx: VkForgeContext) -> str:
    """Generate the PipelineFunction struct and array for all pipelines"""
    content = """\
typedef struct VkForgePipelineFunction VkForgePipelineFunction;
struct VkForgePipelineFunction
{{
    VkPipeline (*CreatePipelineForFunc)(
        VkAllocationCallbacks* allocator,
        void* next,
        VkDevice device,
        VkPipelineLayout pipeline_layout
    );
    const char* pipeline_name;
    uint32_t pipeline_index;
}};

{static_pipeline_functions}

static VkForgePipelineFunction** VKFORGE_PIPELINE_FUNCTIONS = PIPELINE_FUNCTIONS;
static uint32_t VKFORGE_PIPELINE_FUNCTION_COUNT = {pipeline_count};
"""
    if ctx.forgeModel.Pipeline:
        # Generate static pipeline function structs
        pipeline_funcs = []
        for i, pipeline in enumerate(ctx.forgeModel.Pipeline):
            pipeline_funcs.append(
                f"static VkForgePipelineFunction PIPELINE_FUNC_{i} = {{\n"
                f"    VkForge_CreatePipelineFor{pipeline.name},\n"
                f"    \"{pipeline.name}\",\n"
                f"    {i}\n"
                "};"
            )
        
        # Generate the array of pipeline functions
        pipeline_array = (
            "static VkForgePipelineFunction* PIPELINE_FUNCTIONS[] = {{\n"
            "    " + ",\n    ".join([f"&PIPELINE_FUNC_{i}" for i in range(len(ctx.forgeModel.Pipeline))]) + "\n"
            "}};"
        )
        
        output = content.format(
            static_pipeline_functions="\n".join(pipeline_funcs) + "\n" + pipeline_array,
            pipeline_count=len(ctx.forgeModel.Pipeline)
        )
    else:
        output = content.format(
            static_pipeline_functions="static VkForgePipelineFunction* PIPELINE_FUNCTIONS[] = {{NULL}};",
            pipeline_count=0
        )
    
    return output

def CreateCreateForgeLayout(ctx: VkForgeContext) -> str:
    content = """\
VkForgeLayout* VkForge_CreateForgeLayout
(
    VkSurfaceKHR surface, 
    VkPhysicalDevice physical_device, 
    VkDevice device
)
{{
    assert(device);

    VkForgeLayout* layout = (VkForgeLayout*)SDL_malloc(sizeof(VkForgeLayout));
    if (!layout)
    {{
        SDL_LogError(0, "Failed to allocate memory for VkForgeLayout");
        exit(1);
    }}

    // Initialize all counts to 0
    SDL_memset(layout, 0, sizeof(VkForgeLayout));

    layout->surface = surface;
    layout->physical_device = physical_device;
    layout->device = device;
    return layout;
}}
"""
    return content.format()

def CreateDestroyForgeLayout(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_DestroyForgeLayout(VkForgeLayout* forgeLayout)
{{
    if (forgeLayout)
    {{
        SDL_free(forgeLayout);
    }}
}}
"""
    return content.format()

def CreateForgeLayoutQueue(ctx: VkForgeContext) -> str:
    content = """\
VkForgeLayoutQueue* VkForge_CreateForgeLayoutQueue()
{{
    VkForgeLayoutQueue* queue = (VkForgeLayoutQueue*)SDL_malloc(sizeof(VkForgeLayoutQueue));
    if (!queue)
    {{
        SDL_LogError(0, "Failed to allocate memory for VkForgeLayoutQueue");
        exit(1);
    }}

    SDL_memset(queue, 0, sizeof(VkForgeLayoutQueue));
    return queue;
}}

void VkForge_DestroyForgeLayoutQueue(VkForgeLayoutQueue* queue)
{{
    if (queue)
    {{
        SDL_free(queue);
    }}
}}
"""
    return content.format()

def CreateFindPipelineFunction(ctx: VkForgeContext) -> str:
    content = """\
static const VkForgePipelineFunction* FindPipelineFunction(const char* pipeline_name)
{{
    for( uint32_t i = 0; i < VKFORGE_PIPELINE_FUNCTION_COUNT; i++ )
    {{
        if( strcmp(pipeline_name, VKFORGE_PIPELINE_FUNCTIONS[i]->pipeline_name) == 0 )
        {{
            return VKFORGE_PIPELINE_FUNCTIONS[i];
        }}
    }}
    return NULL;
}}
"""
    return content.format()

def CreateFindPipelineLayoutIndex(ctx: VkForgeContext) -> str:
    content = """\
static uint32_t FindPipelineLayoutIndex(const char* pipeline_name)
{{
    for( uint32_t i = 0; i < VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_count; i++ )
    {{
        if( strcmp(pipeline_name, VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_buffer[i]->pipeline_name) == 0 )
        {{
            return VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_buffer[i]->pipeline_layout_design_index;
        }}
    }}
    return UINT32_MAX;
}}
"""
    return content.format()

def CreateBuildStageFlags(ctx: VkForgeContext) -> str:
    content = """\
static VkShaderStageFlags BuildStageFlags(const VkForgeLayoutBindDesign* bind)
{{
    if (!bind || bind->mode_count == 0) return 0;
    
    VkShaderStageFlags flags = bind->mode_buffer[0];
    for (uint32_t i = 1; i < bind->mode_count; i++)
    {{
        flags |= bind->mode_buffer[i];
    }}
    return flags;
}}
"""
    return content.format()

def CreateDescriptorSetLayoutBindings(ctx: VkForgeContext) -> str:
    content = """\
static void CreateDescriptorSetLayoutBindings(
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    VkDescriptorSetLayoutBinding* out_bindings)
{{
    for (uint32_t j = 0; j < set_design->bind_design_count; j++)
    {{
        const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
        if( !bind ) continue;

        out_bindings[j] = (VkDescriptorSetLayoutBinding){{
            .binding = j,
            .descriptorType = bind->type,
            .descriptorCount = bind->count,
            .stageFlags = BuildStageFlags(bind)
        }};
    }}
}}
"""
    return content.format()

def CreateDescriptorSetLayout(ctx: VkForgeContext) -> str:
    content = """\
static VkResult CreateDescriptorSetLayout(
    VkDevice device,
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    VkDescriptorSetLayout* out_dsetLayout)
{{
    VkDescriptorSetLayoutBinding bindings[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {{0}};
    CreateDescriptorSetLayoutBindings(set_design, bindings);

    VkDescriptorSetLayoutCreateInfo setLayoutInfo = {{
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
        .bindingCount = set_design->bind_design_count,
        .pBindings = bindings
    }};

    VkResult result = vkCreateDescriptorSetLayout(device, &setLayoutInfo, NULL, out_dsetLayout);

    return result;
}}
"""
    return content.format()

def CreateGetDescriptorPoolRequirements(ctx: VkForgeContext) -> str:
    content = """\
// Updated helper function for pool requirements
static void GetDescriptorPoolRequirements(
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design,
    uint32_t*                                outDescriptorPoolSizeCount,
    VkDescriptorPoolSize*                    outDescriptorPoolSizes)
{{
    if(!outDescriptorPoolSizeCount && !outDescriptorPoolSizes) return;

    uint32_t pool_size_count = 0;
    VkDescriptorPoolSize temp_pool_sizes[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {{0}};

    // Calculate required pool sizes
    for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
    {{
        const VkForgeLayoutDescriptorSetLayoutDesign* set_design =
            pipeline_design->descriptorset_layout_design_buffer[i];

        if (!set_design) continue;

        for (uint32_t j = 0; j < set_design->bind_design_count; j++)
        {{
            const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
            if (!bind) continue;

            bool found = false;
            for (uint32_t k = 0; k < pool_size_count; k++)
            {{
                if (temp_pool_sizes[k].type == bind->type)
                {{
                    temp_pool_sizes[k].descriptorCount += bind->count;
                    found = true;
                    break;
                }}
            }}

            if (!found)
            {{
                temp_pool_sizes[pool_size_count].type = bind->type;
                temp_pool_sizes[pool_size_count].descriptorCount = bind->count;
                pool_size_count++;
            }}
        }}
    }}

    // Return the count if requested
    if (outDescriptorPoolSizeCount)
    {{
        *outDescriptorPoolSizeCount = pool_size_count;
    }}

    // Return the actual pool sizes if requested
    if (outDescriptorPoolSizes)
    {{
        for (uint32_t i = 0; i < pool_size_count; i++)
        {{
            outDescriptorPoolSizes[i] = temp_pool_sizes[i];
        }}
    }}
}}
"""
    return content.format()

def CreateQueueDescriptorResourceForForgePipelineLayout(ctx: VkForgeContext) -> str:
    content = """\
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
{{
    assert(queue);
    assert(pipelineLayout);

    if (set >= pipelineLayout->descriptor_set_count)
    {{
        SDL_LogError(0, "Set %u out of bounds for pipeline layout (max: %u)", set, pipelineLayout->descriptor_set_count);
        exit(1);
    }}

    // Get the pipeline layout design
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design = pipelineLayout->design;
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design =
        pipeline_design->descriptorset_layout_design_buffer[set];

    if (binding >= set_design->bind_design_count)
    {{
        SDL_LogError(0, "Binding %u out of bounds for set %u", binding, set);
        exit(1);
    }}

    const VkForgeLayoutBindDesign* bind_design = set_design->bind_design_buffer[binding];
    VkDescriptorType expected_type = bind_design->type;

    // Validate resource based on descriptor type
    if (VkForge_IsDescriptorTypeImage(expected_type))
    {{
        // Validate image resource
        if (resource.image.imageView == VK_NULL_HANDLE)
        {{
            SDL_LogError(0, "ImageView cannot be null for image descriptor type");
            exit(1);
        }}
        if ((expected_type == VK_DESCRIPTOR_TYPE_SAMPLER ||
             expected_type == VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER) &&
            resource.image.sampler == VK_NULL_HANDLE)
        {{
            SDL_LogError(0, "Sampler cannot be null for descriptor type %d", expected_type);
            exit(1);
        }}
    }}
    else if (VkForge_IsDescriptorTypeBuffer(expected_type))
    {{
        // Validate buffer resource
        if (resource.buffer.buffer == VK_NULL_HANDLE)
        {{
            SDL_LogError(0, "Buffer cannot be null for buffer descriptor type");
            exit(1);
        }}
    }}
    else
    {{
        SDL_LogError(0, "Unsupported descriptor type: %d", expected_type);
        exit(1);
    }}

    uint32_t already_queued_count = queue->descriptor_resource_queue_count;

    if(already_queued_count)
    {{
        // Check if this set/binding is already queued for the same pipeline layout
        for (uint32_t i = 0; i < already_queued_count; i++)
        {{
            if (queue->descriptor_resource_queue[i].set == set &&
                queue->descriptor_resource_queue[i].binding == binding &&
                queue->descriptor_resource_queue[i].pipeline_layout_index == pipelineLayout->pipeline_layout_index)
            {{
                // Check if resource handles are different
                bool needs_update = false;

                if (VkForge_IsDescriptorTypeImage(expected_type))
                {{
                    needs_update = (queue->descriptor_resource_queue[i].resource.image.imageView != resource.image.imageView ||
                                queue->descriptor_resource_queue[i].resource.image.sampler != resource.image.sampler ||
                                queue->descriptor_resource_queue[i].resource.image.imageLayout != resource.image.imageLayout);
                }}
                else if (VkForge_IsDescriptorTypeBuffer(expected_type))
                {{
                    needs_update = (queue->descriptor_resource_queue[i].resource.buffer.buffer != resource.buffer.buffer ||
                                queue->descriptor_resource_queue[i].resource.buffer.offset != resource.buffer.offset ||
                                queue->descriptor_resource_queue[i].resource.buffer.range != resource.buffer.range);
                }}

                if (needs_update)
                {{
                    // Update Resource
                    queue->descriptor_resource_queue[i].resource = resource;

                    SDL_Log("Queued Updated Resource for set %u binding %u", set, binding);
                }}
                return;
            }}
        }}
    }}

    // Check if queue is full
    if (queue->descriptor_resource_queue_count >= VKFORGE_MAX_DESCRIPTOR_RESOURCES)
    {{
        SDL_LogError(0, "Descriptor Resource Queue is full: %d Max", VKFORGE_MAX_DESCRIPTOR_RESOURCES);
        exit(1);
    }}

    // Add new entry to queue
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].resource = resource;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].set = set;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].binding = binding;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].pipeline_layout_index = pipelineLayout->pipeline_layout_index;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].type = expected_type;
    queue->descriptor_resource_queue[queue->descriptor_resource_queue_count].count = bind_design->count;

    SDL_Log("Queued Resource for set %u binding %u", set, binding);

    queue->descriptor_resource_queue_count++;
}}
"""
    return content.format()

def CreateWriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(ctx: VkForgeContext) -> str:
    content = """\
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
{{
    assert(layout);
    assert(queue);
    assert(pipelineLayout);

    if (queue->descriptor_resource_queue_count == 0)
    {{
        return;
    }}

    uint32_t write_count = 0;
    VkWriteDescriptorSet writes[VKFORGE_MAX_DESCRIPTOR_RESOURCES] = {{0}};

    // For each queued resource that belongs to this pipeline layout
    for (uint32_t i = 0; i < queue->descriptor_resource_queue_count; i++)
    {{
        VkForgeDescriptorResourceQueue* entry = &queue->descriptor_resource_queue[i];
        
        // Only process entries for this specific pipeline layout
        if (entry->pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {{
            continue;
        }}

        if (entry->set >= pipelineLayout->descriptor_set_count)
        {{
            SDL_LogError(0, "Set %u out of bounds for pipeline layout", entry->set);
            exit(1);
        }}

        VkDescriptorSet descriptorset = pipelineLayout->descriptor_sets[entry->set];

        if (descriptorset == VK_NULL_HANDLE)
        {{
            SDL_LogError(0, "Descriptor set not found for set %u", entry->set);
            exit(1);
        }}

        // Prepare the write descriptor
        writes[write_count] = (VkWriteDescriptorSet){{
            .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
            .dstSet = descriptorset,
            .dstBinding = entry->binding,
            .descriptorCount = entry->count,
            .descriptorType = entry->type,
        }};

        // Set the appropriate descriptor info
        if (VkForge_IsDescriptorTypeImage(entry->type))
        {{
            writes[write_count].pImageInfo = &entry->resource.image;
        }}
        else if (VkForge_IsDescriptorTypeBuffer(entry->type))
        {{
            writes[write_count].pBufferInfo = &entry->resource.buffer;
        }}

        SDL_Log("Preparing to Write Resource for set %u binding %u", entry->set, entry->binding);
        write_count++;
    }}

    if (write_count > 0)
    {{
        // Update all descriptor sets
        vkUpdateDescriptorSets(
            layout->device,
            write_count,
            writes,
            0, NULL
        );

        SDL_Log("Wrote %u Resources for pipeline layout", write_count);
    }}

    // Remove processed entries from the queue
    uint32_t new_index = 0;
    for (uint32_t i = 0; i < queue->descriptor_resource_queue_count; i++)
    {{
        if (queue->descriptor_resource_queue[i].pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {{
            // Keep entries for other pipeline layouts
            if (new_index != i)
            {{
                queue->descriptor_resource_queue[new_index] = queue->descriptor_resource_queue[i];
            }}
            new_index++;
        }}
    }}
    
    queue->descriptor_resource_queue_count = new_index;
}}
"""
    return content.format()

def CreateClearDescriptorResourceQueueFunctions(ctx: VkForgeContext) -> str:
    content = """\
/**
 * @brief Clears all queued descriptor resources for a specific pipeline layout
 * @param queue The VkForge layout queue instance
 * @param pipelineLayout The pipeline layout to clear queue for
 */
void VkForge_ClearDescriptorResourceQueueForForgePipelineLayout(
    VkForgeLayoutQueue* queue, 
    VkForgePipelineLayout* pipelineLayout)
{{
    assert(queue);
    assert(pipelineLayout);

    uint32_t new_index = 0;
    for (uint32_t i = 0; i < queue->descriptor_resource_queue_count; i++)
    {{
        if (queue->descriptor_resource_queue[i].pipeline_layout_index != pipelineLayout->pipeline_layout_index)
        {{
            // Keep entries for other pipeline layouts
            if (new_index != i)
            {{
                queue->descriptor_resource_queue[new_index] = queue->descriptor_resource_queue[i];
            }}
            new_index++;
        }}
    }}
    
    queue->descriptor_resource_queue_count = new_index;
}}

/**
 * @brief Clears all queued descriptor resources
 * @param queue The VkForge layout queue instance
 */
void VkForge_ClearDescriptorResourceQueue(VkForgeLayoutQueue* queue)
{{
    assert(queue);
    queue->descriptor_resource_queue_count = 0;
}}
"""
    return content.format()

def CreateBindForgePipelineLayoutPerWriteDescriptorResourceQueue(ctx: VkForgeContext) -> str:
    content = """\
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
{{
    assert(layout);
    assert(queue);
    assert(pipelineLayout);
    assert(commandBuffer);

    // First write any queued descriptor resources
    VkForge_WriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(layout, queue, pipelineLayout);

    // Bind descriptor sets to the command buffer
    if (pipelineLayout->descriptor_set_count > 0)
    {{
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
    }}
}}
"""
    return content.format()

def GetLayoutStrings(ctx: VkForgeContext):
    return [
        Create_LayoutMaxes(ctx),
        CreateForgeReferencedLayoutDesign(ctx),
        CreatePipelineFunctionStruct(ctx),
        CreateCreateForgeLayout(ctx),
        CreateDestroyForgeLayout(ctx),
        CreateForgeLayoutQueue(ctx),
        CreateFindPipelineFunction(ctx),
        CreateFindPipelineLayoutIndex(ctx),
        CreateBuildStageFlags(ctx),
        CreateDescriptorSetLayoutBindings(ctx),
        CreateDescriptorSetLayout(ctx),
        CreateGetDescriptorPoolRequirements(ctx),
        CreateQueueDescriptorResourceForForgePipelineLayout(ctx),
        CreateWriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(ctx),
        CreateClearDescriptorResourceQueueFunctions(ctx),
        CreateBindForgePipelineLayoutPerWriteDescriptorResourceQueue(ctx),
    ]

######################################################
#
# HEADER
#
######################################################

def CreateForgeLayout_Header(ctx: VkForgeContext):
    content = """\
/** DEFINES **/
#define VKFORGE_MAX_DESCRIPTOR_RESOURCES VKFORGE_MAX_DESCRIPTOR_BINDINGS

/** Main Types **/
typedef struct VkForgeLayout         VkForgeLayout;
typedef struct VkForgePipelineLayout VkForgePipelineLayout;
typedef struct VkForgePipeline       VkForgePipeline;
typedef struct VkForgeLayoutQueue    VkForgeLayoutQueue;

// Extern Types
typedef struct VkForgeLayoutPipelineLayoutDesign VkForgeLayoutPipelineLayoutDesign;

// Other Types
typedef struct VkForgeDescriptorResourceQueue VkForgeDescriptorResourceQueue;

struct VkForgeDescriptorResourceQueue
{{
    VkForgeDescriptorResource resource;
    uint16_t                  set;
    uint16_t                  binding;
    uint16_t                  pipeline_layout_index;
    VkDescriptorType          type;
    uint16_t                  count;
    const char*               logname;
}};

struct VkForgeLayout
{{
    VkSurfaceKHR          surface;
    VkPhysicalDevice      physical_device;
    VkDevice              device;
}};

struct VkForgeLayoutQueue
{{
    VkForgeDescriptorResourceQueue descriptor_resource_queue[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
    VkWriteDescriptorSet           write_descriptor_set     [VKFORGE_MAX_DESCRIPTOR_RESOURCES];
    uint32_t                       descriptor_resource_queue_count;
}};

struct VkForgePipelineLayout
{{
    VkPipelineLayout                   pipelineLayout;
    VkForgeLayoutPipelineLayoutDesign* design;
    uint32_t                           pipeline_layout_index;
    uint8_t                            descriptor_set_count;
    VkDescriptorSetLayout              descriptor_set_layouts[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
    VkDescriptorSet                    descriptor_sets[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
    VkDescriptorPool                   descriptor_pool;
}};

struct VkForgePipeline
{{
    VkPipeline pipeline;
    uint32_t   pipeline_index;
}};

/** API **/
VkForgePipelineLayout VkForge_CreateForgePipelineLayout      (VkForgeLayout* forgeLayout, const char* pipelineName);
void                  VkForge_DestroyForgePipelineLayout     (VkForgeLayout* forgeLayout, VkForgePipelineLayout* pipelineLayout);
bool                  VkForge_IsForgePipelineLayoutCompatible(VkForgeLayout* forgeLayout, const char* pipelineName, VkForgePipelineLayout forgePipelineLayout);
VkForgePipeline       VkForge_CreateForgePipeline            (VkForgeLayout* forgeLayout, const char* pipelineName, VkForgePipelineLayout compatibleForgePipelineLayout);
void                  VkForge_DestroyForgePipeline           (VkForgeLayout* forgeLayout, VkForgePipeline* pipeline);

void VkForge_QueueDescriptorResourceForForgePipelineLayout(
    VkForgeLayoutQueue* queue,
    VkForgePipelineLayout* pipelineLayout,
    uint16_t set,
    uint16_t binding,
    VkForgeDescriptorResource resource
);
void VkForge_WriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(VkForgeLayout* layout, VkForgeLayoutQueue* queue, VkForgePipelineLayout* pipelineLayout);
void VkForge_ClearDescriptorResourceQueueForForgePipelineLayout(VkForgeLayoutQueue* queue, VkForgePipelineLayout* pipelineLayout);
void VkForge_ClearDescriptorResourceQueue(VkForgeLayoutQueue* queue);
"""
    return content.format()

def GetLayoutHeaderStrings(ctx: VkForgeContext):
    return [
        CreateForgeLayout_Header(ctx)
    ]
