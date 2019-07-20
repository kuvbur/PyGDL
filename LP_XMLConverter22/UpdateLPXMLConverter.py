import os
import sys
import shutil
import stat
import subprocess

os.chdir (os.path.dirname (os.path.abspath (__file__)))

def CopyFiles (sourceFolder, destFolder, rsrcFolderName, copiedFiles):
	fileList = [
		"AttributeManager.dll",
		"BinFileTypes.txt",
		"Brep.dll",
		"BrepOperations.dll",
		"SMLibBrepOperations.dll",
        "CommandConnection.dll",
		"GDL.dll",
		"Geometry.dll",
		"Graphix.dll",
		"GSModeler.dll",
		"GSModeler2D.dll",
		"GSMSections.dll",
		"GSProfiler.dll",
		"GSRoot.dll",
		"GSTestEnvironment.dll",
		"GSUtils.dll",
		"GSXML.dll",
		"GSXMLUtils.dll",
		"GSZLib.dll",
		"GX.dll",
		"GXImage.dll",
		"GXImageBase.dll",
		"Pattern.dll",
		"InputOutput.dll",
        "JSON.dll",
        "JSONConversion.dll",
		"JACK.dll",
		"LibPartFile.dll",
		"LibraryManager.dll",
		"LP_XML.xsd",
		"LP_XML_UnusedParamsToSkip.xsd",
		"LP_XMLConv.gdl",
		"LP_XMLConverter.exe",
		"LP_XMLConverterLib.dll",
		"Math.dll",
        "Measure.dll",
		"Model3D.dll",
		"Network.dll",
		"NLib.dll",
		"NMTLib.dll",
		"ObjectDatabase.dll",
		"ProductVersion.xml",
		"ProjectFile.dll",
		"PointCloud.dll",
		"PointCloudManager.dll",
		"ProfileGeneratorEngine.dll",
		"ProfileGeometry.dll",
		"TextEngine.dll",
		"TWRoot.dll",
		"UsageLogger.dll",
		"VBAttributes.dll",
		"VBUtils.dll",
		"VectorImage.dll",
		"libbz2-1.dll",
		"libcairo-2.dll",
		"libcroco-0.6-3.dll",
		"libexpat-1.dll",
		"libffi-6.dll",
		"libfontconfig-1.dll",
		"libfreetype-6.dll",
		"libgcc_s_seh-1.dll",
		"libgdk_pixbuf-2.0-0.dll",
		"libgio-2.0-0.dll",
		"libglib-2.0-0.dll",
		"libgmodule-2.0-0.dll",
		"libgobject-2.0-0.dll",
		"libgraphite2.dll",
		"libharfbuzz-0.dll",
		"libiconv-2.dll",
		"libintl-8.dll",
		"liblzma-5.dll",
		"libpango-1.0-0.dll",
		"libpangocairo-1.0-0.dll",
		"libpangoft2-1.0-0.dll",
		"libpangowin32-1.0-0.dll",
		"libpcre-1.dll",
		"libpixman-1-0.dll",
		"libpng16-16.dll",
		"librsvg-2-2.dll",
		"libstdc++-6.dll",
		"libwinpthread-1.dll",
		"libxml2-2.dll",
		"zlib1.dll",
		"Add-Ons\\GDL\\ExprGDL.gdx",
		"Add-Ons\\GDL\\GDL Data In-Out.gdx",
		"Add-Ons\\GDL\\GDL DateTime.gdx",
		"Add-Ons\\GDL\\GDL File Manager In-Out.gdx",
		"Add-Ons\\GDL\\GDL MacAddr.gdx",
		"Add-Ons\\GDL\\GDL MVO Name.gdx",
		"Add-Ons\\GDL\\GDL PolyOperations.gdx",
		"Add-Ons\\GDL\\GDL ProjectPath.gdx",
		"Add-Ons\\GDL\\GDL Text In-Out.gdx",
		"Add-Ons\\GDL\\GDL XML In-Out.gdx",
		"Add-Ons\\GDL\\Property Data In.gdx"
	]

	success = True
	for fileName in fileList:
		sourceFile = os.path.join (sourceFolder, fileName)
		destFile = os.path.join (destFolder, fileName)
		copiedFiles.append (destFile)

		if not os.path.exists (sourceFile):
			print 'Error: Source file does not exist: ' + sourceFile
			success = False
			continue

		try:
			folderPath = os.path.split (destFile)[0]
			if not os.path.exists (folderPath):
				os.makedirs (folderPath)
			shutil.copy (sourceFile, destFile)
			os.chmod (destFile, stat.S_IWRITE)
		except:
			print 'Error: Failed to write file: ' + destFile
			success = False
			continue

		rsrcFile = os.path.split (sourceFile)[1] + '.mui'
		sourceRsrcFile = os.path.join (os.path.split (sourceFile)[0], rsrcFolderName, rsrcFile)
		destRsrcFile = os.path.join (os.path.split (destFile)[0], rsrcFolderName, rsrcFile)
		
		if not os.path.exists (sourceRsrcFile):
			continue
		
		try:
			folderPath = os.path.split (destRsrcFile)[0]
			if not os.path.exists (folderPath):
				os.makedirs (folderPath)
			shutil.copy (sourceRsrcFile, destRsrcFile)
			os.chmod (destFile, stat.S_IWRITE)
		except:
			print 'Error: Failed to write file: ' + rsrcFile
			success = False
			continue		

	return success

def GetFolderFiles (folderPath, excludeDirs, excludeFiles):
	def GetFolderFilesInternal (folderPath, excludeDirs, excludeFiles, fileList):
		for fileName in os.listdir (folderPath):
			filePath = os.path.join (folderPath, fileName)
			lastName = os.path.split (filePath)[1]
			if os.path.isdir (filePath):
				if not lastName in excludeDirs:
					GetFolderFilesInternal (filePath, excludeDirs, excludeFiles, fileList)
			else:
				if not lastName in excludeFiles:
					fileList.append (filePath)
	fileList = []
	GetFolderFilesInternal (folderPath, excludeDirs, excludeFiles, fileList)
	return fileList

def CheckFiles (destFolder, copiedFiles):
	excludeDirs = [
		'Documentation',
		'en'
	]
	excludeFiles = [
		'UpdateLPXMLConverter.py'
	]

	fileList = GetFolderFiles (destFolder, excludeDirs, excludeFiles)

	success = True;
	for filePath in fileList:
		fileFound = False
		if filePath in copiedFiles:
			fileFound = True
		else:
			fileAndExt = os.path.splitext (filePath)
			newFilePath = fileAndExt[0] + fileAndExt[1].lower ()
			if newFilePath in copiedFiles:
				fileFound = True
		if not fileFound:
			print 'Error: Unneccessary file found: ' + filePath
			success = False
			continue
	return success

def CheckLPXMLConverter (destFolder):
	exePath = os.path.join (destFolder, 'LP_XMLConverter.exe')
	exeResult = subprocess.call (exePath, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
	success = True
	if exeResult != 0:
		print 'Error: Failed to start LP_XMLConverter'
		success = False
	return success

def Main (argv):
	if len (argv) != 3:
		print 'Usage: UpdateLPXMLConverter.py <sourceFolder> <destinationFolder>'
		return 1

	sourceFolder = os.path.abspath (argv[1])
	rsrcFolderName = 'en'
	destFolder = os.path.abspath (argv[2])

	copiedFiles = []
	if not CopyFiles (sourceFolder, destFolder, rsrcFolderName, copiedFiles):
		return 1;
	if not CheckFiles (destFolder, copiedFiles):
		return 1;
	if not CheckLPXMLConverter (destFolder):
		return 1;

	print 'Successful update.'
	return 0

exit (Main (sys.argv))