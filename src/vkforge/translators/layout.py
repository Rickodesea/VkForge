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
        
        # Filter out empty components
        filtered_components = {}
        for key, value in static_components.items():
            if value and value.strip():
                filtered_components[key] = value
            else:
                filtered_components[key] = ""
        
        output = content.format(
            static_arrays=filtered_components['static_arrays'],
            static_bind_designs=filtered_components['static_bind_designs'],
            static_descriptor_set_layouts=filtered_components['static_descriptor_set_layouts'],
            static_pipeline_layouts=filtered_components['static_pipeline_layouts'],
            static_references=filtered_components['static_references'],
            pipeline_layout_design_count=len(layouts),
            pipeline_layout_design_buffer="PIPELINE_LAYOUT_DESIGNS" if layouts else "NULL",
            reference_count=len(references),
            reference_buffer="REFERENCES" if references else "NULL"
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
    
    # Generate unique stage arrays and mapping
    stage_signatures = {}  # stage_list -> unique_name
    stage_mappings = {}    # original_name -> unique_name
    stage_arrays = []
    stage_counter = 0
    
    # First pass: collect all unique stage combinations
    for layout_idx, layout in enumerate(layouts):
        if layout:
            for set_idx, set1 in enumerate(layout):
                if set1:
                    for bind_idx, bind in enumerate(set1):
                        if bind:  # Only for non-empty bindings
                            _, _, stages = bind
                            # Convert stages to sorted tuple for uniqueness
                            stages_tuple = tuple(sorted([map_value(SHADER_STAGE_MAP, stage) for stage in stages]))
                            
                            if stages_tuple not in stage_signatures:
                                unique_name = f"STAGE_UNIT_{stage_counter:02d}"
                                stage_signatures[stages_tuple] = unique_name
                                stage_arrays.append(f"static uint32_t {unique_name}[] = {{ {', '.join(map(str, stages_tuple))} }};")
                                stage_counter += 1
                            
                            # Map original name to unique name
                            original_name = f"STAGE_{layout_idx}_{set_idx}_{bind_idx}"
                            stage_mappings[original_name] = stage_signatures[stages_tuple]
    
    # Generate stage arrays and macros
    if stage_arrays:
        components['static_arrays'] = "\n".join(stage_arrays)
        
        # Generate macro mappings
        macro_mappings = []
        for original_name, unique_name in stage_mappings.items():
            macro_mappings.append(f"#define {original_name} {unique_name}")
        
        components['static_arrays'] += "\n\n" + "\n".join(macro_mappings)

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
                            type1, count, stages = bind
                            type1 = map_value(DESCRIPTOR_TYPE_MAP, type1)
                            # Use the mapped stage name via macro
                            stage_name = f"STAGE_{layout_idx}_{set_idx}_{bind_idx}"
                            bind_designs.append(
                                "static VkForgeLayoutBindDesign BIND_" + f"{layout_idx}_{set_idx}_{bind_idx}" + " = {\n" +
                                f"    {type1}, {count}, {len(stages)}, {stage_name}\n" +
                                "};"
                            )
                            set_bind_designs.append("&BIND_" + f"{layout_idx}_{set_idx}_{bind_idx}")
                        else:
                            set_bind_designs.append("NULL")
                    
                    # Create array for this set's bind designs
                    bind_design_arrays.append(
                        "static VkForgeLayoutBindDesign* BIND_DESIGNS_" + f"{layout_idx}_{set_idx}" + "[] = {\n" +
                        "    " + ", ".join(set_bind_designs) + "\n" +
                        "};"
                    )
    
    if bind_designs or bind_design_arrays:
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
                        "static VkForgeLayoutDescriptorSetLayoutDesign DESCRIPTOR_SET_LAYOUT_" + f"{layout_idx}_{set_idx}" + " = {\n" +
                        f"    {len(set1)}, BIND_DESIGNS_{layout_idx}_{set_idx}\n" +
                        "};"
                    )
                    layout_descriptor_sets.append("&DESCRIPTOR_SET_LAYOUT_" + f"{layout_idx}_{set_idx}")
            
            # Create array for this layout's descriptor sets
            if layout_descriptor_sets:
                descriptor_set_layout_arrays.append(
                    "static VkForgeLayoutDescriptorSetLayoutDesign* DESCRIPTOR_SET_LAYOUTS_" + f"{layout_idx}" + "[] = {\n" +
                    "    " + ", ".join(layout_descriptor_sets) + "\n" +
                    "};"
                )
    
    if descriptor_set_layouts or descriptor_set_layout_arrays:
        components['static_descriptor_set_layouts'] = "\n".join(descriptor_set_layouts + descriptor_set_layout_arrays)
    
    # Generate pipeline layouts - FIXED: Generate for ALL layouts, not just non-empty ones
    pipeline_layouts = []
    pipeline_layout_entries = []
    
    for layout_idx, layout in enumerate(layouts):
        # Always generate pipeline layout, even if empty
        if layout:  # If layout has descriptor sets
            pipeline_layouts.append(
                "static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_" + f"{layout_idx}" + " = {\n" +
                f"    {len(layout)}, DESCRIPTOR_SET_LAYOUTS_{layout_idx}\n" +
                "};"
            )
        else:  # If layout is empty
            pipeline_layouts.append(
                "static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_" + f"{layout_idx}" + " = {\n" +
                "    0, NULL\n" +
                "};"
            )
        pipeline_layout_entries.append("&PIPELINE_LAYOUT_" + f"{layout_idx}")
    
    # Create array of all pipeline layouts - FIXED: Always generate the array
    if pipeline_layouts:
        pipeline_layout_array = (
            "static VkForgeLayoutPipelineLayoutDesign* PIPELINE_LAYOUT_DESIGNS[] = {\n" +
            "    " + ",\n    ".join(pipeline_layout_entries) + "\n" +
            "};"
        )
        components['static_pipeline_layouts'] = "\n".join(pipeline_layouts) + "\n" + pipeline_layout_array
    
    # Generate references
    references_list = []
    references_entries = []
    
    for i, (key, val) in enumerate(references.items()):
        references_list.append(
            "static VkForgeLayoutReferenceDesign REFERENCE_" + f"{i}" + " = {\n" +
            f"    {val}, \"{key}\"\n" +
            "};"
        )
        references_entries.append("&REFERENCE_" + f"{i}")
    
    # Create array of references
    if references_list:
        references_array = (
            "static VkForgeLayoutReferenceDesign* REFERENCES[] = {\n" +
            "    " + ",\n    ".join(references_entries) + "\n" +
            "};"
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
        ).format()
        
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

def CreateCreateForgePipelineLayout(ctx: VkForgeContext) -> str:
    content = """\
VkForgePipelineLayout VkForge_CreateForgePipelineLayout(
    VkForgeLayout *forgeLayout,
    const char *pipelineName)
{{
    assert(forgeLayout);
    assert(pipelineName);

    // Find the pipeline layout index for the given pipeline name
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipelineName);
    if (pipeline_layout_index == UINT32_MAX)
    {{
        SDL_LogError(0, "Pipeline layout not found for pipeline: %s", pipelineName);
        exit(1);
    }}

    // Get the pipeline layout design
    const VkForgeLayoutPipelineLayoutDesign *pipeline_design =
        VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

    VkForgePipelineLayout pipelineLayout = {{0}};
    pipelineLayout.pipeline_layout_index = pipeline_layout_index;
    pipelineLayout.design = (VkForgeLayoutPipelineLayoutDesign *)pipeline_design;
    pipelineLayout.descriptor_set_count = pipeline_design->descriptorset_layout_design_count;

    // Create descriptor set layouts (only if there are any)
    for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
    {{
        const VkForgeLayoutDescriptorSetLayoutDesign *set_design =
            pipeline_design->descriptorset_layout_design_buffer[i];

        VkResult result = CreateDescriptorSetLayout(
            forgeLayout->device,
            set_design,
            &pipelineLayout.descriptor_set_layouts[i]);

        if (result != VK_SUCCESS)
        {{
            SDL_LogError(0, "Failed to create descriptor set layout %u: %d", i, result);
            exit(1);
        }}
    }}

    // Create pipeline layout
    VkPipelineLayoutCreateInfo pipelineLayoutInfo = {{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .setLayoutCount = pipeline_design->descriptorset_layout_design_count,
        .pSetLayouts = pipelineLayout.descriptor_set_layouts}};

    VkResult result = vkCreatePipelineLayout(
        forgeLayout->device,
        &pipelineLayoutInfo,
        NULL,
        &pipelineLayout.pipelineLayout);

    if (result != VK_SUCCESS)
    {{
        SDL_LogError(0, "Failed to create pipeline layout: %d", result);
        exit(1);
    }}

    // Only create descriptor pool and allocate sets if we have descriptor sets
    if (pipeline_design->descriptorset_layout_design_count > 0)
    {{
        // Calculate descriptor pool requirements
        uint32_t pool_size_count = 0;
        VkDescriptorPoolSize pool_sizes[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {{0}};

        GetDescriptorPoolRequirements(pipeline_design, &pool_size_count, NULL);

        // Check if we actually have any descriptor bindings
        if (pool_size_count > 0)
        {{
            GetDescriptorPoolRequirements(pipeline_design, NULL, pool_sizes);

            // Create descriptor pool
            VkDescriptorPoolCreateInfo poolInfo = {{
                .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,
                .maxSets = pipeline_design->descriptorset_layout_design_count,
                .poolSizeCount = pool_size_count,
                .pPoolSizes = pool_sizes}};

            result = vkCreateDescriptorPool(
                forgeLayout->device,
                &poolInfo,
                NULL,
                &pipelineLayout.descriptor_pool);

            if (result != VK_SUCCESS)
            {{
                SDL_LogError(0, "Failed to create descriptor pool: %d", result);
                vkDestroyPipelineLayout(forgeLayout->device, pipelineLayout.pipelineLayout, NULL);
                exit(1);
            }}

            // Allocate descriptor sets
            VkDescriptorSetAllocateInfo allocInfo = {{
                .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,
                .descriptorPool = pipelineLayout.descriptor_pool,
                .descriptorSetCount = pipeline_design->descriptorset_layout_design_count,
                .pSetLayouts = pipelineLayout.descriptor_set_layouts}};

            result = vkAllocateDescriptorSets(
                forgeLayout->device,
                &allocInfo,
                pipelineLayout.descriptor_sets);

            if (result != VK_SUCCESS)
            {{
                SDL_LogError(0, "Failed to allocate descriptor sets: %d", result);
                vkDestroyDescriptorPool(forgeLayout->device, pipelineLayout.descriptor_pool, NULL);
                vkDestroyPipelineLayout(forgeLayout->device, pipelineLayout.pipelineLayout, NULL);
                exit(1);
            }}
        }}
        else
        {{
            // No descriptor bindings needed, no pool required
            pipelineLayout.descriptor_pool = VK_NULL_HANDLE;
            // Initialize descriptor sets to NULL handles
            for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
            {{
                pipelineLayout.descriptor_sets[i] = VK_NULL_HANDLE;
            }}
        }}
    }}
    else
    {{
        // No descriptor sets needed
        pipelineLayout.descriptor_pool = VK_NULL_HANDLE;
        // No need to initialize descriptor_sets array since count is 0
    }}

    SDL_Log("Created pipeline layout for pipeline: %s", pipelineName);
    return pipelineLayout;
}}
"""
    return content.format()

def CreateDestroyForgePipelineLayout(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_DestroyForgePipelineLayout(
    VkForgeLayout* forgeLayout, 
    VkForgePipelineLayout* pipelineLayout)
{{
    assert(forgeLayout);
    assert(pipelineLayout);

    if (pipelineLayout->descriptor_pool != VK_NULL_HANDLE)
    {{
        vkDestroyDescriptorPool(forgeLayout->device, pipelineLayout->descriptor_pool, NULL);
        pipelineLayout->descriptor_pool = VK_NULL_HANDLE;
    }}

    if (pipelineLayout->pipelineLayout != VK_NULL_HANDLE)
    {{
        vkDestroyPipelineLayout(forgeLayout->device, pipelineLayout->pipelineLayout, NULL);
        pipelineLayout->pipelineLayout = VK_NULL_HANDLE;
    }}

    for (uint32_t i = 0; i < pipelineLayout->descriptor_set_count; i++)
    {{
        if (pipelineLayout->descriptor_set_layouts[i] != VK_NULL_HANDLE)
        {{
            vkDestroyDescriptorSetLayout(forgeLayout->device, pipelineLayout->descriptor_set_layouts[i], NULL);
            pipelineLayout->descriptor_set_layouts[i] = VK_NULL_HANDLE;
        }}
    }}

    pipelineLayout->descriptor_set_count = 0;
    SDL_Log("Destroyed pipeline layout");
}}
"""
    return content.format()

def CreateIsForgePipelineLayoutCompatible(ctx: VkForgeContext) -> str:
    content = """\
bool VkForge_IsForgePipelineLayoutCompatible(
    VkForgeLayout* forgeLayout,
    const char* pipelineName,
    VkForgePipelineLayout forgePipelineLayout)
{{
    assert(forgeLayout);
    assert(pipelineName);

    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipelineName);
    return (pipeline_layout_index != UINT32_MAX && 
            pipeline_layout_index == forgePipelineLayout.pipeline_layout_index);
}}
"""
    return content.format()

def CreateCreateForgePipeline(ctx: VkForgeContext) -> str:
    content = """\
VkForgePipeline VkForge_CreateForgePipeline(
    VkForgeLayout* forgeLayout,
    const char* pipelineName,
    VkForgePipelineLayout compatibleForgePipelineLayout)
{{
    assert(forgeLayout);
    assert(pipelineName);

    // Verify compatibility
    if (!VkForge_IsForgePipelineLayoutCompatible(forgeLayout, pipelineName, compatibleForgePipelineLayout))
    {{
        SDL_LogError(0, "Pipeline layout is not compatible with pipeline: %s", pipelineName);
        exit(1);
    }}

    // Find the pipeline function
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipelineName);
    if (!pipeline_func)
    {{
        SDL_LogError(0, "Pipeline function not found for: %s", pipelineName);
        exit(1);
    }}

    /// DYNAMIC RENDERING REQUIRED STRUCTURE ///
    VkSurfaceFormatKHR surfaceFormat = VkForge_GetSurfaceFormat(
        forgeLayout->surface,
        forgeLayout->physical_device,
        VK_FORMAT_B8G8R8A8_UNORM // Default format
    );
    
    VkPipelineRenderingCreateInfo renderingInfo = {{0}};
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
    {{
        SDL_LogError(0, "Failed to create pipeline %s", pipelineName);
        exit(1);
    }}

    VkForgePipeline result = {{0}};
    result.pipeline = pipeline;
    result.pipeline_index = pipeline_func->pipeline_index;

    SDL_Log("Created pipeline: %s", pipelineName);
    return result;
}}
"""
    return content.format()

def CreateDestroyForgePipeline(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_DestroyForgePipeline(VkForgeLayout* forgeLayout, VkForgePipeline* pipeline)
{{
    assert(forgeLayout);
    assert(pipeline);

    if (pipeline->pipeline != VK_NULL_HANDLE)
    {{
        vkDestroyPipeline(forgeLayout->device, pipeline->pipeline, NULL);
        pipeline->pipeline = VK_NULL_HANDLE;
    }}

    SDL_Log("Destroyed pipeline");
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
        CreateCreateForgePipelineLayout(ctx),
        CreateDestroyForgePipelineLayout(ctx),
        CreateIsForgePipelineLayoutCompatible(ctx),
        CreateCreateForgePipeline(ctx),
        CreateDestroyForgePipeline(ctx),
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
    typedef struct VkForgeLayout VkForgeLayout;
    typedef struct VkForgePipelineLayout VkForgePipelineLayout;
    typedef struct VkForgePipeline VkForgePipeline;
    typedef struct VkForgeLayoutQueue VkForgeLayoutQueue;

    // Extern Types
    typedef struct VkForgeLayoutPipelineLayoutDesign VkForgeLayoutPipelineLayoutDesign;

    // Other Types
    typedef struct VkForgeDescriptorResourceQueue VkForgeDescriptorResourceQueue;

    struct VkForgeDescriptorResourceQueue
    {{
        VkForgeDescriptorResource resource;
        uint16_t set;
        uint16_t binding;
        uint16_t pipeline_layout_index;
        VkDescriptorType type;
        uint16_t count;
        const char *logname;
    }};

    struct VkForgeLayout
    {{
        VkSurfaceKHR surface;
        VkPhysicalDevice physical_device;
        VkDevice device;
    }};

    struct VkForgeLayoutQueue
    {{
        VkForgeDescriptorResourceQueue descriptor_resource_queue[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
        VkWriteDescriptorSet write_descriptor_set[VKFORGE_MAX_DESCRIPTOR_RESOURCES];
        uint32_t descriptor_resource_queue_count;
    }};

    struct VkForgePipelineLayout
    {{
        VkPipelineLayout pipelineLayout;
        VkForgeLayoutPipelineLayoutDesign *design;
        uint32_t pipeline_layout_index;
        uint8_t descriptor_set_count;
        VkDescriptorSetLayout descriptor_set_layouts[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
        VkDescriptorSet descriptor_sets[VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
        VkDescriptorPool descriptor_pool;
    }};

    struct VkForgePipeline
    {{
        VkPipeline pipeline;
        uint32_t pipeline_index;
    }};

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
"""
    return content.format()

def GetLayoutHeaderStrings(ctx: VkForgeContext):
    return [
        CreateForgeLayout_Header(ctx)
    ]
