import os
from pathlib import Path
from vkforge.context import VkForgeContext
from vkforge.translators import *
from vkforge.mappings import *

TYPE_INCLUDE = f'#include "{FILE.TYPE}"'
FUNC_INCLUDE = f'#include "{FILE.FUNC}"'

def IncludeStandardDefinitionHeaders():
    return """\
#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>
"""

def IncludeStandardDeclarationHeaders():
    return """\
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
"""

def WriteCMakeLists(ctx: VkForgeContext):
    pass


def Write_C_Definition_Module(ctx: VkForgeContext, filename, stringFunc):
    content = """\
{standard_includes}
{type_include}
{func_include}

{code}

"""
    output = content.format(
        standard_includes=IncludeStandardDefinitionHeaders(),
        type_include=TYPE_INCLUDE,
        func_include=FUNC_INCLUDE,
        code="\n".join(stringFunc(ctx)),
    )

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(output)
        print(f"GENERATED: {filepath}")


def Write_C_Declaration_Module(ctx: VkForgeContext, filename, stringFunc):
    content = """\
#pragma once

{standard_includes}

#ifdef __cplusplus
extern "C" {{
#endif

{code}

#ifdef __cplusplus
}}
#endif
"""
    output = content.format(
        standard_includes=IncludeStandardDeclarationHeaders(),
        code="\n".join(stringFunc(ctx)),
    )

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(output)
        print(f"GENERATED: {filepath}")

def Generate(ctx: VkForgeContext):
    Write_C_Definition_Module(ctx, FILE.CORE, GetCoreStrings)
    Write_C_Definition_Module(ctx, FILE.UTIL, GetUtilStrings)
    Write_C_Definition_Module(ctx, FILE.PIPELINE_C, GetPipelineStrings)
    Write_C_Declaration_Module(ctx, FILE.TYPE, GetTypeStrings)
