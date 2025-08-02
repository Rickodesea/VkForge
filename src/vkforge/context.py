from dataclasses import dataclass
from .schema import VkForgeModel
from .shader import VkForgeShaderConfig
from .layout import VkForgeLayout


@dataclass
class VkForgeContext:
    sourceDir: str = None
    buildDir: str = None
    forgeConfig: VkForgeModel = None
    shaderConfig: VkForgeShaderConfig = None
    layout: VkForgeLayout = None
