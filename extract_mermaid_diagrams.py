"""
Mermaid Diagram Extractor
Extracts Mermaid diagrams from markdown files and saves them as PNG images.

Requirements:
    pip install playwright
    python -m playwright install chromium

Usage:
    python extract_mermaid_diagrams.py
"""

import re
import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


class MermaidExtractor:
    def __init__(self, docs_dir="docs", output_dir="docs/images"):
        self.docs_dir = Path(docs_dir)
        self.output_dir = Path(output_dir)
        self.mermaid_live_url = "https://mermaid.live/"

    def extract_mermaid_blocks(self, markdown_file):
        """Extract all Mermaid code blocks from a markdown file."""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all mermaid code blocks
        pattern = r'```mermaid\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        return matches

    def generate_figure_name(self, chapter_name, index, diagram_content):
        """Generate a descriptive filename for the diagram."""
        # Extract chapter number
        chapter_match = re.search(r'CHAPTER_(\d+)', chapter_name)
        chapter_num = chapter_match.group(1) if chapter_match else "X"

        # Try to infer diagram type from content
        diagram_type = "diagram"
        content_lower = diagram_content.lower()

        if "graph tb" in content_lower or "graph lr" in content_lower:
            diagram_type = "architecture"
        elif "sequencediagram" in content_lower:
            diagram_type = "sequence"
        elif "erdiagram" in content_lower:
            diagram_type = "er_diagram"
        elif "statediagram" in content_lower:
            diagram_type = "state_machine"
        elif "flowchart" in content_lower:
            diagram_type = "flowchart"

        # Generate filename
        filename = f"fig_{chapter_num}_{index}_{diagram_type}.png"
        return filename

    async def save_mermaid_as_png(self, mermaid_code, output_path):
        """Use Playwright to render Mermaid diagram and save as PNG."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Go to Mermaid Live Editor
            await page.goto(self.mermaid_live_url)

            # Wait for editor to load
            await page.wait_for_selector('.CodeMirror', timeout=10000)

            # Clear existing content and insert mermaid code
            await page.evaluate("""
                const editor = document.querySelector('.CodeMirror').CodeMirror;
                editor.setValue('');
            """)

            await page.type('.CodeMirror textarea', mermaid_code)

            # Wait for diagram to render
            await page.wait_for_timeout(2000)

            # Find the SVG element containing the diagram
            svg_element = await page.query_selector('#view svg')

            if svg_element:
                # Take screenshot of the SVG
                await svg_element.screenshot(path=str(output_path))
                print(f"✓ Saved: {output_path.name}")
            else:
                print(f"✗ Failed to render: {output_path.name}")

            await browser.close()

    async def process_chapter(self, chapter_file):
        """Process a single chapter file and extract all diagrams."""
        print(f"\n{'='*60}")
        print(f"Processing: {chapter_file.name}")
        print(f"{'='*60}")

        # Extract Mermaid blocks
        mermaid_blocks = self.extract_mermaid_blocks(chapter_file)

        if not mermaid_blocks:
            print("No Mermaid diagrams found.")
            return

        print(f"Found {len(mermaid_blocks)} Mermaid diagram(s)")

        # Create output directory for this chapter
        chapter_output_dir = self.output_dir / chapter_file.stem.lower()
        chapter_output_dir.mkdir(parents=True, exist_ok=True)

        # Process each diagram
        for idx, mermaid_code in enumerate(mermaid_blocks, start=1):
            # Generate filename
            filename = self.generate_figure_name(chapter_file.stem, idx, mermaid_code)
            output_path = chapter_output_dir / filename

            # Save as PNG
            try:
                await self.save_mermaid_as_png(mermaid_code, output_path)
            except Exception as e:
                print(f"✗ Error saving {filename}: {e}")

        print(f"\nCompleted: {len(mermaid_blocks)} diagrams saved to {chapter_output_dir}")

    async def process_all_chapters(self):
        """Process all chapter markdown files in the docs directory."""
        # Find all chapter files
        chapter_files = sorted(self.docs_dir.glob("CHAPTER_*.md"))

        if not chapter_files:
            print(f"No chapter files found in {self.docs_dir}")
            return

        print(f"\n{'#'*60}")
        print(f"# Mermaid Diagram Extractor")
        print(f"# Found {len(chapter_files)} chapter file(s)")
        print(f"{'#'*60}")

        # Process each chapter
        for chapter_file in chapter_files:
            await self.process_chapter(chapter_file)

        print(f"\n{'='*60}")
        print(f"All diagrams extracted successfully!")
        print(f"Images saved to: {self.output_dir}")
        print(f"{'='*60}\n")


async def main():
    """Main entry point."""
    extractor = MermaidExtractor(
        docs_dir="docs",
        output_dir="docs/images"
    )

    await extractor.process_all_chapters()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
