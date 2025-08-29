#version 450

// VkForge pull vertex binding information as well as other information from both
// Shader and Config.

// Per-vertex data (for a quad)
// Quad vertices (0,0), (1,0), (1,1), (0,1)
layout(location = 0) in vec2 inPosition;  // Binding at Vertex Buffer 0
layout(location = 1) in vec2 inUV;

// Per-instance data (from the Entity struct)
layout(location = 2) in vec4 inColor;     // Entity.color[4] // Binding at Vertex Buffer 1
layout(location = 3) in vec2 inPos;       // Entity.pos[2]
layout(location = 4) in vec2 inSize;      // Entity.size[2]

// Output to fragment shader
layout(location = 0) out vec4 fragColor;
layout(location = 1) out vec2 fragUV;

void main() {
    // Transform position (scale quad by size, then offset by position)
    vec2 worldPos = (inPosition * inSize) + inPos;
    
    // Output position (clip space)
    gl_Position = vec4(worldPos, 0.0, 1.0);
    //gl_Position = vec4(positions[gl_VertexIndex], 0.0, 1.0);
    
    // Pass color to fragment shader
    fragColor = inColor;
    fragUV = inUV;
}