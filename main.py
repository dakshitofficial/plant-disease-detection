from pathlib import Path

dataset_path = Path("dataset/archive/plantvillage dataset/color")

if not dataset_path.exists():
    print("❌ Dataset path nahi mila!")
else:
    folders = [f for f in dataset_path.iterdir() if f.is_dir()]

    print("✅ Color dataset mil gaya!")
    print("Total classes:", len(folders))

    print("\nClasses:")
    for folder in folders:
        images = list(folder.glob("*.JPG")) + list(folder.glob("*.jpg"))
        print(f"{folder.name} -> {len(images)} images")