from dataclasses import dataclass
from .schema import VkForgeConfig
from .shader import VkForgeShaderConfig
from .layout import VkForgeLayout


@dataclass
class VkForgeContext:
    sourceDir: str = None
    buildDir: str = None
    forgeConfig: VkForgeConfig = None
    shaderConfig: VkForgeShaderConfig = None
    layout: VkForgeLayout = None
