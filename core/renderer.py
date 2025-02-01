class Renderer:
    def __init__(self):
        pass

    def render(self, markdown_text):
        import markdown
        html_output = markdown.markdown(markdown_text)
        return html_output

    def save_rendered(self, html_output, file_path):
        with open(file_path, 'w') as file:
            file.write(html_output)