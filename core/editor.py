class Editor:
    def __init__(self):
        self.content = ""

    def load(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.content = file.read()

    def save(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(self.content)

    def set_content(self, text):
        self.content = text

    def get_content(self):
        return self.content

    def clear(self):
        self.content = ""