from vkforge import VkForgeModel
import yaml

yml_string = """
ID: VkForge 0.5
Pipeline:
  - name: MyDefaultPipeline
    ShaderModule:
      - path: vert.spv
      - path: frag.spv
    VertexInputBindingDescription:
      - stride: Vertex
        first_location: 0
"""

# yml_path = Path(__file__).parent / "fixtures" / "my_config.yml"
# raw_data = yaml.safe_load(yml_path.read_text())


def test_forge_config():
    raw_data = yaml.safe_load(yml_string)
    forgeConfig = VkForgeModel(**raw_data)

    assert isinstance(forgeConfig.Pipeline, list)
