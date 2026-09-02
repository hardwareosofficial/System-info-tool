function Component()
{
    // Default constructor
}

Component.prototype.createOperations = function()
{
    // Call default implementation to install the component's content
    component.addOperations(createOperations);
    
    // Add platform-specific operations
    if (systemInfo.productType === "windows") {
        // Create desktop shortcut on Windows
        component.addOperation("CreateShortcut",
            "@TargetDir@/SystemInfoTool.exe",
            "@DesktopDir@/SystemInfoTool.lnk");
        
        // Create Start Menu shortcut
        component.addOperation("CreateShortcut",
            "@TargetDir@/SystemInfoTool.exe",
            "@StartMenuDir@/SystemInfoTool.lnk");
    } else if (systemInfo.productType === "osx") {
        // Create application symlink on macOS
        component.addOperation("CreateShortcut",
            "@TargetDir@/SystemInfoTool.app",
            "@ApplicationsDir@/SystemInfoTool.app");
    } else {
        // Create desktop shortcut on Linux
        component.addOperation("CreateShortcut",
            "@TargetDir@/SystemInfoTool",
            "@DesktopDir@/SystemInfoTool.desktop");
    }
}