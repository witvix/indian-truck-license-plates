"""
Print dataset stats and draw the plate boxes + plate text on a few sample images.

Usage:
    python examples/show_samples.py indian-truck-license-plates-sample [--n 8] [--out samples_out]

Needs: pip install opencv-python pandas
"""

import argparse
from pathlib import Path

import cv2
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", type=Path, help="Unzipped dataset folder")
    parser.add_argument("--n", type=int, default=8, help="Images to draw")
    parser.add_argument("--out", type=Path, default=Path("samples_out"))
    args = parser.parse_args()

    plates = pd.read_csv(args.root / "plates.csv")
    meta = pd.read_csv(args.root / "metadata.csv")
    print(f"{len(meta)} images, {len(plates)} plates, {plates.state_code.nunique()} state codes")
    print(f"night photos: {(meta.light == 'night').mean():.0%}, two-line plates: {(plates.layout == 'two_line').mean():.0%}")
    print("top states:\n" + plates.state_code.value_counts().head(10).to_string())

    args.out.mkdir(parents=True, exist_ok=True)
    for name, group in list(plates.groupby("image"))[: args.n]:
        img = cv2.imread(str(args.root / "images" / name))
        thickness = max(2, img.shape[1] // 400)
        for p in group.itertuples():
            cv2.rectangle(img, (p.x_min, p.y_min), (p.x_max, p.y_max), (0, 255, 0), thickness)
            cv2.putText(
                img, p.plate_text, (p.x_min, max(30, p.y_min - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2
            )
        cv2.imwrite(str(args.out / name), img)
    print(f"wrote {min(args.n, plates.image.nunique())} annotated images to {args.out}/")


if __name__ == "__main__":
    main()
