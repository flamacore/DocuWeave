class Renderer:
    def __init__(self):
        pass

    def render(self, markdown_text: str) -> str:
        import markdown
        html_output = markdown.markdown(markdown_text)
        import re
        html_output = re.sub(r'<pre><code>(.*?)</code></pre>', lambda m: m.group(1), html_output, flags=re.DOTALL)
        return html_output

    def save_rendered(self, html_output, file_path):
        with open(file_path, 'w') as file:
            file.write(html_output)