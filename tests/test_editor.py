import unittest
from core.editor import Editor

class TestEditor(unittest.TestCase):

    def setUp(self):
        self.editor = Editor()

    def test_load_markdown(self):
        self.editor.load_markdown("sample.md")
        self.assertEqual(self.editor.get_content(), "# Sample Markdown\n\nThis is a sample markdown file.")

    def test_save_markdown(self):
        self.editor.set_content("# New Content")
        self.editor.save_markdown("new_sample.md")
        with open("new_sample.md", "r") as file:
            content = file.read()
        self.assertEqual(content, "# New Content")

    def test_edit_content(self):
        self.editor.set_content("# Original Content")
        self.editor.edit_content("## Edited Content")
        self.assertEqual(self.editor.get_content(), "## Edited Content")

if __name__ == '__main__':
    unittest.main()