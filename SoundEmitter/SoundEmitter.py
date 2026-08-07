#Copy this code in the script section of your Variants
#Works for Vred 2024
sound = vrNodeService.findNode("Engine_sound")
filename = r"ADD_YOUR_FILE_PATH_HERE"
sound.setSoundFile(filename)
sound.start()

#Copy this prt if you rork in Vred 2023
sound = findNode("Engine_sound")
filename = 'ADD_YOUR_FILE_PATH_HERE'
sound.setFieldString("soundFile", filename)
sound.setFieldBool("play", true) 
