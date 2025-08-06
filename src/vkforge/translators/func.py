from vkforge.context import VkForgeContext
from vkforge.mappings import *

def CreateVoidEnum(ctx: VkForgeContext) -> str:
    content = """\
#define {name}(Var, Type, Func, Sizelimit, ...) \\
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \\
    Func(__VA_ARGS__, &Var##_count, 0); \\
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \\
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \\
}} while(0)
"""
    output = content.format(name=FUNC_NAME.VOID_ENUM)

    return output

def CreateEnum(ctx: VkForgeContext) -> str:
    content = """\
#define {name}(Var, Type, Func, Sizelimit, ...) \\
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \\
    Func(__VA_ARGS__, &Var##_count, 0); \\
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \\
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \\
}} while(0)
"""
    output = content.format(name=FUNC_NAME.ENUM)

    return output

def GetFuncStrings(ctx: VkForgeContext):
    return [
        CreateEnum(ctx),
        CreateVoidEnum(ctx)
    ]