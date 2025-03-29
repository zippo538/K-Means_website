import markdown
from bs4 import BeautifulSoup
from pathlib import Path
from flask import render_template
import os


class MarkdownRenderer:
    def __init__(self, template_name='pages/render_md.html', extensions=None, configs=None):
        self.template_name = template_name
        self.extensions = extensions or ['tables', 'fenced_code', 'codehilite']
        self.configs = configs or {
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False
            }
        }

    def render_file(self, md_path):
        """Render markdown file to HTML"""
        if not os.path.exists(md_path):
            raise FileNotFoundError(f"Markdown file not found: {md_path}")
        
        md_text = Path(md_path).read_text(encoding='utf-8')
        html = markdown.markdown(
            md_text,
            extensions=self.extensions,
            extension_configs=self.configs
        )
        
        return render_template(
            self.template_name,
            content=html,
            title=Path(md_path).stem.replace('_', ' ').title()
        )

    def render_text(self, md_text, title="Markdown Content"):
        """Render raw markdown text to HTML"""
        html = markdown.markdown(
            md_text,
            extensions=self.extensions,
            extension_configs=self.configs
        )
        
        return render_template(
            self.template_name,
            content=html,
            title=title
        )