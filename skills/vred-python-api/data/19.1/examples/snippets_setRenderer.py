# setRenderer
# source: setRenderer.html

# © 2026 Autodesk, Inc. All rights reserved.

# A function to switch the active renderer in VRED.

def setRenderer(name):
    """Switch the active renderer.

    This provides the same renderer choices as the --renderer command line parameter.

    Args:
        name: The renderer to activate. Valid choices are:
            - "gl"    - OpenGL rasterization
            - "vk"    - Vulkan rasterization
            - "cpurt" - CPU Raytracing
            - "gpurt" - GPU Raytracing
    """
    if name == "gl":
        vrRenderSettings.setRasterizationMode(0)
        vrOSGWidget.enableRaytracing(False)
    elif name == "vk":
        vrRenderSettings.setRasterizationMode(1)
        vrOSGWidget.enableRaytracing(False)
    elif name == "cpurt":
        vrRenderSettings.setRaytracingMode(0)
        vrOSGWidget.enableRaytracing(True)
    elif name == "gpurt":
        vrRenderSettings.setRaytracingMode(1)
        vrOSGWidget.enableRaytracing(True)
    else:
        raise ValueError(f"Invalid renderer name '{name}'")


# Switch to the Vulkan renderer
setRenderer("vk")
