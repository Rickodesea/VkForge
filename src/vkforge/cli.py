import yaml
import json
import argparse
import os
from pathlib import Path
from .schema import VkForgeConfig
from .mappings import K
from .shader import load_shader_config
from typing import Any
from dataclasses import is_dataclass, asdict, fields
from pydantic import BaseModel
from pathlib import Path

def deep_serialize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: deep_serialize(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [deep_serialize(v) for v in obj]

    elif isinstance(obj, tuple):
        return tuple(deep_serialize(v) for v in obj)

    elif isinstance(obj, set):
        return {deep_serialize(v) for v in obj}

    elif isinstance(obj, Path):
        return str(obj)

    elif isinstance(obj, BaseModel):
        # Recursively deep-walk model fields BEFORE dumping
        values = {k: deep_serialize(v) for k, v in obj.model_dump().items()}
        return values

    elif is_dataclass(obj):
        # Recursively deep-walk dataclass fields BEFORE dumping
        data = {f.name: deep_serialize(getattr(obj, f.name)) for f in fields(obj)}
        return data

    else:
        return obj


def load_file(config_path: str) -> dict:
    config_path:Path = Path(config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Can not find {config_path} file.")
    
    if config_path.suffix.lower() in {".yaml", ".yml"}:
        with open(config_path) as f:
            return yaml.safe_load(f)
    elif config_path.suffix.lower() == ".json":
        with open(config_path) as f:
            return json.load(f)
    else:
        raise ValueError(f"Can determine file type from extension: {config_path.suffix}")

def main():
    parser = argparse.ArgumentParser(description='VkForge - Vulkan API Implemention Generation for Renderer Development.')
    parser.add_argument('config_path', help='Relative or Absolute Path to VkForge Implementation VkForgeConfig. It may be YAML or JSON file. File type is determined by its extension.')
    parser.add_argument('--impl-dir', default='vkforge_impl', help='Directory where VkForge Source Implementation is generated. It is created if it does not exist. If the directory is not an absolute path then the directory is considered relative to the current working directory of the running VkForge script.')
    parser.add_argument(
        '--config-roots',
        help='Directories from which all path references (for example, shader path) in the VkForge config are relative to. Each path in the config, it is first checked by itself then by each path in --config-roots in order.',
        nargs='*',   # Accept 0 or more paths
        default=[]   # Fallback if user omits it
    )
    parser.add_argument('--shader-build-dir', default='build/bin', help='Directory compiled shaders are saved. If the paths of the shaders in the config are GLSL source instead of SPIR-V binaries, then VkForge will leverage glslangValidator to compile the shaders and store the SPIR-V in this directory.')

    args = parser.parse_args()
    raw_data = load_file(args.config_path)

    forgeConfig = VkForgeConfig(**raw_data)
    shaderConfig = load_shader_config(args.config_roots, args.shader_build_dir, forgeConfig)


    inst = {
        K.ROOTS: args.config_roots,
        K.FORGE: forgeConfig,
        K.SHADER: shaderConfig
    }


    print(json.dumps(deep_serialize(inst), indent=4))

if __name__ == '__main__':
    main()

#from importlib.resources import files
#template_path = files("vkforge.templates") / "template1.glsl"
#print(template_path.read_text())

