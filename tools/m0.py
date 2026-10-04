"""Repository-local entry point; no editable install or API key needed."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rfqfuzz.cli import main
main()
