from .schema import VkForgeConfig
from .shader import ShaderConfig
from dataclasses import dataclass
from typing import List

@dataclass
class DesignInfo:
    fc: VkForgeConfig = None
    sc: ShaderConfig = None

def design_name(di: DesignInfo, name: str | list[str]) -> str:
    style = di.fc.namestyle if di.fc.namestyle else "snake_case"
    space = di.fc.namespace

    if isinstance(name, str):
        if style == "snake_case":
            if space: 
                return f"{space}{name.strip()}"
            else:
                return f"{name.strip()}"
        if style == "pascal_case" or style == "camel_case":
            if space:
                return f"{space}{name.strip().capitalize()}"
            else:
                return f"{name.strip().capitalize()}"
    elif isinstance(name, list):
        if style == "snake_case":
            if space:
                return f"{space}{'_'.join([n.strip() for n in name])}"
            else:
                return f"{'_'.join([n.strip() for n in name])}"
        if style == "pascal_case":
            if space:
                return f"{space}{'_'.join([n.strip().capitalize() for n in name])}"
            else:
                return f"{'_'.join([n.strip().capitalize() for n in name])}"
        if style == "camel_case":
            if space:
                return f"{space}{''.join([n.strip().capitalize() for n in name])}"
            else:
                return f"{''.join([n.strip().capitalize() for n in name])}"
