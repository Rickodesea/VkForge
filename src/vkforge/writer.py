import os
from pathlib import Path
from vkforge.context import VkForgeContext
from vkforge.translators import GetCoreStrings

CORE_FILE = "core.c"
TYPES_INCLUDE = '#include "types.h"'
DECLARES_INCLUDE = '#include "declares.h"'


def IncludeStandardHeaders():
    return """\
#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>
"""


def WriteCMakeLists(ctx: VkForgeContext):
    pass


def WriteCore(ctx: VkForgeContext):
    content = """\
{standard_includes}
{types_include}
{declares_include}

{code}

"""
    output = content.format(
        standard_includes=IncludeStandardHeaders(),
        types_include=TYPES_INCLUDE,
        declares_include=DECLARES_INCLUDE,
        code="\n".join(GetCoreStrings(ctx)),
    )

    filename = CORE_FILE
    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(output)
        print(f"Generated '{filepath}'")


def Generate(ctx: VkForgeContext):
    WriteCore(ctx)
