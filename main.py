"""
main.py — CLI entry point for the OCR pipeline.

Usage:
    python main.py --image path/to/image.png
    python main.py --image path/to/image.png --mode table --lang en
    python main.py --image path/to/image.png --mode document --lang hi --format csv excel text
"""

import argparse
import sys
import os

# Add project root to path so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline
from config import OUTPUT_DIR, LANG_MAP


def main():
    parser = argparse.ArgumentParser(
        description="OCR Pipeline — Extract text and tables from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --image sample_images/sample_table.png --mode table
  python main.py --image sample_images/sample_document.png --mode document
  python main.py --image photo.jpg --mode auto --lang hi --format csv excel text
        """,
    )

    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Path to the input image file.",
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["auto", "document", "table"],
        default="auto",
        help="Processing mode: auto (detect), document (text), table (structured). Default: auto.",
    )
    parser.add_argument(
        "--lang", "-l",
        choices=list(LANG_MAP.keys()),
        default="en",
        help=f"Language for OCR. Supported: {', '.join(LANG_MAP.keys())}. Default: en.",
    )
    parser.add_argument(
        "--output", "-o",
        default=OUTPUT_DIR,
        help=f"Output directory. Default: {OUTPUT_DIR}",
    )
    parser.add_argument(
        "--format", "-f",
        nargs="+",
        choices=["csv", "excel", "text"],
        default=["csv", "text"],
        help="Output formats. Default: csv text.",
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.isfile(args.image):
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)

    print("=" * 60)
    print("  OCR Pipeline")
    print("=" * 60)
    print(f"  Image:    {args.image}")
    print(f"  Mode:     {args.mode}")
    print(f"  Language: {args.lang}")
    print(f"  Output:   {args.output}")
    print(f"  Formats:  {', '.join(args.format)}")
    print("=" * 60)
    print()

    # Run the pipeline
    result = run_pipeline(
        image_path=args.image,
        mode=args.mode,
        lang=args.lang,
        output_dir=args.output,
        save_formats=args.format,
    )

    # Print summary
    print()
    print("=" * 60)
    print("  Results Summary")
    print("=" * 60)
    print(f"  Mode used:      {result['mode_used']}")
    print(f"  OCR engine:     {result['engine']}")
    if result["confidence"] is not None:
        print(f"  Avg confidence: {result['confidence']:.2%}")
    print(f"  Time:           {result['time_seconds']}s")
    print()

    if result["mode_used"] == "table":
        table = result["table_data"]
        print(f"  Table size: {len(table)} rows × {len(table[0]) if table else 0} cols")
        print()
        # Print first few rows as preview
        print("  Preview (first 5 rows):")
        print("  " + "-" * 50)
        for row in table[:5]:
            print("  | " + " | ".join(cell[:20] for cell in row) + " |")
        if len(table) > 5:
            print(f"  ... and {len(table) - 5} more rows")
    else:
        text = result["text"]
        preview = text[:500]
        print("  Extracted text preview:")
        print("  " + "-" * 50)
        for line in preview.split("\n")[:10]:
            print(f"  {line}")
        if len(text) > 500:
            print(f"  ... ({len(text)} total characters)")

    print()
    print("  Output files:")
    for f in result["output_files"]:
        print(f"    → {f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
