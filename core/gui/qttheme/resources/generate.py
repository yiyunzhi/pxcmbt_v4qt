import os
import shutil
from pathlib import Path


########################################################################
class ResourcesGenerator:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, primary, secondary, disabled, source, cache_path='theme'):
        """Constructor"""

        if cache_path.startswith('/'):
            self.index = cache_path
        elif cache_path.startswith('.'):
            self.index = cache_path[1:]
        else:
            self.index=cache_path

        self.contex = [
            (os.path.join(self.index, 'disabled'), disabled),
            (os.path.join(self.index, 'primary'), primary),
        ]

        self.source = source
        self.secondary = secondary
        self.primary = primary
        self.disabled = disabled

        for folder, _ in self.contex:
            shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder, exist_ok=True)

    # ----------------------------------------------------------------------

    def generate(self):
        """"""
        for icon in os.listdir(self.source):
            if not icon.endswith('.svg'):
                continue

            with open(os.path.join(self.source, icon), 'r') as file_input:
                _content_original = file_input.read()

                for folder, color in self.contex:
                    _new_content = self.replace_color(_content_original, color)
                    _new_content = self.replace_color(
                        _new_content, self.secondary, '#ff0000')

                    _file_to_write = os.path.join(folder, icon)
                    with open(_file_to_write, 'w') as file_output:
                        file_output.write(_new_content)

    @staticmethod
    def replace_color(content, replace, color='#0000ff'):
        """"""
        _colors = [color] + [''.join(list(color)[:i] + ['\\\n'] + list(color)[i:]) for i in range(1, 7)]
        for c in _colors:
            content = content.replace(c, replace)
        replace = '#ffffff00'
        color = '#000000'
        _colors = [color] + [''.join(list(color)[:i] + ['\\\n'] + list(color)[i:]) for i in range(1, 7)]
        for c in _colors:
            content = content.replace(c, replace)
        return content
