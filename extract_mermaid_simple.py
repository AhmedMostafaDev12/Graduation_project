"""
Simple Mermaid Diagram Extractor with High-Res PNG Conversion
Extracts Mermaid diagrams from markdown files and converts them to high-resolution PNG images.

Requirements:
    pip install subprocess (built-in)
    npm install -g @mermaid-js/mermaid-cli

Usage:
    python extract_mermaid_simple.py

    The script will:
    1. Extract all Mermaid diagrams from CHAPTER_*.md files
    2. Save them as .mmd files
    3. Automatically convert them to high-res .png files (3000px width, perfect for Word)
"""

import re
import os
import subprocess
from pathlib import Path


class SimpleMermaidExtractor:
    def __init__(self, docs_dir="docs", output_dir="docs/images", auto_convert=True):
        self.docs_dir = Path(docs_dir)
        self.output_dir = Path(output_dir)
        self.diagrams_extracted = 0
        self.auto_convert = auto_convert
        self.conversion_errors = []

    def extract_mermaid_blocks(self, markdown_file):
        """Extract all Mermaid code blocks from a markdown file."""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all mermaid code blocks with line numbers
        pattern = r'```mermaid\n(.*?)```'
        matches = []

        for match in re.finditer(pattern, content, re.DOTALL):
            # Get line number
            line_num = content[:match.start()].count('\n') + 1
            matches.append((line_num, match.group(1)))

        return matches

    def infer_diagram_type(self, diagram_content):
        """Infer diagram type from content."""
        content_lower = diagram_content.lower()

        if "erdiagram" in content_lower:
            return "er_diagram"
        elif "sequencediagram" in content_lower:
            return "sequence"
        elif "statediagram" in content_lower:
            return "state_machine"
        elif "flowchart" in content_lower:
            return "flowchart"
        elif "graph tb" in content_lower or "graph lr" in content_lower:
            return "architecture"
        else:
            return "diagram"

    def generate_figure_name(self, chapter_name, index, diagram_content):
        """Generate a descriptive filename for the diagram."""
        # Extract chapter number
        chapter_match = re.search(r'CHAPTER_(\d+)', chapter_name)
        chapter_num = chapter_match.group(1) if chapter_match else "X"

        # Infer diagram type
        diagram_type = self.infer_diagram_type(diagram_content)

        # Generate filename
        filename = f"fig_{chapter_num}_{index}_{diagram_type}"
        return filename

    def convert_mmd_to_svg(self, mmd_path):
        """Convert a .mmd file to high-resolution PNG using mermaid-cli."""
        png_path = mmd_path.with_suffix('.png')

        # Try to find mmdc command
        mmdc_cmd = 'mmdc'
        if os.name == 'nt':  # Windows
            # Use full path on Windows to avoid PATH issues
            mmdc_full_path = r'C:\Users\USER\AppData\Roaming\npm\mmdc.cmd'
            if os.path.exists(mmdc_full_path):
                mmdc_cmd = mmdc_full_path

        try:
            # Run mermaid-cli to convert to high-res PNG
            # -w 3000: Width 3000px for very high resolution
            # -b white: White background
            # -s 2: Scale 2x for even higher quality
            result = subprocess.run(
                [mmdc_cmd, '-i', str(mmd_path), '-o', str(png_path), '-w', '3000', '-b', 'white', '-s', '2'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, png_path
            else:
                error_msg = result.stderr or result.stdout
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Conversion timeout (>30s)"
        except FileNotFoundError:
            return False, "mmdc command not found. Install: npm install -g @mermaid-js/mermaid-cli"
        except Exception as e:
            return False, str(e)

    def process_chapter(self, chapter_file):
        """Process a single chapter file and extract all diagrams."""
        print(f"\n{'='*70}")
        print(f"Processing: {chapter_file.name}")
        print(f"{'='*70}")

        # Extract Mermaid blocks
        mermaid_blocks = self.extract_mermaid_blocks(chapter_file)

        if not mermaid_blocks:
            print("No Mermaid diagrams found.")
            return

        print(f"Found {len(mermaid_blocks)} Mermaid diagram(s)\n")

        # Create output directory for this chapter
        chapter_output_dir = self.output_dir / chapter_file.stem.lower()
        chapter_output_dir.mkdir(parents=True, exist_ok=True)

        # Create summary file
        summary_lines = [
            f"# {chapter_file.stem} - Mermaid Diagrams\n",
            f"Total diagrams: {len(mermaid_blocks)}\n\n"
        ]

        # Process each diagram
        for idx, (line_num, mermaid_code) in enumerate(mermaid_blocks, start=1):
            # Generate filename
            base_filename = self.generate_figure_name(chapter_file.stem, idx, mermaid_code)
            mmd_filename = f"{base_filename}.mmd"
            mmd_path = chapter_output_dir / mmd_filename

            # Save .mmd file
            with open(mmd_path, 'w', encoding='utf-8') as f:
                f.write(mermaid_code.strip())

            # Infer description
            diagram_type = self.infer_diagram_type(mermaid_code)

            print(f"[OK] Diagram {idx:2d} | Line {line_num:4d} | Type: {diagram_type:15s} | Saved: {mmd_filename}")

            # Convert to PNG if auto_convert is enabled
            if self.auto_convert:
                success, result = self.convert_mmd_to_svg(mmd_path)
                if success:
                    print(f"  -> Converted to PNG: {result.name}")
                else:
                    print(f"  [X] Conversion failed: {result}")
                    self.conversion_errors.append((mmd_filename, result))

            # Add to summary
            summary_lines.append(f"{idx}. **{base_filename}** (Line {line_num})\n")
            summary_lines.append(f"   - Type: {diagram_type}\n")
            summary_lines.append(f"   - Files: `{mmd_filename}`, `{base_filename}.png`\n\n")

            self.diagrams_extracted += 1

        # Save summary file
        summary_path = chapter_output_dir / "README.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.writelines(summary_lines)

        print(f"\n[OK] Summary saved to: {summary_path}")
        print(f"[OK] All diagrams saved to: {chapter_output_dir}")

    def process_all_chapters(self):
        """Process all chapter markdown files in the docs directory."""
        # Find all chapter files
        chapter_files = sorted(self.docs_dir.glob("CHAPTER_*.md"))

        if not chapter_files:
            print(f"No chapter files found in {self.docs_dir}")
            return

        print(f"\n{'#'*70}")
        print(f"# Mermaid Diagram Extractor - Simple Mode")
        print(f"# Found {len(chapter_files)} chapter file(s)")
        print(f"{'#'*70}")

        # Process each chapter
        for chapter_file in chapter_files:
            self.process_chapter(chapter_file)

        print(f"\n{'='*70}")
        print(f"Extraction Complete!")
        print(f"{'='*70}")
        print(f"Total diagrams extracted: {self.diagrams_extracted}")
        print(f"Output directory: {self.output_dir.absolute()}")

        if self.auto_convert:
            successful = self.diagrams_extracted - len(self.conversion_errors)
            print(f"\nPNG Conversion Results:")
            print(f"  [OK] Successful: {successful}")
            print(f"  [X] Failed: {len(self.conversion_errors)}")

            if self.conversion_errors:
                print(f"\nConversion Errors:")
                for filename, error in self.conversion_errors:
                    print(f"  - {filename}: {error}")
                print(f"\nTo retry failed conversions manually:")
                print(f"  cd docs/images/[chapter_folder]")
                print(f"  mmdc -i [diagram].mmd -o [diagram].png -w 3000 -b white -s 2")
        else:
            print(f"\nNext Steps:")
            print(f"1. Install mermaid-cli if not already installed:")
            print(f"   npm install -g @mermaid-js/mermaid-cli")
            print(f"\n2. Convert .mmd files to high-res PNG:")
            print(f"   cd docs/images/[chapter_folder]")
            print(f"   mmdc -i [diagram].mmd -o [diagram].png -w 3000 -b white -s 2")

        print(f"{'='*70}\n")

    def generate_batch_convert_script(self):
        """Generate batch conversion scripts for Windows and Linux."""
        # Windows batch script
        windows_script = """@echo off
echo Converting Mermaid diagrams to PNG...

for /r %%f in (*.mmd) do (
    echo Converting %%~nf.mmd...
    mmdc -i "%%f" -o "%%~dpnf.png"
)

echo Done!
pause
"""
        windows_path = self.output_dir / "convert_all_windows.bat"
        with open(windows_path, 'w') as f:
            f.write(windows_script)
        print(f"[OK] Created Windows batch script: {windows_path}")

        # Linux/Mac bash script
        bash_script = """#!/bin/bash
echo "Converting Mermaid diagrams to PNG..."

find . -name "*.mmd" -type f | while read file; do
    echo "Converting $(basename "$file")..."
    mmdc -i "$file" -o "${file%.mmd}.png"
done

echo "Done!"
"""
        bash_path = self.output_dir / "convert_all.sh"
        with open(bash_path, 'w') as f:
            f.write(bash_script)

        # Make executable on Unix systems
        try:
            os.chmod(bash_path, 0o755)
        except:
            pass

        print(f"[OK] Created Linux/Mac bash script: {bash_path}")


def main():
    """Main entry point."""
    extractor = SimpleMermaidExtractor(
        docs_dir="docs",
        output_dir="docs/images",
        auto_convert=True  # Automatically convert to high-res PNG
    )

    extractor.process_all_chapters()

    # Generate batch conversion scripts (for backup/manual conversion)
    if not extractor.auto_convert:
        print(f"\nGenerating batch conversion scripts...")
        extractor.generate_batch_convert_script()


if __name__ == "__main__":
    main()
