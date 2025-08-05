from vkforge.context import VkForgeContext
from vkforge.mappings import *
from vkforge.schema import VkPipelineModel, VkVertexInputBindingDescriptionModel

def BuildBind(bindTuple:tuple, indent=0):
    bind = "\n"
    bind += "\t" * indent + "{\n" # open bracket
    child_indent = indent + 1
    if bindTuple:
        type1, count, stages = bindTuple
        stages = list(stages)

        type1 = map_value(DESCRIPTOR_TYPE_MAP, type1)
        for i in range(len(stages)):
            stages[i] = map_value(SHADER_STAGE_MAP, stages[i])

        bind += "\t" * child_indent + f"{type1},\n"
        bind += "\t" * child_indent + f"{count},\n"

        stage_str = "{ "
        for i, stage in enumerate(stages):
            stage_str += f"{stage}"
            if i < len(stages) - 1:
                stage_str += " | "
        stage_str += " }"

        bind += "\t" * child_indent + f"{stage_str},\n"
    else:
        bind += "\t" * child_indent + "0, 0, {0}\n"
    bind += "\t" * indent + "}" # close bracket
    return bind


def BuildSet1(setList:list, indent=0):
    set1 = "\n"
    set1 += "\t" * indent + "{\n" # open bracket
    child_indent = indent + 1
    if setList:
        set1 += "\t" * child_indent + "/** Bindings **/\n"
        set1 += "\t" * child_indent + f"{len(setList)},\n"
        set1 += "\t" * child_indent + "{" # child open
        child_indent2 = child_indent + 1
        for bind in setList:
            set1 += BuildBind(bind, child_indent2) + ",\n"
        set1 += "\t" * child_indent + "}\n" # child close
    else:
        set1 += "\n"
        set1 += "\t" * child_indent + "{0}\n"
    set1 += "\t" * indent + "}" # close bracket
    return set1

def BuildPipelineLayout(layoutList:list, indent=0):
    layout = "\n"
    layout += "\t" * indent + "{\n" # open bracket
    child_indent = indent + 1
    if layoutList:
        layout += "\t" * child_indent + "/** DescriptorSet Layouts **/\n"
        layout += "\t" * child_indent + f"{len(layoutList)},\n"
        layout += "\t" * child_indent + "{" # child open
        child_indent2 = child_indent + 1
        for set1 in layoutList:
            layout += BuildSet1(set1, child_indent2) + ",\n"
        layout += "\t" * child_indent + "}\n" # child close
    else:
        layout += "\n"
        layout += "\t" * child_indent + "{0}\n"
    layout += "\t" * indent + "}" # close bracket
    return layout

def BuildReference(key:str, val:int, indent=0):
    reference = "\n"
    reference += "\t" * indent + "{ " # open bracket
    reference += f'{val}, "{key}"'
    reference += " }" # close bracket
    return reference

def BuiledReferencedLayoutDesign(layoutsList:list, references:dict, indent=0):
    layouts = "\n"
    layouts += "\t" * indent + "{\n" # open bracket
    child_indent = indent + 1
    child_indent2 = child_indent + 1
    if layoutsList:
        layouts += "\t" * child_indent + "/** Pipeline Layouts **/\n"
        layouts += "\t" * child_indent + f"{len(layoutsList)},\n"
        layouts += "\t" * child_indent + "{" # child open
        for pipeline_layout in layoutsList:
            layouts += BuildPipelineLayout(pipeline_layout, child_indent2) + ",\n"
        layouts += "\t" * child_indent + "},\n" # child close

        layouts += "\t" * child_indent + "/** References **/\n"
        layouts += "\t" * child_indent + f"{len(references)},\n"
        layouts += "\t" * child_indent + "{" # child open
        for key, val in references.items():
            layouts += BuildReference(key, val, child_indent2) + ","
        layouts += "\n" + "\t" * child_indent + "}\n" # child close
    else:
        layouts += "\n"
        layouts += "\t" * child_indent + "0, {0}, 0, {0}\n"
    layouts += "\t" * indent + "}" # close bracket
    return layouts

def CreateForgeReferencedLayoutDesign(ctx: VkForgeContext) -> str:
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
    VkForgeLayoutBindDesign* bind_design_buffer;
}};
    
typedef struct VkForgeLayoutPipelineLayoutDesign VkForgeLayoutPipelineLayoutDesign;
struct VkForgeLayoutPipelineLayoutDesign
{{
    uint32_t descriptorset_layout_design_count;
    VkForgeLayoutDescriptorSetLayoutDesign* descriptorset_layout_design_buffer;
}};

typedef struct VkForgeLayoutReferenceDesign VkForgeLayoutReferenceDesign;
struct VkForgeLayoutReferenceDesign
{{
    uint32_t    pipeline_layout_design_index; 
    const char* pipline_name
}};

typedef struct VkForgeReferencedLayoutDesign VkForgeReferencedLayoutDesign;
struct VkForgeReferencedLayoutDesign
{{
    uint32_t pipeline_layout_design_count;
    VkForgeLayoutPipelineLayoutDesign* pipeline_layout_design_buffer;
    uint32_t reference_count;
    VkForgeLayoutReferenceDesign* reference_buffer;
}};

static VkForgeReferencedLayoutDesign VKFORGE_REFERENCED_LAYOUT_DESIGN = {forge_layout_design_content};
"""
    if ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]:
        layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
        references = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.REFERENCES]
        forge_layout_design_content = BuiledReferencedLayoutDesign(layouts, references)
    else:
        forge_layout_design_content = "{0}"
    output = content.format(forge_layout_design_content=forge_layout_design_content)

    return output

def CreateForgeLayout(ctx: VkForgeContext) -> str:
    content = """\
struct {name}
{{
    uint8_t               pipeline_count;
    VkPipeline            pipeline_buffer[{max_pipelines}];
    uint8_t               descriptorset_count;
    VkDescriptorSet       descriptorset_buffer[{max_descriptorset_layouts}];
    uint8_t               pipeline_layout_count;
    VkPipelineLayout      pipeline_layout_buffer[{max_pipeline_layouts}];
    uint8_t               descriptorset_layout_count;
    VkDescriptorSetLayout descriptorset_layout_buffer[{max_descriptorset_layouts}];
}};
"""
    output = content.format(
        name=TYPE_NAME.LAYOUT,
        max_pipelines=TYPE_NAME.MAX_PIPELINES,
        max_descriptorset_layouts=TYPE_NAME.MAX_DESCRIPTORSET_LAYOUTS,
        max_pipeline_layouts=TYPE_NAME.MAX_PIPELINE_LAYOUTS
    )

    return output

def BuildShaderStage(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    stageInfo = ""
    indent2 = indent + 1
    indent3 = indent2 + 1

    for shaderId in shaderIds:
        shader = ctx.shaderData[SHADER.LIST][shaderId]
        stageInfo += "\t" * indent + f"VkShaderModule shader_{shader[SHADER.MODE]} = "
        stageInfo += f"{FUNC_NAME.SHADER}(device, \"{shader[SHADER.BINPATH].as_posix()}\");\n"
        stageInfo += "\t" * indent + f"if( VK_NULL_HANDLE == shader_{shader[SHADER.MODE]} )\n"
        stageInfo += "\t" * indent + "{\n"
        stageInfo += "\t" * indent2 + f'SDL_LogError(0, "Failed to create {shader[SHADER.MODE]} shader for {pipelineName} pipeline\\n");\n'
        stageInfo += "\t" * indent2 + "exit(1);\n"
        stageInfo += "\t" * indent + "}\n\n"

    stageInfo += "\t" * indent + "VkPipelineShaderStageCreateInfo stageInfo[] =\n"
    stageInfo += "\t" * indent + "{\n"

    for shaderId in shaderIds:
        stageInfo += "\t" * indent2 + "{\n"

        shader = ctx.shaderData[SHADER.LIST][shaderId]

        stageInfo += "\t" * indent3 + ".sType  = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,\n"
        stageInfo += "\t" * indent3 + ".stage  = " + f"{map_value(SHADER_STAGE_MAP, shader[SHADER.MODE])},\n"
        stageInfo += "\t" * indent3 + ".module = " + f"shader_{shader[SHADER.MODE]},\n"
        stageInfo += "\t" * indent3 + ".pName  = " + f"\"{shader[SHADER.ENTRYNAME]}\",\n"

        stageInfo += "\t" * indent2 + "},\n"

    stageInfo += "\t" * indent + "};\n"
    return stageInfo

def BuildInputBinding(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    binding = "\n"
    indent2 = indent + 1
    indent3 = indent2 + 1

    binding += "\t" * indent + "VkVertexInputBindingDescription bindingDesc[] =\n"
    binding += "\t" * indent + "{\n"

    for i, inputBinding in enumerate(pipelineModule.VertexInputBindingDescription):
        rate = inputBinding.inputRate
        if inputBinding.stride_kind == 'TYPE':
            stride = f"sizeof({inputBinding.stride})"
        else:
            stride = inputBinding.stride
        
        binding += "\t" * indent2 + "{\n"

        binding += "\t" * indent3 + f".binding = {i},\n"
        binding += "\t" * indent3 + f".stride = {stride},\n"
        binding += "\t" * indent3 + f".binding = {map_value(INPUT_RATE_MAP, rate)},\n"

        binding += "\t" * indent2 + "},\n"
    
    binding += "\t" * indent + "};\n"

    return binding

def GetInputAttributeList(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
) -> list:
    attribute_list = []
    binding_list = []
    
    for i, inputBinding in enumerate(pipelineModule.VertexInputBindingDescription):
        binding_list.append((i, inputBinding.first_location, inputBinding.inputRate, inputBinding.stride_kind))
    
    # Handle case where first_location 0 is not in the list
    if not any(b[1] == 0 for b in binding_list):
        binding_list.append((len(binding_list), 0, 'VK_VERTEX_INPUT_RATE_VERTEX', 'INT'))
    
    # Sort binding_list by binding first, first_location second
    binding_list.sort(key=lambda x: (x[0], x[1]))

    for shaderId in shaderIds:
        shader = ctx.shaderData[SHADER.LIST][shaderId]
        
        # input binding / attribute applies to only vertex shaders
        mode = shader[SHADER.MODE]
        if not mode == "vert":
            continue
        
        reflect = shader[SHADER.REFLECT]
        input_list = reflect.get(REFLECT.INPUT, {})
        for input_item in input_list:
            location = input_item["location"]
            type1 = input_item["type"]
            attribute = {
                ATTR.LOCATION: location,
                ATTR.FORMAT: map_dict(GLSL_TYPE_MAP, type1, "format"),
                ATTR.SIZE: map_dict(GLSL_TYPE_MAP, type1, "size")
            }
            attribute_list.append(attribute)
    
    def GetBindingInfo(binding_list, attribute):
        location = attribute[ATTR.LOCATION]
        # Find the binding with the largest first_location <= location
        candidates = [b for b in binding_list if b[1] <= location]
        if not candidates:
            return binding_list[0]  # default to first binding
        # Return the binding with largest first_location <= location
        return max(candidates, key=lambda x: x[1])
    
    for i in range(len(attribute_list)):
        bindingInfo = GetBindingInfo(binding_list, attribute_list[i])
        binding, _, _, _ = bindingInfo
        attribute_list[i][ATTR.BINDING] = binding

    # Sort attribute list by binding first and location second
    attribute_list.sort(key=lambda x: (x[ATTR.BINDING], x[ATTR.LOCATION]))

    def GetAttributeIndexList(attribute_list, binding):
        return [i for i, attr in enumerate(attribute_list) if attr[ATTR.BINDING] == binding]
    
    for binding, _, _, kind in binding_list:
        attribute_index_list = GetAttributeIndexList(attribute_list, binding)
        if kind == 'TYPE' and pipelineModule.VertexInputBindingDescription[binding].stride_members:
            members = pipelineModule.VertexInputBindingDescription[binding].stride_members
            type1 = pipelineModule.VertexInputBindingDescription[binding].stride
            for i, index in enumerate(attribute_index_list):
                if i < len(members):
                    attribute_list[index][ATTR.OFFSET] = f"offsetof({type1}, {members[i]})"
        else:
            sizeoffset = "0"
            for index in attribute_index_list:
                attribute_list[index][ATTR.OFFSET] = sizeoffset
                sizeoffset += " + " + attribute_list[index][ATTR.SIZE]
    
    return attribute_list
                
def BuildInputAttribute(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    attribute = "\n"
    indent2 = indent + 1
    indent3 = indent2 + 1

    attribute += "\t" * indent + "VkVertexInputAttributeDescription attributeDesc[] =\n"
    attribute += "\t" * indent + "{\n"

    attribute_list = GetInputAttributeList(ctx, pipelineModule, pipelineName, shaderIds)

    if attribute_list:
        for attribute_item in attribute_list:
            attribute += "\t" * indent2 + "{\n"

            attribute += "\t" * indent3 + f".binding = {attribute_item[ATTR.BINDING]},\n"
            attribute += "\t" * indent3 + f".location = {attribute_item[ATTR.LOCATION]},\n"
            attribute += "\t" * indent3 + f".format = {attribute_item[ATTR.FORMAT]},\n"
            attribute += "\t" * indent3 + f".offset = {attribute_item[ATTR.OFFSET]},\n"

            attribute += "\t" * indent2 + "},\n"
    else:
        attribute += "\t" * indent2 + "0\n"

    attribute += "\t" * indent + "};\n"
    return attribute

def BuildPipeline(ctx: VkForgeContext, pipelineModule:VkPipelineModel):
    pipelineName = pipelineModule.name
    shaderIds = ctx.shaderData[SHADER.COMBO][pipelineName]

    pipeline = ""
    pipeline += BuildShaderStage(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildInputBinding(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildInputAttribute(ctx, pipelineModule, pipelineName, shaderIds)

    return pipeline

def CreatePipelines(ctx: VkForgeContext):
    pipelines = ""
    for pipelineModule in ctx.forgeModel.Pipeline:
        pipelines += BuildPipeline(ctx, pipelineModule)
    
    return pipelines

def GetPipelineStrings(ctx: VkForgeContext):
    return [
        CreateForgeReferencedLayoutDesign(ctx),
        CreateForgeLayout(ctx),
        CreatePipelines(ctx)
    ]