from typing import List, Tuple, Dict
from .schema import VkForgeConfig, VkShaderModule
from pathlib import Path
import os
from .mappings import SHADER_STAGE_MAP
import subprocess
import json
from dataclasses import dataclass, field


@dataclass
class ShaderDetail:
    sm: VkShaderModule = None
    binary_path: Path = None
    source_path: Path = None
    entrypoint: Tuple[str, str] = None
    r: dict = None  # reflection details


@dataclass
class VkForgeShaderConfig:
    details: Dict[str, ShaderDetail] = field(default_factory=dict)
    combinations: List[List[str]] = field(default_factory=list)


def find_shader(roots: List[str], id: str) -> Path:
    file_path = Path(id)
    if os.path.exists(file_path):
        return file_path

    for root in roots:
        joined = os.path.join(root, id)
        file_path = Path(joined)
        if os.path.exists(file_path):
            return file_path
    raise FileNotFoundError(f"Unable to find {id} shader")


def shader_is_source(extension: str) -> bool:
    extension_list = [".glsl"]
    extension_list.extend(["." + mode for mode in SHADER_STAGE_MAP.keys()])
    return extension in extension_list


def shader_is_binary(extension: str) -> bool:
    return extension == None or extension in [".spv"]


from pathlib import Path
import subprocess


def disassemble_shader(build_dir: str, shader_path: Path, mode: str) -> Path:
    output_path = (
        Path(build_dir) / f"{shader_path.stem}.disassembled.{mode}.glsl"
    )

    Path(build_dir).mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["spirv-cross", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "spirv-cross not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    result = subprocess.run(
        [
            "spirv-cross",
            str(shader_path),
            "--version",
            "450",
            "--output",
            str(output_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"spirv-cross failed for {shader_path}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return output_path


def compile_shader(build_dir: str, shader_path: Path) -> Path:
    try:
        subprocess.run(
            ["glslangValidator", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "glslangValidator not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    build_dir = Path(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Compose output path
    output_file = build_dir / (shader_path.name + ".spv")

    # Compile GLSL to SPIR-V
    result = subprocess.run(
        ["glslangValidator", "-V", str(shader_path), "-o", str(output_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Shader compilation failed for {shader_path}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return output_file


def reflect_shader(shader_path: Path) -> dict:
    try:
        subprocess.run(
            ["spirv-cross", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "spirv-cross not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    # Run reflection
    result = subprocess.run(
        ["spirv-cross", str(shader_path), "--reflect"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"spirv-cross reflection failed for {shader_path}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    try:
        reflection_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"spirv-cross did not produce valid JSON:\n" f"Output:\n{result.stdout}"
        )

    return reflection_data


def validate_shader_entrypoint(sm: VkShaderModule, r: dict) -> Tuple[str, str]:
    if sm.pName:
        name = sm.pName.strip()
        for entrypoint in r.get("entryPoints", []):
            if name == entrypoint.get("name", ""):
                mode = entrypoint.get("mode")
                if not mode:
                    raise ValueError(
                        f"Can not confirm mode for shader {sm.path} at entrypoint {name}"
                    )
        raise ValueError(
            f"User defined entrypoint {name} is not found in shader {sm.path}"
        )
    else:
        entrypoints = r.get("entryPoints")
        if entrypoints:
            first_entrypoint = entrypoints[0]
            name = first_entrypoint.get("name")
            if not name:
                raise ValueError(
                    f"Can not confirm entrypoint name for shader {sm.path}"
                )
            mode = first_entrypoint.get("mode")
            if not mode:
                raise ValueError(
                    f"Can not confirm mode for shader {sm.path} at entrypoint {name}"
                )
    if sm.mode:
        if not sm.mode.strip() == mode:
            raise ValueError(
                f"User defined {sm.mode} mode does not match "
                "the {mode} mode extracted from {sm.path} shader."
            )
    return (name, mode)


def validate_shader_combination(build_dir: str, shaders: List[ShaderDetail]):
    try:
        subprocess.run(
            ["glslangValidator", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "glslangValidator not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    shader_sources = [str(shader.source_path) for shader in shaders]
    build_dir = Path(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    output_file = build_dir / "validation" / ("shader_validation" + ".mod")

    result = subprocess.run(
        ["glslangValidator", "-l"] + shader_sources + ["-V", "-o", output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Shader validation failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def load_shader_config(
    roots: List[str], build_dir: str, fc: VkForgeConfig
) -> VkForgeShaderConfig:
    sc = VkForgeShaderConfig()
    shader_seen = set()

    for pipeline in fc.Pipeline:
        pipeline_shaders = []
        pipeline_combinations = []
        for shader_module in pipeline.ShaderModule:
            id = shader_module.path
            pipeline_combinations.append(id)

            if not id in shader_seen:
                shader_seen.add(id)

                shader_path = find_shader(roots, id)
                shader_ext = shader_path.suffix

                if shader_is_source(shader_ext):
                    shader_source_path = shader_path
                    shader_binary_path = compile_shader(build_dir, shader_path)
                    spirv_details = reflect_shader(shader_binary_path)
                    entrypoint = validate_shader_entrypoint(
                        shader_module, spirv_details
                    )
                elif shader_is_binary(shader_ext):
                    shader_binary_path = shader_path
                    spirv_details = reflect_shader(shader_binary_path)
                    entrypoint = validate_shader_entrypoint(
                        shader_module, spirv_details
                    )
                    _, mode = entrypoint
                    shader_source_path = disassemble_shader(
                        build_dir, shader_binary_path, mode
                    )
                else:
                    raise ValueError(
                        f"Can not determine if shader is GLSL source or "
                        "SPIR-V binary from the extension: {shader_ext}"
                    )

                sd = ShaderDetail()
                sd.sm = shader_module
                sd.entrypoint = entrypoint
                sd.binary_path = shader_binary_path
                sd.source_path = shader_source_path
                sd.r = spirv_details

                sc.details[id] = sd
            else:
                sd = sc.details.get(id)
                if not sd:
                    raise ValueError(f"Could not find shader details for {id}")
            pipeline_shaders.append(sd)
        validate_shader_combination(build_dir, pipeline_shaders)
        sc.combinations.append(pipeline_combinations)
    return sc
