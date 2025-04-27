import markdown
from bs4 import BeautifulSoup
from pathlib import Path
from flask import render_template
import os
import re


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
    def _process_images(self, html, base_path):
        """Enhance images with lightbox and lazy loading"""
        soup = BeautifulSoup(html, 'html.parser')
        
        for img in soup.find_all('img'):
            if not img.get('src').startswith(('http', 'data:')):
                # Handle local images
                img_path = Path(base_path) / img['src']
                img['src'] = f"/static/{img_path}"
                img['data-original'] = img['src']
                img['loading'] = "lazy"
                
                # Wrap in lightbox anchor
                img.wrap(soup.new_tag("a", href=img['src'], **{
                    'data-lightbox': 'gallery',
                    'data-title': img.get('alt', '')
                }))
                
                # Add caption if alt text exists
                if img.get('alt'):
                    caption = soup.new_tag("div", **{'class': 'image-caption'})
                    caption.string = img['alt']
                    img.insert_after(caption)
        
        return str(soup)