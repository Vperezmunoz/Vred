# Menu with Show Terminal button
# source: vr_terminal.html

# © 2026 Autodesk, Inc. All rights reserved.

# Create VR menu button
vr_terminal = vrImmersiveUiService.createTool("VR_Terminal")

# Set text label on button
vr_terminal.setText("Show\nTerminal")

# Set module to display when clicked
vr_terminal.setViewContent('Terminal')
