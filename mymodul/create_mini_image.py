from PIL import Image


def create_thumbnail(input_path, output_path, size=(100, 100)):
    with Image.open(input_path) as img:
        img.thumbnail(size)
        img.save(output_path)


if __name__ == "__main__":
    create_thumbnail()
