import unittest
from core.renderer import Renderer

class TestRenderer(unittest.TestCase):

    def setUp(self):
        self.renderer = Renderer()

    def test_render_simple_markdown(self):
        markdown_text = "# Hello World"
        expected_html = "<h1>Hello World</h1>"
        self.assertEqual(self.renderer.render(markdown_text), expected_html)

    def test_render_markdown_with_bold(self):
        markdown_text = "**Bold Text**"
        expected_html = "<strong>Bold Text</strong>"
        self.assertEqual(self.renderer.render(markdown_text), expected_html)

    def test_render_markdown_with_list(self):
        markdown_text = "- Item 1\n- Item 2"
        expected_html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        self.assertEqual(self.renderer.render(markdown_text), expected_html)

    def test_render_empty_markdown(self):
        markdown_text = ""
        expected_html = ""
        self.assertEqual(self.renderer.render(markdown_text), expected_html)

if __name__ == '__main__':
    unittest.main()