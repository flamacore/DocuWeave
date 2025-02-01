class Controller:
    def __init__(self, editor, renderer):
        self.editor = editor
        self.renderer = renderer

    def load_markdown(self, file_path):
        content = self.editor.load(file_path)
        return content

    def save_markdown(self, file_path, content):
        self.editor.save(file_path, content)

    def render_markdown(self, markdown_text):
        html_content = self.renderer.render(markdown_text)
        return html_content

    def update_editor(self, new_content):
        self.editor.set_content(new_content)

    def get_editor_content(self):
        return self.editor.get_content()