#version 450

// VkForge pull vertex binding information as well as other information from both
// Shader and Config.

// Per-vertex data (for a quad)
// Quad vertices (0,0), (1,0), (1,1), (0,1)
layout(location = 0) in vec2 inPosition;  // Binding at Vertex Buffer 0

// Per-instance data (from the VisualRect struct)
layout(location = 1) in vec4 inColor;     // VisualRect.color[4] // Binding at Vertex Buffer 1
layout(location = 2) in vec2 inPos;       // VisualRect.pos[2]
layout(location = 3) in vec2 inSize;      // VisualRect.size[2]

// Output to fragment shader
layout(location = 0) out vec4 fragColor;

vec2 positions[6] = vec2[](
    // First triangle (bottom-left, top-left, top-right)
    vec2(-0.5, -0.5),  // Bottom-left
    vec2(-0.5,  0.5),  // Top-left
    vec2( 0.5,  0.5),  // Top-right

    // Second triangle (bottom-left, top-right, bottom-right)
    vec2(-0.5, -0.5),  // Bottom-left
    vec2( 0.5,  0.5),  // Top-right
    vec2( 0.5, -0.5)   // Bottom-right
);

void main() {
    // Transform position (scale quad by size, then offset by position)
    vec2 worldPos = (inPosition * inSize) + inPos;
    
    // Output position (clip space)
    gl_Position = vec4(worldPos, 0.0, 1.0);
    //gl_Position = vec4(positions[gl_VertexIndex], 0.0, 1.0);
    
    // Pass color to fragment shader
    fragColor = inColor;
}