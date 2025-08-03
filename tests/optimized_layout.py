from vkforge.layout import optimize_pipeline_layouts, check_for_errors_single_descriptorsets
import json

def convert_sets_to_lists(obj):
    if isinstance(obj, dict):
        return {k: convert_sets_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, tuple):
        return [convert_sets_to_lists(i) for i in obj]
    elif isinstance(obj, list):
        return [convert_sets_to_lists(i) for i in obj]
    else:
        return obj

def js(d):
    clean_data = convert_sets_to_lists(d)
    return json.dumps(clean_data, indent=4)


# ---- SIMPLE ----
data = {
    "descriptorset_layouts": {
        "A": {"set": 1, "binding": 0, "type": "ubo", "count": 1, "stages": {"vert"}},
        "B": {"set": 1, "binding": 0, "type": "sampler2D", "count": 1, "stages": {"frag"}}
    },
    "descriptorset_layout_references": {
        "pipeline_1": ["A"],
        "pipeline_2": ["B"]
    }
}

print("DATA:", js(data), "OPTIMIZED:", js(optimize_pipeline_layouts(data)))


# ---- SPLIT ----
data = {
    "descriptorset_layouts": {
        "A": {"set": 0, "binding": 0, "type": "ubo", "count": 1, "stages": {"vert"}},
        "B": {"set": 1, "binding": 0, "type": "sampler2D", "count": 1, "stages": {"frag"}},
        "C": {"set": 0, "binding": 0, "type": "image2D", "count": 1, "stages": {"frag"}}
    },
    "descriptorset_layout_references": {
        "pipeline_1": ["A", "B"],
        "pipeline_2": ["B", "C"]
    }
}
print("DATA:", js(data), "OPTIMIZED:", js(optimize_pipeline_layouts(data)))

# ---- SINGLE MULTI-STAGE ----
data = {
    "descriptorset_layouts": {
        "A": {"set": 0, "binding": 0, "type": "ubo", "count": 1, "stages": {"vert", "frag"}},
    },
    "descriptorset_layout_references": {
        "pipeline_1": ["A"]
    }
}
print("DATA:", js(data), "OPTIMIZED:", js(optimize_pipeline_layouts(data)))

# ---- MULTI-BIND ----
data = {
    "descriptorset_layouts": {
        "A": {"set": 0, "binding": 0, "type": "ubo", "count": 1, "stages": {"vert"}},
        "B": {"set": 0, "binding": 1, "type": "ssbo", "count": 1, "stages": {"frag"}},
        "C": {"set": 0, "binding": 2, "type": "sampler2D", "count": 1, "stages": {"frag"}}
    },
    "descriptorset_layout_references": {
        "pipeline_1": ["A", "B"],
        "pipeline_2": ["B", "C"]
    }
}
print("DATA:", js(data), "OPTIMIZED:", js(optimize_pipeline_layouts(data)))

# ---- SUPER COMPLEX ----
data = {
    "descriptorset_layouts": {
        "A": {"set": 0, "binding": 0, "type": "ubo", "count": 1, "stages": {"vert"}},
        "B": {"set": 0, "binding": 1, "type": "ssbo", "count": 1, "stages": {"vert", "comp"}},
        "C": {"set": 1, "binding": 0, "type": "sampler2D", "count": 1, "stages": {"frag"}},
        "D": {"set": 1, "binding": 1, "type": "image2D", "count": 1, "stages": {"frag"}},
        "E": {"set": 2, "binding": 0, "type": "sampler", "count": 1, "stages": {"frag"}},
        "F": {"set": 2, "binding": 0, "type": "ubo", "count": 1, "stages": {"vert", "frag"}}
    },
    "descriptorset_layout_references": {
        "pipeline_1": ["A", "C"],
        "pipeline_2": ["B", "D"],
        "pipeline_3": ["E", "A"],
        "pipeline_4": ["F"],
        "pipeline_5": ["A", "B", "C", "D"]
    }
}
print("DATA:", js(data), "OPTIMIZED:", js(optimize_pipeline_layouts(data)))
