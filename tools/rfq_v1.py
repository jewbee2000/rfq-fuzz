"""Repository entry point; also available as installed `rfqfuzz`."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from rfqfuzz.v1.cli import main
raise SystemExit(main())
