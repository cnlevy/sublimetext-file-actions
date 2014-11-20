import sublime, sublime_plugin, os.path, shutil, json

class CopyRelativeFilenameCommand(sublime_plugin.WindowCommand):
	def __init__(self, window):
		self.window = window
		settings = sublime.load_settings('FileActions.sublime-settings')
		self.copy_filename_root_changed(settings.get("copy_filename_root"))
		settings.add_on_change("copy_filename_root", lambda : self.copy_filename_root_changed(settings.get("copy_filename_root")))
		
	def copy_filename_root_changed(self,root):
		self.root_folder = root
		self.saveRoot(root, 
			sublime.load_resource('Packages/FileActions/Side Bar.sublime-menu'), 
			os.path.join(sublime.packages_path(), 'User', 'FileActions', 'Side Bar.sublime-menu'))
		self.saveRoot(root, 
			sublime.load_resource('Packages/FileActions/Context.sublime-menu'), 
			os.path.join(sublime.packages_path(), 'User', 'FileActions', 'Context.sublime-menu'))
		
	def saveRoot(self, root, menu, saveAs):
		menu_json = json.loads(menu)
		menu_item = [item for item in menu_json if 'command' in item and item['command'] == 'copy_relative_filename'][0]
		new_caption = "Copy filename relative to "+root
		menu_item['caption'] = new_caption
		with open(saveAs,'w') as f:
			json.dump(menu_json, f, indent="\t")

	def run(self):
		file_name = self.window.active_view().file_name()
		root_path = os.path.join(self.window.folders()[0], self.root_folder.lstrip('/\\'))
		rel_name = file_name[len(root_path):].replace('\\','/').lstrip('/')
		sublime.set_clipboard(rel_name)
		sublime.status_message("Copied '"+rel_name+"' to clipboard")

class MoveFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.file_name = self.window.active_view().file_name()
		ext = os.path.splitext(self.file_name)[1]
		basename = os.path.basename(self.file_name)
		view = self.window.show_input_panel('Rename to:', self.file_name, self.on_done, None, None)
		view.sel().clear()
		view.sel().add(sublime.Region(view.size()-len(basename),view.size()-len(ext)))

	def on_done(self, new_name):
		if (os.path.exists(new_name)):
			sublime.status_message("Filename already exists. Cannot move the file")
		else:	
			os.rename(self.file_name, new_name)
			self.window.run_command('close')
			self.window.open_file(new_name)
			sublime.status_message("File moved to "+new_name)

class DuplicateFileCommand(sublime_plugin.WindowCommand):

	def run(self):
		self.file_name = self.window.active_view().file_name()
		ext = os.path.splitext(self.file_name)[1]
		basename = os.path.basename(self.file_name)
		view = self.window.show_input_panel('Copy to:', self.file_name, self.on_done, None, None)
		view.sel().clear()
		view.sel().add(sublime.Region(view.size()-len(basename),view.size()-len(ext)))

	def on_done(self, new_name):
		if (os.path.exists(new_name)):
			sublime.status_message("Filename already exists. Cannot move the file")
		else:	
			shutil.copyfile(self.file_name, new_name)
			self.window.run_command('close')
			self.window.open_file(new_name)
			sublime.status_message("File copied to "+new_name)
