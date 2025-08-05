from vkforge.context import VkForgeContext
from vkforge.mappings import *

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

def CreateForgeLayoutDesign(ctx: VkForgeContext) -> str:
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

def GetPipelineStrings(ctx: VkForgeContext):
    return [
        CreateForgeLayoutDesign(ctx)
    ]