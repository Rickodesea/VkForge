from dataclasses import dataclass
from .schema import VkForgeModel


@dataclass
class VkForgeContext:
    sourceDir: str = None
    buildDir: str = None
    forgeConfig: VkForgeModel = None
    shaderConfig: dict = None
    layout: dict = None
