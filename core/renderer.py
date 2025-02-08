import os
import re
import markdown

class Renderer:
    def __init__(self):
        pass

    def render(self, markdown_text: str) -> str:
        # Simply return the trimmed text, assuming it is already HTML.
        return markdown_text.strip()

    def save_rendered(self, html_output, file_path):
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(html_output)

    def get_theme_variables(self) -> str:
        """Extract the inner CSS variable definitions from dark_theme.qss and escape curly braces for formatting."""
        qss_path = os.path.join(os.path.dirname(__file__), "..", "resources", "dark_theme.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as file:
                qss_content = file.read()
            # Extract block between THEME_VARIABLES_START and THEME_VARIABLES_END
            m = re.search(r'/\* THEME_VARIABLES_START \*/(.*?)/\* THEME_VARIABLES_END \*/',
                          qss_content, flags=re.DOTALL)
            if m:
                block = m.group(1).strip()
                # Extract only the content inside the first :root { ... } block if present
                m_inner = re.search(r':root\s*{(.*)}', block, flags=re.DOTALL)
                if m_inner:
                    vars_content = m_inner.group(1).strip()
                else:
                    vars_content = block
                # Escape literal braces for .format()
                return vars_content.replace("{", "{{").replace("}", "}}")
            else:
                return ""
        except Exception as e:
            print(f"Error reading theme variables: {e}")
            return ""